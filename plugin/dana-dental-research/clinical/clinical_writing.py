"""
clinical/clinical_writing.py

THE WRITING LAYER — separates internal reasoning structure from clinician-facing language.

The engine reasons in labels: HARD_BLOCKER, INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT,
POTENTIALLY_COMPROMISED, driver_problem_identified. Those labels are load-bearing and stay. What
must not survive to the page is the label itself.

A clinician reading "SUFFICIENCY: PARTIALLY_SUFFICIENT / HARD BLOCKER: YES / DRIVER_PROBLEM:
UNKNOWN" has been handed a debugging trace and asked to do the translation. The system already
did the reasoning; making the reader decode it wastes the work and, worse, obscures the one thing
they came for — what to do about this patient.

So: internal rigour unchanged, external language clinical. Nothing here removes a gate, softens a
safety rule, or changes a verdict. It changes only how a verdict is said.

DEFAULT IS CLINICAL MODE. Audit and technical representations remain available, and are produced
only when asked for.
"""
import re
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# MODES
# ═══════════════════════════════════════════════════════════════════════════════════════════════
CLINICAL = "CLINICAL"      # default — natural clinician-facing consultation
ACADEMIC = "ACADEMIC"      # more references, methodology, evidence strength
TEACHING = "TEACHING"      # explains why each decision is made
AUDIT = "AUDIT"            # internal gates, blockers, provenance, decision profiles
TECHNICAL = "TECHNICAL"    # developer/debug representation

MODES = (CLINICAL, ACADEMIC, TEACHING, AUDIT, TECHNICAL)
DEFAULT_MODE = CLINICAL

MODE_RULE = (
    "CLINICAL is the default and is used unless the clinician explicitly asks for audit, "
    "technical, governance, developer or debug output. Internal state is never exposed by "
    "default; it is translated."
)

MODES_EXPOSING_INTERNALS = (AUDIT, TECHNICAL)


def resolve_mode(requested=None):
    """A mode is used only when explicitly asked for. Anything unrecognised falls back to
    CLINICAL rather than to the most detailed mode."""
    if requested is None:
        return DEFAULT_MODE
    r = str(requested).strip().upper()
    aliases = {"DEBUG": TECHNICAL, "DEVELOPER": TECHNICAL, "GOVERNANCE": AUDIT,
               "TRACE": AUDIT, "DEFAULT": CLINICAL}
    r = aliases.get(r, r)
    return r if r in MODES else DEFAULT_MODE


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# TRANSLATION — internal label to clinical Arabic
# ═══════════════════════════════════════════════════════════════════════════════════════════════
TRANSLATIONS: Dict[str, str] = {
    # Missing-data priority
    "HARD_BLOCKER": "هذه المعلومة ضرورية قبل اتخاذ هذا القرار",
    "DECISION_MODIFIER": "هذا العامل قد يغيّر اختيار العلاج أو ترتيبه",
    "RISK_MODIFIER": "هذا العامل يرفع مستوى الخطورة لكنه لا يمنع العلاج تلقائيًا",
    "PLANNING_REFINER": "هذه المعلومة تساعد في تحسين التصميم النهائي لكنها لا تمنع القرار الحالي",
    "DOCUMENTATION_GAP": "نقص توثيقي روتيني لا يؤثر على القرار الحالي",

    # Sufficiency
    "SUFFICIENT": "المعطيات الحالية كافية لاتخاذ هذا القرار",
    "SUFFICIENT_FOR_CONSERVATIVE_DECISION":
        "المعطيات الحالية كافية لتحديد الاتجاه العلاجي المحافظ",
    "PARTIALLY_SUFFICIENT":
        "المعطيات الحالية كافية لتحديد الاتجاه العام، مع بقاء تفاصيل تحتاج استكمالًا",
    "INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT":
        "المعطيات الحالية كافية لتحديد الاتجاه العلاجي المحافظ، لكنها غير كافية بعد لاعتماد "
        "تحضير نهائي غير قابل للرجوع",
    "INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN":
        "المعطيات الحالية لا تكفي لاعتماد التصميم التعويضي النهائي",
    "INSUFFICIENT_FOR_SURGICAL_DECISION":
        "المعطيات الحالية لا تكفي لاتخاذ قرار جراحي",
    "INSUFFICIENT": "المعطيات الحالية غير كافية لاتخاذ هذا القرار",
    "OUT_OF_SCOPE": "هذه الحالة خارج نطاق تغطية النظام الحالي",

    # Prognosis
    "FAVORABLE": "الإنذار ملائم",
    "GUARDED": "الإنذار متحفّظ",
    "POOR": "الإنذار ضعيف",
    "UNDETERMINED": "لا يمكن تحديد الإنذار بدقة بعد",
    "POTENTIALLY_COMPROMISED":
        "الإنذار قد يكون أقل ملاءمة، ويحتاج تأكيد العوامل المؤثرة",
    "HIGHER_RISK_THAN_COMPARATOR": "الخطورة أعلى مقارنةً بالخيار البديل",

    # Appropriateness
    "BIOLOGICALLY_INDICATED": "هناك استطباب بيولوجي واضح لهذا العلاج",
    "ELECTIVE_BUT_ACCEPTABLE":
        "العلاج اختياري وليس له استطباب بيولوجي، لكنه قد يكون مقبولًا بعد مناقشة التكلفة "
        "البيولوجية والبدائل",
    "ELECTIVE_HIGH_BIOLOGIC_COST":
        "العلاج اختياري وتكلفته البيولوجية مرتفعة، ويحتاج مناقشة صريحة للبدائل قبل المضي",
    "INAPPROPRIATE": "هذا الخيار غير مناسب للحالة كما هي موصوفة",
    "DO_NOT_PROCEED": "لا أنصح بالمضي بهذا الخيار في الوضع الحالي",
    "HOLD": "يجب تأجيل القرار النهائي حتى استكمال التقييم",

    # Relevance
    "RELEVANT": "عامل مؤثر في هذا القرار",
    "CONDITIONALLY_RELEVANT": "عامل يصبح مؤثرًا في حالات محددة",
    "NOT_RELEVANT": "غير مؤثر في هذا القرار",

    # Evidence
    "VERIFIED": "تم التحقق من البيانات الببليوغرافية للمرجع",
    "VERIFIED_WITH_METADATA_DISCREPANCY":
        "تم التحقق من المرجع مع اختلاف في سنة النشر بين المصدرين",
    "PARTIALLY_VERIFIED": "تحقق جزئي من المرجع",
    "NOT_VERIFIED": "لم يتم التحقق من المرجع",
    "RETRACTED": "المرجع مسحوب ولا يصلح لدعم توصية سريرية",
    "NOT ASSESSABLE": "لا يمكن تقدير درجة اليقين من المعطيات المتاحة",
    "DIRECT": "ينطبق مباشرة على هذه الحالة",
    "PARTIALLY DIRECT": "ينطبق جزئيًا على هذه الحالة",
    "INDIRECT": "لا ينطبق مباشرة على هذه الحالة",
}


def translate(label, mode=CLINICAL):
    """Internal label to clinical prose. In AUDIT/TECHNICAL the label is returned unchanged."""
    if resolve_mode(mode) in MODES_EXPOSING_INTERNALS:
        return label
    return TRANSLATIONS.get(label, label)


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# JARGON GUARD
# ═══════════════════════════════════════════════════════════════════════════════════════════════
# Terms that must not appear in a clinician-facing answer. These are implementation names and
# enum values, not clinical concepts — a clinician has no use for them and their presence is the
# clearest single signal that internal state leaked into the output.
FORBIDDEN_IN_CLINICAL = (
    "driver_problem_identified", "blocks_diagnosis", "blocks_prognosis", "case_state.py",
    "prognosis.py", "decision_context.py", "sufficiency engine", "decision profile",
    "suppressed fields", "internal protocol gate", "CLINICAL_INFERENCE", "JUDG enum",
    "HARD_BLOCKER", "DECISION_MODIFIER", "RISK_MODIFIER", "PLANNING_REFINER",
    "DOCUMENTATION_GAP", "PARTIALLY_SUFFICIENT", "INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT",
    "INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN", "INSUFFICIENT_FOR_SURGICAL_DECISION",
    "SUFFICIENT_FOR_CONSERVATIVE_DECISION", "POTENTIALLY_COMPROMISED",
    "HIGHER_RISK_THAN_COMPARATOR", "NOT_RELEVANT", "CONDITIONALLY_RELEVANT",
    "ELECTIVE_BUT_ACCEPTABLE", "ELECTIVE_HIGH_BIOLOGIC_COST", "DO_NOT_PROCEED",
    "may_hard_block", "assess_axis", "sufficiency_for",
)

# Openers that turn a consultation into a status report.
FORBIDDEN_OPENERS = re.compile(
    r"^\s*(case state\s*:|sufficiency\s*:|data sufficiency\s*:|red[- ]flag(s)?\s*:|"
    r"\d+\s*/\s*\d+\s*fields|safety gate|current decision\s*:\s*(do not proceed|blocked)|"
    r"status\s*:|verdict\s*:)", re.I)

TIER_CODE = re.compile(r"\bT[0-4]\b")


def check_clinical_prose(text, mode=CLINICAL):
    """
    Verify a clinician-facing answer contains no internal engine vocabulary and does not open
    like a status report. In AUDIT/TECHNICAL modes the check is not applied — internals are the
    point there.
    """
    mode = resolve_mode(mode)
    if mode in MODES_EXPOSING_INTERNALS:
        return {"result": "PASS", "mode": mode, "findings": [],
                "note": "Internal vocabulary is expected in this mode."}

    findings = []
    for term in FORBIDDEN_IN_CLINICAL:
        if re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", text):
            findings.append({"kind": "INTERNAL_JARGON", "term": term,
                             "problem": f"{term!r} is engine vocabulary, not clinical language.",
                             "suggestion": TRANSLATIONS.get(term,
                                                            "Express the meaning, not the label.")})
    first_line = (text.strip().split("\n") or [""])[0]
    if FORBIDDEN_OPENERS.search(first_line):
        findings.append({"kind": "STATUS_REPORT_OPENER", "term": first_line[:60],
                         "problem": "The answer opens with a status line rather than the clinical "
                                    "message.",
                         "suggestion": "Open with what you think, why, and what should happen next."})
    for m in TIER_CODE.finditer(text):
        findings.append({"kind": "INTERNAL_TIER_CODE", "term": m.group(0),
                         "problem": "Irreversibility tier codes are internal.",
                         "suggestion": "Describe the biological cost in words."})
    return {"result": "FAIL" if findings else "PASS", "mode": mode, "findings": findings}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════════════════════
SECTIONS = (
    "التقييم السريري",
    "المشكلة الرئيسية",
    "التشخيص التفريقي",
    "تفسير المعطيات الحالية",
    "القرار السريري الحالي",
    "خطة العلاج وتسلسلها",
    "البدائل",
    "ما الذي قد يغيّر القرار",
    "الإنذار",
    "الأدلة العلمية وحدودها",
    "الخلاصة السريرية",
)

# Sections a short answer may legitimately omit. The decision and its rationale may never be.
ALWAYS_REQUIRED = ("المشكلة الرئيسية", "القرار السريري الحالي")

STRUCTURE_RULE = (
    "Sections are used where they help. A simple question gets a short answer; a complex "
    "multidisciplinary case may use all of them. Mechanically emitting eleven headings for a "
    "one-line question is the same failure as emitting forty missing-data fields."
)

CALIBRATED_VERBS = ("تشير المعطيات إلى", "يرفع الاحتمال", "يتوافق مع", "يُرجَّح",
                    "قد يكون عاملًا مساهمًا", "تدعمه الأدلة", "لا يمكن إثبات",
                    "لا يوجد ما يبرر افتراض")
OVERCLAIMING_VERBS = ("يثبت", "يؤكد قطعًا", "دائمًا", "حتمًا", "السبب المباشر", "الحل الوحيد")

RESPECTFUL_PREFERENCE = (
    "تفضيل المريض مفهوم، لكنه لا يشكل بحد ذاته استطبابًا سريريًا.",
    "يمكن احترام الهدف الجمالي مع مناقشة التكلفة البيولوجية والبدائل.",
    "إذا اختار المريض المسار الاختياري بعد موافقة مستنيرة، فيجب توثيق ذلك بوضوح.",
)
ADVERSARIAL_PREFERENCE = ("طلب المريض غير مقبول", "المريضة مصرة", "يجب رفض طلبها")


# Negation particles. A negated absolute is calibrated language, not an overclaim: "لا يثبت"
# ("does not prove") is exactly the phrasing the calibration rule asks for, and flagging it
# punishes the correct sentence. Detected by looking at what immediately precedes the verb.
NEGATIONS = ("لا ", "ولا ", "لم ", "ولم ", "لن ", "ليس ", "وليس ", "غير ")


def _is_negated(text, index):
    prefix = text[max(0, index - 12):index]
    return any(prefix.endswith(n) for n in NEGATIONS)


def check_claim_calibration(text):
    """
    Flags absolute Arabic verbs where calibrated language belongs.

    A negated absolute is not an overclaim — "لا يثبت" is the calibrated form — so negation is
    checked before a finding is raised.
    """
    findings = []
    for verb in OVERCLAIMING_VERBS:
        start = 0
        while True:
            i = text.find(verb, start)
            if i == -1:
                break
            start = i + len(verb)
            if _is_negated(text, i):
                continue
            findings.append({"kind": "OVERCLAIM", "term": verb,
                             "context": text[max(0, i - 40):i + 40].replace("\n", " "),
                             "suggestion": f"استخدم لغة معايرة مثل: {CALIBRATED_VERBS[0]}"})
            break
    for phrase in ADVERSARIAL_PREFERENCE:
        if phrase in text:
            findings.append({"kind": "ADVERSARIAL_TOWARD_PATIENT", "term": phrase,
                             "suggestion": RESPECTFUL_PREFERENCE[0]})
    return {"result": "FAIL" if findings else "PASS", "findings": findings}


class ClinicalConsultation:
    """
    A clinician-facing answer.

    `internal` holds the engine state that produced it — kept, never printed in CLINICAL mode,
    and rendered in full in AUDIT mode. That is the whole design: one object, two readings.
    """

    def __init__(self, assessment=None, main_problem=None, differential=None,
                 interpretation=None, current_decision=None, plan=None, alternatives=None,
                 what_would_change=None, prognosis=None, evidence=None, conclusion=None,
                 internal=None):
        self.body = {
            "التقييم السريري": assessment,
            "المشكلة الرئيسية": main_problem,
            "التشخيص التفريقي": differential,
            "تفسير المعطيات الحالية": interpretation,
            "القرار السريري الحالي": current_decision,
            "خطة العلاج وتسلسلها": plan,
            "البدائل": alternatives,
            "ما الذي قد يغيّر القرار": what_would_change,
            "الإنذار": prognosis,
            "الأدلة العلمية وحدودها": evidence,
            "الخلاصة السريرية": conclusion,
        }
        self.internal = internal or {}

    def render(self, mode=CLINICAL):
        mode = resolve_mode(mode)
        if mode == TECHNICAL:
            return {"mode": mode, "internal": self.internal, "body": self.body}
        if mode == AUDIT:
            lines = [self._prose(), "", "---", "", "### Audit trace", ""]
            for k, v in self.internal.items():
                lines.append(f"- **{k}**: {v}")
            return "\n".join(lines)
        return self._prose()

    def _prose(self):
        out = []
        for section in SECTIONS:
            value = self.body.get(section)
            if not value:
                continue
            out.append(f"**{section}**")
            out.append(value.strip())
            out.append("")
        return "\n".join(out).strip()

    def validate(self, mode=CLINICAL):
        problems = []
        for required in ALWAYS_REQUIRED:
            if not self.body.get(required):
                problems.append(f"القسم المطلوب غائب: {required}")
        prose = self._prose()
        jargon = check_clinical_prose(prose, mode)
        calib = check_claim_calibration(prose)
        # The decision must appear early — within the first third of the answer.
        decision_text = self.body.get("القرار السريري الحالي") or ""
        idx = prose.find(decision_text) if decision_text else -1
        decision_early = 0 <= idx <= max(len(prose) // 2, 400)
        if decision_text and not decision_early:
            problems.append("القرار السريري لا يظهر مبكرًا في الإجابة.")
        return {
            "result": ("FAIL" if problems or jargon["findings"] or calib["findings"] else "PASS"),
            "problems": problems,
            "jargon": jargon["findings"],
            "calibration": calib["findings"],
            "decision_appears_early": decision_early,
            "sections_used": [s for s in SECTIONS if self.body.get(s)],
            "structure_rule": STRUCTURE_RULE,
        }


def evidence_line(study_type, verification, certainty, directness):
    """The compact evidence line permitted by §67 — one line, after the clinical paragraph, not
    metadata scattered through it."""
    return f"Evidence: {study_type} · {verification} · {certainty} certainty · {directness}"

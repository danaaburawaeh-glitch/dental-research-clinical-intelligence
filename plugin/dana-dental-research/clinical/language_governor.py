"""
clinical/language_governor.py

WORDING GOVERNANCE FOR CLINICAL OUTPUT.

Clinical language carries force. "Recommended" invites a judgement; "mandatory" removes one. When
a system writes "mandatory" about something that is merely usual practice, it is not being careful
— it is overstating what is known, and it puts a clinician in the position of either deferring to
a rule that does not exist or learning to discount the system's wording entirely.

This module governs five failure modes that all reduce to the same thing: saying something more
strongly, or more categorically, than the underlying basis supports.

    1. MANDATORY LANGUAGE       — absolute words used without an absolute basis
    2. RISK -> CONTRAINDICATION — a risk modifier written as a prohibition
    3. DETERMINISTIC CLAIMS     — "always causes", "necessarily removes", "will fail"
    4. FALSE REVERSIBILITY      — "fully reversible" for things that are not
    5. CROSS-STUDY NUMBERS      — figures from different studies compared as if head-to-head

Every check returns findings, and every finding names the calibrated alternative. A governor that
only forbids produces stilted output; one that offers the right phrasing produces better writing.

WHAT THIS IS NOT
----------------
It is not a style filter, and it does not soften genuine safety language. An absolute word with a
genuine basis passes untouched — see JUSTIFICATIONS. "Do not place a definitive restoration on an
untreated active infection" is a real rule and reads like one.
"""
import re
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# 1. Mandatory language
# ---------------------------------------------------------------------------
ABSOLUTE_TERMS = (
    "mandatory", "required", "must", "contraindicated", "prohibited", "never", "always",
    "essential", "cannot proceed", "compulsory", "obligatory",
)

# The only bases on which an absolute word may stand.
BASIS_PROTOCOL = "A_EXPLICIT_PROTOCOL_RULE"
BASIS_IFU = "B_MANUFACTURER_IFU"
BASIS_SAFETY_STANDARD = "C_ACCEPTED_SAFETY_STANDARD"
BASIS_UNSAFE_WITHOUT = "D_GENUINELY_UNSAFE_WITHOUT_IT"
BASIS_NEAR_ABSOLUTE_EVIDENCE = "E_EVIDENCE_SUPPORTS_NEAR_ABSOLUTE_RULE"
JUSTIFICATIONS = (BASIS_PROTOCOL, BASIS_IFU, BASIS_SAFETY_STANDARD, BASIS_UNSAFE_WITHOUT,
                  BASIS_NEAR_ABSOLUTE_EVIDENCE)

CALIBRATED_ALTERNATIVES = {
    "mandatory": "recommended / strongly recommended",
    "required": "recommended / should be considered",
    "must": "should / is appropriate to",
    "contraindicated": "a significant risk modifier / relative contraindication in this context",
    "prohibited": "not appropriate here / inadvisable without addressing X",
    "never": "generally not / rarely appropriate",
    "always": "generally / in most cases",
    "essential": "important / strongly preferred",
    "cannot proceed": "should not proceed until X is established",
    "compulsory": "strongly recommended",
    "obligatory": "strongly recommended",
}

CALIBRATED_VOCABULARY = (
    "recommended", "strongly recommended", "should be considered", "appropriate", "preferred",
    "risk modifier", "conditional", "may be indicated", "depends on",
)

MANDATORY_RULE = (
    "An absolute word may be used only on an explicit protocol rule, a manufacturer IFU "
    "requirement, an accepted safety standard, a procedure that is genuinely unsafe without the "
    "step, or evidence supporting a near-absolute rule. An evidence-supported association is "
    "never promoted into a mandatory protocol rule."
)


class LanguageFinding:
    def __init__(self, kind, term, context, problem, suggestion, severity="MAJOR"):
        self.kind = kind
        self.term = term
        self.context = context
        self.problem = problem
        self.suggestion = suggestion
        self.severity = severity

    def to_dict(self):
        return {"kind": self.kind, "term": self.term, "context": self.context,
                "problem": self.problem, "suggestion": self.suggestion, "severity": self.severity}


def _context(text, span, width=70):
    a = max(0, span[0] - width // 2)
    b = min(len(text), span[1] + width)
    return ("…" if a else "") + text[a:b].replace("\n", " ").strip() + ("…" if b < len(text) else "")


def check_absolute_language(text, justified_terms=None):
    """
    justified_terms: {term_or_phrase: basis} for absolutes that genuinely have one of the five
    bases. A term is justified only where the caller can name which basis applies, so the
    justification is auditable rather than assumed.
    """
    justified = {k.lower(): v for k, v in (justified_terms or {}).items()}
    for term, basis in justified.items():
        if basis not in JUSTIFICATIONS:
            raise ValueError(
                f"{basis!r} is not one of the five permitted bases {JUSTIFICATIONS}. An absolute "
                f"word without a nameable basis is exactly what this check exists to catch.")
    findings = []
    lowered = text.lower()
    for term in ABSOLUTE_TERMS:
        for m in re.finditer(rf"\b{re.escape(term)}\b", lowered):
            ctx = _context(text, m.span())
            if any(j in ctx.lower() for j in justified):
                continue
            findings.append(LanguageFinding(
                "ABSOLUTE_LANGUAGE", term, ctx,
                problem=(f"{term!r} states an absolute. Unless one of the five bases applies, this "
                         f"overstates what is known and converts a recommendation into a rule."),
                suggestion=f"Use: {CALIBRATED_ALTERNATIVES[term]}."))
    return findings


# ---------------------------------------------------------------------------
# 2. Risk factor is not a contraindication
# ---------------------------------------------------------------------------
RISK_NOT_CONTRAINDICATION = {
    "thin gingival phenotype": ("a high esthetic-risk modifier for immediate implant placement",
                                "It raises the risk of mid-facial recession and changes whether "
                                "connective tissue grafting is considered. It does not exclude "
                                "the patient from immediate placement."),
    "periapical lesion": ("a factor requiring debridement and assessment",
                          "A periapical lesion does not automatically contraindicate immediate "
                          "implant placement; outcomes depend on infection control, debridement "
                          "and primary stability."),
    "smoking": ("a risk modifier affecting healing and long-term outcome",
                "Smoking changes risk, consent and maintenance planning. It is not an automatic "
                "prohibition."),
    "diabetes": ("a risk modifier whose weight depends on glycaemic control and the procedure",
                 "Well-controlled diabetes is a different risk from uncontrolled diabetes. Neither "
                 "is an automatic prohibition."),
    "bruxism": ("a risk modifier affecting material choice, design and maintenance",
                "Bruxism is not an automatic contraindication to ceramic restorations."),
    "parafunction": ("a risk modifier affecting design and consent", ""),
    "thin facial plate": ("an anatomic and esthetic risk factor",
                          "A facial plate under 1 mm is an anatomic risk finding. It is not a "
                          "diagnosis of peri-implant disease."),
}

CONTRAINDICATION_PATTERN = re.compile(
    r"\b(contraindicat\w*|prohibit\w*|preclud\w*|rules? out|excludes?|disqualif\w*|"
    r"not a candidate|cannot have|must not (?:have|receive|undergo))\b", re.I)


def check_risk_not_contraindication(text):
    """Flags a passage where a known risk modifier sits near contraindication language."""
    findings = []
    lowered = text.lower()
    for risk, (correct_role, note) in RISK_NOT_CONTRAINDICATION.items():
        for m in re.finditer(re.escape(risk), lowered):
            window = lowered[max(0, m.start() - 220): m.end() + 220]
            hit = CONTRAINDICATION_PATTERN.search(window)
            if hit:
                findings.append(LanguageFinding(
                    "RISK_AS_CONTRAINDICATION", risk, _context(text, m.span()),
                    problem=(f"{risk!r} appears alongside {hit.group(0)!r}. A risk factor must not "
                             f"become a contraindication automatically."),
                    suggestion=(f"State {risk} as {correct_role}. {note}").strip(),
                    severity="CRITICAL"))
    return findings


# ---------------------------------------------------------------------------
# 3. Deterministic claims
# ---------------------------------------------------------------------------
DETERMINISTIC_PATTERNS = (
    (re.compile(r"\bevery\s+(crown\s+)?replacement\s+\w*\s*(removes|necessarily)", re.I),
     "Crown removal MAY result in additional structural loss or core damage, depending on "
     "technique, material and the state of the underlying core."),
    (re.compile(r"\bnecessarily\s+removes\b", re.I),
     "Use 'may result in' — the amount of structure lost depends on technique and material."),
    (re.compile(r"\bmoves the tooth closer to non-?restorability\b", re.I),
     "Repeated restorative intervention CAN progressively reduce structural reserve and MAY "
     "increase future restorative complexity."),
    (re.compile(r"\b(will|shall)\s+(fail|debond|fracture)\b", re.I),
     "Use 'is at increased risk of' — a risk is not a prediction of an individual outcome."),
    (re.compile(r"\bguarantee(s|d)?\b", re.I),
     "No clinical outcome is guaranteed; state the expected range and its uncertainty."),
    (re.compile(r"\binevitabl\w+\b", re.I),
     "Use 'commonly' or 'frequently' unless the outcome genuinely cannot be avoided."),
)


def check_deterministic_language(text):
    findings = []
    for pattern, suggestion in DETERMINISTIC_PATTERNS:
        for m in pattern.finditer(text):
            findings.append(LanguageFinding(
                "DETERMINISTIC_CLAIM", m.group(0), _context(text, m.span()),
                problem="States as inevitable something that varies with technique, material and "
                        "circumstance.",
                suggestion=suggestion))
    return findings


# ---------------------------------------------------------------------------
# 4. Reversibility language
# ---------------------------------------------------------------------------
NOT_FULLY_REVERSIBLE = {
    "internal bleaching": ("minimally invasive / structure-preserving / conservative",
                           "Internal bleaching requires access through the coronal structure and "
                           "alters the tooth. It is conservative; it is not reversible."),
    "botox": ("temporary / time-limited / non-surgical / pharmacologic",
              "Botulinum toxin wears off; that makes it temporary, not reversible. It is not "
              "equivalent to a removable mock-up, which can be taken off at will."),
    "botulinum": ("temporary / time-limited / non-surgical / pharmacologic",
                  "Botulinum toxin wears off; that makes it temporary, not reversible."),
    "equilibration": ("a simulation and planning aid",
                      "Equilibration performed on mounted casts is a simulation, not a "
                      "therapeutic reversible trial — nothing was done to the patient, so nothing "
                      "about the patient's response has been tested."),
    "mock-up": ("a communication and planning aid for form, length and proportion",
                "A digital or resin mock-up is not proof of clinical outcome, and does not "
                "reliably preview final ceramic optical behaviour or shade."),
}

REVERSIBLE_PATTERN = re.compile(r"\b(fully|completely|entirely|totally)\s+reversible\b", re.I)


def check_reversibility_language(text):
    findings = []
    lowered = text.lower()
    for m in REVERSIBLE_PATTERN.finditer(text):
        window = lowered[max(0, m.start() - 200): m.end() + 200]
        subject = next((k for k in NOT_FULLY_REVERSIBLE if k in window), None)
        alt, note = NOT_FULLY_REVERSIBLE.get(subject, ("conservative / minimally invasive", ""))
        findings.append(LanguageFinding(
            "FALSE_REVERSIBILITY", m.group(0), _context(text, m.span()),
            problem=(f"'{m.group(0)}' claims complete reversibility"
                     + (f" for {subject}. {note}" if subject else ". Few clinical interventions "
                        "are fully reversible; most are conservative or temporary.")),
            suggestion=f"Use: {alt}.", severity="CRITICAL" if subject else "MAJOR"))
    return findings


# ---------------------------------------------------------------------------
# 5. Cross-study numeric comparison
# ---------------------------------------------------------------------------
_PCT = r"\d+(?:\.\d+)?\s?%"
CROSS_STUDY_COMPARISON = re.compile(
    rf"({_PCT})[^.]{{0,60}}?\b(?:vs\.?|versus|compared (?:with|to))\b[^.]{{0,60}}?({_PCT})", re.I)
ZERO_EVENT_PATTERN = re.compile(
    r"\b(?:0|zero|no)\s+(?:recession|failures?|complications?|events?)\b|\b100\s?%\s+(?:survival|success)\b",
    re.I)

NO_DIRECT_COMPARISON_TEXT = (
    "The available comparative evidence does not support a categorical claim of superiority."
)


def check_numeric_comparison(text, head_to_head_supported=False):
    """
    Flags two percentages compared across a 'vs' unless the caller states that a genuine
    head-to-head comparison exists in the evidence.

    Crown 96% against veneer 90%, or endodontic 91% against implant 89%, are figures from
    different designs, populations and follow-up periods. Setting them beside a 'vs' invites a
    patient-level conclusion the evidence never made.
    """
    findings = []
    if not head_to_head_supported:
        for m in CROSS_STUDY_COMPARISON.finditer(text):
            findings.append(LanguageFinding(
                "CROSS_STUDY_NUMERIC_COMPARISON", m.group(0), _context(text, m.span()),
                problem=("Two outcome figures are compared directly. Unless they come from a "
                         "genuine head-to-head comparison, they differ in design, population, "
                         "follow-up and intervention, and the comparison is not one the evidence "
                         "made."),
                suggestion=NO_DIRECT_COMPARISON_TEXT, severity="CRITICAL"))
    return findings


def check_zero_event_language(text, limitation_stated=False):
    findings = []
    for m in ZERO_EVENT_PATTERN.finditer(text):
        if limitation_stated:
            continue
        findings.append(LanguageFinding(
            "ZERO_EVENT_OVERCLAIM", m.group(0), _context(text, m.span()),
            problem=("A zero-event or 100% figure from a limited dataset is being presented as "
                     "though it predicts this patient's outcome. Zero events in a small, short "
                     "study is weak evidence of a low rate, not evidence of no risk."),
            suggestion=("Use: 'no events were reported in the limited studies available', and "
                        "state the sample size and follow-up that produced it."),
            severity="CRITICAL"))
    return findings


# ---------------------------------------------------------------------------
# 6. Claim-category separation
# ---------------------------------------------------------------------------
PROTOCOL_RULE = "PROTOCOL RULE"
EVIDENCE_SUPPORTED = "EVIDENCE-SUPPORTED RECOMMENDATION"
CLINICAL_JUDGMENT = "CLINICAL JUDGMENT"
PATIENT_PREFERENCE = "PATIENT PREFERENCE"
UNKNOWN_BASIS = "UNKNOWN"
CLAIM_CATEGORIES = (PROTOCOL_RULE, EVIDENCE_SUPPORTED, CLINICAL_JUDGMENT, PATIENT_PREFERENCE,
                    UNKNOWN_BASIS)

CATEGORY_SEPARATION_RULE = (
    "PROTOCOL RULE, EVIDENCE-SUPPORTED RECOMMENDATION, CLINICAL JUDGMENT, PATIENT PREFERENCE and "
    "UNKNOWN are five different things. None may masquerade as another. A clinical judgement "
    "presented as a protocol rule borrows an authority it does not have; an evidence-supported "
    "association presented as a protocol rule does the same."
)


class ClinicalStatement:
    """One clinical statement, its basis category, and — where the basis is evidence — its links."""

    def __init__(self, text, category, source=None, evidence=None, absolute_basis=None):
        if category not in CLAIM_CATEGORIES:
            raise ValueError(f"{category!r} is not one of {CLAIM_CATEGORIES}")
        if category == PROTOCOL_RULE and not source:
            raise ValueError(
                "A PROTOCOL RULE must name the protocol it comes from. Without a named source it "
                "is a clinical judgement wearing a protocol's authority.")
        if category == EVIDENCE_SUPPORTED and not evidence:
            raise ValueError(
                "An EVIDENCE-SUPPORTED RECOMMENDATION must carry its evidence links (citation, "
                "verification state, study type, certainty, directness).")
        self.text = text
        self.category = category
        self.source = source
        self.evidence = evidence
        self.absolute_basis = absolute_basis

    def check_language(self):
        justified = {}
        if self.absolute_basis:
            for term in ABSOLUTE_TERMS:
                if re.search(rf"\b{re.escape(term)}\b", self.text, re.I):
                    justified[term] = self.absolute_basis
        findings = check_absolute_language(self.text, justified)
        findings += check_deterministic_language(self.text)
        findings += check_reversibility_language(self.text)
        findings += check_risk_not_contraindication(self.text)
        return findings

    def to_dict(self):
        return {"statement": self.text, "basis_category": self.category, "source": self.source,
                "evidence": self.evidence, "absolute_basis": self.absolute_basis,
                "language_findings": [f.to_dict() for f in self.check_language()]}


# ---------------------------------------------------------------------------
# 7. Elective is not the same as inappropriate
# ---------------------------------------------------------------------------
BIOLOGICALLY_INDICATED = "BIOLOGICALLY_INDICATED"
ELECTIVE_BUT_ACCEPTABLE = "ELECTIVE_BUT_ACCEPTABLE"
ELECTIVE_HIGH_BIOLOGIC_COST = "ELECTIVE_HIGH_BIOLOGIC_COST"
INAPPROPRIATE = "INAPPROPRIATE"
DO_NOT_PROCEED = "DO_NOT_PROCEED"
APPROPRIATENESS = (BIOLOGICALLY_INDICATED, ELECTIVE_BUT_ACCEPTABLE, ELECTIVE_HIGH_BIOLOGIC_COST,
                   INAPPROPRIATE, DO_NOT_PROCEED)

ELECTIVE_RULE = (
    "A treatment that is not biologically indicated may still be ethically acceptable. Elective "
    "is not a synonym for inappropriate: where the patient understands the trade-offs, "
    "alternatives have been discussed, expectations are realistic, the risks are acceptable and "
    "consent is documented, an elective request is a legitimate clinical choice."
)

CONSENT_CONDITIONS = ("patient_understands_tradeoffs", "alternatives_discussed",
                      "expectations_realistic", "risks_acceptable", "consent_documented")


def classify_appropriateness(biologically_indicated, biologic_cost="moderate",
                             consent_conditions=None, unsafe=False, wrong_etiology=False):
    """
    consent_conditions: set of CONSENT_CONDITIONS that actually hold.

    `wrong_etiology` is separated from `unsafe` deliberately. The most serious risk in several
    esthetic cases is not that the procedure goes wrong but that a technically flawless procedure
    is aimed at the wrong cause — see the diagnosis-precedes-treatment rule.
    """
    met = set(consent_conditions or ())
    if unsafe:
        return {"classification": DO_NOT_PROCEED,
                "reason": "The procedure is unsafe or inappropriate for this patient as assessed.",
                "conditions_met": sorted(met), "elective_rule": ELECTIVE_RULE}
    if wrong_etiology:
        return {"classification": INAPPROPRIATE,
                "reason": ("The proposed treatment does not address the established cause. "
                           "Treatment follows diagnosis; an irreversible procedure aimed at the "
                           "wrong etiology is the principal risk here, not procedural "
                           "complication."),
                "conditions_met": sorted(met), "elective_rule": ELECTIVE_RULE}
    if biologically_indicated:
        return {"classification": BIOLOGICALLY_INDICATED,
                "reason": "There is a biological indication independent of patient preference.",
                "conditions_met": sorted(met), "elective_rule": ELECTIVE_RULE}

    missing = [c for c in CONSENT_CONDITIONS if c not in met]
    if missing:
        return {"classification": ELECTIVE_HIGH_BIOLOGIC_COST if biologic_cost == "high"
                else ELECTIVE_BUT_ACCEPTABLE,
                "reason": ("Elective. Not yet fully consented: "
                           + ", ".join(missing) + ". This is a consent gap to close, not a reason "
                           "to refuse the request."),
                "conditions_met": sorted(met), "outstanding_conditions": missing,
                "elective_rule": ELECTIVE_RULE}
    return {"classification": ELECTIVE_HIGH_BIOLOGIC_COST if biologic_cost == "high"
            else ELECTIVE_BUT_ACCEPTABLE,
            "reason": ("Elective, and appropriately consented. Not biologically indicated, which "
                       "is a statement about the indication — not a prohibition."),
            "conditions_met": sorted(met), "outstanding_conditions": [],
            "elective_rule": ELECTIVE_RULE}


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------
PASS = "PASS"
FAIL = "FAIL"


def review(text, justified_terms=None, head_to_head_supported=False, limitation_stated=False):
    """Run every wording check over a block of clinical output."""
    findings = (check_absolute_language(text, justified_terms)
                + check_risk_not_contraindication(text)
                + check_deterministic_language(text)
                + check_reversibility_language(text)
                + check_numeric_comparison(text, head_to_head_supported)
                + check_zero_event_language(text, limitation_stated))
    critical = [f for f in findings if f.severity == "CRITICAL"]
    return {
        "result": FAIL if findings else PASS,
        "critical_count": len(critical),
        "findings": [f.to_dict() for f in findings],
        "mandatory_rule": MANDATORY_RULE,
        "category_separation_rule": CATEGORY_SEPARATION_RULE,
    }

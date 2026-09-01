"""
clinical/clinical_reasoning.py

Reasoning structure: what a diagnostic tool can establish, what is actually driving a case, how
irreversibility is graded, how proportionate a safety note should be, and the order an answer is
delivered in.

These are separate concerns held in one module because they share a single failure mode: an
answer that is individually correct in every part and wrong as a whole. A CBCT report that is
accurate but treated as decisive. A set of technically sound restorations that worsen the smile
they were meant to improve. A safety sweep that is complete and buries the clinical answer.
"""
from typing import Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# 1. DIAGNOSTIC CERTAINTY HIERARCHY
# ═══════════════════════════════════════════════════════════════════════════════════════════════
CLINICAL_EXAMINATION = "clinical_examination"
HISTORY = "history"
IMAGING = "imaging"
ADJUNCTIVE_TEST = "adjunctive_test"
INTRAOPERATIVE = "intraoperative_findings"
SPECIALIST_ASSESSMENT = "specialist_assessment"

DIAGNOSTIC_HIERARCHY = (HISTORY, CLINICAL_EXAMINATION, IMAGING, ADJUNCTIVE_TEST,
                        INTRAOPERATIVE, SPECIALIST_ASSESSMENT)

DECISIVE = "DECISIVE"
STRONGLY_INFORMATIVE = "STRONGLY_INFORMATIVE"
INFORMATIVE = "INFORMATIVE"
ADJUNCT_ONLY = "ADJUNCT_ONLY"
CONTRIBUTORY_STRENGTHS = (DECISIVE, STRONGLY_INFORMATIVE, INFORMATIVE, ADJUNCT_ONLY)

HIERARCHY_RULE = (
    "No diagnostic tool is described as decisive unless it genuinely is. Most tools shift a "
    "probability; they do not settle a question. A negative result on a test that cannot exclude "
    "a condition is not a negative finding about the condition."
)


class DiagnosticTool:
    def __init__(self, name, tier, strength, can_establish=(), cannot_establish=(),
                 negative_result_meaning=None, note=None):
        if tier not in DIAGNOSTIC_HIERARCHY:
            raise ValueError(f"{tier!r} is not in {DIAGNOSTIC_HIERARCHY}")
        if strength not in CONTRIBUTORY_STRENGTHS:
            raise ValueError(f"{strength!r} is not in {CONTRIBUTORY_STRENGTHS}")
        self.name = name
        self.tier = tier
        self.strength = strength
        self.can_establish = tuple(can_establish)
        self.cannot_establish = tuple(cannot_establish)
        self.negative_result_meaning = negative_result_meaning
        self.note = note

    @property
    def is_decisive(self):
        return self.strength == DECISIVE

    def to_dict(self):
        return {"tool": self.name, "tier": self.tier, "strength": self.strength,
                "can_establish": list(self.can_establish),
                "cannot_establish": list(self.cannot_establish),
                "negative_result_meaning": self.negative_result_meaning, "note": self.note,
                "is_decisive": self.is_decisive}


TOOLS: Dict[str, DiagnosticTool] = {
    "cbct_vrf": DiagnosticTool(
        "CBCT for suspected vertical root fracture", IMAGING, INFORMATIVE,
        can_establish=("presence of a visible fracture line in some cases",
                       "bone loss patterns that raise or lower suspicion"),
        cannot_establish=("exclusion of a vertical root fracture",),
        negative_result_meaning=(
            "A negative CBCT does not reliably exclude a vertical root fracture. Beam-hardening "
            "and artefact from existing root fillings and posts limit sensitivity, and a fracture "
            "narrower than the voxel resolution may not be visible at all. CBCT may increase or "
            "decrease suspicion; it does not rule the diagnosis out."),
        note="Direct visualisation — surgical exposure, or examination after extraction — remains "
             "the confirmatory finding."),

    "cbct_facial_wall": DiagnosticTool(
        "CBCT for implant facial wall assessment", IMAGING, STRONGLY_INFORMATIVE,
        can_establish=("approximate facial bone thickness and level before extraction",),
        cannot_establish=("the actual state of the socket wall after extraction",),
        negative_result_meaning=(
            "CBCT informs risk before the tooth is removed. Direct inspection of the socket after "
            "extraction may change the plan, and the plan should be built to allow that."),
        note="A pre-operative estimate is planning information, not a commitment."),

    "t_scan": DiagnosticTool(
        "Digital occlusal analysis (e.g. T-Scan)", ADJUNCTIVE_TEST, ADJUNCT_ONLY,
        can_establish=("relative timing and distribution of occlusal contacts as recorded by the "
                       "sensor",),
        cannot_establish=("that an occlusal contact is causing a patient's pain",
                          "a diagnosis of temporomandibular disorder"),
        negative_result_meaning=(
            "An occlusal recording describes contacts. It does not establish that any contact is "
            "responsible for symptoms."),
        note="An adjunct. Not a diagnostic gold standard and not objective proof of pain "
             "causation."),

    "mounted_casts": DiagnosticTool(
        "Mounted casts and centric relation records", ADJUNCTIVE_TEST, INFORMATIVE,
        can_establish=("static and simulated dynamic relationships for planning",),
        cannot_establish=("the patient's clinical response to an occlusal change",),
        negative_result_meaning=None,
        note="An adjunct where indicated, not a universal prerequisite. Equilibration performed "
             "on mounted casts is a simulation and planning aid — nothing has been done to the "
             "patient, so nothing about the patient's response has been tested."),

    "diagnostic_mockup": DiagnosticTool(
        "Diagnostic mock-up (resin or digital)", ADJUNCTIVE_TEST, INFORMATIVE,
        can_establish=("form", "length", "proportion", "smile integration", "phonetics",
                       "patient communication and consent"),
        cannot_establish=("final ceramic optical behaviour", "final shade", "translucency",
                          "the definitive esthetic result"),
        negative_result_meaning=None,
        note="For shade, use dedicated shade communication, try-in pastes and ceramic try-in "
             "evaluation. A resin mock-up does not preview ceramic optics."),

    "emg": DiagnosticTool(
        "Surface electromyography", ADJUNCTIVE_TEST, ADJUNCT_ONLY,
        can_establish=("recorded muscle electrical activity",),
        cannot_establish=("a diagnosis of temporomandibular disorder", "pain causation"),
        note="An adjunct. Not a diagnostic gate."),

    "periodontal_charting": DiagnosticTool(
        "Full periodontal charting", CLINICAL_EXAMINATION, STRONGLY_INFORMATIVE,
        can_establish=("probing depths", "bleeding on probing", "recession",
                       "clinical attachment level", "furcation and mobility"),
        cannot_establish=("grade without additional history and radiographic bone loss over time",),
        note="The basis for formal staging and grading."),
}


def tool(name) -> DiagnosticTool:
    if name not in TOOLS:
        raise ValueError(f"Unknown diagnostic tool {name!r}. Known: {sorted(TOOLS)}")
    return TOOLS[name]


def check_tool_claim(name, claimed_strength):
    """Refuses a claim that a tool is more decisive than it is."""
    t = tool(name)
    rank = {s: i for i, s in enumerate(reversed(CONTRIBUTORY_STRENGTHS))}
    overclaimed = rank.get(claimed_strength, 0) > rank.get(t.strength, 0)
    return {
        "tool": t.name, "actual_strength": t.strength, "claimed_strength": claimed_strength,
        "overclaimed": overclaimed,
        "reason": (f"{t.name} is {t.strength}, not {claimed_strength}. "
                   f"It cannot establish: {', '.join(t.cannot_establish)}."
                   if overclaimed else "Claim is within what the tool supports."),
        "negative_result_meaning": t.negative_result_meaning,
        "hierarchy_rule": HIERARCHY_RULE,
    }


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# 2. TREATMENT FOLLOWS DIAGNOSIS
# ═══════════════════════════════════════════════════════════════════════════════════════════════
WRONG_ETIOLOGY_RULE = (
    "In several esthetic and functional presentations the principal risk is not procedural "
    "complication but irreversible treatment directed at the wrong etiology. A technically "
    "flawless gingivectomy performed for skeletal vertical maxillary excess, or veneers placed "
    "for a problem of tooth position, fails despite being executed well. Treatment follows "
    "diagnosis."
)

ETIOLOGY_SENSITIVE_PRESENTATIONS = {
    "excessive_gingival_display": (
        "altered passive eruption", "dentoalveolar extrusion", "skeletal vertical maxillary "
        "excess", "short upper lip", "hypermobile upper lip", "gingival enlargement"),
    "midline_asymmetry": (
        "dental midline deviation", "skeletal asymmetry", "tooth position", "facial asymmetry"),
    "implant_esthetic_failure": (
        "implant three-dimensional malposition", "soft-tissue phenotype", "facial bone loss",
        "restorative contour", "peri-implant disease"),
    "tmd_symptoms": (
        "myalgia", "arthralgia", "disc displacement", "sleep bruxism", "referred pain",
        "systemic or psychosocial contributors"),
    "anterior_tooth_wear": (
        "erosion", "attrition", "abrasion", "abfraction", "parafunction", "combination"),
}


def etiology_check(presentation, established_etiology=None, proposed_treatment=None):
    """A named presentation with no established etiology cannot justify irreversible treatment."""
    candidates = ETIOLOGY_SENSITIVE_PRESENTATIONS.get(presentation, ())
    if not candidates:
        return {"presentation": presentation, "etiology_sensitive": False,
                "may_proceed_to_irreversible": True, "rule": WRONG_ETIOLOGY_RULE}
    established = established_etiology in candidates if established_etiology else False
    return {
        "presentation": presentation,
        "etiology_sensitive": True,
        "candidate_etiologies": list(candidates),
        "established_etiology": established_etiology,
        "may_proceed_to_irreversible": established,
        "reason": ("Etiology established; treatment can be matched to it."
                   if established else
                   f"The etiology of {presentation.replace('_', ' ')} is not established. "
                   f"Candidates differ in the treatment they require: "
                   f"{', '.join(candidates)}. Irreversible treatment selected before the cause is "
                   f"established risks a technically correct procedure aimed at the wrong target."),
        "proposed_treatment": proposed_treatment,
        "rule": WRONG_ETIOLOGY_RULE,
    }


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# 3. DRIVER PROBLEM
# ═══════════════════════════════════════════════════════════════════════════════════════════════
DRIVER_PROBLEMS = (
    "implant_malposition", "gingival_architecture", "tooth_position", "midline_discrepancy",
    "skeletal_asymmetry", "periodontal_disease", "occlusal_scheme", "vertical_dimension",
    "structural_tooth_loss", "shade_mismatch_only",
)

DRIVER_RULE = (
    "Identify what is driving the presentation before planning tooth by tooth. Sequencing is "
    "built around the driver problem. Individually correct restorations that ignore it can each "
    "be defensible and still leave the whole smile worse — the commonest way a multidisciplinary "
    "esthetic case fails."
)


def driver_analysis(driver, contributing=None, per_tooth_plan_proposed=False):
    if driver is not None and driver not in DRIVER_PROBLEMS:
        raise ValueError(f"Unknown driver problem {driver!r}. Known: {DRIVER_PROBLEMS}")
    return {
        "driver_problem": driver,
        "contributing_factors": list(contributing or []),
        "identified": driver is not None,
        "may_plan_tooth_by_tooth": driver is not None,
        "warning": (None if driver is not None else
                    "No driver problem has been identified. Building a tooth-by-tooth plan now "
                    "risks a set of technically correct restorations that do not address what is "
                    "actually wrong."),
        "sequencing_note": (f"Sequence around {driver}: correct the driver, or plan the "
                            f"restorations to accommodate it deliberately and say so."
                            if driver else None),
        "rule": DRIVER_RULE,
    }


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# 4. IRREVERSIBILITY TIER LOGIC
# ═══════════════════════════════════════════════════════════════════════════════════════════════
TIER_DIMENSIONS = ("tissue_removal", "structural_loss", "enamel_or_ceramic_removed",
                   "occlusal_scheme_permanently_changed", "biologic_impact", "surgical_extent",
                   "reversibility")

TIER_RULE = (
    "Irreversibility tier reflects what is done to tissue, not how many teeth it is done to. Ten "
    "additive composite veneers are not more irreversible than one full-coverage crown. Counting "
    "teeth as a proxy for irreversibility produces a tier that rises with scale and stays flat "
    "with harm — the opposite of what the tier is for."
)


def tier_from_dimensions(tissue_removal="none", structural_loss="none",
                         enamel_or_ceramic_removed=False,
                         occlusal_scheme_permanently_changed=False, surgical_extent="none",
                         tooth_count=1):
    """
    Grade from what is actually done. `tooth_count` is accepted and deliberately ignored for the
    tier itself; it is reported separately as scope, which is a different property.
    """
    if surgical_extent in ("bone", "extensive") or occlusal_scheme_permanently_changed:
        tier = "T4" if occlusal_scheme_permanently_changed and structural_loss == "substantial" \
            else "T3"
    elif structural_loss == "substantial" or tissue_removal == "substantial":
        tier = "T3"
    elif enamel_or_ceramic_removed or structural_loss == "limited" or tissue_removal == "limited":
        tier = "T2"
    elif tissue_removal == "none" and not enamel_or_ceramic_removed and structural_loss == "none":
        tier = "T1" if surgical_extent == "none" else "T2"
    else:
        tier = "T1"
    return {
        "tier": tier,
        "scope_teeth": tooth_count,
        "dimensions": {
            "tissue_removal": tissue_removal, "structural_loss": structural_loss,
            "enamel_or_ceramic_removed": enamel_or_ceramic_removed,
            "occlusal_scheme_permanently_changed": occlusal_scheme_permanently_changed,
            "surgical_extent": surgical_extent},
        "tooth_count_note": ("Scope is reported separately from tier. More teeth means more "
                             "consent, more cost and more chair time; it does not by itself mean "
                             "a more irreversible procedure."),
        "rule": TIER_RULE,
    }


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# 5. RED-FLAG PROPORTIONALITY
# ═══════════════════════════════════════════════════════════════════════════════════════════════
ROUTINE_DOCUMENTATION_GAP = "ROUTINE_DOCUMENTATION_GAP"
SAFETY_CONCERN = "SAFETY_CONCERN"
HARD_SAFETY_BLOCK = "HARD_SAFETY_BLOCK"

PROPORTIONALITY_RULE = (
    "An incomplete red-flag sweep in a stable elective case is a documentation gap. It is noted "
    "once and does not dominate the answer. Alarmist framing where no emergency signal exists "
    "trains the reader to discount the framing when one does."
)


def red_flag_proportionality(sweep_status, any_flag_present, case_is_stable_elective):
    if any_flag_present:
        return {"framing": HARD_SAFETY_BLOCK,
                "reason": "A relevant red flag is present. This takes precedence over the "
                          "clinical question asked.",
                "dominates_answer": True, "rule": PROPORTIONALITY_RULE}
    if sweep_status == "INCOMPLETE_SWEEP" and case_is_stable_elective:
        return {"framing": ROUTINE_DOCUMENTATION_GAP,
                "reason": "The sweep is not fully documented, and no emergency signal is present "
                          "in a stable elective case. Note the gap; answer the question.",
                "dominates_answer": False, "rule": PROPORTIONALITY_RULE}
    if sweep_status == "INCOMPLETE_SWEEP":
        return {"framing": SAFETY_CONCERN,
                "reason": "The sweep is incomplete and the case is not a stable elective one. "
                          "Complete the sweep before proceeding.",
                "dominates_answer": True, "rule": PROPORTIONALITY_RULE}
    return {"framing": None, "reason": "Sweep complete, no flags.", "dominates_answer": False,
            "rule": PROPORTIONALITY_RULE}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# 6. ANSWER PRIORITIZATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════
ANSWER_SECTIONS = ("CURRENT DECISION", "WHY", "KEY DISCRIMINATOR", "NEXT STEP", "DETAILS")

ANSWER_RULE = (
    "Lead with the decision. A clinician reading forty fields of missing data before reaching the "
    "answer has been given a form, not advice. Detail follows the decision; it does not precede "
    "it."
)


class ClinicalAnswer:
    def __init__(self, current_decision, why, key_discriminator, next_step, details=None):
        self.current_decision = current_decision
        self.why = why
        self.key_discriminator = key_discriminator
        self.next_step = next_step
        self.details = details or {}

    def validate(self):
        problems = []
        for name, value in (("CURRENT DECISION", self.current_decision), ("WHY", self.why),
                            ("KEY DISCRIMINATOR", self.key_discriminator),
                            ("NEXT STEP", self.next_step)):
            if not value or not str(value).strip():
                problems.append(f"{name} is empty. It is a required section.")
        return {"result": "FAIL" if problems else "PASS", "problems": problems,
                "rule": ANSWER_RULE}

    def to_markdown(self):
        lines = [f"**CURRENT DECISION** — {self.current_decision}", "",
                 f"**WHY** — {self.why}", "",
                 f"**KEY DISCRIMINATOR** — {self.key_discriminator}", "",
                 f"**NEXT STEP** — {self.next_step}"]
        if self.details:
            lines += ["", "**DETAILS**", ""]
            for k, v in self.details.items():
                lines.append(f"- *{k}*: {v}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# 7. IMPLANT TIMING SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════
IMPLANT_TIMING_RULE = (
    "Extraction, immediate placement, immediate provisionalization and immediate functional "
    "loading are four decisions, not one. Bundling them means a patient who is a candidate for "
    "one is treated as a candidate for all four, and a contraindication to loading is read as a "
    "contraindication to placement."
)

INDICATED = "INDICATED"
CONDITIONAL = "CONDITIONAL"
SEPARATE_DECISION = "SEPARATE_DECISION"
NOT_INDICATED = "NOT_INDICATED"


def implant_timing(extraction=INDICATED, placement=CONDITIONAL, provisionalization=CONDITIONAL,
                   functional_loading=SEPARATE_DECISION, notes=None):
    return {
        "extraction": extraction,
        "immediate_placement": placement,
        "immediate_provisionalization": provisionalization,
        "immediate_functional_loading": functional_loading,
        "notes": dict(notes or {}),
        "rule": IMPLANT_TIMING_RULE,
        "bundled": False,
    }

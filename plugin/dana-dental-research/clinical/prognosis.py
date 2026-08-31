"""
clinical/prognosis.py

Categorical prognosis assessment. Closes the Phase D gap where prognosis was recorded but never
systematically assessed.

WHAT THIS DOES NOT DO
---------------------
It produces **no numeric probability**. Not a percentage, not a survival estimate, not a score.
M2 §5 requires a named categorical scale with the criteria driving each assignment; CORE §3
forbids any number without a source. A computed "78% survival" from a chairside dataset would be
an invented statistic wearing a decimal point.

It also does not decide from findings alone. It evaluates the determinants the clinician recorded,
and where a determinant that governs the answer is missing, the answer is UNDETERMINED. That is a
result, not a failure — CORE §2's "prognosis before prosthesis" only means something if
UNDETERMINED actually blocks planning.

FIVE AXES, ASSESSED SEPARATELY
------------------------------
tooth · periodontal · restorative · prosthetic · functional-occlusal risk. They diverge in
practice: a tooth may be periodontally sound and restoratively hopeless, or structurally fine and
functionally doomed. Collapsing them into one label hides exactly the disagreement that matters.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from case_state import CaseState, UNKNOWN, INFERRED, INSUFFICIENT, OUT_OF_SCOPE

# ---------------------------------------------------------------------------
# The four categories. No fifth, no numbers.
# ---------------------------------------------------------------------------
FAVORABLE = "FAVORABLE"
GUARDED = "GUARDED"
POOR = "POOR"
UNDETERMINED = "UNDETERMINED"
CATEGORIES = (FAVORABLE, GUARDED, POOR, UNDETERMINED)

NO_NUMBERS_RULE = (
    "Prognosis is categorical only. No percentage, survival figure or score is produced — a number "
    "derived from a chairside dataset would be a fabricated statistic (CORE §3, M2 §5)."
)

SCALE_NOTE = (
    "This is DANA's internal four-category scale, used so the gate is enforceable. When reporting "
    "to a clinician, state which named published scale the clinician is using (e.g. Kwok & Caton, "
    "McGuire) — M2 §5 requires a named scale, and this internal one is not a substitute for it."
)

# Axes
AXIS_TOOTH = "tooth"
AXIS_PERIODONTAL = "periodontal"
AXIS_RESTORATIVE = "restorative"
AXIS_PROSTHETIC = "prosthetic"
AXIS_FUNCTIONAL = "functional_occlusal"
AXES = (AXIS_TOOTH, AXIS_PERIODONTAL, AXIS_RESTORATIVE, AXIS_PROSTHETIC, AXIS_FUNCTIONAL)

# Determinants per axis. A determinant marked critical, when missing, forces UNDETERMINED for that
# axis — it is not averaged away by the determinants that are present.
DETERMINANTS: Dict[str, Dict[str, bool]] = {
    AXIS_TOOTH: {
        "restorability_verdict_with_criteria": True,
        "pulpal_status": True,
        "remaining_tooth_structure_quantified": True,
        "caries_risk_assessment_tool": False,
        "strategic_value": False,
    },
    AXIS_PERIODONTAL: {
        "periodontal_status": True,          # inflammation / BOP / pockets
        "attachment_level": True,
        "mobility": False,
        "furcation": False,
        "crown_root_ratio": False,
        "compliance_history": False,
    },
    AXIS_RESTORATIVE: {
        "remaining_tooth_structure_quantified": True,
        "ferrule": True,
        "existing_restoration_quality": False,
        "isolation_feasibility": False,
        "occlusal_loading_contacts": False,
    },
    AXIS_PROSTHETIC: {
        "abutment_evaluation_and_prognosis": True,
        "occlusal_scheme": False,
        "antagonist_status": False,
        "adaptive_capacity": False,
        "edentulous_span_classification": False,
    },
    AXIS_FUNCTIONAL: {
        "parafunction_assessment": True,
        "occlusal_scheme": False,
        "ovd_assessment_with_method": False,
        "antagonist_status": False,
    },
}

# Findings that are adverse by their nature. The clinician supplies which are present; this module
# does not infer them from anything.
# Each adverse finding carries (ceiling, axes it actually bears on). Applying every finding to
# every axis would make the five axes decorative — the point of separating them is that active
# periodontal disease and an inadequate ferrule are different problems with different consequences.
ADVERSE_FINDINGS = {
    "active_periodontal_disease": (POOR, (AXIS_PERIODONTAL, AXIS_TOOTH, AXIS_PROSTHETIC)),
    "uncontrolled_caries": (POOR, (AXIS_TOOTH, AXIS_RESTORATIVE)),
    "non_restorable": (POOR, (AXIS_TOOTH, AXIS_RESTORATIVE, AXIS_PROSTHETIC)),
    "vertical_root_fracture": (POOR, (AXIS_TOOTH, AXIS_RESTORATIVE, AXIS_PROSTHETIC)),
    "inadequate_ferrule": (GUARDED, (AXIS_RESTORATIVE, AXIS_PROSTHETIC)),
    "questionably_restorable": (GUARDED, (AXIS_TOOTH, AXIS_RESTORATIVE)),
    "uncontrolled_parafunction": (GUARDED, (AXIS_FUNCTIONAL, AXIS_RESTORATIVE, AXIS_PROSTHETIC)),
    "unfavourable_crown_root_ratio": (GUARDED, (AXIS_PERIODONTAL, AXIS_PROSTHETIC)),
    "furcation_involvement": (GUARDED, (AXIS_PERIODONTAL, AXIS_TOOTH)),
    "poor_compliance": (GUARDED, (AXIS_PERIODONTAL, AXIS_PROSTHETIC)),
    "unresolved_periapical_pathology": (GUARDED, (AXIS_TOOTH, AXIS_RESTORATIVE)),
}
ADVERSE_FINDING_WEIGHT = {k: v[0] for k, v in ADVERSE_FINDINGS.items()}

CONFIDENCE_HIGH = "High"
CONFIDENCE_MODERATE = "Moderate"
CONFIDENCE_LOW = "Low"
CONFIDENCE_CANNOT = "Cannot assess"


@dataclass
class AxisPrognosis:
    axis: str
    category: str = UNDETERMINED
    basis: str = ""
    supporting_findings: List[str] = field(default_factory=list)
    adverse_findings: List[str] = field(default_factory=list)
    missing_determinants: List[str] = field(default_factory=list)
    confidence: str = CONFIDENCE_CANNOT

    def to_dict(self):
        return asdict(self)


def _confidence(missing_critical, missing_any, adverse):
    if missing_critical:
        return CONFIDENCE_CANNOT
    if missing_any:
        return CONFIDENCE_LOW if len(missing_any) > 2 else CONFIDENCE_MODERATE
    return CONFIDENCE_MODERATE if adverse else CONFIDENCE_HIGH


def assess_axis(case: CaseState, axis: str, adverse_findings=None, supporting_findings=None,
                tooth=None):
    """
    Assess one axis. `adverse_findings` are keys from ADVERSE_FINDING_WEIGHT that the clinician has
    recorded as present. Nothing is inferred from the case record beyond whether a determinant is
    known.
    """
    if axis not in DETERMINANTS:
        raise ValueError(f"Unknown prognosis axis {axis!r}. Axes: {AXES}")
    # Only findings that bear on THIS axis are considered here.
    adverse = [a for a in (adverse_findings or [])
               if a in ADVERSE_FINDINGS and axis in ADVERSE_FINDINGS[a][1]]
    unknown_adverse = [a for a in (adverse_findings or []) if a not in ADVERSE_FINDINGS]
    if unknown_adverse:
        raise ValueError(f"Unrecognised adverse finding(s) {unknown_adverse}. The list is fixed so "
                         "an ad-hoc label cannot silently change a prognosis.")
    supporting = list(supporting_findings or [])

    spec = DETERMINANTS[axis]
    missing_critical, missing_other = [], []
    for key, critical in spec.items():
        if not case.known(key):
            (missing_critical if critical else missing_other).append(key)

    # Rule 1 — a missing critical determinant ends the assessment. It is not averaged away.
    if missing_critical:
        return AxisPrognosis(
            axis=axis, category=UNDETERMINED,
            basis=(f"Critical determinant(s) not established: {', '.join(missing_critical)}. "
                   "Prognosis cannot be assigned without them, and is not estimated from the "
                   "determinants that are present."),
            supporting_findings=supporting, adverse_findings=adverse,
            missing_determinants=missing_critical + missing_other,
            confidence=CONFIDENCE_CANNOT)

    # Rule 2 — the worst adverse finding sets the ceiling. Conservative conflict resolution:
    # good news never offsets bad news on the same axis.
    category = FAVORABLE
    if adverse:
        weights = [ADVERSE_FINDING_WEIGHT[a] for a in adverse]
        category = POOR if POOR in weights else GUARDED

    # Rule 3 — an [Inferred] critical determinant caps the axis at GUARDED. An inference is not a
    # finding (CORE §5), and a favourable prognosis resting on one overstates what is known.
    inferred_critical = [k for k, crit in spec.items()
                         if crit and case.get(k) and case.get(k).provenance == INFERRED]
    if inferred_critical and category == FAVORABLE:
        category = GUARDED
        supporting = supporting + [
            f"Capped at GUARDED: critical determinant(s) {', '.join(inferred_critical)} are "
            "[Inferred], not [Observed]."]

    basis_bits = []
    if adverse:
        basis_bits.append(f"adverse: {', '.join(adverse)}")
    if supporting:
        basis_bits.append(f"supporting: {len(supporting)} finding(s)")
    if missing_other:
        basis_bits.append(f"non-critical gaps: {', '.join(missing_other)}")
    basis = ("All critical determinants established. "
             + ("; ".join(basis_bits) if basis_bits else "no adverse findings recorded."))

    return AxisPrognosis(axis=axis, category=category, basis=basis,
                         supporting_findings=supporting, adverse_findings=adverse,
                         missing_determinants=missing_other,
                         confidence=_confidence(missing_critical, missing_other, adverse))


def assess(case: CaseState, adverse_findings=None, supporting_findings=None, axes=None,
           tooth=None):
    """
    Assess all five axes and produce the overall result.

    Overall category is the WORST axis, never an average. A tooth that is periodontally favourable
    and restoratively poor is not "guarded overall" — it is poor, and the reason is restorative.
    """
    axes = axes or AXES
    results = {a: assess_axis(case, a, adverse_findings, supporting_findings, tooth) for a in axes}

    order = {FAVORABLE: 0, GUARDED: 1, POOR: 2, UNDETERMINED: 3}
    worst = max((r.category for r in results.values()), key=lambda c: order[c])
    driving = [a for a, r in results.items() if r.category == worst]

    all_missing = sorted({m for r in results.values() for m in r.missing_determinants})
    blocking = worst == UNDETERMINED

    return {
        "case_ref": case.case_ref,
        "tooth": tooth,
        "overall": worst,
        "driven_by": driving,
        "axes": {a: r.to_dict() for a, r in results.items()},
        "missing_determinants": all_missing,
        "blocks_irreversible_planning": blocking,
        "block_reason": (
            "Prognosis is UNDETERMINED because critical determinants are missing. Definitive "
            "irreversible treatment planning is blocked until they are established "
            "(CORE §2, M2 §5)." if blocking else None),
        "scale_note": SCALE_NOTE,
        "no_numbers_rule": NO_NUMBERS_RULE,
        "overall_rule": "Overall prognosis is the worst axis, never an average of the axes.",
    }


# ---------------------------------------------------------------------------
# Part 4 — the ordering rule
# ---------------------------------------------------------------------------
ORDER = ("case_state", "data_sufficiency", "red_flag_sweep", "clinical_findings", "prognosis",
         "irreversible_treatment_planning")

ORDER_RULE = (
    "Prognosis is assessed only after the case state is built, data sufficiency is verdicted, the "
    "red-flag sweep is complete and clinical findings are recorded — and before any irreversible "
    "treatment planning."
)


class PrognosisOrderError(RuntimeError):
    """Raised when prognosis is attempted out of order. Never downgraded to a warning."""


def assess_in_order(case: CaseState, sweep_result: Optional[Dict[str, Any]] = None,
                    adverse_findings=None, supporting_findings=None, tooth=None):
    """
    Enforced-order entry point. Use this rather than `assess()` in the output path.

    Refuses — rather than returning a weaker answer — when the prerequisites are not met, because a
    prognosis produced before the red-flag sweep or on an insufficient dataset is worse than no
    prognosis: it looks like an answer.
    """
    if not case.in_scope():
        raise PrognosisOrderError(
            f"Case discipline {case.discipline!r} is out of scope; no prognosis is produced. "
            + ORDER_RULE)

    suff = case.sufficiency()
    if suff["verdict"] in (INSUFFICIENT, OUT_OF_SCOPE):
        return {
            "overall": UNDETERMINED,
            "blocks_irreversible_planning": True,
            "block_reason": (f"Data sufficiency is {suff['verdict']} — {suff['reason']} Prognosis "
                             "is not assessed on an insufficient dataset."),
            "axes": {}, "missing_determinants": [m["item"] for m in suff["missing"]],
            "order_rule": ORDER_RULE, "no_numbers_rule": NO_NUMBERS_RULE,
        }

    if sweep_result is None or sweep_result.get("status") == "INCOMPLETE_SWEEP":
        raise PrognosisOrderError(
            "Red-flag sweep is incomplete or was not run. Prognosis follows the sweep, never "
            "precedes it. " + ORDER_RULE)
    if sweep_result.get("status") == "RED_FLAG":
        return {
            "overall": UNDETERMINED,
            "blocks_irreversible_planning": True,
            "block_reason": ("A red flag is present. Clinical escalation precedes prognosis and "
                             "planning (CORE §15)."),
            "axes": {}, "missing_determinants": [],
            "order_rule": ORDER_RULE, "no_numbers_rule": NO_NUMBERS_RULE,
        }

    result = assess(case, adverse_findings, supporting_findings, tooth=tooth)
    result["order_rule"] = ORDER_RULE
    return result


def apply_to_case(case: CaseState, tooth: str, result: Dict[str, Any]):
    """
    Write the assessed prognosis onto the case, so `treatment_plan.py`'s existing
    prognosis-before-prosthesis gate sees it. UNDETERMINED is written as UNDETERMINED — the gate
    is meant to fire.
    """
    case.prognosis[tooth] = result["overall"] if result["overall"] != UNDETERMINED else ""
    case.prognosis_scale = case.prognosis_scale or "DANA internal 4-category (see scale_note)"
    return case

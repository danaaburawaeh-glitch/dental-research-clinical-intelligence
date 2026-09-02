"""
clinical/case_state.py

The case-state model — the spine of the clinical layer.

Everything downstream reads this. Its one job is to make the CORE §5 distinction between what was
reported, what was observed, what was inferred and what is simply unknown impossible to lose.

Migrated from M1 V0.4 §2 (data ledger domains, universal provenance rule) and M2 V0.4 §1
(minimum datasets). No clinical threshold, dose or interval appears here — M2 is explicit that it
carries none by design, and neither does this module.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------------------------
# CORE provenance tags — the four, and only these four.
# ---------------------------------------------------------------------------
REPORTED = "[Reported]"    # said by the patient or carried in a record; not yet clinically observed
OBSERVED = "[Observed]"    # directly examined, or a documented actual examination finding
INFERRED = "[Inferred]"    # a reasonable deduction — NOT a confirmed fact; always carries its basis
UNKNOWN = "[Unknown]"      # not stated at all, and must not be guessed

PROVENANCE_TAGS = (REPORTED, OBSERVED, INFERRED, UNKNOWN)

PROVENANCE_RULE = (
    "A tag is never promoted. [Inferred] stays [Inferred] however obvious it looks; it never "
    "becomes [Observed] or [Reported]. [Unknown] is never filled with a plausible guess — honest "
    "emptiness beats a confident invention."
)

# ---------------------------------------------------------------------------
# Scope gate — v1.0 is deliberately two disciplines, not general dentistry.
# ---------------------------------------------------------------------------
SCOPE_FIXED_PROSTHODONTICS = "fixed_prosthodontics"
SCOPE_ESTHETIC_RESTORATIVE = "esthetic_restorative"
IN_SCOPE_DISCIPLINES = (SCOPE_FIXED_PROSTHODONTICS, SCOPE_ESTHETIC_RESTORATIVE)
OUT_OF_SCOPE = "OUT_OF_SCOPE"

SCOPE_NOTE = (
    "v1.0 covers Fixed Prosthodontics and Esthetic Restorative Dentistry only. A case outside "
    "that scope is refused rather than answered less well — an assistant that degrades quietly "
    "outside its competence is more dangerous than one that stops."
)

# ---------------------------------------------------------------------------
# M1 §2 data-ledger domains
# ---------------------------------------------------------------------------
LEDGER_DOMAINS = (
    "chief_complaint", "medical_history", "medications", "allergies", "dental_history",
    "extraoral", "intraoral_soft_tissue", "periodontal", "endodontic_pulpal",
    "caries_restorative_status", "occlusion_function", "tmj_muscles", "parafunction",
    "radiographic", "esthetic_parameters", "patient_expectations", "budget_time_compliance",
)

# ---------------------------------------------------------------------------
# M2 §1 minimum datasets. Only the sets in v1.0 scope are enforced.
# Field names are checklist items, not thresholds.
# ---------------------------------------------------------------------------
MINIMUM_UNIVERSAL = (  # M2 §1.1
    "age", "sex", "chief_complaint", "medical_history", "medications", "allergies",
    "pregnancy_lactation_status", "smoking_substance_use", "dental_history", "anxiety_level",
    "notation_system", "patient_expectations", "budget_time_constraints", "compliance_history",
)
MINIMUM_PROSTHODONTIC = (  # M2 §1.5
    "existing_prosthesis_assessment", "edentulous_span_classification",
    "abutment_evaluation_and_prognosis", "occlusal_scheme", "ovd_assessment_with_method",
    "freeway_space", "centric_relation_records", "anterior_guidance", "arch_relationship",
    "ridge_form_mucosa", "mounted_casts_or_scans", "smile_analysis", "phonetics",
    "parafunction_assessment", "adaptive_capacity",
)
MINIMUM_ESTHETIC = (  # M2 §1.8
    "facial_midline", "horizontal_reference_planes", "lip_dynamics", "smile_line",
    "buccal_corridor", "gingival_levels_symmetry", "zenith_positions", "tooth_proportions",
    "incisal_edge_position", "dental_midline", "axial_inclinations",
    "shade_with_reference_and_lighting", "surface_texture_translucency", "phonetics_functional",
    "standardised_photographic_set", "patient_stated_concern", "expectation_screening",
)
MINIMUM_RESTORATIVE = (  # M2 §1.4 — needed whenever a tooth is to be restored
    "caries_risk_assessment_tool", "remaining_tooth_structure_quantified",
    "existing_restoration_quality", "ferrule", "occlusal_loading_contacts", "antagonist_status",
    "isolation_feasibility", "pulpal_status", "restorability_verdict_with_criteria",
)

DATASET_BY_SCOPE = {
    SCOPE_FIXED_PROSTHODONTICS: MINIMUM_UNIVERSAL + MINIMUM_RESTORATIVE + MINIMUM_PROSTHODONTIC,
    SCOPE_ESTHETIC_RESTORATIVE: MINIMUM_UNIVERSAL + MINIMUM_RESTORATIVE + MINIMUM_ESTHETIC,
}

# ---------------------------------------------------------------------------
# Sufficiency verdicts — M1 §4
# ---------------------------------------------------------------------------
SUFFICIENT = "SUFFICIENT"
PARTIALLY_SUFFICIENT = "PARTIALLY SUFFICIENT"
INSUFFICIENT = "INSUFFICIENT"

# Decision-value ranking for missing data (M1 §3). Higher blocks more.
DECISION_VALUE = {
    "blocks_diagnosis": 4,
    "blocks_prognosis": 3,
    "blocks_irreversible_treatment": 3,
    "changes_plan": 2,
    "refines_plan": 1,
}

# Items whose absence blocks by their nature, not by a caller's opinion. Each is tied to a rule
# M2 states directly: the medical screen gates invasive planning (§3), restorability and ferrule
# gate any restoration (§1.4), abutment prognosis gates fixed prosthodontics (§1.5), and an
# unknown allergy list makes material selection unsafe (§3.9).
INTRINSICALLY_BLOCKING = {
    "medical_history": "blocks_irreversible_treatment",
    "medications": "blocks_irreversible_treatment",
    "allergies": "blocks_irreversible_treatment",
    "restorability_verdict_with_criteria": "blocks_diagnosis",
    "remaining_tooth_structure_quantified": "blocks_prognosis",
    "ferrule": "blocks_prognosis",
    "abutment_evaluation_and_prognosis": "blocks_prognosis",
    "pulpal_status": "blocks_diagnosis",
    "parafunction_assessment": "blocks_prognosis",
    "expectation_screening": "blocks_irreversible_treatment",
}

# Beyond a certain share of the minimum dataset missing, "partially sufficient" is a misleading
# label whatever the individual ranks say. A case with most of its dataset absent has not been
# examined; it has been mentioned.
INSUFFICIENT_MISSING_FRACTION = 0.5


class ProvenanceError(ValueError):
    """Raised when the provenance contract is violated. Never silently corrected."""


@dataclass
class DataPoint:
    """
    One finding, with its provenance. The provenance tag is mandatory and validated.

    `basis` is REQUIRED for [Inferred] — M1's rule is that an inference always carries what it was
    inferred from. An inference without a basis is indistinguishable from an invention, so it is
    rejected at construction rather than allowed through to be caught later (or not).
    """
    domain: str
    finding: Any
    provenance: str
    basis: Optional[str] = None          # required when provenance == [Inferred]
    source: Optional[str] = None         # who said/observed it
    date: Optional[str] = None           # recency matters clinically

    def __post_init__(self):
        if self.provenance not in PROVENANCE_TAGS:
            raise ProvenanceError(
                f"Unknown provenance tag {self.provenance!r}. Must be one of {PROVENANCE_TAGS}.")
        if self.provenance == INFERRED and not self.basis:
            raise ProvenanceError(
                f"[Inferred] data point in domain {self.domain!r} has no basis. An inference "
                "without its basis is an invention. Supply `basis`, or record it as [Unknown].")
        if self.provenance == UNKNOWN and self.finding not in (None, "", UNKNOWN):
            raise ProvenanceError(
                f"[Unknown] data point in domain {self.domain!r} carries a finding "
                f"({self.finding!r}). If something is known, tag it accordingly; [Unknown] must "
                "not be used to smuggle in a guess.")

    def to_dict(self):
        return asdict(self)


@dataclass
class CaseState:
    """
    The structured case record. Built incrementally; never guesses a value it was not given.
    """
    case_ref: str
    discipline: str
    notation: Optional[str] = None                     # FDI / Universal / Palmer (M1 header line)
    data: Dict[str, DataPoint] = field(default_factory=dict)
    prognosis: Dict[str, str] = field(default_factory=dict)     # tooth -> prognosis label
    prognosis_scale: Optional[str] = None                        # named scale, per M2 §5
    intent: Optional[str] = None                                 # what decision is being asked for

    # ------------------------------------------------------------------
    def in_scope(self):
        return self.discipline in IN_SCOPE_DISCIPLINES

    def record(self, key, finding, provenance, basis=None, source=None, date=None, domain=None):
        """Record one data point. Raises rather than accepting a malformed provenance claim."""
        dp = DataPoint(domain=domain or key, finding=finding, provenance=provenance,
                       basis=basis, source=source, date=date)
        self.data[key] = dp
        return dp

    def get(self, key):
        return self.data.get(key)

    def known(self, key):
        """True only when the item is present AND not [Unknown]. An inference counts as known-ish
        but callers that need certainty should check the tag themselves."""
        dp = self.data.get(key)
        return dp is not None and dp.provenance != UNKNOWN

    # ------------------------------------------------------------------
    def required_dataset(self):
        return DATASET_BY_SCOPE.get(self.discipline, ())

    def missing_items(self):
        """Items in the required minimum dataset that are absent or explicitly [Unknown]."""
        return [k for k in self.required_dataset() if not self.known(k)]

    def missing_data_report(self, decision_value_map=None):
        """
        M1 §3 — missing data ranked by decision value. For each item: what it is, why it matters,
        which conclusion it would change.

        `decision_value_map` lets a caller mark specific items as blocking; anything unmapped
        defaults to `changes_plan`, which is deliberately not the lowest rank — an item in a
        MINIMUM dataset is by definition not a nicety.
        """
        decision_value_map = decision_value_map or {}
        out = []
        for item in self.missing_items():
            # Caller's ranking wins only where it is MORE blocking than the intrinsic one — a
            # caller may not downgrade an item M2 treats as gating.
            intrinsic = INTRINSICALLY_BLOCKING.get(item)
            supplied = decision_value_map.get(item)
            if supplied and intrinsic:
                kind = supplied if DECISION_VALUE.get(supplied, 0) > DECISION_VALUE.get(intrinsic, 0) else intrinsic
            else:
                kind = supplied or intrinsic or "changes_plan"
            out.append({
                "item": item,
                "decision_value": kind,
                "rank": DECISION_VALUE.get(kind, 2),
                "why_it_matters": f"Part of the minimum dataset for {self.discipline}.",
                "provenance": self.data[item].provenance if item in self.data else UNKNOWN,
            })
        out.sort(key=lambda x: -x["rank"])
        return out

    def sufficiency(self, decision_value_map=None, decision=None, conditions_met=None):
        """
        Sufficiency verdict, with the reason.

        `decision` (v1.2.1) scopes the verdict to the decision actually being made. Without it the
        legacy discipline-wide behaviour is preserved unchanged, so existing callers are
        unaffected — but a caller that knows which decision it is answering gets a verdict about
        that decision instead of about the whole minimum dataset.

        This is the fix for the case where a narrow, conservative question was answered
        "INSUFFICIENT" because prosthodontic fields unrelated to it were absent.
        """
        if decision is not None:
            return self.sufficiency_for(decision, conditions_met)
        if not self.in_scope():
            return {
                "verdict": OUT_OF_SCOPE,
                "reason": (f"Discipline {self.discipline!r} is outside v1.0 scope. {SCOPE_NOTE}"),
                "missing": [],
            }
        missing = self.missing_data_report(decision_value_map)
        required = self.required_dataset()
        blocking = [m for m in missing if m["rank"] >= DECISION_VALUE["blocks_prognosis"]]
        fraction = (len(missing) / len(required)) if required else 0.0
        if not missing:
            verdict, reason = SUFFICIENT, "Minimum dataset complete for this discipline."
        elif blocking:
            verdict = INSUFFICIENT
            reason = (f"{len(blocking)} item(s) missing that block diagnosis, prognosis or "
                      f"irreversible treatment: "
                      f"{', '.join(m['item'] for m in blocking[:5])}"
                      f"{'…' if len(blocking) > 5 else ''}.")
        elif fraction >= INSUFFICIENT_MISSING_FRACTION:
            verdict = INSUFFICIENT
            reason = (f"{len(missing)} of {len(required)} minimum-dataset items are missing "
                      f"({fraction:.0%}). Too little of the case has been established to plan on.")
        else:
            verdict = PARTIALLY_SUFFICIENT
            reason = f"{len(missing)} item(s) of the minimum dataset are missing."
        assert not (verdict == SUFFICIENT and missing), "SUFFICIENT with outstanding gaps"
        return {"verdict": verdict, "reason": reason, "missing": missing}

    # ------------------------------------------------------------------
    def sufficiency_for(self, decision, conditions_met=None):
        """
        Decision-scoped sufficiency (v1.2.1). Delegates to decision_context, which holds the
        relevance model. Returns the same shape as `sufficiency()` plus the decision-specific
        fields, so callers can read `verdict` either way.
        """
        import decision_context as dc
        if not self.in_scope():
            return {"verdict": OUT_OF_SCOPE, "reason": SCOPE_NOTE, "missing": [],
                    "decision": decision}
        result = dc.assess_sufficiency(decision, self.known, conditions_met)
        result["missing"] = [
            {"item": item, "priority": prio, "rank": dc.PRIORITY_RANK[prio],
             "relevance": dc.relevance(decision, item),
             "condition": dc.condition_for(decision, item),
             "why_it_matters": f"{prio} for {decision}."}
            for prio, items in result["by_priority"].items() for item in items]
        result["missing"].sort(key=lambda m: -m["rank"])
        return result

    def sufficiency_across(self, decisions, conditions_met=None):
        """What this case can and cannot support right now, decision by decision."""
        import decision_context as dc
        return dc.sufficiency_across(decisions, self.known, conditions_met)

    def relevant_missing(self, decision):
        """Missing items that are RELEVANT to this decision. NOT_RELEVANT items are suppressed
        entirely — they are not gaps for a decision they cannot change (issue 45)."""
        import decision_context as dc
        return [i for i in dc.required_items(decision)
                if not self.known(i) and dc.relevance(decision, i) != dc.NOT_RELEVANT]

    def suppressed_for(self, decision):
        """Minimum-dataset items deliberately NOT reported for this decision, with the reason.
        Kept visible for audit: suppression must be inspectable, not silent."""
        import decision_context as dc
        return [i for i in self.required_dataset() if dc.relevance(decision, i) == dc.NOT_RELEVANT]

    # ------------------------------------------------------------------
    def prognosis_undetermined_teeth(self):
        """
        M2 §5 / CORE §2 — teeth with no assignable prognosis. Restorative planning on these is
        blocked. A tooth absent from `prognosis` is undetermined, not implicitly fine.
        """
        return sorted([t for t, p in self.prognosis.items()
                       if not p or str(p).strip().upper() in ("", "UNDETERMINED",
                                                              "PROGNOSIS UNDETERMINED")])

    def provenance_summary(self):
        counts = {tag: 0 for tag in PROVENANCE_TAGS}
        for dp in self.data.values():
            counts[dp.provenance] += 1
        return counts

    def to_dict(self):
        return {
            "case_ref": self.case_ref,
            "discipline": self.discipline,
            "notation": self.notation,
            "intent": self.intent,
            "data": {k: v.to_dict() for k, v in self.data.items()},
            "prognosis": dict(self.prognosis),
            "prognosis_scale": self.prognosis_scale,
            "provenance_summary": self.provenance_summary(),
        }


def header_line(case: CaseState, mode: str, decision=None):
    """
    M1 universal rule: every template opens with this line.

    With a decision supplied the sufficiency reported is the decision's, not the discipline's —
    the difference between "this case is INSUFFICIENT" and "this case is sufficient to discuss
    the conservative option and not to cut the preparation".
    """
    s = case.sufficiency(decision=decision) if decision else case.sufficiency()
    line = (f"{mode} · {case.case_ref} · Notation: {case.notation or UNKNOWN} · "
            f"Data sufficiency: {s['verdict']}")
    return line + (f" (for: {decision})" if decision else "")

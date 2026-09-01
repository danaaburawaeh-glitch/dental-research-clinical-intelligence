"""
evidence/directness.py  —  CLINICAL DIRECTNESS (v1.2)

Answers a question that evidence level cannot: does this study answer THE question that was
asked, about THE patients being treated, with THE material being considered, over THE time that
matters?

A systematic review is a systematic review whatever it is about. Directness is what stops a
high-tier tag from being read as a high-relevance answer, and it is assessed on six dimensions
the brief names explicitly:

    population · procedure · material · comparison · outcome · follow-up

Each is rated HIGH / MODERATE / LOW / UNKNOWN against the framed question, and the overall
verdict is derived from them by a fixed, documented rule rather than by impression.

THE AGGREGATION RULE
--------------------
    any LOW        -> INDIRECT      (a decisive mismatch on one dimension is not averaged away)
    else any UNKNOWN -> UNKNOWN     (an unrated dimension cannot be assumed to match)
    else any MODERATE -> PARTIALLY DIRECT
    else            -> DIRECT

LOW dominates UNKNOWN deliberately. A known mismatch is a finding; an unknown is an absence, and
a finding outranks an absence. Both outrank optimism.

THE LABORATORY RULE — enforced in code, not by convention
---------------------------------------------------------
An in-vitro study, a finite element model, and a trial registry record can never be DIRECT for a
claim about what happens to a patient. Bond strength in a testing machine is not restoration
survival in a mouth; a mesh model is not a jaw; a registered trial is not a result. These are
capped at INDIRECT by `assess()` regardless of how the six dimensions were rated, and the cap is
reported in the result so it is visible rather than mysterious.
"""
import _paths  # noqa: F401

import study_design as sd

# ── Overall verdicts ────────────────────────────────────────────────────────────────────────
DIRECT = "DIRECT"
PARTIALLY_DIRECT = "PARTIALLY DIRECT"
INDIRECT = "INDIRECT"
UNKNOWN = "UNKNOWN"
VERDICTS = (DIRECT, PARTIALLY_DIRECT, INDIRECT, UNKNOWN)

# Ordered worst-to-best, for comparison and capping.
_ORDER = {INDIRECT: 0, UNKNOWN: 1, PARTIALLY_DIRECT: 2, DIRECT: 3}

# ── Per-dimension ratings ───────────────────────────────────────────────────────────────────
HIGH = "HIGH"
MODERATE = "MODERATE"
LOW = "LOW"
RATING_UNKNOWN = "UNKNOWN"
RATINGS = (HIGH, MODERATE, LOW, RATING_UNKNOWN)

DIMENSIONS = ("population", "procedure", "material", "comparison", "outcome", "follow_up")

# Dimensions that may legitimately be N/A rather than unrated — a single-arm study has no
# comparison, and that is a property of the question, not a gap in the appraisal.
NOT_APPLICABLE = "N/A"

LAB_CAP_NOTE = (
    "Laboratory and computational evidence is capped at INDIRECT for any claim about patient "
    "outcomes. It may describe a mechanism or a plausibility; it may never stand in for what "
    "happens clinically. (del7-evidence-hierarchy.md §3, the laboratory firewall.)"
)
REGISTRY_CAP_NOTE = (
    "A trial registry record is capped at INDIRECT: it records that a trial exists, not what it "
    "found. REGISTRY ONLY — NOT EVIDENCE OF EFFICACY."
)


class DirectnessAssessment:
    def __init__(self, verdict, dimensions, rationale, capped_from=None, cap_reason=None):
        self.verdict = verdict
        self.dimensions = dimensions
        self.rationale = rationale
        self.capped_from = capped_from
        self.cap_reason = cap_reason

    @property
    def was_capped(self):
        return self.capped_from is not None

    def to_dict(self):
        return {
            "verdict": self.verdict,
            "dimensions": dict(self.dimensions),
            "rationale": self.rationale,
            "capped_from": self.capped_from,
            "cap_reason": self.cap_reason,
        }

    def __repr__(self):
        return f"<Directness {self.verdict}>"


def aggregate(dimensions):
    """Apply the fixed aggregation rule to a dict of dimension -> rating."""
    values = [v for k, v in dimensions.items() if v != NOT_APPLICABLE]
    if not values:
        return UNKNOWN, "No dimension was rated — directness cannot be assessed."
    if LOW in values:
        low = sorted(k for k, v in dimensions.items() if v == LOW)
        return INDIRECT, (f"LOW match on {', '.join(low)}. A decisive mismatch on any single "
                          f"dimension makes the evidence indirect for this question; it is not "
                          f"offset by high ratings elsewhere.")
    if RATING_UNKNOWN in values:
        unrated = sorted(k for k, v in dimensions.items() if v == RATING_UNKNOWN)
        return UNKNOWN, (f"{', '.join(unrated)} could not be rated against the framed question. "
                         f"An unrated dimension is not assumed to match.")
    if MODERATE in values:
        mod = sorted(k for k, v in dimensions.items() if v == MODERATE)
        return PARTIALLY_DIRECT, (f"MODERATE match on {', '.join(mod)}; all other rated "
                                  f"dimensions HIGH.")
    return DIRECT, "HIGH match on every rated dimension against the framed question."


def assess(dimensions=None, design_classification=None, outcome_is_patient_important=None):
    """
    dimensions: dict of DIMENSIONS -> rating. Any dimension omitted is treated as UNKNOWN,
        which is the honest default: not rated is not the same as matching.
    design_classification: a study_design.DesignClassification. When it is a laboratory,
        computational or registry record, the verdict is capped at INDIRECT.
    outcome_is_patient_important: optional bool. False (a surrogate outcome — bond strength,
        marginal gap, a radiographic proxy) forces the outcome dimension to LOW, because a
        surrogate does not directly answer a question about patients.

    Returns a DirectnessAssessment.
    """
    dims = {d: RATING_UNKNOWN for d in DIMENSIONS}
    for key, value in (dimensions or {}).items():
        if key not in DIMENSIONS:
            raise ValueError(f"{key!r} is not one of the six directness dimensions {DIMENSIONS}")
        if value not in RATINGS and value != NOT_APPLICABLE:
            raise ValueError(f"{value!r} is not a valid rating; use one of {RATINGS} or N/A")
        dims[key] = value

    if outcome_is_patient_important is False:
        dims["outcome"] = LOW

    verdict, rationale = aggregate(dims)

    capped_from = None
    cap_reason = None
    if design_classification is not None:
        cap = None
        if design_classification.registry_only:
            cap, cap_reason = INDIRECT, REGISTRY_CAP_NOTE
        elif design_classification.lab_firewall or \
                design_classification.design in (sd.IN_VITRO, sd.FINITE_ELEMENT):
            cap, cap_reason = INDIRECT, LAB_CAP_NOTE
        if cap is not None and _ORDER[verdict] > _ORDER[cap]:
            capped_from, verdict = verdict, cap
            rationale = (f"{rationale} Capped from {capped_from} to {cap}: {cap_reason}")

    return DirectnessAssessment(verdict, dims, rationale, capped_from, cap_reason)


def is_at_least(verdict, minimum):
    """Comparison helper for gates that require, say, at least PARTIALLY DIRECT."""
    return _ORDER[verdict] >= _ORDER[minimum]

"""
evidence/conflict.py  —  CONFLICTING EVIDENCE (v1.2)

When high-quality sources disagree, the disagreement IS the finding.

WHAT THIS MODULE REFUSES TO DO
------------------------------
It provides no way to average two effect estimates, and that absence is the design. Informally
pooling a 92% survival figure from one review and an 81% figure from another produces 86.5% — a
number that appears in neither source, describes no population, and inherits the weaknesses of
both. It reads as a synthesis and is a fabrication. Where pooling is legitimate it is done by
meta-analysts with the primary data, and its result is retrieved, not computed here.

The alternative offered instead is an EVIDENCE CONFLICT: both positions stated in full, with the
concrete dimensions along which the studies differ, a candidate explanation for the divergence,
and what would settle it.

CONFLICT IS NOT THE SAME AS DISAGREEMENT IN QUALITY
---------------------------------------------------
Two sources pointing different ways are only a conflict when both are strong enough to be taken
seriously. A retracted paper does not conflict with anything — it is excluded. An in-vitro result
does not conflict with a clinical trial — they answer different questions, and the laboratory
firewall already governs that. `detect()` therefore screens on certainty and directness before
reporting a conflict, and reports the weaker-source case as a `SUPERSEDED_BY_QUALITY` note rather
than as a genuine disagreement.
"""
import _paths  # noqa: F401

import certainty as ce
import directness as dr

# Direction a source's finding points, relative to the framed comparison.
FAVOURS_INTERVENTION = "FAVOURS_INTERVENTION"
FAVOURS_COMPARATOR = "FAVOURS_COMPARATOR"
NO_DIFFERENCE = "NO_DIFFERENCE"
DIRECTION_UNCLEAR = "DIRECTION_UNCLEAR"
DIRECTIONS = (FAVOURS_INTERVENTION, FAVOURS_COMPARATOR, NO_DIFFERENCE, DIRECTION_UNCLEAR)

# The dimensions along which two disagreeing bodies of evidence are compared. Every one of them
# must be answered — with "not established" where that is the truth — before a conflict is
# reported, because "the studies just disagree" is where explanation stops being attempted.
COMPARISON_DIMENSIONS = ("population", "methods", "follow_up", "interventions", "risk_of_bias")

EVIDENCE_CONFLICT = "EVIDENCE CONFLICT"
SUPERSEDED_BY_QUALITY = "SUPERSEDED_BY_QUALITY"

NOT_ESTABLISHED = "not established"

NO_AVERAGING_RULE = (
    "Conflicting estimates are never averaged, split, or reconciled into a middle value. A "
    "number that appears in neither source describes no population and cannot be cited. Both "
    "positions are reported as they stand."
)

# A source must reach at least this certainty, and at least this directness, before its
# disagreement with another source counts as a genuine evidence conflict.
MIN_CERTAINTY_FOR_CONFLICT = (ce.HIGH, ce.MODERATE, ce.LOW)
MIN_DIRECTNESS_FOR_CONFLICT = dr.PARTIALLY_DIRECT


class EvidenceSource:
    """One side of a disagreement, with everything needed to explain it."""

    def __init__(self, record_id, finding, direction, design=None, certainty=None,
                 directness=None, population=None, methods=None, follow_up=None,
                 interventions=None, risk_of_bias=None, citation_state=None):
        if direction not in DIRECTIONS:
            raise ValueError(f"{direction!r} is not one of {DIRECTIONS}")
        self.record_id = record_id
        self.finding = finding
        self.direction = direction
        self.design = design
        self.certainty = certainty
        self.directness = directness
        self.citation_state = citation_state
        self.population = population
        self.methods = methods
        self.follow_up = follow_up
        self.interventions = interventions
        self.risk_of_bias = risk_of_bias

    def dimension(self, name):
        return getattr(self, name, None) or NOT_ESTABLISHED

    @property
    def certainty_rating(self):
        return getattr(self.certainty, "rating", self.certainty)

    @property
    def directness_verdict(self):
        return getattr(self.directness, "verdict", self.directness)

    def to_dict(self):
        return {
            "record_id": self.record_id, "finding": self.finding, "direction": self.direction,
            "design": getattr(self.design, "design", self.design),
            "certainty": self.certainty_rating, "directness": self.directness_verdict,
            "citation_state": self.citation_state,
            **{d: self.dimension(d) for d in COMPARISON_DIMENSIONS},
        }


class EvidenceConflict:
    def __init__(self, source_a, source_b, likely_explanation=None, what_would_settle_it=None,
                 effect_on_decision=None):
        self.source_a = source_a
        self.source_b = source_b
        self.likely_explanation = likely_explanation
        self.what_would_settle_it = what_would_settle_it
        self.effect_on_decision = effect_on_decision

    def differences(self):
        """Dimension-by-dimension comparison. A dimension where either side is not established is
        reported as such — an unexplained difference is not the same as no difference."""
        out = {}
        for dim in COMPARISON_DIMENSIONS:
            a, b = self.source_a.dimension(dim), self.source_b.dimension(dim)
            out[dim] = {
                "source_a": a, "source_b": b,
                "differs": (a != b) if NOT_ESTABLISHED not in (a, b) else None,
            }
        return out

    def unexplained_dimensions(self):
        return [d for d, v in self.differences().items() if v["differs"] is None]

    def to_dict(self):
        return {
            "type": EVIDENCE_CONFLICT,
            "source_a": self.source_a.to_dict(),
            "source_b": self.source_b.to_dict(),
            "differences": self.differences(),
            "unexplained_dimensions": self.unexplained_dimensions(),
            "likely_explanation": self.likely_explanation or (
                "Not established. The divergence has not been explained; it is reported as an "
                "open disagreement rather than attributed to a cause that was not identified."),
            "effect_on_decision": self.effect_on_decision or (
                "The conflict lowers the confidence available for this decision. State what each "
                "source shows and proceed under the disagreement rather than behind it."),
            "what_would_settle_it": self.what_would_settle_it or (
                "Not established — name the study or data that would resolve it."),
            "no_averaging_rule": NO_AVERAGING_RULE,
            "pooled_estimate": None,
        }

    def to_markdown(self):
        a, b = self.source_a, self.source_b
        lines = [f"### {EVIDENCE_CONFLICT}", "",
                 f"**Source A — {a.record_id}**  ",
                 f"{a.finding}  ",
                 f"Design: {getattr(a.design, 'design', a.design)} · Certainty: {a.certainty_rating} · "
                 f"Directness: {a.directness_verdict} · Citation: {a.citation_state}", "",
                 f"**Source B — {b.record_id}**  ",
                 f"{b.finding}  ",
                 f"Design: {getattr(b.design, 'design', b.design)} · Certainty: {b.certainty_rating} · "
                 f"Directness: {b.directness_verdict} · Citation: {b.citation_state}", "",
                 "**Where they differ**", "",
                 "| Dimension | Source A | Source B |", "|---|---|---|"]
        for dim, values in self.differences().items():
            lines.append(f"| {dim.replace('_', ' ')} | {values['source_a']} | {values['source_b']} |")
        d = self.to_dict()
        lines += ["", f"**Likely explanation for the disagreement:** {d['likely_explanation']}",
                  "", f"**What it means for this decision:** {d['effect_on_decision']}",
                  "", f"**What would settle it:** {d['what_would_settle_it']}",
                  "", f"_{NO_AVERAGING_RULE}_"]
        return "\n".join(lines)


def _strong_enough(source):
    return (source.certainty_rating in MIN_CERTAINTY_FOR_CONFLICT
            and source.directness_verdict in dr.VERDICTS
            and dr.is_at_least(source.directness_verdict or dr.UNKNOWN,
                               MIN_DIRECTNESS_FOR_CONFLICT))


def detect(sources):
    """
    sources: list of EvidenceSource.

    Returns {"conflicts": [EvidenceConflict], "quality_notes": [...], "directions": {...}}.

    A conflict is reported when two sources point in opposing directions AND both are strong
    enough to be taken seriously. Where one side is materially weaker, a quality note is emitted
    instead — that is not a conflict in the evidence, it is a difference in evidence quality, and
    presenting it as a conflict would give the weaker source a standing it has not earned.
    """
    conflicts = []
    quality_notes = []
    opposing = {FAVOURS_INTERVENTION: FAVOURS_COMPARATOR, FAVOURS_COMPARATOR: FAVOURS_INTERVENTION}

    for i, a in enumerate(sources):
        for b in sources[i + 1:]:
            if a.direction == DIRECTION_UNCLEAR or b.direction == DIRECTION_UNCLEAR:
                continue
            genuinely_opposed = (opposing.get(a.direction) == b.direction) or (
                {a.direction, b.direction} == {FAVOURS_INTERVENTION, NO_DIFFERENCE}) or (
                {a.direction, b.direction} == {FAVOURS_COMPARATOR, NO_DIFFERENCE})
            if not genuinely_opposed:
                continue

            a_ok, b_ok = _strong_enough(a), _strong_enough(b)
            if a_ok and b_ok:
                conflicts.append(EvidenceConflict(a, b))
            elif a_ok or b_ok:
                stronger, weaker = (a, b) if a_ok else (b, a)
                quality_notes.append({
                    "type": SUPERSEDED_BY_QUALITY,
                    "stronger": stronger.record_id, "weaker": weaker.record_id,
                    "reason": (
                        f"{weaker.record_id} points the other way, but its certainty is "
                        f"{weaker.certainty_rating} and its directness {weaker.directness_verdict}. "
                        f"This is a difference in evidence quality, not a conflict between "
                        f"comparable bodies of evidence. Report the divergence, and do not present "
                        f"the weaker source as an equal counterweight."),
                })
            else:
                quality_notes.append({
                    "type": SUPERSEDED_BY_QUALITY,
                    "stronger": None, "weaker": f"{a.record_id}, {b.record_id}",
                    "reason": ("Both sources are too weak or too indirect for their disagreement "
                               "to settle anything. The honest reading is that the evidence does "
                               "not currently answer this question."),
                })

    return {"conflicts": conflicts, "quality_notes": quality_notes,
            "directions": {s.record_id: s.direction for s in sources}}

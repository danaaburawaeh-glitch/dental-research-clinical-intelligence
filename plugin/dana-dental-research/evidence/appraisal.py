"""
evidence/appraisal.py  —  EVIDENCE APPRAISAL ENGINE (v1.2)

Records what is actually known about how well a study was conducted, and — with equal weight —
what is not known.

THE DESIGN PROBLEM THIS SOLVES
------------------------------
An appraisal form with fifteen fields invites completion. The temptation, for a language model
as much as for a tired reviewer, is to fill a blank with something plausible: a sample size that
sounds right for the design, a follow-up that matches the abstract's framing, a risk-of-bias
judgement extrapolated from the journal's reputation. Every one of those is an invention wearing
the costume of an appraisal.

So a field here cannot hold a bare value. It holds a value AND the provenance of that value, and
the provenance vocabulary is deliberately three words wide:

    REPORTED  — the source states it. Record where: abstract, full text, registry entry.
    INFERRED  — derived from something the source does state. The basis is mandatory and is
                stored; an INFERRED field without a basis is refused at construction time.
    UNKNOWN   — not established. This is the default for every field, and it is a legitimate,
                complete answer that requires no apology.

`UNKNOWN` is not a gap to be closed before the appraisal is usable. It is the appraisal's most
important output, because it is what the certainty engine reads to decide that a body of
evidence is NOT ASSESSABLE rather than quietly rating it LOW.

FORMAL TOOLS
------------
RoB 2, ROBINS-I, AMSTAR 2, QUADAS-2 and GRADE are named only when two conditions hold: the
design is one the tool applies to, and the information the tool requires was actually available.
`risk_of_bias()` refuses to attach a tool name otherwise. A structured judgement without a tool
name is honest; a tool name over partial information is a fabricated credential.
"""
import _paths  # noqa: F401

import study_design as sd

REPORTED = "REPORTED"
INFERRED = "INFERRED"
UNKNOWN = "UNKNOWN"
PROVENANCE = (REPORTED, INFERRED, UNKNOWN)

# Where a REPORTED value came from. Recorded because an abstract-sourced number and a
# full-text-sourced number are not equally reliable, and §6 of the brief turns on the difference.
FROM_ABSTRACT = "abstract"
FROM_FULL_TEXT = "full_text"
FROM_REGISTRY = "registry"
FROM_STRUCTURED_METADATA = "structured_metadata"
FROM_USER = "user_supplied"


class ProvenanceError(ValueError):
    """Raised when a field is given a value without a defensible account of where it came from."""


class AppraisalField:
    """One appraised item: a value, its provenance, and — when inferred — its basis."""

    __slots__ = ("value", "provenance", "source", "basis", "note")

    def __init__(self, value=None, provenance=UNKNOWN, source=None, basis=None, note=None):
        if provenance not in PROVENANCE:
            raise ProvenanceError(f"{provenance!r} is not one of {PROVENANCE}")
        if provenance == INFERRED and not basis:
            raise ProvenanceError(
                "An INFERRED appraisal value requires a basis naming what it was inferred from. "
                "Without one it is indistinguishable from an invented value.")
        if provenance == REPORTED and value is None:
            raise ProvenanceError(
                "A field cannot be REPORTED with no value. If the source does not state it, "
                "the provenance is UNKNOWN.")
        if provenance == UNKNOWN and value is not None:
            raise ProvenanceError(
                "A field with a value cannot carry UNKNOWN provenance — say where it came from.")
        self.value = value
        self.provenance = provenance
        self.source = source
        self.basis = basis
        self.note = note

    @property
    def known(self):
        return self.provenance in (REPORTED, INFERRED)

    def to_dict(self):
        return {"value": self.value, "provenance": self.provenance, "source": self.source,
                "basis": self.basis, "note": self.note}

    def __repr__(self):
        return f"<AppraisalField {self.value!r} {self.provenance}>"


def unknown(note=None):
    """The default state of every appraisal field. Explicit, not empty."""
    return AppraisalField(None, UNKNOWN, note=note)


def reported(value, source=FROM_ABSTRACT, note=None):
    return AppraisalField(value, REPORTED, source=source, note=note)


def inferred(value, basis, note=None):
    return AppraisalField(value, INFERRED, basis=basis, note=note)


# ── The appraisal fields required by the brief ──────────────────────────────────────────────
APPRAISAL_FIELDS = (
    "study_design",
    "sample_size",
    "number_of_studies",
    "number_of_participants",
    "follow_up",
    "comparator_quality",
    "risk_of_bias",
    "outcome_relevance",
    "directness",
    "consistency",
    "precision",
    "publication_bias_signals",
    "funding_conflict_signals",
    "major_limitations",
)

# The domains the certainty engine needs before it will rate anything at all.
CERTAINTY_CRITICAL_FIELDS = ("risk_of_bias", "directness", "consistency", "precision")


class Appraisal:
    """A per-study (or per-body-of-evidence) appraisal. Every field defaults to UNKNOWN."""

    def __init__(self, record_id=None, design_classification=None, **fields):
        unexpected = set(fields) - set(APPRAISAL_FIELDS)
        if unexpected:
            raise ValueError(f"Unknown appraisal field(s): {sorted(unexpected)}")
        self.record_id = record_id
        self.design_classification = design_classification
        for name in APPRAISAL_FIELDS:
            value = fields.get(name)
            if value is None:
                value = unknown()
            if not isinstance(value, AppraisalField):
                raise ProvenanceError(
                    f"Field {name!r} must be an AppraisalField carrying its provenance, not a "
                    f"bare value. Use reported(), inferred() or unknown().")
            setattr(self, name, value)

        # The design classification is authoritative for the study_design field — it already
        # carries its own provenance and must not be restated by hand.
        if design_classification is not None:
            self.study_design = AppraisalField(
                design_classification.design,
                REPORTED if design_classification.provenance == sd.REPORTED else (
                    INFERRED if design_classification.provenance == sd.INFERRED else UNKNOWN),
                source=FROM_STRUCTURED_METADATA,
                basis=design_classification.basis
                if design_classification.provenance == sd.INFERRED else None,
            ) if design_classification.provenance != sd.UNKNOWN else unknown(
                note=design_classification.basis)

    # ── Completeness reporting ──────────────────────────────────────────────────────────────
    def known_fields(self):
        return tuple(n for n in APPRAISAL_FIELDS if getattr(self, n).known)

    def unknown_fields(self):
        return tuple(n for n in APPRAISAL_FIELDS if not getattr(self, n).known)

    def completeness(self):
        """A count, never a percentage score. A 9/14 'completeness' reads as a grade; the list
        of what is missing is what a reader actually needs."""
        known = self.known_fields()
        return {
            "known": len(known),
            "total": len(APPRAISAL_FIELDS),
            "known_fields": list(known),
            "unknown_fields": list(self.unknown_fields()),
            "certainty_critical_unknown": [f for f in CERTAINTY_CRITICAL_FIELDS
                                           if not getattr(self, f).known],
        }

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "design": (self.design_classification.to_dict()
                       if self.design_classification is not None else None),
            "fields": {n: getattr(self, n).to_dict() for n in APPRAISAL_FIELDS},
            "completeness": self.completeness(),
        }


# ── Formal appraisal tools ──────────────────────────────────────────────────────────────────
ROB2 = "RoB 2"
ROBINS_I = "ROBINS-I"
AMSTAR2 = "AMSTAR 2"
QUADAS2 = "QUADAS-2"
GRADE = "GRADE"

TOOL_APPLICABILITY = {
    ROB2: (sd.RCT,),
    ROBINS_I: (sd.PROSPECTIVE_COHORT, sd.RETROSPECTIVE_COHORT, sd.COHORT_DIRECTION_UNREPORTED,
               sd.CASE_CONTROL),
    AMSTAR2: (sd.SYSTEMATIC_REVIEW, sd.META_ANALYSIS),
    QUADAS2: (sd.DIAGNOSTIC_ACCURACY,),
}

# The minimum items a tool needs before its name may be attached to a judgement. These are the
# domain headings of each instrument, not a re-implementation of it — this module never computes
# a tool's score, it only records a properly-sourced one and refuses an improperly-sourced one.
TOOL_REQUIRED_DOMAINS = {
    ROB2: ("randomisation_process", "deviations_from_intended_interventions", "missing_outcome_data",
           "measurement_of_the_outcome", "selection_of_the_reported_result"),
    ROBINS_I: ("confounding", "selection_of_participants", "classification_of_interventions",
               "deviations_from_intended_interventions", "missing_data",
               "measurement_of_outcomes", "selection_of_the_reported_result"),
    AMSTAR2: ("protocol_registered", "comprehensive_search", "study_selection_duplicate",
              "risk_of_bias_assessment", "appropriate_meta_analysis_methods",
              "publication_bias_assessed"),
    QUADAS2: ("patient_selection", "index_test", "reference_standard", "flow_and_timing"),
}

TOOL_MISUSE_NOTE = (
    "A formal appraisal tool was NOT applied. Naming a tool over partial information would "
    "present an unearned credential — the judgement below is a structured reading of what the "
    "source reports, and is labelled as such."
)


def risk_of_bias(design_classification, tool=None, domain_judgements=None, overall=None,
                 source=FROM_FULL_TEXT, note=None):
    """
    Record a risk-of-bias judgement.

    tool: one of ROB2 / ROBINS_I / AMSTAR2 / QUADAS2, or None for a structured non-tool reading.
    domain_judgements: dict of the tool's own domains -> judgement, as reported by whoever
        applied it. Required, and checked for completeness, whenever `tool` is named.

    Returns an AppraisalField. Refuses to attach a tool name when the tool does not apply to
    this design, or when its required domains were not supplied — the two ways a tool name gets
    borrowed rather than earned.
    """
    if tool is None:
        if overall is None:
            return unknown(note=note or "Risk of bias was not assessed.")
        return AppraisalField(
            {"tool": None, "overall": overall, "domains": domain_judgements or {}},
            REPORTED, source=source,
            note=note or TOOL_MISUSE_NOTE)

    if tool not in TOOL_APPLICABILITY:
        raise ValueError(f"{tool!r} is not a recognised appraisal tool")

    applicable = TOOL_APPLICABILITY[tool]
    design = design_classification.design if design_classification else None
    if design not in applicable:
        raise ValueError(
            f"{tool} does not apply to a {design!r}. It applies to {list(applicable)}. "
            f"Applying it anyway would produce a rating the instrument does not support.")

    supplied = set(domain_judgements or {})
    required = set(TOOL_REQUIRED_DOMAINS[tool])
    missing = sorted(required - supplied)
    if missing:
        raise ValueError(
            f"{tool} requires all of {sorted(required)}. Missing: {missing}. A partial "
            f"application must not be reported under the tool's name — record a structured "
            f"judgement with tool=None instead.")

    return AppraisalField(
        {"tool": tool, "overall": overall, "domains": dict(domain_judgements)},
        REPORTED, source=source, note=note)


def appraise(record, design_classification=None, extracted=None):
    """
    Build an Appraisal from a retrieved record plus whatever was actually extracted from it.

    `extracted` is a dict of AppraisalField objects keyed by APPRAISAL_FIELDS names. Anything
    absent from it stays UNKNOWN. Nothing in this function reads a value out of the record's
    prose and promotes it to REPORTED — extraction is a separate, explicit act performed by the
    caller who actually read the source.
    """
    classification = design_classification or sd.classify(record)
    fields = dict(extracted or {})

    # The one thing that can be filled automatically, because it is a structured fact about the
    # record rather than a reading of its contents.
    if classification.registry_only and "major_limitations" not in fields:
        fields["major_limitations"] = reported(
            "Registry record: describes a planned or conducted trial, not its findings. "
            "REGISTRY ONLY — NOT EVIDENCE OF EFFICACY.",
            source=FROM_REGISTRY)

    return Appraisal(record_id=record.get("pmid") or record.get("doi") or record.get("nct_id"),
                     design_classification=classification, **fields)

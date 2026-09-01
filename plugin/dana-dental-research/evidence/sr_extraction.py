"""
evidence/sr_extraction.py  —  SYSTEMATIC REVIEW INTELLIGENCE (v1.2)

Structured extraction of what a systematic review or meta-analysis actually reports.

THE FABRICATION RISK THIS MODULE IS BUILT AROUND
------------------------------------------------
A systematic review's abstract typically states its headline: how many studies, a pooled
estimate, sometimes an I-squared value. It typically does NOT state its risk-of-bias
instrument's per-domain findings, its funnel-plot inspection, its full participant total, or its
limitations section. Those live in the full text — which this system does not retrieve, because
no connector in this plugin provides full text (Crossref supplies metadata, never content).

The failure mode is therefore specific and predictable: an abstract-derived extraction gets
completed from plausible knowledge of how such reviews are usually reported, and the resulting
table looks like a full-text extraction. Every number in it would be real-sounding and
unsourced.

So this module distinguishes two kinds of blank, and refuses to let a value exist without a
stated origin:

    NOT REPORTED    — the source was read and does not state this. A finding about the review.
    NOT AVAILABLE   — the source was not read at this depth. A finding about our retrieval.

`NOT AVAILABLE` is the default for every field whenever `full_text_retrieved` is False, and a
field cannot be set from a full-text-only origin while that flag is False.
"""
import _paths  # noqa: F401

import study_design as sd
from appraisal import (AppraisalField, ProvenanceError, REPORTED, UNKNOWN,
                       FROM_ABSTRACT, FROM_FULL_TEXT, FROM_REGISTRY, FROM_USER)

NOT_REPORTED = "NOT REPORTED"
NOT_AVAILABLE = "NOT AVAILABLE"

# Every field the brief requires, in its order.
SR_FIELDS = (
    "number_of_included_studies",
    "study_designs_included",
    "total_participants",
    "intervention",
    "comparator",
    "follow_up",
    "primary_outcomes",
    "pooled_effect_estimates",
    "confidence_intervals",
    "heterogeneity",
    "risk_of_bias_method",
    "grade_method",
    "publication_bias_assessment",
    "major_limitations",
)

# Fields that in practice are only reliably established from the full text. Attempting to set
# one from an abstract is allowed but recorded, because abstracts do sometimes carry them; what
# is refused is setting one at all when nothing beyond metadata was retrieved.
FULL_TEXT_TYPICAL_FIELDS = (
    "risk_of_bias_method", "grade_method", "publication_bias_assessment", "major_limitations",
    "study_designs_included",
)

# Fields carrying numbers that the Numeric Evidence Gate will police downstream.
NUMERIC_FIELDS = ("number_of_included_studies", "total_participants", "pooled_effect_estimates",
                  "confidence_intervals", "heterogeneity")


class SystematicReviewProfile:
    """
    Extraction record for one systematic review or meta-analysis.

    full_text_retrieved: whether the full text was actually obtained and read. Defaults to False,
    which is the truth for every record this plugin retrieves through its own connectors.
    """

    def __init__(self, record_id=None, design_classification=None, full_text_retrieved=False,
                 **fields):
        if design_classification is not None and design_classification.design not in (
                sd.SYSTEMATIC_REVIEW, sd.META_ANALYSIS):
            raise ValueError(
                f"This profile applies to a systematic review or meta-analysis; the record was "
                f"classified as {design_classification.design!r}. Extracting review-level fields "
                f"from a record that is not a review would misrepresent what it contains.")

        unexpected = set(fields) - set(SR_FIELDS)
        if unexpected:
            raise ValueError(f"Unknown systematic-review field(s): {sorted(unexpected)}")

        self.record_id = record_id
        self.design_classification = design_classification
        self.full_text_retrieved = bool(full_text_retrieved)

        for name in SR_FIELDS:
            value = fields.get(name)
            if value is None:
                value = self._default_absent()
            elif not isinstance(value, AppraisalField):
                raise ProvenanceError(
                    f"Field {name!r} must be an AppraisalField carrying its provenance. A bare "
                    f"value has no origin, and a review field with no origin is the exact "
                    f"failure mode this module exists to prevent.")
            elif value.provenance == REPORTED and not self.full_text_retrieved and \
                    value.source == FROM_FULL_TEXT:
                raise ProvenanceError(
                    f"Field {name!r} is marked as reported from the full text, but "
                    f"full_text_retrieved is False. Set full_text_retrieved=True only when the "
                    f"full text was genuinely obtained.")
            setattr(self, name, value)

    def _default_absent(self):
        if self.full_text_retrieved:
            return AppraisalField(None, UNKNOWN, note=NOT_REPORTED)
        return AppraisalField(None, UNKNOWN, note=NOT_AVAILABLE)

    # ── Reporting ───────────────────────────────────────────────────────────────────────────
    def absent_fields(self):
        """Returns {field: NOT REPORTED | NOT AVAILABLE} for everything not established."""
        out = {}
        for name in SR_FIELDS:
            field = getattr(self, name)
            if not field.known:
                out[name] = field.note or (NOT_REPORTED if self.full_text_retrieved
                                           else NOT_AVAILABLE)
        return out

    def established_fields(self):
        return tuple(n for n in SR_FIELDS if getattr(self, n).known)

    def numeric_claims(self):
        """Every extracted number, with the source that carries it. The Numeric Evidence Gate
        reads this to decide whether a figure may appear in a Clinical Bottom Line."""
        claims = []
        for name in NUMERIC_FIELDS:
            field = getattr(self, name)
            if field.known:
                claims.append({
                    "field": name, "value": field.value, "provenance": field.provenance,
                    "source": field.source, "record_id": self.record_id,
                })
        return claims

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "design": (self.design_classification.to_dict()
                       if self.design_classification else None),
            "full_text_retrieved": self.full_text_retrieved,
            "fields": {n: getattr(self, n).to_dict() for n in SR_FIELDS},
            "established_fields": list(self.established_fields()),
            "absent_fields": self.absent_fields(),
            "extraction_caveat": (
                None if self.full_text_retrieved else
                "The full text of this review was not retrieved. Fields marked NOT AVAILABLE "
                "were not read and are not a statement about what the review contains. No "
                "connector in this plugin supplies full text — Crossref provides metadata only."),
        }

    def to_markdown(self):
        rows = ["| Field | Value | Provenance |", "|---|---|---|"]
        for name in SR_FIELDS:
            field = getattr(self, name)
            if field.known:
                value = str(field.value)
                prov = f"{field.provenance} ({field.source})" if field.source else field.provenance
            else:
                value = field.note or NOT_AVAILABLE
                prov = "—"
            rows.append(f"| {name.replace('_', ' ')} | {value} | {prov} |")
        return "\n".join(rows)


def from_abstract(record, design_classification=None, **extracted):
    """
    Build a profile from a record whose abstract (and structured metadata) is all that was
    retrieved. Everything not explicitly passed comes back NOT AVAILABLE.

    Convenience only — it adds nothing that could not be constructed directly, and it deliberately
    refuses to parse the abstract text for numbers. Reading "34 studies were included" out of an
    abstract string and recording it as REPORTED is exactly the kind of automated extraction that
    produces a confidently wrong table when the sentence was "34 studies were screened".
    """
    classification = design_classification or sd.classify(record)
    return SystematicReviewProfile(
        record_id=record.get("pmid") or record.get("doi"),
        design_classification=classification,
        full_text_retrieved=False,
        **extracted)

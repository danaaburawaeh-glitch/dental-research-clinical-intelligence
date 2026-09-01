"""
evidence/pipeline.py  —  THE SIX-STAGE SEPARATION (v1.2)

The v1.2 brief's central architectural requirement: retrieval, verification, appraisal,
certainty, synthesis and clinical applicability are six distinct stages, and a result from one
never substitutes for a result from another.

    RETRIEVAL      -> the record exists and was fetched
    VERIFICATION   -> the citation is accurate, and the paper has not been retracted
    APPRAISAL      -> how well the study was conducted, and what was not established
    CERTAINTY      -> how much confidence the body of evidence justifies
    SYNTHESIS      -> what the assembled evidence says, with conflicts preserved
    APPLICABILITY  -> whether it applies to this patient, in this setting

WHY A STATE MACHINE
-------------------
Every one of these collapses into the one before it under pressure. Retrieval becomes evidence
("PubMed returned 431 results"). Verification becomes appraisal ("the citation checks out, so
the finding stands"). Appraisal becomes certainty ("large sample, therefore reliable"). Certainty
becomes applicability ("high certainty, therefore do it for this patient"). Each collapse is a
single plausible sentence away, and none of them announces itself.

`EvidencePipeline` makes the boundaries load-bearing: a stage cannot run before its predecessor,
`synthesise()` refuses records that have not passed verification, and `stage_report()` shows
which stage every conclusion actually came from.

ORDERING GUARANTEE (inherited from v0.4.3, preserved)
------------------------------------------------------
The retraction gate runs before study classification and DEL-7 tagging, not after. A retracted
record must never be classified as usable evidence even transiently — PIPELINE_ORDERING_AUDIT.md
records why that ordering is checked rather than assumed.
"""
import _paths  # noqa: F401

import appraisal as ap
import certainty as ce
import citation_verification as cv
import directness as dr
import numeric_gate as ng
import overlap as ov
import study_design as sd
from shared.retraction_gate import apply_retraction_gate

RETRIEVAL = "RETRIEVAL"
VERIFICATION = "VERIFICATION"
APPRAISAL = "APPRAISAL"
CERTAINTY = "CERTAINTY"
SYNTHESIS = "SYNTHESIS"
APPLICABILITY = "CLINICAL_APPLICABILITY"

STAGES = (RETRIEVAL, VERIFICATION, APPRAISAL, CERTAINTY, SYNTHESIS, APPLICABILITY)


class StageError(RuntimeError):
    """Raised when a stage is run out of order, or on records that have not cleared the stage
    before it."""


class PipelineRecord:
    """One record, and the outcome of each stage it has passed through."""

    def __init__(self, record):
        self.record = record
        self.retraction_outcome = None      # "included" | "excluded" | "flagged"
        self.retraction_reason = None
        self.verification = None
        self.design_classification = None
        self.appraisal = None
        self.directness = None
        self.certainty = None
        self.excluded_at = None
        self.exclusion_reason = None

    @property
    def record_id(self):
        return (self.record.get("pmid") or self.record.get("doi")
                or self.record.get("nct_id") or self.record.get("title"))

    @property
    def is_excluded(self):
        return self.excluded_at is not None

    @property
    def citation_state(self):
        return self.verification["state"] if self.verification else None

    @property
    def del7_tag(self):
        return sd.del7_tag(self.design_classification) if self.design_classification else "UNVER"

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "retraction_outcome": self.retraction_outcome,
            "retraction_reason": self.retraction_reason,
            "citation_state": self.citation_state,
            "design": (self.design_classification.to_dict()
                       if self.design_classification else None),
            "del7_tag": self.del7_tag,
            "directness": self.directness.to_dict() if self.directness else None,
            "certainty": self.certainty.to_dict() if self.certainty else None,
            "appraisal": self.appraisal.to_dict() if self.appraisal else None,
            "excluded_at": self.excluded_at,
            "exclusion_reason": self.exclusion_reason,
        }


class EvidencePipeline:
    def __init__(self, question=None, search_strategy=None):
        self.question = question
        self.search_strategy = search_strategy
        self.records = []
        self.completed_stages = []
        self.overlap_result = None
        self.notes = []

    # ── Stage guard ─────────────────────────────────────────────────────────────────────────
    def _require(self, stage):
        index = STAGES.index(stage)
        if index and STAGES[index - 1] not in self.completed_stages:
            raise StageError(
                f"{stage} cannot run before {STAGES[index - 1]}. The stages are separate on "
                f"purpose: a result from one never stands in for a result from another.")
        if stage in self.completed_stages:
            raise StageError(f"{stage} has already run.")

    def _complete(self, stage):
        self.completed_stages.append(stage)

    # ── 1. RETRIEVAL ────────────────────────────────────────────────────────────────────────
    def retrieve(self, records, connector_status=None):
        """Accept what the connectors returned. Nothing is judged here — a retrieved record is a
        record, not evidence."""
        self._require(RETRIEVAL)
        self.records = [PipelineRecord(r) for r in records]
        self.overlap_result = ov.detect(records)
        self.notes.append({
            "stage": RETRIEVAL, "connector_status": connector_status,
            "retrieved": len(self.records),
            "independent_studies": self.overlap_result["independent_study_count"],
            "cohort_overlap": [a.to_dict() for a in self.overlap_result["cohort_assessments"]],
            "cohort_assessment_coverage": self.overlap_result["cohort_assessment_coverage"],
            "note": ("A retrieval count is not an evidence count. "
                     f"{len(self.records)} records reduce to "
                     f"{self.overlap_result['independent_study_count']} independent studies "
                     f"after overlap detection."),
        })
        self._complete(RETRIEVAL)
        return self

    # ── 2. VERIFICATION (retraction gate first, then citation) ──────────────────────────────
    def verify(self, verifications=None, crossref_records=None):
        """
        verifications: optional {record_id: verify_citation() result} where the caller already
            performed the dual-source check (e.g. over the remote MCP transport).
        crossref_records: optional {record_id: crossref EvidenceRecord} to check against.

        The retraction gate runs FIRST — before any classification — preserving the v0.4.3
        ordering guarantee.
        """
        self._require(VERIFICATION)

        gated = apply_retraction_gate([r.record for r in self.records])
        by_id = {}
        for outcome in ("included", "excluded", "flagged"):
            for record in gated[outcome]:
                key = (record.get("pmid") or record.get("doi") or record.get("nct_id")
                       or record.get("title"))
                by_id[key] = (outcome, record.get("exclusion_reason") or record.get("flag_reason"))

        for pr in self.records:
            outcome, reason = by_id.get(pr.record_id, ("included", None))
            pr.retraction_outcome = outcome
            pr.retraction_reason = reason
            if outcome == "excluded":
                pr.excluded_at = VERIFICATION
                pr.exclusion_reason = reason or "RETRACTED — EXCLUDED FROM SYNTHESIS"

            supplied = (verifications or {}).get(pr.record_id)
            if supplied is not None:
                pr.verification = supplied
            else:
                crossref = (crossref_records or {}).get(pr.record_id)
                pr.verification = cv.verify_citation(pr.record, crossref)

            if pr.verification["state"] == cv.RETRACTED and not pr.is_excluded:
                pr.excluded_at = VERIFICATION
                pr.exclusion_reason = "RETRACTED — EXCLUDED FROM SYNTHESIS"

        self.notes.append({
            "stage": VERIFICATION,
            "excluded": [r.record_id for r in self.records if r.is_excluded],
            "flagged": [r.record_id for r in self.records if r.retraction_outcome == "flagged"],
            "note": ("Verification establishes that a citation is accurate and that the paper "
                     "stands. It establishes nothing about the strength of what the paper found."),
        })
        self._complete(VERIFICATION)
        return self

    def active_records(self):
        return [r for r in self.records if not r.is_excluded]

    # ── 3. APPRAISAL ────────────────────────────────────────────────────────────────────────
    def appraise(self, extractions=None):
        """extractions: {record_id: {field: AppraisalField}} — whatever was actually extracted."""
        self._require(APPRAISAL)
        extractions = extractions or {}
        for pr in self.active_records():
            pr.design_classification = sd.classify(pr.record)
            pr.appraisal = ap.appraise(pr.record, pr.design_classification,
                                       extractions.get(pr.record_id))
        self.notes.append({
            "stage": APPRAISAL,
            "note": ("Study design was classified only after the retraction gate ran — a "
                     "retracted record is never classified as usable evidence, even transiently."),
            "unknown_fields": {r.record_id: r.appraisal.completeness()["unknown_fields"]
                               for r in self.active_records()},
        })
        self._complete(APPRAISAL)
        return self

    # ── 4. CERTAINTY ────────────────────────────────────────────────────────────────────────
    def assess_certainty(self, directness_ratings=None, domains=None, pools_randomized=None,
                         author_grades=None):
        self._require(CERTAINTY)
        directness_ratings = directness_ratings or {}
        domains = domains or {}
        pools_randomized = pools_randomized or {}
        author_grades = author_grades or {}

        for pr in self.active_records():
            pr.directness = dr.assess(directness_ratings.get(pr.record_id),
                                      pr.design_classification)
            record_domains = domains.get(pr.record_id)
            self._record_domains_in_appraisal(pr, record_domains)
            pr.certainty = ce.assess(
                pr.design_classification, pr.appraisal, pr.directness,
                domains=record_domains,
                pools_randomized_trials=pools_randomized.get(pr.record_id),
                author_grade=author_grades.get(pr.record_id))

        self.notes.append({
            "stage": CERTAINTY,
            "not_assessable": [r.record_id for r in self.active_records()
                               if r.certainty.rating == ce.NOT_ASSESSABLE],
            "note": ("Certainty is the system's own structured assessment, not GRADE. Where a "
                     "record's domains were not established, it is NOT ASSESSABLE rather than "
                     "rated low."),
        })
        self._complete(CERTAINTY)
        return self

    @staticmethod
    def _record_domains_in_appraisal(pipeline_record, record_domains):
        """
        A GRADE domain judgement supplied at the certainty stage IS an appraisal finding — it
        states that risk of bias, consistency or precision was assessed and what was found. It is
        written back into the appraisal so the two stages cannot disagree about what is known.

        Without this the cross-check in `certainty.assess()` blocks every rating, because the
        appraisal would record the domains as UNKNOWN while the caller had just judged them. The
        provenance recorded is FROM_USER: these came from the layer performing the assessment,
        not from the record's own metadata, and the appraisal says so.
        """
        if not record_domains:
            return
        mapping = {"risk_of_bias": "risk_of_bias", "inconsistency": "consistency",
                   "imprecision": "precision"}
        appraisal = pipeline_record.appraisal
        for domain, level in record_domains.items():
            field_name = mapping.get(domain)
            if field_name and not getattr(appraisal, field_name).known:
                setattr(appraisal, field_name, ap.reported(
                    level, source=ap.FROM_USER,
                    note=("Judged at the certainty stage by the assessing layer, not read from "
                          "the record's own metadata.")))
        if not appraisal.directness.known and pipeline_record.directness is not None:
            appraisal.directness = ap.reported(
                pipeline_record.directness.verdict, source=ap.FROM_USER,
                note="Taken from the directness assessment performed at the certainty stage.")

    # ── 5. SYNTHESIS ────────────────────────────────────────────────────────────────────────
    def synthesise(self):
        """Sort the surviving records into the four buckets. Refuses to run over unverified or
        unappraised records — the guarantee that a synthesis cannot outrun its evidence."""
        self._require(SYNTHESIS)

        for pr in self.active_records():
            if pr.verification is None:
                raise StageError(f"{pr.record_id} reached synthesis without verification.")
            if pr.certainty is None:
                raise StageError(f"{pr.record_id} reached synthesis without a certainty "
                                 f"assessment.")
            if pr.citation_state == cv.RETRACTED:
                raise StageError(
                    f"{pr.record_id} is RETRACTED and reached synthesis. This is the single most "
                    f"severe failure this pipeline exists to prevent.")

        buckets = {"DIRECT_EVIDENCE": [], "INDIRECT_SUPPORTING_EVIDENCE": [],
                   "CLINICAL_EXTRAPOLATION": [], "UNKNOWN_UNRESOLVED": []}
        contextual = []

        for pr in self.active_records():
            if pr.retraction_outcome == "flagged":
                contextual.append(pr)
                continue
            verdict = pr.directness.verdict
            if verdict == dr.DIRECT and pr.certainty.is_assessable:
                buckets["DIRECT_EVIDENCE"].append(pr)
            elif verdict in (dr.PARTIALLY_DIRECT, dr.INDIRECT):
                buckets["INDIRECT_SUPPORTING_EVIDENCE"].append(pr)
            else:
                buckets["UNKNOWN_UNRESOLVED"].append(pr)

        excluded = [pr for pr in self.records if pr.is_excluded]

        self.notes.append({
            "stage": SYNTHESIS,
            "buckets": {k: [r.record_id for r in v] for k, v in buckets.items()},
            "contextual_flagged": [r.record_id for r in contextual],
            "excluded": [{"record_id": r.record_id, "reason": r.exclusion_reason}
                         for r in excluded],
            "note": ("Excluded records appear here as a provenance note only. They are never "
                     "citations backing a clinical claim."),
        })
        self._complete(SYNTHESIS)
        return {"buckets": buckets, "contextual": contextual, "excluded": excluded,
                "overlap": self.overlap_result}

    # ── 6. CLINICAL APPLICABILITY ───────────────────────────────────────────────────────────
    def assess_applicability(self, population_match=None, feasible_locally=None,
                             patient_fit=None, regulatory_state=None):
        """
        Deliberately last and deliberately separate. High certainty about a population is not
        applicability to a patient, and a lawful, available, acceptable option is a different
        question again from an effective one.
        """
        self._require(APPLICABILITY)
        assessed = [population_match, feasible_locally, patient_fit]
        if any(a is None for a in assessed):
            rating = "CANNOT ASSESS"
            basis = ("Applicability was not fully assessed: "
                     + ", ".join(name for name, value in
                                 (("population match", population_match),
                                  ("local feasibility", feasible_locally),
                                  ("patient fit", patient_fit)) if value is None)
                     + " not established.")
        elif all(a == "HIGH" for a in assessed):
            rating, basis = "HIGH APPLICABILITY", "Population, feasibility and patient fit all match."
        elif any(a == "LOW" for a in assessed):
            rating, basis = "LOW APPLICABILITY", "At least one dimension is a poor match."
        else:
            rating, basis = "MODERATE APPLICABILITY", "A partial match on at least one dimension."

        result = {
            "rating": rating, "basis": basis,
            "population_match": population_match, "feasible_locally": feasible_locally,
            "patient_fit": patient_fit, "regulatory_state": regulatory_state,
            "note": ("Applicability is separate from certainty and from evidence level. Whether "
                     "an option may lawfully be used here is a separate question again, answered "
                     "by the Saudi regulatory gate, not by evidence."),
        }
        self.notes.append({"stage": APPLICABILITY, **result})
        self._complete(APPLICABILITY)
        return result

    # ── Reporting ───────────────────────────────────────────────────────────────────────────
    def stage_report(self):
        return {
            "question": self.question,
            "stages_completed": list(self.completed_stages),
            "stages_outstanding": [s for s in STAGES if s not in self.completed_stages],
            "records": [r.to_dict() for r in self.records],
            "notes": self.notes,
            "separation_rule": (
                "RETRIEVAL / VERIFICATION / APPRAISAL / CERTAINTY / SYNTHESIS / APPLICABILITY are "
                "six separate findings. A bibliographically verified paper is never, on that "
                "basis alone, strong evidence."),
        }

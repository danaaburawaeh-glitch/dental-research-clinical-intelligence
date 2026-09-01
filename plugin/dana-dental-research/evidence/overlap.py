"""
evidence/overlap.py  —  DUPLICATION AND OVERLAP (v1.2)

Stops the same finding from being counted twice, without deleting evidence to achieve it.

FOUR DISTINCT THINGS, OFTEN CONFLATED
-------------------------------------
    DUPLICATE RECORD              the same paper retrieved twice (two connectors, two queries)
    SAME STUDY, MULTIPLE REPORTS  one trial published as several papers — a primary report, a
                                  longer follow-up, a subgroup analysis
    UPDATED SYSTEMATIC REVIEW     a later review superseding an earlier one on the same question
    OVERLAPPING META-ANALYSES     two reviews pooling substantially the same primary studies

Only the first is a duplicate in the bibliographic sense, and only the first is a candidate for
merging. The other three are real, separate publications whose *evidence* overlaps — counting
them as independent inflates the apparent weight of the evidence base, and deleting them loses
information. So this module never deletes and never silently merges. It produces findings, each
naming a preferred source and the records retained alongside it, with a reason.

WHY OLDER EVIDENCE IS RETAINED
------------------------------
The brief's instruction is precise: prefer the newest or highest-quality synthesis "but preserve
older relevant evidence when it materially changes interpretation." A 2024 review that excluded
the long-follow-up cohort a 2016 review included does not supersede it — it answers a narrower
question more recently. Recency is not quality (see rank.py; brief §15). Every finding here
therefore carries `retained` as well as `preferred`, and `supersedes_entirely` is set only when
an update explicitly states it replaces the earlier version.

Bibliographic de-duplication itself is delegated to `connectors/shared/deduplication.py`, which
already implements the strong-identifier discipline (a shared DOI with disagreeing titles is a
FLAGGED_CONFLICT, never a merge). This module adds the three evidence-level overlap types on top.
"""
import _paths  # noqa: F401

import re

import study_design as sd
from shared.deduplication import deduplicate
from shared.identifiers import normalize_doi, normalize_pmid, normalize_title
from shared.normalization import titles_match

DUPLICATE_RECORD = "DUPLICATE_RECORD"
SAME_STUDY_MULTIPLE_REPORTS = "SAME_STUDY_MULTIPLE_REPORTS"
UPDATED_SYSTEMATIC_REVIEW = "UPDATED_SYSTEMATIC_REVIEW"
OVERLAPPING_META_ANALYSIS = "OVERLAPPING_META_ANALYSIS"

OVERLAP_TYPES = (DUPLICATE_RECORD, SAME_STUDY_MULTIPLE_REPORTS, UPDATED_SYSTEMATIC_REVIEW,
                 OVERLAPPING_META_ANALYSIS)

# How much of the smaller review's included-study set must be shared before two syntheses are
# treated as overlapping rather than independent.
OVERLAP_THRESHOLD = 0.5

_UPDATE_MARKERS = ("an update", "updated systematic review", "update of", ": an update",
                   "updated meta-analysis")


class OverlapFinding:
    def __init__(self, overlap_type, records, preferred, retained, reason,
                 supersedes_entirely=False, shared_evidence=None):
        self.overlap_type = overlap_type
        self.records = records
        self.preferred = preferred
        self.retained = retained
        self.reason = reason
        self.supersedes_entirely = supersedes_entirely
        self.shared_evidence = shared_evidence or []

    @property
    def counts_as_independent_studies(self):
        """How many independent studies this cluster contributes to the evidence base. Always 1 —
        that is what an overlap finding means."""
        return 1

    def to_dict(self):
        return {
            "overlap_type": self.overlap_type,
            "record_ids": [_rid(r) for r in self.records],
            "preferred": _rid(self.preferred) if self.preferred else None,
            "retained": [_rid(r) for r in self.retained],
            "reason": self.reason,
            "supersedes_entirely": self.supersedes_entirely,
            "shared_evidence": list(self.shared_evidence),
            "counts_as_independent_studies": self.counts_as_independent_studies,
            "handling": (
                "Retained records stay in the evidence table and keep their citations. They are "
                "not counted again toward the weight of the evidence base, and they are not "
                "deleted — an older synthesis can still materially change interpretation."),
        }


def _rid(record):
    return (record.get("pmid") or normalize_doi(record.get("doi")) or record.get("nct_id")
            or normalize_title(record.get("title")))


def _year(record):
    return record.get("publication_year") or 0


def _trial_ids(record):
    """Registry identifiers a record reports, from structured fields only. An NCT id appearing in
    an abstract string is picked up too, because trial registration numbers are one of the few
    identifiers that free text carries reliably — but the origin is recorded by the caller."""
    ids = set()
    for key in ("nct_id", "trial_registration", "trial_ids"):
        value = record.get(key)
        if isinstance(value, str):
            ids.add(value.strip().upper())
        elif isinstance(value, (list, tuple, set)):
            ids.update(str(v).strip().upper() for v in value)
    text = " ".join(str(record.get(k) or "") for k in ("abstract", "title"))
    ids.update(m.upper() for m in re.findall(r"NCT\d{8}", text, flags=re.IGNORECASE))
    return {i for i in ids if i}


def _included_pmids(record):
    """The primary studies a review reports including, when the caller extracted them."""
    value = record.get("included_study_pmids") or record.get("included_studies") or []
    return {normalize_pmid(v) or str(v).strip() for v in value if v}


def _title_stem(title):
    """Title with an explicit update marker stripped, for matching a review against its update."""
    t = (normalize_title(title) or "")
    for marker in ("an update", "update", "updated systematic review", "updated meta analysis"):
        t = t.replace(marker, " ")
    return re.sub(r"\s+", " ", t).strip()


def detect(records, classifications=None):
    """
    records: list of EvidenceRecord-shaped dicts.
    classifications: optional {record_id: DesignClassification}. When absent, designs are
        classified here.

    Returns {"deduplicated": [...], "merge_log": [...], "findings": [OverlapFinding, ...],
             "independent_study_count": int}

    Nothing is removed from `records`. `deduplicated` is the connector layer's bibliographic
    de-duplication output; `findings` describes the evidence-level overlaps on top of it.
    """
    deduped, merge_log = deduplicate(records)

    classifications = classifications or {}

    def design_of(record):
        rid = _rid(record)
        if rid in classifications:
            return classifications[rid]
        return sd.classify(record)

    findings = []
    for entry in merge_log:
        if entry.get("action") == "MERGED":
            findings.append(OverlapFinding(
                DUPLICATE_RECORD, [], None, [],
                reason=(f"The same record was retrieved more than once "
                        f"({entry.get('identity_basis')} {entry.get('identity_value')}). Merged "
                        f"by the connector-layer de-duplicator on a matching strong identifier "
                        f"with agreeing titles.")))

    findings.extend(_same_study_multiple_reports(deduped))
    findings.extend(_review_overlaps(deduped, design_of))

    clustered = set()
    for f in findings:
        for r in f.records:
            clustered.add(_rid(r))
    independent = len([r for r in deduped if _rid(r) not in clustered]) + len(
        [f for f in findings if f.records])

    return {
        "deduplicated": deduped,
        "merge_log": merge_log,
        "findings": findings,
        "independent_study_count": independent,
        "counting_rule": (
            "Each overlap cluster contributes ONE independent study to the weight of the "
            "evidence base, however many papers it produced. Every paper keeps its citation."),
    }


def _same_study_multiple_reports(records):
    """Cluster by shared trial registration identifier — the only reliable structured signal that
    two papers report the same study. Topic similarity is never used: two papers about the same
    intervention are not thereby the same trial."""
    by_trial = {}
    for record in records:
        for trial_id in _trial_ids(record):
            by_trial.setdefault(trial_id, []).append(record)

    findings = []
    for trial_id, group in by_trial.items():
        if len(group) < 2:
            continue
        # Prefer the report with the longest follow-up where stated, else the most recent.
        preferred = max(group, key=lambda r: (r.get("follow_up_months") or 0, _year(r)))
        retained = [r for r in group if r is not preferred]
        findings.append(OverlapFinding(
            SAME_STUDY_MULTIPLE_REPORTS, group, preferred, retained,
            reason=(f"These records share trial registration {trial_id}. They report the same "
                    f"study, not independent studies, and must be counted once. The report with "
                    f"the longest stated follow-up is preferred; the others are retained because "
                    f"a subgroup or earlier report may carry outcomes the preferred one does not."),
            shared_evidence=[trial_id]))
    return findings


def _review_overlaps(records, design_of):
    reviews = [r for r in records
               if design_of(r).design in (sd.SYSTEMATIC_REVIEW, sd.META_ANALYSIS)]
    findings = []
    seen_pairs = set()

    for i, a in enumerate(reviews):
        for b in reviews[i + 1:]:
            pair = tuple(sorted((_rid(a) or "", _rid(b) or "")))
            if pair in seen_pairs:
                continue

            older, newer = (a, b) if _year(a) <= _year(b) else (b, a)

            # An explicit update: same title stem, later year, update wording present.
            newer_title = (newer.get("title") or "").lower()
            is_update = any(m in newer_title for m in _UPDATE_MARKERS)
            if is_update and _title_stem(newer.get("title")) and \
                    titles_match(_title_stem(newer.get("title")), _title_stem(older.get("title")),
                                 threshold=0.6) and _year(newer) > _year(older):
                seen_pairs.add(pair)
                findings.append(OverlapFinding(
                    UPDATED_SYSTEMATIC_REVIEW, [older, newer], newer, [older],
                    reason=(f"{_rid(newer)} describes itself as an update of the same review "
                            f"question as {_rid(older)}. The update is preferred. The earlier "
                            f"version is retained, not discarded — it is only superseded for the "
                            f"studies the update actually re-examined."),
                    supersedes_entirely=False))
                continue

            # Overlapping syntheses: shared included primary studies, where the caller
            # established what each review included.
            a_inc, b_inc = _included_pmids(a), _included_pmids(b)
            if a_inc and b_inc:
                shared = a_inc & b_inc
                smaller = min(len(a_inc), len(b_inc))
                if smaller and len(shared) / smaller >= OVERLAP_THRESHOLD:
                    seen_pairs.add(pair)
                    larger = a if len(a_inc) >= len(b_inc) else b
                    other = b if larger is a else a
                    findings.append(OverlapFinding(
                        OVERLAPPING_META_ANALYSIS, [a, b], larger, [other],
                        reason=(f"These syntheses share {len(shared)} of the smaller review's "
                                f"{smaller} included studies "
                                f"({len(shared) / smaller:.0%} overlap). Their pooled estimates "
                                f"are not independent findings and must not be presented as two "
                                f"reviews agreeing. The broader synthesis is preferred; the other "
                                f"is retained, since a narrower review may apply a stricter "
                                f"inclusion standard that materially changes interpretation."),
                        shared_evidence=sorted(shared)))
    return findings

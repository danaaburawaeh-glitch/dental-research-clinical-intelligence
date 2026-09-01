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

    # Cohort overlap needs features PubMed abstracts do not carry (institution, study period,
    # sample size). It is run here anyway, and reported, so that "no cohort overlap was assessed"
    # is visible as a stated limitation rather than an invisible omission. Enrich the records with
    # those fields — from full texts, or supplied by the clinician — to make it informative.
    cohort_assessments = assess_all_cohort_overlaps(deduped)
    assessable = [r for r in deduped
                  if _institutions(r) or _period(r) or _sample(r)]

    return {
        "deduplicated": deduped,
        "merge_log": merge_log,
        "findings": findings,
        "cohort_assessments": cohort_assessments,
        "cohort_assessment_coverage": {
            "records_with_assessable_features": len(assessable),
            "records_total": len(deduped),
            "note": (
                "Cohort overlap is graded from institution, study period, sample size, "
                "intervention, site and population features. Records lacking them cannot be "
                "assessed, and their absence of a flag is not evidence of independence."
                if len(assessable) < len(deduped) else
                "All retrieved records carried assessable cohort features."),
        },
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


# ══════════════════════════════════════════════════════════════════════════════════════════════
# COHORT OVERLAP ASSESSMENT (v1.2 RC)
#
# The trial-registration clustering above is exact and safe, and it is blind to the commonest
# real overlap in dentistry: two retrospective reports of the same patient cohort from the same
# unit, years apart, with no registration identifier anywhere. Real case from validation —
# PMID 22259802 (Beier 2012, Innsbruck, veneers placed 1987-2009) and PMID 11203615 (Dumfahrt
# 2000, same institution, shared author, veneers of 1-10 years' service). Almost certainly
# overlapping patients; nothing in the structured metadata says so.
#
# Counting those as two independent studies overstates the evidence base. Merging them on a
# hunch destroys evidence. So this layer does neither: it grades the SUSPICION, names the
# features that produced it, lowers the confidence available for pooled interpretation, and
# keeps both citations.
#
# THE RULE THAT MATTERS MOST: shared authorship alone is never an overlap signal. Prolific
# groups publish repeatedly on the same topic with entirely different patients; if co-authorship
# were sufficient, every productive research unit would be collapsed into a single study.
# ══════════════════════════════════════════════════════════════════════════════════════════════

NO_OVERLAP_SIGNAL = "NO_OVERLAP_SIGNAL"
POSSIBLE_OVERLAP = "POSSIBLE_OVERLAP"
PROBABLE_OVERLAP = "PROBABLE_OVERLAP"
CONFIRMED_OVERLAP = "CONFIRMED_OVERLAP"

OVERLAP_LEVELS = (NO_OVERLAP_SIGNAL, POSSIBLE_OVERLAP, PROBABLE_OVERLAP, CONFIRMED_OVERLAP)

# Features that, on their own, materially raise the suspicion of a shared cohort.
STRONG_FEATURES = ("shared_institution", "study_period_overlap", "identical_sample_size")
# Features that corroborate but cannot carry a level alone.
SUPPORTING_FEATURES = ("same_intervention", "same_country_or_site", "same_population_description",
                       "same_follow_up_window", "nested_sample_size")
# Recorded, reported, and deliberately excluded from the level calculation.
NON_COUNTING_FEATURES = ("shared_authors",)

AUTHORS_ALONE_RULE = (
    "Shared authorship is reported but never counts toward an overlap level. Research groups "
    "publish repeatedly on their own subject with different patients; treating co-authorship as "
    "an overlap signal would collapse every productive unit into a single study."
)

CONFIRMED_REQUIREMENT = (
    "CONFIRMED_OVERLAP requires an explicit shared identifier (trial registration) or a stated "
    "linkage in one of the records themselves. It is never reached by accumulating "
    "circumstantial features, however many."
)


class CohortOverlapAssessment:
    def __init__(self, level, record_a, record_b, features, triggered, explanation):
        if level not in OVERLAP_LEVELS:
            raise ValueError(f"{level!r} is not one of {OVERLAP_LEVELS}")
        self.level = level
        self.record_a = record_a
        self.record_b = record_b
        self.features = features
        self.triggered = triggered
        self.explanation = explanation

    @property
    def counts_as_independent_studies(self):
        """
        How much independent weight the pair contributes.

        POSSIBLE deliberately returns None rather than a number: the honest answer is that it is
        not established whether this is one study or two, and picking either would assert
        something the evidence does not support.
        """
        if self.level in (CONFIRMED_OVERLAP, PROBABLE_OVERLAP):
            return 1
        if self.level == POSSIBLE_OVERLAP:
            return None
        return 2

    @property
    def reduces_pooled_confidence(self):
        return self.level in (POSSIBLE_OVERLAP, PROBABLE_OVERLAP, CONFIRMED_OVERLAP)

    @property
    def deletes_a_study(self):
        """Always False. Recorded as a property so the guarantee is testable, not just stated."""
        return False

    def to_dict(self):
        return {
            "level": self.level,
            "record_a": _rid(self.record_a),
            "record_b": _rid(self.record_b),
            "citations_preserved": [_rid(self.record_a), _rid(self.record_b)],
            "features_evaluated": dict(self.features),
            "triggered_by": list(self.triggered),
            "explanation": self.explanation,
            "counts_as_independent_studies": self.counts_as_independent_studies,
            "reduces_pooled_confidence": self.reduces_pooled_confidence,
            "deletes_a_study": self.deletes_a_study,
            "authors_alone_rule": AUTHORS_ALONE_RULE,
            "confirmed_requirement": CONFIRMED_REQUIREMENT,
            "pooled_interpretation_caution": self._caution(),
        }

    def _caution(self):
        if self.level == CONFIRMED_OVERLAP:
            return ("These records report the same study. Count them once. Both citations are "
                    "retained; neither is deleted.")
        if self.level == PROBABLE_OVERLAP:
            return ("Treat as one study for the purpose of weighing the evidence, pending "
                    "verification against the full texts. Both citations are retained, and the "
                    "overlap is stated as probable rather than established.")
        if self.level == POSSIBLE_OVERLAP:
            return ("These records may report overlapping patients. Do not present them as two "
                    "independent confirmations without checking. Neither is discounted, and the "
                    "independent-study count is left unresolved rather than guessed.")
        return "No overlap signal beyond anything reported above. Treat as independent."


def _norm(text):
    return " ".join(str(text or "").lower().split()) or None


def _institutions(record):
    value = record.get("institutions") or record.get("affiliations") or record.get("institution")
    if isinstance(value, str):
        value = [value]
    return {_norm(v) for v in (value or []) if _norm(v)}


def _period(record):
    """Returns (start, end) as ints, from an explicit study period or recruitment dates."""
    for key in ("study_period", "recruitment_dates", "enrolment_period"):
        value = record.get(key)
        if isinstance(value, (list, tuple)) and len(value) == 2:
            try:
                return int(str(value[0])[:4]), int(str(value[1])[:4])
            except (TypeError, ValueError):
                continue
    start, end = record.get("study_start_year"), record.get("study_end_year")
    if start and end:
        try:
            return int(start), int(end)
        except (TypeError, ValueError):
            return None
    return None


def _periods_overlap(a, b):
    pa, pb = _period(a), _period(b)
    if not pa or not pb:
        return None
    return max(pa[0], pb[0]) <= min(pa[1], pb[1])


def _sample(record):
    value = record.get("sample_size_n") or record.get("n_units") or record.get("enrollment")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def assess_cohort_overlap(record_a, record_b):
    """
    Grade the suspicion that two records report overlapping patients.

    Every feature is evaluated three-valued — True (agrees), False (differs), None (not
    established on at least one side) — so "we could not tell" is never scored as "no".
    """
    features = {}
    triggered = []

    ids_a, ids_b = _trial_ids(record_a), _trial_ids(record_b)
    shared_ids = ids_a & ids_b
    features["shared_registration_id"] = bool(shared_ids) if (ids_a and ids_b) else None

    linkage = None
    for rec, other in ((record_a, record_b), (record_b, record_a)):
        declared = rec.get("same_cohort_as") or rec.get("supersedes") or rec.get("extends")
        if declared and _rid(other) and str(_rid(other)) in str(declared):
            linkage = f"{_rid(rec)} declares a linkage to {_rid(other)}"
    features["explicit_linkage"] = bool(linkage) if linkage else None

    inst_a, inst_b = _institutions(record_a), _institutions(record_b)
    features["shared_institution"] = bool(inst_a & inst_b) if (inst_a and inst_b) else None

    features["study_period_overlap"] = _periods_overlap(record_a, record_b)

    sa, sb = _sample(record_a), _sample(record_b)
    features["identical_sample_size"] = (sa == sb) if (sa and sb) else None
    features["nested_sample_size"] = (sa != sb) if (sa and sb) else None

    ia = _norm(record_a.get("intervention") or record_a.get("material"))
    ib = _norm(record_b.get("intervention") or record_b.get("material"))
    features["same_intervention"] = (ia == ib) if (ia and ib) else None

    ca = _norm(record_a.get("country") or record_a.get("site"))
    cb = _norm(record_b.get("country") or record_b.get("site"))
    features["same_country_or_site"] = (ca == cb) if (ca and cb) else None

    pa = _norm(record_a.get("population_description"))
    pb = _norm(record_b.get("population_description"))
    features["same_population_description"] = (pa == pb) if (pa and pb) else None

    fa = _norm(record_a.get("follow_up_window"))
    fb = _norm(record_b.get("follow_up_window"))
    features["same_follow_up_window"] = (fa == fb) if (fa and fb) else None

    auth_a = {_norm(x).split()[-1] for x in (record_a.get("authors") or []) if _norm(x)}
    auth_b = {_norm(x).split()[-1] for x in (record_b.get("authors") or []) if _norm(x)}
    shared_authors = auth_a & auth_b
    features["shared_authors"] = bool(shared_authors) if (auth_a and auth_b) else None

    # ── Level ───────────────────────────────────────────────────────────────────────────────
    if features["shared_registration_id"] is True:
        triggered.append(f"shared trial registration identifier ({', '.join(sorted(shared_ids))})")
        return CohortOverlapAssessment(
            CONFIRMED_OVERLAP, record_a, record_b, features, triggered,
            "Both records carry the same trial registration identifier — an explicit shared "
            "identifier, which is the only basis on which overlap is confirmed.")
    if features["explicit_linkage"] is True:
        triggered.append(linkage)
        return CohortOverlapAssessment(
            CONFIRMED_OVERLAP, record_a, record_b, features, triggered,
            f"Explicit source linkage: {linkage}.")

    strong = [f for f in STRONG_FEATURES if features.get(f) is True]
    supporting = [f for f in SUPPORTING_FEATURES if features.get(f) is True]
    triggered.extend(strong + supporting)

    if len(strong) >= 2 and len(supporting) >= 1:
        level = PROBABLE_OVERLAP
        explanation = (
            f"Two or more strong features agree ({', '.join(strong)}) with corroboration from "
            f"{', '.join(supporting)}. Same unit, overlapping period and matching clinical "
            f"detail together make a shared cohort more likely than not — but nothing here is an "
            f"identifier, so this is probable, not confirmed.")
    elif strong and (supporting or features.get("shared_authors") is True):
        level = POSSIBLE_OVERLAP
        extra = ", ".join(supporting) or "shared authorship (reported, not counted)"
        explanation = (
            f"One strong feature ({', '.join(strong)}) with weaker corroboration ({extra}). "
            f"Enough to stop treating these as independent confirmations without checking; not "
            f"enough to treat them as one study.")
    elif len(supporting) >= 3:
        level = POSSIBLE_OVERLAP
        explanation = (
            f"No strong feature, but several supporting ones agree ({', '.join(supporting)}). "
            f"Circumstantial: worth checking before pooling.")
    else:
        level = NO_OVERLAP_SIGNAL
        if features.get("shared_authors") is True and not strong and not supporting:
            triggered.append("shared authors (reported, not counted toward the level)")
            explanation = (
                "The records share at least one author and nothing else. " + AUTHORS_ALONE_RULE)
        else:
            explanation = ("No feature combination reached an overlap signal. Treat the records "
                           "as independent unless something outside this metadata says otherwise.")

    return CohortOverlapAssessment(level, record_a, record_b, features, triggered, explanation)


def assess_all_cohort_overlaps(records, minimum_level=POSSIBLE_OVERLAP):
    """Pairwise assessment across a retrieved set. Returns assessments at or above
    `minimum_level`; nothing is removed from `records`."""
    order = {lvl: i for i, lvl in enumerate(OVERLAP_LEVELS)}
    out = []
    for i, a in enumerate(records):
        for b in records[i + 1:]:
            assessment = assess_cohort_overlap(a, b)
            if order[assessment.level] >= order[minimum_level]:
                out.append(assessment)
    return out

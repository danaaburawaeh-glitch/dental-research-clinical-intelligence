"""
evidence/certainty.py  —  CERTAINTY OF EVIDENCE (v1.2)

How much confidence does this body of evidence justify? Deliberately kept apart from three
things it is constantly confused with: whether the citation is real (citation_verification.py),
what tier the source sits in (DEL-7), and whether it answers this question (directness.py).

TWO CHANNELS, NEVER MERGED
--------------------------
    AUTHOR-REPORTED GRADE
        A GRADE rating that the paper's own authors performed and reported. Recorded verbatim,
        attributed to them, with the outcome it applies to. This system does not produce it and
        does not adjust it.

    DENTAL AI STRUCTURED CERTAINTY ASSESSMENT
        This module's own output. It is GRADE-INSPIRED — it borrows GRADE's domains and its
        starting-point-by-design logic — and it is not GRADE. GRADE is a consensus process
        applied per outcome across a body of evidence by people who read the full texts. Calling
        this output "GRADE" would claim a methodology that was not carried out.

`assess()` refuses to emit the word GRADE for its own rating. `author_reported_grade()` is the
only path by which the word attaches to anything, and it requires an attributed source.

CONSERVATIVE BY CONSTRUCTION
----------------------------
Three properties make this engine err downward:

  1. It never upgrades. GRADE permits raising certainty for a large effect, a dose-response
     gradient, or when plausible confounding would only reduce the observed effect. Those
     judgements need the full text and a reviewer's read of the clinical context. Without them,
     an upgrade is a guess in the direction of confidence — the one direction where a wrong
     guess does harm. Downgrades apply; upgrades do not.

  2. Missing information produces NOT ASSESSABLE, never a default rating. If risk of bias,
     consistency, precision or directness was not established, there is nothing to rate. A body
     of evidence rated LOW sounds like a finding about the evidence; NOT ASSESSABLE correctly
     says the assessment did not happen.

  3. Laboratory, computational and registry records are NOT ASSESSABLE for clinical certainty
     outright. Rating them at all would imply they sit on the same scale as clinical evidence.
"""
import _paths  # noqa: F401

import study_design as sd
import appraisal as ap
import directness as dr

# ── Ratings ─────────────────────────────────────────────────────────────────────────────────
HIGH = "HIGH"
MODERATE = "MODERATE"
LOW = "LOW"
VERY_LOW = "VERY LOW"
NOT_ASSESSABLE = "NOT ASSESSABLE"
RATINGS = (HIGH, MODERATE, LOW, VERY_LOW, NOT_ASSESSABLE)

# The rateable scale, in descending order. NOT ASSESSABLE is off the scale, not its bottom rung.
_SCALE = (HIGH, MODERATE, LOW, VERY_LOW)

ASSESSMENT_LABEL = "DENTAL AI STRUCTURED CERTAINTY ASSESSMENT"
AUTHOR_GRADE_LABEL = "AUTHOR-REPORTED GRADE"

NOT_GRADE_NOTE = (
    "This is a structured, GRADE-inspired certainty assessment produced by this system. It is "
    "NOT a GRADE rating. GRADE is applied per outcome, across a body of evidence, by reviewers "
    "working from full texts and an explicit evidence profile. Where the source authors "
    "performed GRADE themselves, their rating is reported separately and attributed to them."
)

# ── Starting points by design ───────────────────────────────────────────────────────────────
# Mirrors GRADE's convention: trials start high, observational studies start low.
_START = {
    sd.META_ANALYSIS: HIGH,
    sd.SYSTEMATIC_REVIEW: HIGH,
    sd.RCT: HIGH,
    sd.GUIDELINE: MODERATE,          # a guideline's own certainty depends on what it rests on
    sd.PROSPECTIVE_COHORT: LOW,
    sd.RETROSPECTIVE_COHORT: LOW,
    sd.COHORT_DIRECTION_UNREPORTED: LOW,
    sd.CASE_CONTROL: LOW,
    sd.DIAGNOSTIC_ACCURACY: LOW,
    sd.CROSS_SECTIONAL: LOW,
    sd.CASE_SERIES: VERY_LOW,
    sd.CASE_REPORT: VERY_LOW,
    sd.NARRATIVE_REVIEW: VERY_LOW,
    sd.EXPERT_OPINION: VERY_LOW,
}

# Designs that are never rated on the clinical certainty scale at all.
_UNRATEABLE = (sd.IN_VITRO, sd.FINITE_ELEMENT, sd.REGISTRY_RECORD, sd.OTHER)

# A systematic review is only as good as what it pools. An SR of observational studies does not
# start HIGH — that is one of the most common ways a certainty rating gets inflated.
SR_OF_NON_RANDOMIZED_START = LOW

# ── Downgrade domains ───────────────────────────────────────────────────────────────────────
SERIOUS = "SERIOUS"
VERY_SERIOUS = "VERY SERIOUS"
NOT_SERIOUS = "NOT SERIOUS"
DOMAIN_LEVELS = (NOT_SERIOUS, SERIOUS, VERY_SERIOUS)
_DOWNGRADE_STEPS = {NOT_SERIOUS: 0, SERIOUS: 1, VERY_SERIOUS: 2}

DOMAINS = ("risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias")


class CertaintyAssessment:
    def __init__(self, rating, label, starting_point, downgrades, reasons, not_assessable_reason=None,
                 author_grade=None):
        self.rating = rating
        self.label = label
        self.starting_point = starting_point
        self.downgrades = downgrades
        self.reasons = reasons
        self.not_assessable_reason = not_assessable_reason
        self.author_grade = author_grade

    @property
    def is_assessable(self):
        return self.rating != NOT_ASSESSABLE

    def to_dict(self):
        return {
            "rating": self.rating,
            "label": self.label,
            "is_grade": False,
            "not_grade_note": NOT_GRADE_NOTE,
            "starting_point": self.starting_point,
            "downgrades": dict(self.downgrades),
            "reasons": list(self.reasons),
            "not_assessable_reason": self.not_assessable_reason,
            "author_reported_grade": (self.author_grade.to_dict() if self.author_grade else None),
            "upgrades_applied": None,
            "upgrade_policy": (
                "This engine never upgrades certainty. GRADE's upgrade criteria (large effect, "
                "dose-response, plausible confounding acting against the effect) require a full-"
                "text reading this system does not perform; applying them from an abstract would "
                "raise confidence on a guess."),
        }

    def __repr__(self):
        return f"<Certainty {self.rating}>"


class AuthorReportedGrade:
    """A GRADE rating performed and reported by the source's own authors."""

    def __init__(self, rating, outcome, reported_by, source=ap.FROM_FULL_TEXT, note=None):
        if rating not in (HIGH, MODERATE, LOW, VERY_LOW):
            raise ValueError(f"{rating!r} is not a GRADE rating")
        if not outcome:
            raise ValueError("A GRADE rating applies to a specific outcome — name it.")
        if not reported_by:
            raise ValueError(
                "An author-reported GRADE rating must be attributed to whoever reported it. "
                "Unattributed, it is indistinguishable from this system inventing one.")
        self.rating = rating
        self.outcome = outcome
        self.reported_by = reported_by
        self.source = source
        self.note = note

    def to_dict(self):
        return {"label": AUTHOR_GRADE_LABEL, "rating": self.rating, "outcome": self.outcome,
                "reported_by": self.reported_by, "source": self.source, "note": self.note,
                "produced_by_this_system": False}


def _step_down(start, steps):
    idx = _SCALE.index(start)
    return _SCALE[min(idx + steps, len(_SCALE) - 1)]   # floors at VERY LOW, never below


def _domain_from_directness(directness_assessment):
    """Map the directness verdict onto GRADE's indirectness domain."""
    if directness_assessment is None:
        return None, "Directness was not assessed."
    v = directness_assessment.verdict
    if v == dr.DIRECT:
        return NOT_SERIOUS, "Directly answers the framed question."
    if v == dr.PARTIALLY_DIRECT:
        return SERIOUS, "Partially direct — one or more dimensions only moderately match."
    if v == dr.INDIRECT:
        return VERY_SERIOUS, "Indirect — a decisive mismatch on at least one dimension."
    return None, "Directness could not be rated, so indirectness cannot be judged."


def assess(design_classification, appraisal=None, directness_assessment=None,
           domains=None, pools_randomized_trials=None, author_grade=None):
    """
    design_classification : study_design.DesignClassification — required. Certainty starts from
        design, so an unnamed design has no starting point.
    appraisal             : appraisal.Appraisal — read for whether the certainty-critical fields
        were actually established.
    directness_assessment : directness.DirectnessAssessment — supplies the indirectness domain.
    domains               : optional explicit {domain: NOT_SERIOUS|SERIOUS|VERY_SERIOUS} for the
        remaining GRADE domains. Any domain left unspecified is treated as NOT ESTABLISHED, which
        contributes to NOT ASSESSABLE rather than being read as NOT SERIOUS.
    pools_randomized_trials : for a systematic review or meta-analysis — True if it pools
        randomized trials, False if it pools non-randomized studies, None if not established.
    author_grade          : an AuthorReportedGrade, carried through untouched.

    Returns a CertaintyAssessment.
    """
    design = design_classification.design if design_classification else None

    if design is None or design_classification.provenance == sd.UNKNOWN:
        return CertaintyAssessment(
            NOT_ASSESSABLE, ASSESSMENT_LABEL, None, {}, [],
            not_assessable_reason=("The study design was not established. Certainty starts from "
                                   "design; without one there is nothing to start from."),
            author_grade=author_grade)

    if design in _UNRATEABLE:
        return CertaintyAssessment(
            NOT_ASSESSABLE, ASSESSMENT_LABEL, None, {}, [],
            not_assessable_reason=(
                f"{design} is not rated on the clinical certainty scale. "
                + (dr.REGISTRY_CAP_NOTE if design_classification.registry_only else dr.LAB_CAP_NOTE)
                if design != sd.OTHER else
                "The design could not be named, so no starting point applies."),
            author_grade=author_grade)

    start = _START.get(design)
    reasons = []

    if design in (sd.SYSTEMATIC_REVIEW, sd.META_ANALYSIS):
        if pools_randomized_trials is False:
            start = SR_OF_NON_RANDOMIZED_START
            reasons.append(
                "Starting point set to LOW: this synthesis pools non-randomized studies. A "
                "systematic review inherits the certainty of what it pools — the synthesis "
                "method does not raise the evidence beneath it.")
        elif pools_randomized_trials is None:
            return CertaintyAssessment(
                NOT_ASSESSABLE, ASSESSMENT_LABEL, None, {}, reasons,
                not_assessable_reason=(
                    "This is a systematic review or meta-analysis, but what it pools "
                    "(randomized or non-randomized studies) was not established. Its starting "
                    "certainty depends entirely on that, so it has not been assumed."),
                author_grade=author_grade)
        else:
            reasons.append("Starting point HIGH: synthesis of randomized trials.")
    else:
        reasons.append(f"Starting point {start}: study design is {design}.")

    # ── Assemble the five domains ───────────────────────────────────────────────────────────
    supplied = dict(domains or {})
    for name, level in supplied.items():
        if name not in DOMAINS:
            raise ValueError(f"{name!r} is not a GRADE domain; expected one of {DOMAINS}")
        if level not in DOMAIN_LEVELS:
            raise ValueError(f"{level!r} is not one of {DOMAIN_LEVELS}")

    resolved = {}
    unestablished = []

    ind_level, ind_reason = _domain_from_directness(directness_assessment)
    if "indirectness" in supplied:
        resolved["indirectness"] = supplied["indirectness"]
    elif ind_level is not None:
        resolved["indirectness"] = ind_level
        reasons.append(f"Indirectness: {ind_level} — {ind_reason}")
    else:
        unestablished.append("indirectness")

    for domain in ("risk_of_bias", "inconsistency", "imprecision", "publication_bias"):
        if domain in supplied:
            resolved[domain] = supplied[domain]
        else:
            unestablished.append(domain)

    if unestablished:
        return CertaintyAssessment(
            NOT_ASSESSABLE, ASSESSMENT_LABEL, start, resolved, reasons,
            not_assessable_reason=(
                "Certainty was not rated because these domains were never established: "
                + ", ".join(sorted(unestablished)) +
                ". A rating produced over unestablished domains would be a guess presented as an "
                "assessment. This is an absence of assessment, not a finding of low certainty."),
            author_grade=author_grade)

    # Cross-check against the appraisal: a domain cannot be judged NOT SERIOUS on information the
    # appraisal itself records as UNKNOWN.
    if appraisal is not None:
        critical_unknown = appraisal.completeness()["certainty_critical_unknown"]
        if critical_unknown:
            return CertaintyAssessment(
                NOT_ASSESSABLE, ASSESSMENT_LABEL, start, resolved, reasons,
                not_assessable_reason=(
                    "The appraisal records these certainty-critical fields as UNKNOWN: "
                    + ", ".join(critical_unknown) +
                    ". Domain judgements supplied over fields the appraisal itself could not "
                    "establish are not accepted."),
                author_grade=author_grade)

    steps = 0
    for domain, level in resolved.items():
        step = _DOWNGRADE_STEPS[level]
        steps += step
        if step:
            reasons.append(f"Downgraded {step} level(s) for {domain.replace('_', ' ')}: {level}.")

    rating = _step_down(start, steps)
    if steps == 0:
        reasons.append("No domain warranted a downgrade.")
    reasons.append("No upgrade was applied — this engine never upgrades certainty.")

    return CertaintyAssessment(rating, ASSESSMENT_LABEL, start, resolved, reasons,
                               author_grade=author_grade)

<!--
REFERENCE-ID: certainty-of-evidence
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
New in v1.2. Executable implementation: `evidence/certainty.py`.
-->

# Certainty of Evidence

Loaded by: evidence-research, quality-control.

How much confidence does this body of evidence justify? A separate question from whether the
citation is real (`citation-verification.md`), what tier the source sits in
(`del7-evidence-hierarchy.md`), and whether it answers this question (`evidence-directness.md`).

## Ratings

**HIGH · MODERATE · LOW · VERY LOW · NOT ASSESSABLE**

NOT ASSESSABLE is off the scale, not at the bottom of it. "LOW" is a finding about the evidence;
"NOT ASSESSABLE" correctly says the assessment did not happen.

## Two channels, never merged

| Channel | What it is |
|---|---|
| **AUTHOR-REPORTED GRADE** | A GRADE rating the source's own authors performed and reported. Recorded verbatim, attributed to them, with the outcome it applies to. This system neither produces nor adjusts it. |
| **DENTAL AI STRUCTURED CERTAINTY ASSESSMENT** | This system's own output. GRADE-inspired — it borrows GRADE's domains and starting points — and **not GRADE**. |

**Do not claim formal GRADE if the paper's authors did not perform GRADE.** GRADE is a consensus
process applied per outcome, across a body of evidence, by reviewers working from full texts and
an explicit evidence profile. Labelling this system's output "GRADE" would claim a methodology
that was not carried out. `evidence/certainty.py` refuses to emit the word for its own rating, and
`AuthorReportedGrade` requires both a named outcome and an attribution before it will exist.

## Starting points, by design

| Design | Starts at |
|---|---|
| Meta-analysis / systematic review **of randomized trials** | HIGH |
| Randomized controlled trial | HIGH |
| Guideline | MODERATE |
| Meta-analysis / systematic review **of non-randomized studies** | LOW |
| Cohort · case-control · cross-sectional · diagnostic accuracy | LOW |
| Case series · case report · narrative review · expert opinion | VERY LOW |
| In-vitro · finite element · trial registry record | **NOT ASSESSABLE** |

**A systematic review is only as good as what it pools.** Where what a review pooled was not
established, the result is NOT ASSESSABLE — its starting certainty depends entirely on that and
is never assumed. This is one of the most common routes to an inflated rating.

## Downgrade domains

Five, each NOT SERIOUS / SERIOUS (−1) / VERY SERIOUS (−2): **risk of bias · inconsistency ·
indirectness · imprecision · publication bias**. Indirectness is taken automatically from the
directness assessment. The result floors at VERY LOW.

## Three conservative properties

1. **It never upgrades.** GRADE permits raising certainty for a large effect, a dose-response
   gradient, or confounding that would only reduce the observed effect. Those judgements need the
   full text and a reviewer's read of the clinical context. Without them an upgrade is a guess in
   the direction of confidence — the one direction where a wrong guess does harm.

2. **Missing information produces NOT ASSESSABLE, never a default.** If any of the five domains
   was not established, there is nothing to rate. The engine additionally cross-checks the
   appraisal: a domain cannot be judged over a field the appraisal itself records as UNKNOWN.

3. **Laboratory, computational and registry records are NOT ASSESSABLE outright.** Rating them at
   all would imply they sit on the same scale as clinical evidence.

## Reporting

State the rating, its label, its starting point, every downgrade with its reason, and — where the
authors reported one — their GRADE rating separately and attributed. Where the result is NOT
ASSESSABLE, say which domains were missing.

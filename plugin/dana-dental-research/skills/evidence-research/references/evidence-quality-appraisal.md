<!--
REFERENCE-ID: evidence-quality-appraisal
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
SOURCE: authoritative M3 §7 (Google Drive 1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8)
LAST-SYNCHRONIZED: 2026-09-01
v1.2: mandatory provenance on every appraised field, and tool-application refusal.
Executable implementation: `evidence/appraisal.py`.
This file did not exist in v0.2.1. Identified in M3_MIGRATION_AUDIT.md as the largest genuine
content gap: the current plugin previously covered this in one line of evidence-research/SKILL.md.
-->

# Evidence Quality Appraisal

Loaded by: evidence-research.

**Do not equate study design with quality.** A well-designed cohort study can outweigh a poorly
conducted RCT. Appraise, don't just classify.

## Provenance on every field (v1.2)

An appraisal form with fifteen fields invites completion. The temptation — for a language model
as much as for a tired reviewer — is to fill a blank with something plausible: a sample size that
sounds right for the design, a follow-up matching the abstract's framing, a risk-of-bias
judgement extrapolated from the journal's reputation. Every one of those is an invention wearing
the costume of an appraisal.

So a field holds a value **and** the provenance of that value:

| Label | Means |
|---|---|
| **REPORTED** | The source states it. Record where: abstract, full text, registry. |
| **INFERRED** | Derived from something the source does state. The basis is **mandatory** and is stored; an INFERRED field without one is refused. |
| **UNKNOWN** | Not established. The default for every field, and a complete answer requiring no apology. |

**Never invent missing appraisal data.** `UNKNOWN` is not a gap to close before the appraisal is
usable — it is the appraisal's most important output, because it is what the certainty engine
reads to return NOT ASSESSABLE rather than quietly rating a body of evidence LOW.

Completeness is reported as a count and a named list of what is missing, never as a percentage
score: "9/14 complete" reads as a grade, while the list of missing fields is what a reader needs.

## For every consequential paper, assess where possible

- Risk of bias
- Sample size
- Follow-up (duration, and whether adequate for the outcome claimed)
- Attrition / dropout
- Outcome definition (patient-important vs surrogate — see evidence-question-formulation.md)
- Comparator
- Confounding
- Precision (confidence interval width)
- Effect size
- Confidence interval
- Consistency (with other evidence on the same question)
- Directness (see evidence-directness.md — a separate, dedicated axis, not folded into this file)
- Funding / conflict-of-interest issues where reported

## Formal appraisal tools

**Do not invent scores.** If a formal appraisal tool is used, name it explicitly. Only apply a tool
when the information it requires is actually available in the source — do not approximate a score
from partial information and present it as if the tool had been properly applied.

**v1.2 — this is enforced.** `evidence/appraisal.py`'s `risk_of_bias()` refuses to attach a tool
name when the tool does not apply to the named design, or when the tool's own required domains
were not supplied. Those are the two ways a tool name gets borrowed rather than earned. A
structured judgement with no tool name is honest; a tool name over partial information is a
fabricated credential, and the function says so in the note it attaches instead.

Recognised tools, by purpose:
- **RoB 2** — risk of bias in randomized trials
- **ROBINS-I** — risk of bias in non-randomized studies of interventions
- **AMSTAR 2** — quality of systematic reviews
- **QUADAS-2** — quality of diagnostic accuracy studies
- **GRADE** — certainty of evidence across a body of evidence (not a single-study tool)

## Reading and reporting a study — required elements

When quoting any study, report: **design · sample size · population and setting · comparator ·
follow-up duration · dropout · effect size with confidence interval · the outcome actually
measured · funding and conflicts where known · the single most important limitation.**

## Hard rules

- **Statistical significance is not clinical relevance.** Report effect size, always — not just a
  p-value or "significant"/"not significant."
- **A wide confidence interval spanning no effect is not a positive result**, even if the point
  estimate looks favourable.
- **Short follow-up cannot answer a longevity question.** A 1-year survival figure does not support
  a 10-year claim.
- **Small single-centre studies are hypothesis-generating** — treat as (L4), not (L3), when the
  design will not carry the weight of the claim being made.
- **Relative risk without absolute risk is misleading.** Give both where available.
- **Do not aggregate heterogeneous studies informally.** If a proper (L2) systematic
  review/meta-analysis exists, use it. If not, present the studies separately and say explicitly
  why they cannot be pooled (differing populations, outcomes, follow-up, etc.) rather than
  eyeballing an informal average.

## Relationship to other files

This file governs *how well* a piece of evidence was conducted. del7-evidence-hierarchy.md governs
*what kind* of source it is. evidence-directness.md governs *whether it answers this specific
question*. All three are independent axes and must be reported together for any consequential
claim — a high DEL-7 tier does not imply good quality, and good quality does not imply direct
applicability.

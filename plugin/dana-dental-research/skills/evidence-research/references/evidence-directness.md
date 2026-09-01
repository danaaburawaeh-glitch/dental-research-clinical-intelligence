<!--
REFERENCE-ID: evidence-directness
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-09-01
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently.
v1.2: six named dimensions (population, procedure, material, comparison, outcome, follow-up),
a fourth verdict (UNKNOWN), a documented aggregation rule, and the laboratory/registry cap
enforced in code. Executable implementation: `evidence/directness.py`.
v0.3: DEL-7 tag definitions moved to del7-evidence-hierarchy.md.
-->

# Evidence Directness Engine

Loaded by: evidence-research, quality-control, treatment-plan-audit, clinical-governance,
scientific-problem-selection.

## Purpose

DEL-7 level alone is not sufficient. A systematic review is a systematic review whatever it is
about — directness is what stops a high tier from being read as a high-relevance answer.

## The four verdicts

**DIRECT · PARTIALLY DIRECT · INDIRECT · UNKNOWN**

UNKNOWN is a real verdict, not a missing one. It means the evidence was not rated against the
framed question, which is different from being rated and found wanting.

## The six dimensions

Each rated **HIGH / MODERATE / LOW / UNKNOWN**, or **N/A** where the dimension does not apply
(a single-arm study genuinely has no comparison — that is a property of the question, not a gap):

| Dimension | Asks |
|---|---|
| **Population** | Same patients — age, condition, risk profile, dentition state? |
| **Procedure** | Same intervention as actually performed? |
| **Material** | Same material or product class, not merely a similar one? |
| **Comparison** | Compared against the alternative actually under consideration? |
| **Outcome** | The outcome that matters to the patient, or a surrogate? |
| **Follow-up** | Long enough to answer the question being asked? |

## The aggregation rule

```
any LOW          -> INDIRECT
else any UNKNOWN -> UNKNOWN
else any MODERATE-> PARTIALLY DIRECT
else             -> DIRECT
```

**LOW dominates UNKNOWN deliberately.** A known mismatch is a finding; an unknown is an absence,
and a finding outranks an absence. Both outrank optimism. A single decisive mismatch is not
averaged away by high ratings elsewhere.

A **surrogate outcome** (bond strength, marginal gap, angular deviation, a radiographic proxy)
forces the outcome dimension to LOW. It does not answer a question about patients.

## The laboratory and registry cap — enforced, not advisory

An in-vitro study, a finite element model, and a trial registry record are **capped at INDIRECT**
for any claim about patient outcomes, however their six dimensions rate.

Bond strength in a testing machine is not restoration survival in a mouth. A mesh model is not a
jaw. A registered trial is not a result. `evidence/directness.py` applies the cap and reports it
(`capped_from`), so the cap is visible rather than mysterious.

## Directness can outweigh a DEL-7 tier advantage

A highly indirect (L2) review may answer a specific clinical question less well than a highly
applicable (L3) cohort study on this exact population, intervention and outcome.

`evidence/rank.py` expresses this as a **one-step tier adjustment**: INDIRECT or UNKNOWN
directness costs one tier position for ordering purposes. One step, not more — a DIRECT case
report still does not outrank a partially direct systematic review. The DEL-7 tag itself is never
changed, only the position in the list, and every resulting inversion is reported with its
reasoning rather than presented bare.

## Worked example

A systematic review of porcelain veneers in general may be (L2). If the question is
"minimal-prep veneers surviving beyond 10 years" and the review pools mixed preparation designs
with shorter follow-ups:

> (L2) · **INDIRECT** · population MODERATE, procedure LOW, material MODERATE, comparison N/A,
> outcome HIGH, follow-up LOW.

Not "(L2), direct proof."

## Hard rule

Never silently upgrade indirect evidence to direct proof. State the verdict and the six dimension
ratings alongside the DEL-7 tag whenever the item materially supports a consequential claim.

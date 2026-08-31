<!--
REFERENCE-ID: evidence-synthesis
VERSION: 0.3
CANONICAL-OWNER: evidence-research
SOURCE: builds on existing v0.2.1 four-bucket structure (previously in evidence-source-
separation.md) plus new structured synthesis algorithm from authoritative M3 (implied by §7, §11,
§12 taken together — M3 does not number this as a separate section, but the four-bucket output
structure was already correct in v0.2.1 and is preserved here as the canonical synthesis file).
LAST-SYNCHRONIZED: 2026-08-29
-->

# Evidence Synthesis

Loaded by: evidence-research.

## Structured synthesis algorithm

Work through these questions in order before producing a final synthesis:

1. What direct evidence exists?
2. What indirect supporting evidence exists?
3. Are findings consistent across sources? (If not, route through
   evidence-conflict-resolution.md.)
4. What is the magnitude of benefit/harm? (effect size — evidence-quality-appraisal.md)
5. How precise are the estimates? (confidence interval width)
6. Is the result clinically meaningful, not just statistically significant?
   (evidence-quality-appraisal.md)
7. How applicable is it to this specific patient/case? (clinical-applicability.md,
   evidence-directness.md)
8. What important uncertainty remains?
9. What would change confidence in this conclusion?

## Required output structure — four separated buckets

Never call one study "the evidence." Separate the body of evidence into:

1. **DIRECT EVIDENCE** — studies directly answering the framed question
   (evidence-question-formulation.md).
2. **INDIRECT SUPPORTING EVIDENCE** — related mechanisms, substrates, techniques, materials, or
   outcomes that do not directly answer the exact question.
3. **CLINICAL EXTRAPOLATION** — reasonable interpretation from the evidence, explicitly labelled
   as inference, never presented as additional evidence.
4. **UNKNOWN / UNRESOLVED** — what current evidence does not adequately answer. Route through
   absence-of-evidence.md for the precise framing of why it's unresolved (nothing found vs search
   failed vs weak/indirect vs genuine no-effect finding).

Do not mix these buckets. A reader should be able to tell, for every claim in the synthesis, which
of the four buckets it came from.

## Before finalising

- Every consequential claim carries a DEL-7 tag (del7-evidence-hierarchy.md).
- Every consequential number passes numeric-evidence-gate.md (bundled from clinical-governance).
- Every citation passes citation-verification.md.
- Applicability is stated per clinical-applicability.md, not assumed from a high DEL-7 tier alone.
- Any conflicting evidence has been handled per evidence-conflict-resolution.md, not silently
  smoothed over.

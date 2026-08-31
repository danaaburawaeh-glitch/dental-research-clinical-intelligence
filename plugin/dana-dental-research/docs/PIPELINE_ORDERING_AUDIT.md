# Pipeline Ordering Audit — v0.4.3

## The contradiction, confirmed exactly as described

`skills/evidence-research/SKILL.md`'s numbered workflow (v0.4.2) read:

```
4. Classify design, then tag DEL-7
5. Appraise quality
6. Assess directness
7. Verify every citation
7a. Apply the executable retraction gate
```

But step 7a's own body text stated: *"is passed through `apply_retraction_gate()` **before**
study classification and DEL-7 tagging (step 4 below), not after."*

This is a genuine, unambiguous contradiction: the gate is numbered to run fifth (after steps
4-7), while its own prose says it must run before step 4. A reader following the numbered list
top-to-bottom would classify and DEL-7-tag every record — including retracted ones — before ever
reaching the gate that's supposed to remove them. This matches exactly what
`RETRACTION_DIRECTIONALITY_AUDIT.md` (v0.4.2) already flagged as a known gap: *"the guarantee
it's always invoked in the right order is still a workflow instruction, not a structural
enforcement"* — v0.4.2 built the gate's logic correctly but never fixed the document's own
internal ordering contradiction that would let a reader skip straight past it.

## Root cause

The retraction gate (`apply_retraction_gate()`) was added in v0.4.1/v0.4.2 as an *addition* to
an already-numbered 13-step list, and was appended as "7a" — after citation verification (step
7) — because that's where it happened to be described, not because that's the correct execution
position. The step's own body text was written correctly (with the real dependency called out
explicitly), but the position in the list was never reconciled with it.

## Fix

Full renumbering per the brief's specified pipeline (1-16), applied to
`skills/evidence-research/SKILL.md`. See that file for the corrected text. Summary of the
reordering:

| Old position | Old step | New position | New step |
|---|---|---|---|
| 1 | Formulate question | 1 | Formulate question (unchanged) |
| 2 | Select source class | 2 | Select source class (unchanged) |
| 3 | Retrieve through gateway | 3 | Retrieve through gateway (unchanged) |
| — | (retraction/correction parsing was implicit inside connector output, never its own step) | 4 | **New explicit step: normalize retrieved records and parse retraction/correction metadata** |
| 7a | Retraction gate (contradictorily positioned after citation verification) | 5 | **Retraction gate — moved to immediately follow retrieval + parsing, before any classification** |
| 7 | Citation verification | 6 | Citation verification — moved before study classification, matching the brief's specified order |
| 4 | Study classification | 7 | Study classification — now correctly follows the gate |
| 4 (same step) | DEL-7 tagging | 8 | DEL-7 tagging — split into its own numbered step per the brief |
| 5 | Quality appraisal | 9 | Quality appraisal (renumbered, unchanged content) |
| 6 | Directness | 10 | Directness (renumbered, unchanged content) |
| 8 | Numeric gate | 11 | Numeric gate (renumbered, unchanged content) |
| 9 | Absence-of-evidence | 12 | Absence-of-evidence (renumbered, unchanged content) — brief groups this with conflict handling |
| 10 | Conflict resolution | 12 | Conflict resolution — brief's step 12 covers both; kept as two clearly-labeled sub-parts of one numbered step rather than forcing an artificial split |
| 11 | Synthesis | 13 | Synthesis (renumbered, unchanged content) |
| 12 | Applicability | 14 | Applicability (renumbered, unchanged content) |
| 13 | Claim-strength calibration | 15 | Claim-strength calibration (renumbered, unchanged content) |
| — | (output mode routing was a separate section, not numbered) | 16 | **Output mode formatting — folded into the numbered list as its own step**, per the brief's explicit step 16, while the detailed mode table remains as supporting content immediately after |

## What did NOT change

Per the brief's explicit scope limits: no connector code was touched, no new connectors were
added, no retraction semantics (the actual classification logic in
`connectors/shared/retraction_gate.py`, `connectors/pubmed/parser.py`,
`connectors/crossref/parser.py`) were modified — this is a pure document-ordering fix. Every
reference file cited by the workflow (`del7-evidence-hierarchy.md`,
`evidence-quality-appraisal.md`, etc.) is unchanged; only the SKILL.md step numbers, their order,
and (for step 4/new-explicit-parsing-step) a small amount of new connective text were touched.

## New content added (not just reordering)

Two things needed actual new text, not just renumbering:

1. **Step 4 (normalize retrieved records and parse retraction/correction metadata)** did not
   exist as its own numbered step in v0.4.2 — retraction/correction parsing was described only
   inside the connector specs (`PUBMED_CONNECTOR_SPEC.md` etc.) and referenced implicitly by
   step 7a's dependency on "already retraction/correction-parsed" records. Making this an
   explicit numbered step (per the brief's required pipeline) closes the gap where a reader could
   reasonably ask "parsed by what, exactly, and when?"

2. **Step 5's three-way handling** (excluded/flagged/included) is preserved from v0.4.2's step 7a
   almost verbatim — that text was already correct, it just needed to move.

## Verification of the fix

A static check (see the new regression test file, scenario 6) confirms the corrected SKILL.md's
numbered list places the retraction gate step at a lower step number than the study-design-
classification step, and that no prose anywhere in the file claims the opposite ordering. This
is deliberately a text-level check — the workflow itself is a Markdown instruction set, not
executable code, so "the file no longer contradicts itself" is the correct and complete claim
for this kind of fix, not "the code enforces this order," which remains the same acknowledged gap
as v0.4.2 (see `RETRACTION_DIRECTIONALITY_AUDIT.md`) — this patch fixes the document's
consistency, not the underlying structural-enforcement limitation, which was never in this
patch's scope.

<!--
REFERENCE-ID: evidence-conflict-resolution
VERSION: 0.3
CANONICAL-OWNER: evidence-research
SOURCE: authoritative M3 §12 (Google Drive 1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8)
LAST-SYNCHRONIZED: 2026-08-29
This file governs evidence-vs-evidence conflict specifically. It is distinct from
clinical-governance's Axis A/B conflict resolution, which governs safety/legal/autonomy vs
evidence — that scope is unchanged and out of scope for this file. This file did not exist in
v0.2.1.
-->

# Evidence Conflict Resolution

Loaded by: evidence-research.

This file governs what happens when **two bodies of evidence disagree with each other** — not
when evidence conflicts with patient safety, legal requirements, or patient autonomy (that is
clinical-governance's Axis A, unchanged and out of scope here).

## Do not resolve conflicts silently or by picking the convenient side

When retrieved evidence conflicts, state explicitly:

1. **What each body of evidence shows.**
2. **Its DEL-7 tag** (del7-evidence-hierarchy.md) for each side.
3. **The most likely explanation for the disagreement** — population differences, technique
   differences, follow-up length, outcome definition, funding/conflict of interest.
4. **What the disagreement means for this decision** — does it change what can be concluded, or
   just how confidently?
5. **What would settle it** — what study or data would resolve the disagreement.

Where the honest answer is "the evidence does not currently settle this," say so, and describe how
a reasonable clinician can proceed under that uncertainty — tagging that route (L4) or (JUDG) as
appropriate (del7-evidence-hierarchy.md).

## Directness can modify interpretation within a DEL-7 level

**Do not simply say "L2 always beats L3."** A highly indirect (L2) review may not answer a direct
clinical question better than a highly applicable (L3) study on this exact population,
intervention, and outcome. Compare directness (evidence-directness.md) alongside DEL-7 tier —
document the reasoning, not just the tier ranking.

Worked shape of the reasoning (not a template to fill mechanically, an illustration of the
comparison this file requires):
> "(L2) systematic review pools mixed populations and shorter follow-ups than the actual question
> asks — PARTIALLY DIRECT at best. (L3) cohort study matches population, intervention, and
> follow-up directly — DIRECT. The (L3) study's directness outweighs the (L2)'s tier advantage for
> this specific question; state both and explain why the (L3) is being weighted more heavily here."

## (JUDG) vs (L1)–(L4) conflict

Where a (JUDG) item conflicts with (L1)–(L4) evidence: say so plainly. It may still be followed as
a clinician's own practice, but it is recorded as a preference held against the evidence — never
reframed as evidence itself, and flagged as worth revisiting.

## Relationship to synthesis

This file governs the specific case of two (or more) sources disagreeing. evidence-synthesis.md
governs the broader process of assembling a full body of evidence (including conflicting sources)
into a final answer — use this file's reasoning as an input to that synthesis, not as a
replacement for it.

<!--
REFERENCE-ID: evidence-conflict-resolution
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
SOURCE: authoritative M3 §12 (Google Drive 1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8)
LAST-SYNCHRONIZED: 2026-09-01
v1.2: the EVIDENCE CONFLICT output, the no-averaging rule, and the quality-difference
distinction. Executable implementation: `evidence/conflict.py`.
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

## Never average conflicting sources

Informally pooling a 92% survival figure from one review and an 81% figure from another produces
86.5% — a number that appears in neither source, describes no population, and inherits the
weaknesses of both. It reads as a synthesis and is a fabrication.

Where pooling is legitimate it is done by meta-analysts with the primary data, and its result is
**retrieved**, not computed here. `evidence/conflict.py` deliberately provides no averaging or
pooling function at all, and emits `pooled_estimate: None` on every conflict.

## The EVIDENCE CONFLICT output (v1.2)

When high-quality sources disagree, the disagreement **is** the finding. Produce:

**EVIDENCE CONFLICT**

1. **Source A** — what it shows, its design, DEL-7 tag, certainty, directness, citation state.
2. **Source B** — the same.
3. **Where they differ**, across five dimensions, each answered — including "not established"
   where that is the truth: **population · methods · follow-up · interventions · risk of bias**.
   An unexplained dimension is reported as unexplained; "the studies just disagree" is where
   explanation stops being attempted.
4. **The most likely explanation** for the divergence, or an explicit statement that it was not
   identified.
5. **What it means for this decision** — does it change what can be concluded, or how confidently?
6. **What would settle it** — the study or data that would resolve it.

## A conflict is not a difference in evidence quality

Two sources pointing different ways are a conflict only when both are strong enough to be taken
seriously. A retracted paper conflicts with nothing — it is excluded. An in-vitro result does not
conflict with a clinical trial — they answer different questions, and the laboratory firewall
governs that.

Where one side is materially weaker, report a **quality note**, not a conflict: state the
divergence, and do not present the weaker source as an equal counterweight. Where both are too
weak, the honest reading is that the evidence does not currently answer the question.

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

<!--
REFERENCE-ID: claim-strength-governor
VERSION: 0.2.1
CANONICAL-OWNER: clinical-governance (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-08-28
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
-->

# Claim Strength Governor

Loaded by: clinical-governance, quality-control, and any skill emitting a clinical/scientific claim.

## Purpose
Classify every clinical or scientific claim before it reaches final output. A risk factor must never
silently become a predicted outcome, and an association must never silently become causation.

## Classification tiers
- FACT — directly observed/measured/reported for this patient, or a settled definitional fact.
- SUPPORTED ASSOCIATION — a verified evidence source reports a statistical association.
- CLINICAL INFERENCE — a reasonable extrapolation from data/evidence, explicitly labelled as inference.
- EXPERT/PRACTICE JUDGEMENT (JUDG) — clinician preference or common practice, not external evidence.
- HYPOTHESIS — plausible but not yet supported by direct evidence.
- UNKNOWN — cannot currently be determined; state what would resolve it.

## Rule
A risk factor is not an outcome. Do not convert "X is associated with / increases risk of Y" into
"X causes Y" or "X will produce Y" unless directly supported by verified quantitative evidence with
matched population, intervention, and timeframe (see evidence-directness.md).

Not acceptable:
"Bruxism means veneers will fail within a few years."

Acceptable:
"Bruxism/parafunction may increase mechanical complication risk and should be assessed when selecting
and protecting a restorative strategy."

## Calibrated language
Use: may, associated with, suggests, supports, is consistent with, evidence is limited, cannot
establish, requires confirmation, in this case appears to.

Avoid unless the underlying evidence genuinely supports the strength of the word: always, guarantees,
will fail, definitely, proves, never, 100%, completely eliminates.

## Application checklist (used by quality-control)
1. Locate every clinically or scientifically consequential sentence.
2. Tag it with one of the six tiers above (may stay implicit in prose, but must be internally correct).
3. Check the verb/modal against the tier — a SUPPORTED ASSOCIATION cannot use "causes" or "will".
4. Check that a risk factor is not silently promoted to a predicted individual outcome.
5. Flag QC FAIL if a HYPOTHESIS or JUDG item is phrased as if it were FACT or SUPPORTED ASSOCIATION.

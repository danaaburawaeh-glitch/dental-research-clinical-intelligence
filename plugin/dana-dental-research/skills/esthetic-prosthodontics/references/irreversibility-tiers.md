<!--
REFERENCE-ID: irreversibility-tiers
VERSION: 0.2.1
CANONICAL-OWNER: clinical-governance (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-08-28
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
-->

# Irreversibility Tiers (corrected)

Loaded by: clinical-governance, clinical-case, esthetic-prosthodontics, treatment-plan-audit,
quality-control.

## Fix applied in v0.2
v0.1 risked defaulting all veneer cases to a single tier regardless of preparation design. v0.2
requires the tier to be assigned only once the actual proposed intervention and preparation design
are known — never assigned generically from the word "veneer" alone.

## Tiers
- T0 — fully reversible (e.g. whitening, removable appliance, no tooth alteration).
- T1 — additive / minimally invasive, no irreversible tooth reduction performed (e.g. bonded
  composite, no-prep veneer with no enamel reduction).
- T2 — limited irreversible tooth reduction, including a minimal-prep veneer *where enamel/dentin
  preparation is actually performed*.
- T3 — substantial reduction, full crown, endodontic treatment, minor surgical procedures.
- T4 — arch-level or full-mouth irreversible reconstruction, or major irreversible alteration of
  vertical dimension/occlusal scheme across multiple teeth.

## Assignment rule
Do not assign a final tier until:
1. The proposed actual intervention is defined (not just the material/product category), and
2. The preparation design is known (no-prep vs minimal-prep vs full reduction).

A "veneer" is not a tier by itself: a genuinely no-prep veneer is T1; a minimal-prep veneer with
enamel reduction is T2; a veneer requiring substantial reduction functions as T3.

## Consequence of tier
Higher tiers demand progressively stronger data sufficiency, documented alternatives, prognosis
assessment, a reversible trial where feasible, fuller consent elements, and more active
challenge/QC scrutiny before being finalised (per clinical-governance).

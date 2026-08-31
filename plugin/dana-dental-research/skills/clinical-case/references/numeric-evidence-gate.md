<!--
REFERENCE-ID: numeric-evidence-gate
VERSION: 0.2.1
CANONICAL-OWNER: clinical-governance (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-08-28
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
-->

# Numeric Evidence Gate

Loaded by: clinical-governance, evidence-research, esthetic-prosthodontics, treatment-plan-audit,
quality-control.

## Purpose
Prevent unsourced numeric hallucination in consequential clinical/scientific claims.

## Scope — applies to any consequential number, including
millimetres, microns, percentages, survival rates, years/follow-up periods, sample size, torque,
preparation depth, ceramic thickness, curing time, doses, drug intervals, thresholds, statistical
estimates, sensitivity/specificity, risk ratios, confidence intervals.

## Every such number must carry one status
- A. VERIFIED — linked to a specific, retrieved, verifiable source.
- B. TYPICAL RANGE — VERIFY — explicitly labelled as a general typical range that requires
  confirmation against a specific product/protocol/source before clinical use.
- C. USER-SUPPLIED — preserved exactly as given by the user/clinician and tagged as user-supplied
  (never silently altered or rounded).
- D. CALCULATED — derived transparently from supplied or verified inputs, with the calculation shown.

Any number that is none of the above is a **QC FAIL** and must not be presented as a clinical fact.

## Example (abstract — this reference must not itself plant an unsourced number)
Not acceptable as a bare fact: "veneers usually require X mm."
Acceptable: "A commonly cited typical range for [parameter] is approximately X-Y [unit] depending on
material/system (TYPICAL RANGE — VERIFY against the specific product/protocol and source before
clinical use); it is not a universal value."
Any preparation-depth, thickness, or similar value requires VERIFIED or TYPICAL RANGE — VERIFY
status before being stated — never a bare figure presented as settled fact.

## QC check
Every consequential number in a final output must be traceable to A/B/C/D above. If a number cannot
be classified, remove it or replace it with a qualitative statement plus a note that the specific
value requires verification.

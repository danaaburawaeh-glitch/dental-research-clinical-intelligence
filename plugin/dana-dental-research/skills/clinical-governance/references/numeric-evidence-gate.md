<!--
REFERENCE-ID: numeric-evidence-gate
VERSION: 1.2.0
CANONICAL-OWNER: clinical-governance (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-09-01
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
v1.2: added the Clinical Bottom Line rule and the executable gate
(`evidence/numeric_gate.py`). The four statuses are unchanged.
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

## The Clinical Bottom Line rule (v1.2)

No numerical claim — **survival %, failure %, risk ratio, odds ratio, hazard ratio, mean
difference, confidence interval** — may appear in a Clinical Bottom Line unless the source
containing that number was **retrieved and verified this session**.

Numerical values are never reconstructed from memory. "Veneer survival is approximately 95% at 10
years" is the most fluent sentence available on the subject: well-formed, roughly consistent with
the literature, and producible with no source at all. A rule competing against that fluency loses;
a gate that scans the finished text does not.

Only **VERIFIED**, **USER-SUPPLIED** and **CALCULATED** figures may appear there. A
**TYPICAL RANGE — VERIFY** figure may not: the Bottom Line is what a reader acts on, and a range
awaiting confirmation is not something to act on.

The gate additionally refuses, at construction:

- a VERIFIED number with no named source record;
- a VERIFIED number whose source was not retrieved this session;
- any number carried by a RETRACTED source;
- a CALCULATED number that does not show its calculation.

**Executable:** `evidence/numeric_gate.py` — `scan()`, `gate_bottom_line()`, `NumericLedger`.
Study counts, participant totals and follow-up durations are not effect estimates and are
governed instead by the provenance rules in `evidence/appraisal.py` and
`evidence/sr_extraction.py`; `check_extraction_numbers()` covers them.

## QC check
Every consequential number in a final output must be traceable to A/B/C/D above. If a number cannot
be classified, remove it or replace it with a qualitative statement plus a note that the specific
value requires verification.

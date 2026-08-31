# Changelog — v0.7.0 → v0.8.0 (Clinical Completion: Minimum Prosthodontic Knowledge & Prognosis)

Narrow phase. Closes exactly the two gaps recorded at the end of Phase D (gaps 27 and 28).

## Part 1 — Source inventory first

Full inventory: `CLINICAL_SOURCE_INVENTORY_v0.8.0.md`. Two findings shaped everything after it.

**Rosenstiel is not in the project.** The registry maps `20_FIXED_PROSTHODONTICS_ROSENSTIEL.md` to
a document that is a 50-section **conversion prompt**, not converted content; the target file was
never produced. Marked **NOT AVAILABLE — DO NOT USE**. No textbook content was reconstructed, and a
test asserts no `[Source: Rosenstiel Ch. X]` anchor appears anywhere.

**The clinic's own Clinical Protocol v1.2 is the real source** — source-tagged per rule, with eight
Crossref-verified references. It is a **working draft, not approved** (eight open items block
approval), so CORE §9.1 requires that caveat on every citation. The reference files carry it and a
test enforces it.

## Part 2 — Four operational references

In `skills/esthetic-prosthodontics/references/`: `prosthodontic-restorability.md`,
`veneer-crown-decision.md`, `prosthodontic-risk-factors.md`, `treatment-sequencing-principles.md`.
No fifth file.

Rules are operational and carry their provenance class. **No numeric threshold is asserted** — not
ferrule height, not wall thickness, not crown-root ratio. Where the protocol records a thickness it
is reproduced only with its own `(JUDG → IFU)` tag and the rule that the product IFU governs. A
test greps the files for any bare `mm` value.

## Part 3 — `clinical/prognosis.py`

Categorical only: **FAVORABLE / GUARDED / POOR / UNDETERMINED**. No percentage, no survival figure,
no score — a number derived from a chairside dataset would be a fabricated statistic (CORE §3).

Five axes assessed **separately**: tooth · periodontal · restorative · prosthetic ·
functional-occlusal. Each reports basis, supporting findings, adverse findings, missing determinants
and confidence.

Three rules make it more than a lookup:
- **A missing critical determinant ends the assessment** at UNDETERMINED. It is not averaged away
  by the determinants that are present.
- **Adverse findings apply only to the axes they bear on.** A first implementation propagated every
  finding to every axis, which made the five axes decorative — active periodontal disease was
  turning the restorative prognosis POOR. Fixed and tested.
- **An `[Inferred]` critical determinant caps its axis at GUARDED**, with the cap explained. An
  inference is not a finding (CORE §5).

**Overall prognosis is the worst axis, never an average.**

## Part 4 — Ordering rule, enforced

`assess_in_order()` runs only after case state → sufficiency → red-flag sweep → findings, and before
irreversible planning. It **raises** rather than degrading when called out of order: a prognosis
produced before the sweep is worse than none, because it looks like an answer. An UNDETERMINED
result sets `blocks_irreversible_planning`, which `safety_veto.review(prognosis_result=…)` turns
into a `SAFETY_BLOCK` for definitive and irreversible acts — while leaving information-only requests
answerable.

## Part 5 — Healthy tooth protection

The least-invasive hierarchy is preserved and made explicit in `healthy-tooth-protection.md` and
`veneer-crown-decision.md`: no treatment → whitening → orthodontics → additive composite →
no-prep/additive ceramic → minimal-prep → more invasive coverage only with an independent
indication. **A full crown is never reached by esthetic convenience.**

## Defect found and fixed

`treatment_plan.py` omitted tier **T0** and labelled T1 "fully reversible", contradicting CORE §7
and the plugin's own `irreversibility-tiers.md`. Since `tier` defaulted to T1, a default item was
mislabelled as fully reversible when it was additive. Tiers now match CORE exactly (T0–T4), the
default is T0, and `REDUCTIVE_TIERS` records that T2 is irreversible too — limited, but tooth
structure does not grow back.

## Tests

`clinical/tests/test_clinical_completion.py` → **66/66**, covering all 10 required scenarios plus
10 invariants. Prior suites unchanged: clinical layer 60/60, Saudi 50/50, ClinicalTrials.gov 50/50.

## Not in this release

M5. Any discipline beyond Fixed Prosthodontics and Esthetic Restorative Dentistry. New connectors.
Six assistants. Oral surgery, orthodontic, endodontic or implant-surgery knowledge. Marketing or
teaching features.

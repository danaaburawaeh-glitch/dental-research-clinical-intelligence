# Package Validation — v0.7.0

`claude plugin validate` → **passed**. `dana-dental-research`, version `0.7.0`.

| Item | Result |
|---|---|
| Skills | 9, five updated to invoke the clinical layer |
| Top-level packages | `connectors/` (5) + `clinical/` (new) |
| New modules | `case_state`, `red_flag_sweep`, `treatment_plan`, `safety_veto`, `evidence_binding` |
| Compile check | all modules compile |
| Archive integrity | `unzip -t` clean; `.plugin` and `.zip` identical |

## Tests

| Suite | Result |
|---|---|
| `clinical/tests/test_clinical_layer.py` | **60/60** |
| `connectors/sfda/tests/test_saudi_governance.py` | **50/50** |
| `connectors/clinical_trials/tests/test_clinical_trials.py` | **50/50** |

## Non-regression

`diff -rq connectors/` against v0.6.0 → **no differences**. Live re-run from a fresh extraction
reproduces prior results.

## Connector states — unchanged from the frozen v0.6.0 baseline

`~~literature` · `~~systematic-reviews` · `~~journal-access` · `~~clinical-trials` CONNECTED ·
`~~regulatory-saudi` **NOT CONNECTED — AUTH REQUIRED** · `~~clinical-guidelines` ·
`~~manufacturer-ifu` NOT CONNECTED.

## Not started

M5. Rosenstiel (no source document exists). Clinical Protocol. Disciplines beyond the two in scope.

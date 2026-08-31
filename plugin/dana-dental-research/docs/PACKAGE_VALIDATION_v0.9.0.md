# Package Validation — v0.9.0

`claude plugin validate` → **passed**. `dana-dental-research`, version `0.9.0`.

| Suite | Result |
|---|---|
| `clinical/tests/test_protocol_approval.py` | **24/24** |
| `clinical/tests/test_clinical_completion.py` | **66/66** |
| `clinical/tests/test_clinical_layer.py` | **60/60** |
| `connectors/sfda/tests/test_saudi_governance.py` | **50/50** |
| `connectors/clinical_trials/tests/test_clinical_trials.py` | **50/50** |

## Non-regression

`diff -rq` on `connectors/` and on `clinical/*.py` against v0.8.0 → **no differences**. No clinical
logic changed; the release is documentation status plus the new approval test.

## Connector states — unchanged from the frozen v0.6.0 baseline

`~~literature` · `~~systematic-reviews` · `~~journal-access` · `~~clinical-trials` CONNECTED ·
`~~regulatory-saudi` NOT CONNECTED — AUTH REQUIRED · `~~clinical-guidelines` ·
`~~manufacturer-ifu` NOT CONNECTED.

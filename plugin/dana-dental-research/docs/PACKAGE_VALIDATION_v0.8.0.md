# Package Validation — v0.8.0

`claude plugin validate` → **passed**. `dana-dental-research`, version `0.8.0`.

| Suite | Result |
|---|---|
| `clinical/tests/test_clinical_completion.py` | **66/66** |
| `clinical/tests/test_clinical_layer.py` | **60/60** |
| `connectors/sfda/tests/test_saudi_governance.py` | **50/50** |
| `connectors/clinical_trials/tests/test_clinical_trials.py` | **50/50** |

## Added

4 references in `skills/esthetic-prosthodontics/references/` · `clinical/prognosis.py` ·
`CLINICAL_SOURCE_INVENTORY_v0.8.0.md`. Updated: `healthy-tooth-protection.md`, `safety_veto.py`
(prognosis gate), `treatment_plan.py` (tier correction), 4 skills, `quality-control`.

## Non-regression

`diff -rq connectors/` against v0.7.0 → **no differences**. Connector states unchanged from the
frozen v0.6.0 baseline; `~~regulatory-saudi` still NOT CONNECTED — AUTH REQUIRED.

## Content checks

No `[Source: Rosenstiel Ch. X]` anchor anywhere. No bare `mm` threshold in the reference files. No
percentage emitted by the prognosis engine. Clinic Protocol cited as a working draft throughout.

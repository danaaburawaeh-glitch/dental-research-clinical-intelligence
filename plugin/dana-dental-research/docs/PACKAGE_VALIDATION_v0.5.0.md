# Package Validation — v0.5.0

## Manifest

`claude plugin validate` → **passed**. `name: dana-dental-research`, `version: 0.5.0`.

## Structure

| Item | Result |
|---|---|
| Skills | 9, unchanged |
| Connectors | 4 packages: `pubmed`, `crossref`, `clinical_trials`, `shared` |
| New connector modules | `clinical_trials/{client,parser,models,errors,rate_limit}.py`, `README.md`, `tests/` |
| New shared module | `shared/trial_publication_linkage.py` |
| Python compile check | all modules compile |
| Archive integrity | `unzip -t` clean |
| `.plugin` / `.zip` | identical content |

## Regression

`connectors/clinical_trials/tests/test_clinical_trials.py` → **50/50 pass**, all 20 required
scenarios covered.

## Non-regression of validated connectors

`diff -rq connectors/pubmed` and `connectors/crossref` against v0.4.5.2 → **no differences**.
Post-package live re-run from a fresh extraction reproduces prior results exactly:
PubMed systematic-review search `SUCCESS` count 36 with the v0.4.5 OR-filter; Crossref
`lookup-doi` `SUCCESS`; retraction gate included=1/excluded=0/flagged=0.

## Connector states in the shipped package

| Placeholder | State |
|---|---|
| `~~literature` | CONNECTED — PubMed/NCBI |
| `~~systematic-reviews` | CONNECTED — PubMed filtered retrieval |
| `~~journal-access` | CONNECTED — METADATA/CITATION VERIFICATION via Crossref |
| `~~clinical-trials` | CONNECTED — ClinicalTrials.gov API v2 |
| `~~clinical-guidelines` | NOT CONNECTED |
| `~~manufacturer-ifu` | NOT CONNECTED |
| `~~regulatory-saudi` | NOT CONNECTED |

## Not started

M4 / SFDA regulatory. M5. Rosenstiel. Clinical Protocol migration.

# Package Validation — v0.6.0

## Manifest

`claude plugin validate` → **passed**. `name: dana-dental-research`, `version: 0.6.0`.

## Structure

| Item | Result |
|---|---|
| Skills | 9, unchanged |
| Connector packages | 5: `pubmed`, `crossref`, `clinical_trials`, `sfda`, `shared` |
| New Saudi references | 4, in `skills/clinical-governance/references/` |
| Python compile check | all modules compile |
| Archive integrity | `unzip -t` clean; `.plugin` and `.zip` identical |

## Tests

| Suite | Result |
|---|---|
| `connectors/sfda/tests/test_saudi_governance.py` | **50/50 pass** (8 required scenarios + 8 invariants) |
| `connectors/clinical_trials/tests/test_clinical_trials.py` | **50/50 pass** (Phase B, non-regression) |

## Non-regression

`diff -rq` on `connectors/pubmed`, `connectors/crossref`, `connectors/clinical_trials` against
v0.5.0 → **no differences**. Post-package live re-run from a fresh extraction reproduces prior
results.

## Connector states in the shipped package

`~~literature` CONNECTED — PubMed/NCBI · `~~systematic-reviews` CONNECTED — PubMed filtered
retrieval · `~~journal-access` CONNECTED — Crossref · `~~clinical-trials` CONNECTED —
ClinicalTrials.gov API v2 · `~~regulatory-saudi` **NOT CONNECTED — AUTH REQUIRED** ·
`~~clinical-guidelines` NOT CONNECTED · `~~manufacturer-ifu` NOT CONNECTED.

## Secrets check

No credential literal appears in any source file. The SFDA connector reads all configuration from
the environment; the only hard-coded URL is the public developer portal.

## Not started

M5. Rosenstiel. Clinical Protocol.

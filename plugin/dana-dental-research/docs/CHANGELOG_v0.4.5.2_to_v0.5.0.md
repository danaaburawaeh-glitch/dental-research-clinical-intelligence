# Changelog — v0.4.5.2 → v0.5.0 (FEATURE RELEASE — Phase B)

## Headline

`~~clinical-trials` is implemented and **CONNECTED — ClinicalTrials.gov API v2**, live-validated
from the packaged code on Claude Code / macOS, 2026-08-31.

Four of seven connectors are now connected. `~~clinical-guidelines`, `~~manufacturer-ifu` and
`~~regulatory-saudi` remain NOT CONNECTED; M4/SFDA is not started.

## Not changed

The validated PubMed and Crossref connectors are **byte-identical** to v0.4.5.2. Verified by
`diff -rq` over `connectors/pubmed/` and `connectors/crossref/`. Their live behaviour was re-run
after packaging and reproduces exactly. M4, M5, Rosenstiel and Clinical Protocol are not migrated.

## Added — connector

```
connectors/clinical_trials/{client,parser,models,errors,rate_limit}.py + README.md
connectors/clinical_trials/tests/test_clinical_trials.py     50 assertions, 20 required scenarios
connectors/shared/trial_publication_linkage.py               linkage + deduplication
```

Reuses `shared/provenance.py` and `shared/retry.py` rather than duplicating them — the retry
semantics are identical to PubMed's and Crossref's.

## API verification came first

`docs/CLINICALTRIALS_API_V2_VERIFICATION.md` records what was verified by issuing real requests,
not by reading documentation. Findings that changed the implementation:

- **Error bodies are plain text, not JSON.** A parser assuming a JSON error envelope would throw
  while handling the error. The client reads the status code first and never JSON-decodes an error
  body.
- **`pageSize` above 1000 is silently clamped** (1001 → 1000 studies, HTTP 200, no error). The
  connector clamps client-side so a caller's `max_results` is never quietly wrong.
- **Unknown parameters are rejected with HTTP 400.** An unrecognised status or phase is therefore
  dropped rather than forwarded — sending a caller's typo would fail the whole query.
- **Modules are omitted, not nulled, when absent.** Every accessor tolerates absence.
- **404 vs 400 on identifiers**: well-formed-but-absent is 404, malformed is 400. The connector
  validates locally so a malformed ID never reaches the network.
- `GET /api/v2/openapi.yaml` returns 404; the `enums` and `metadata` endpoints were used as the
  machine-readable source instead. All 14 statuses, 3 study types, 6 phases and 3 reference types
  come from the live enum endpoint.

## Evidence-safety rules, enforced in code

Sections 5, 6, 9 and 10 of the brief are implemented as data on every record rather than as prose
a consumer might skip:

- `evidence_class` — A (registered, no results) / B (registry results posted) / C (linked
  publication). Category D (independently retrieved publication) is deliberately **not assignable**
  by this connector, because it is a property of a PubMed record.
- `status_safety_note` on all 14 statuses. `COMPLETED` carries "means finished, not succeeded";
  `WITHDRAWN` states the trial never started and that withdrawal is not a negative result;
  `TERMINATED` reports `why_stopped` where given. A regression test asserts no status note
  contains an efficacy word.
- `registry_results` labelled "sponsor-submitted, NOT peer-reviewed", carried structurally with
  nothing calculated from it.
- NCT IDs validated, never repaired. `NCT123` is rejected with `IDENTIFIER_INVALID` and no request
  is issued — it never becomes `NCT00000123`.
- `LINK VERIFIED` requires a real identifier. A `BACKGROUND` reference does not verify a link, and
  topical similarity never does. `LINK MISMATCH` is distinct from "no link found".
- `independent_study_count` — a trial and its publication are one study, never two.

## Added — status taxonomy

Two identifier states, reusing the existing vocabulary otherwise: `NOT_FOUND` (well-formed NCT ID,
no such record) and `IDENTIFIER_INVALID` (malformed, never sent). Kept distinct from
`ZERO_RESULTS` on purpose — a typo and an empty result set are different facts and must produce
different statements to the user.

## Updated — skills

| File | Change |
|---|---|
| `clinical-evidence-safe-search-gateway.md` | `~~clinical-trials` row updated; new routing section — registry answers landscape questions, PubMed remains primary for effectiveness; six mandatory handling rules |
| `absence-of-evidence.md` | Six distinguishable absence situations replace one "no evidence" statement, plus symmetric caution that registry coverage is incomplete |
| `quality-control/SKILL.md` + new `references/registry-vs-published-evidence.md` | Nine-point gate; the critical failure (registration cited as proof of effectiveness) is release-blocking |
| `connector-capability-map.md` (both copies) | `~~clinical-trials` → CONNECTED with the Phase B live validation record |

## Live validation

Six tests, all PASS, from the packaged code against the live API — search (1350 hits), fetch
(NCT00226148, every required field), status filter (all RECRUITING), zero-result (`ZERO_RESULTS`
with the not-proof-of-absence meaning), results-aware (NCT00607022, class B, results parsed), and
the full linkage chain NCT00782171 → PMID 18416725 → DOI → Crossref `VERIFIED`, deduplicating 2
records to 1 study. Detail: `docs/LIVE_CLINICALTRIALS_VALIDATION.md`.

## Known limitations recorded

`UNRESOLVED_GAPS.md` gains six Phase B entries — the most consequential being that registry
coverage is incomplete (absence from ClinicalTrials.gov is weaker evidence of absence than absence
from PubMed), and that the NCT-in-publication linkage direction is partial because PubMed's
`<DataBankList>` is not parsed and Phase B was forbidden from modifying that connector.

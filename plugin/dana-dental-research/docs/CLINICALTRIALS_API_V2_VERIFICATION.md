# ClinicalTrials.gov API v2 — Verification

**Method.** Every statement below was verified by issuing a real HTTP request to the official
`clinicaltrials.gov` host from this machine and reading the actual response — not from a
documentation page, a tutorial, or memory. Where behaviour differs from what documentation would
lead you to expect, the observed behaviour is recorded and marked.

**Verified:** 2026-08-31. **API version reported by the service:** `2.0.5`
(`GET /api/v2/version` → `{"apiVersion":"2.0.5","dataTimestamp":"2026-08-28T09:00:06"}`).

The deprecated classic API (`/api/query/*`) is **not** used anywhere in this connector.

## 1. Base URL and endpoints

| Item | Verified value |
|---|---|
| Base URL | `https://clinicaltrials.gov/api/v2` |
| Study search | `GET /studies` |
| Study detail | `GET /studies/{nctId}` |
| Version | `GET /version` |
| Enumerations | `GET /studies/enums` |
| Field metadata | `GET /studies/metadata` |
| Data-set size | `GET /stats/size` |

`GET /api/v2/openapi.yaml` returns **404** — there is no OpenAPI document at that path on this
host, so the enum and metadata endpoints were used as the authoritative machine-readable source
instead.

## 2. Query syntax — parameters confirmed to return HTTP 200

`query.cond` (condition), `query.intr` (intervention), `query.term` (general terms),
`query.spons` (sponsor), `query.locn` (location), `query.titles`.

Filters: `filter.overallStatus` (accepts a single value or several joined by `|`, verified as OR),
`filter.ids`, `filter.advanced` (Essie expression, e.g. `AREA[HasResults]true`),
`aggFilters`, `postFilter.overallStatus`. Also `sort`, `fields`, `countTotal`.

**Unknown parameters are rejected.** `&bogusParam=1` → **HTTP 400**. The API is strict, so the
connector must never pass a parameter it has not verified.

**Filtering is real, not advisory.** `filter.overallStatus=RECRUITING` over a dental query
returned five studies whose parsed `overallStatus` was `RECRUITING` in every case.

## 3. Pagination

- Response envelope: `{"totalCount": int (only when countTotal=true), "studies": [...],
  "nextPageToken": str}`.
- `pageSize=1` → 1 study; `pageSize=1000` → 1000 studies.
- **`pageSize=1001` → HTTP 200 with 1000 studies.** The cap is applied **silently** — no error is
  raised. Verified directly. The connector therefore clamps to 1000 itself rather than relying on
  the server to complain.
- `pageToken` works: page 1 and page 2 of the same query returned disjoint NCT ID sets
  (`['NCT05340595','NCT06673030','NCT05762692']` then `['NCT04933409','NCT04946292','NCT05162963']`).
- `nextPageToken` is present on both pages; its absence is the end-of-results signal.

## 4. Error responses — plain text, NOT JSON

This is the single most important implementation finding. Error bodies are **`text/plain`**:

| Case | Status | Body (verbatim) |
|---|---|---|
| Unknown query parameter | 400 | *(400, non-JSON)* |
| Invalid enum value | 400 | ``Invalid value in parameter `overallStatus`: `NOT_A_STATUS` `` |
| Well-formed but absent NCT ID | 404 | `NCT number NCT99999999 not found` |
| Malformed NCT ID | 400 | ``Parameter `nctId` has incorrect format`` |

A parser that assumes a JSON error envelope will itself throw while handling the error. The
connector reads `status_code` first and never attempts to JSON-decode an error body.

Note the 400/404 split on identifiers: **malformed** (`NOTANID`) is 400, **well-formed but
non-existent** (`NCT99999999`) is 404. The connector validates the format locally before the
request, so a malformed ID never reaches the network.

## 5. Response JSON schema

Study detail top level: `protocolSection`, `resultsSection` (only when results are posted),
`derivedSection`, `hasResults` (boolean, always present).

`protocolSection` modules observed: `identificationModule`, `statusModule`,
`sponsorCollaboratorsModule`, `descriptionModule`, `conditionsModule`, `designModule`,
`armsInterventionsModule`, `outcomesModule`, `eligibilityModule`, `contactsLocationsModule`,
`referencesModule`, `ipdSharingStatementModule`.

**Modules are omitted, not nulled, when absent.** NCT00000102 has no `outcomesModule` and no
`referencesModule` at all. Every accessor in the parser must tolerate a missing module.

Dates are structs, not strings: `studyFirstPostDateStruct = {"date": "2018-07-27", "type":
"ACTUAL"}`. `type` is `ACTUAL` or `ESTIMATED` — a material distinction the parser preserves
rather than flattening.

`enrollmentInfo = {"count": 21, "type": "ACTUAL"}` — again `ACTUAL` vs `ESTIMATED`. A withdrawn
trial carries `{"count": 0, "type": "ACTUAL"}`, which is meaningful: nobody was enrolled.

## 6. Enumerations (from `GET /studies/enums`, 41 groups)

- **Status (14):** `ACTIVE_NOT_RECRUITING`, `COMPLETED`, `ENROLLING_BY_INVITATION`,
  `NOT_YET_RECRUITING`, `RECRUITING`, `SUSPENDED`, `TERMINATED`, `WITHDRAWN`, `AVAILABLE`,
  `NO_LONGER_AVAILABLE`, `TEMPORARILY_NOT_AVAILABLE`, `APPROVED_FOR_MARKETING`, `WITHHELD`,
  `UNKNOWN`.
- **StudyType (3):** `EXPANDED_ACCESS`, `INTERVENTIONAL`, `OBSERVATIONAL`.
- **Phase (6):** `NA`, `EARLY_PHASE1`, `PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`.
- **Sex (3):** `FEMALE`, `MALE`, `ALL`. **StandardAge (3):** `CHILD`, `ADULT`, `OLDER_ADULT`.
- **AgencyClass (9):** `NIH`, `FED`, `OTHER_GOV`, `INDIV`, `INDUSTRY`, `NETWORK`, `AMBIG`,
  `OTHER`, `UNKNOWN`.
- **ReferenceType (3):** `BACKGROUND`, `RESULT`, `DERIVED`.
- **ReportingStatus (2):** `NOT_POSTED`, `POSTED`.

The full status list is wider than the seven statuses named in the Phase B brief — `WITHHELD` and
the four expanded-access statuses also exist and are handled.

## 7. Posted-results structure

For a study with `hasResults: true` (verified on NCT00607022), `resultsSection` contains:
`participantFlowModule` (`groups`, `periods`), `baselineCharacteristicsModule` (`groups`,
`denoms`, `measures`), `outcomeMeasuresModule` (`outcomeMeasures`), `adverseEventsModule`
(`frequencyThreshold`, `eventGroups`), `moreInfoModule`.

`statusModule` then also carries `resultsFirstSubmitDate`, `resultsFirstSubmitQcDate` and
`resultsFirstPostDateStruct`.

87 dental-implant trials currently carry posted results (`filter.advanced=AREA[HasResults]true`,
`countTotal=true`).

## 8. Intervention, eligibility, sponsor structures

- `armsInterventionsModule.interventions[]`: `{type, name, description, armGroupLabels,
  otherNames}`. `type` is the intervention-type enum (DRUG, DEVICE, PROCEDURE, …).
- `eligibilityModule`: `{eligibilityCriteria (free text), healthyVolunteers (bool), sex,
  minimumAge, maximumAge, stdAges[]}`. Ages are strings with units (`"18 Years"`), not numbers —
  the parser keeps them verbatim rather than coercing.
- `sponsorCollaboratorsModule`: `{leadSponsor: {name, class}, collaborators: [{name, class}],
  responsibleParty: {type, investigatorFullName, investigatorTitle, …}}`. `collaborators` and
  `responsibleParty` are frequently absent.

## 9. Publication references

`protocolSection.referencesModule.references[]` = `{pmid, type, citation}`. Verified on
NCT00782171 → three PMIDs, all `type: RESULT`; and NCT02864862 → one PMID, `type: DERIVED`.

**The `type` value carries the linkage semantics and must not be flattened:**
- `RESULT` — sponsor-submitted publication reporting this trial's results.
- `DERIVED` — NLM-derived from PubMed's own NCT ID link.
- `BACKGROUND` — cited background literature, **not** a report of this trial.

Treating `BACKGROUND` as a results publication would be a fabricated linkage. The connector
classifies by `type` and never asserts a trial↔publication link from a `BACKGROUND` reference.

## 10. Rate limiting

No `X-RateLimit-*`, `Retry-After` or equivalent headers are returned (`server: istio-envoy`). No
documented public quota was confirmed. The connector therefore applies its own conservative
client-side limiter rather than assuming an allowance, and treats HTTP 429 as retryable if it
ever appears.

## 11. Authentication

None required. No API key, no registration. All requests above were unauthenticated.

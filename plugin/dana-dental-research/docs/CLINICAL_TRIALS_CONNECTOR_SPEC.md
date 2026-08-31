# ClinicalTrials.gov Connector Specification — Phase B

Companion to `CLINICALTRIALS_API_V2_VERIFICATION.md` (what the API actually does) — this document
specifies what the connector does with it, and why.

## 1. Scope

`~~clinical-trials` supplies **registry** information: what has been registered, its status, its
design, and — where posted — sponsor-submitted results. It does **not** supply published
evidence. PubMed remains the primary route for treatment-effectiveness questions;
ClinicalTrials.gov supplements it and never replaces it.

## 2. Module layout

```
connectors/clinical_trials/
├── client.py      search + fetch, retry, failure contract, CLI
├── parser.py      API v2 JSON -> ClinicalTrialRecord
├── models.py      record dataclass, verified enums, NCT validation, evidence classification
├── errors.py      status taxonomy (shared vocabulary + 2 identifier states)
├── rate_limit.py  self-imposed client-side limiter
└── README.md
```

Reused from `connectors/shared/` rather than duplicated: `provenance.py` (provenance envelope),
`retry.py` (`with_backoff`, identical retry semantics to PubMed/Crossref). `normalization.py` and
`identifiers.py` are available but not currently needed — registry records are identified by NCT
ID, which has its own validator in `models.py` because its rules differ from a DOI's or a PMID's.

`shared/trial_publication_linkage.py` is new and lives in `shared/` because it reasons about a
registry record and a PubMed record together — it belongs to neither connector alone.

## 3. Core functions

### `clinical_trials_search(...)`

Inputs: `condition`, `intervention`, `keywords`, `recruitment_status`, `study_type`, `phase`,
`sponsor`, `location`, `max_results`, `page_token`.

Mapped to verified parameters: `query.cond`, `query.intr`, `query.term`, `query.spons`,
`query.locn`, `filter.overallStatus`, and Essie `filter.advanced` for phase and study type.

Three deliberate refusals:
- **An unrecognised status or phase is dropped, not forwarded.** The API returns HTTP 400 for an
  invalid enum, so forwarding a caller's typo would fail the entire query instead of ignoring one
  filter.
- **`max_results` is clamped to 1000 client-side.** The server silently truncates above that
  (verified: `pageSize=1001` returns 1000 studies with HTTP 200), so relying on it would make a
  caller's requested size quietly wrong.
- **An empty search is refused**, not issued as an unbounded registry query.

Returns `{status, records, total_count, next_page_token, executed_query, provenance}`.

### `clinical_trials_fetch(nct_id)`

Validates the ID first. Invalid → `IDENTIFIER_INVALID`, **no request issued**. Valid but absent →
`NOT_FOUND` (HTTP 404). If the registry returns a record whose `nctId` differs from the one
requested → `IDENTIFIER_MISMATCH`, never silently accepted.

## 4. ClinicalTrialRecord

All fields required by the brief, plus `why_stopped` (needed for the TERMINATED rule),
`publication_references`, `registry_results`, `evidence_class`, `evidence_class_note`,
`status_safety_note`, and `date_types`.

**Missing stays missing.** A field absent from the API response is `None` — never `0`, never
`"NA"`, never an empty string standing in for a value. Two consequences are tested explicitly: a
trial with no `enrollmentInfo` has `enrollment is None` (not `0`, which would falsely read as
"nobody enrolled"), and a trial with no `phases` has `phases is None` (not `["NA"]`, which is a
real registry value meaning "not applicable").

`ACTUAL` vs `ESTIMATED` is preserved for enrolment and for all three date fields. An estimated
completion date is a plan; an actual one is a fact.

## 5. Registry ≠ published evidence

Enforced at parse time, so it cannot be lost downstream. `evidence_class` is one of:

| Class | Meaning |
|---|---|
| `REGISTERED_NO_RESULTS` (A) | Registration is a statement of intent. Carries no efficacy information at all. |
| `REGISTERED_REGISTRY_RESULTS_POSTED` (B) | Sponsor-submitted structured results. Not peer-reviewed. |
| `REGISTERED_LINKED_PUBLICATION` (C) | A publication is referenced. The publication must still be retrieved and appraised before it counts as evidence. |

Category **D** (a trial publication retrieved independently through PubMed) is deliberately **not
assignable by this connector**: it is a property of a PubMed record, not of a registry record.
Allowing a registry record to claim class D is precisely the conflation Section 6 of the brief
forbids.

Registry status is never mapped to evidence quality. `STATUS_SAFETY_NOTES` covers all 14 verified
statuses; a regression test asserts that no status note contains an efficacy word.

## 6. Publication linking

`LINK VERIFIED` requires a real identifier, in at least one direction:
- the registry's `referencesModule` names the PMID with type `RESULT` or `DERIVED`; or
- the publication's own metadata contains the NCT ID.

`BACKGROUND` references are cited background literature and never verify a link.
`LINK MISMATCH` is returned when the publication names a *different* trial — a distinct outcome
from "no link found", and more informative than either.

Known limitation: the NCT-in-publication direction reads the PubMed record's abstract and title.
PubMed's structured `<DataBankList>` accession numbers (where NCT IDs are formally deposited) are
not parsed, because Phase B must not modify the validated PubMed connector. The registry-side
direction is unaffected and is the stronger signal in practice.

## 7. Deduplication

`deduplicate_trials_and_publications` groups by NCT ID and returns `independent_study_count` —
the only count a synthesis may cite. A linked trial + publication is one study, not two. Records
that cannot be linked by an identifier are **not** merged on suspicion; guessing would be the
fabrication Section 7 forbids.

## 8. Failure states

The existing taxonomy is reused so the gateway needs no new vocabulary. Two identifier states are
added because this registry makes a distinction the other connectors do not:
`NOT_FOUND` (well-formed ID, no record) and `IDENTIFIER_INVALID` (malformed ID, never sent).
These are deliberately not folded into `ZERO_RESULTS` or `UPSTREAM_ERROR` — a typo in an ID and
an empty search result are different facts and must produce different user-facing statements.

Error bodies from this API are **plain text, not JSON**. The client reads the status code first
and never attempts to JSON-decode an error body; the upstream message is surfaced verbatim and
truncated.

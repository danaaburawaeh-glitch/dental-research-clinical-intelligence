# PubMed / NCBI E-utilities Connector Specification — v0.4 Phase A

Verified against: `nlm.nih.gov/dataguide/eutilities/` (NLM "Insider's Guide"), NCBI Bookshelf
E-utilities docs (`ncbi.nlm.nih.gov/books/NBK25497/`, `NBK25499/`, `NBK25500/`), and live
confirmation this session (see `CONNECTOR_IMPLEMENTATION_DECISION.md` Part 2). Retrieved
2026-08-29. Where documentation and memory might differ, documentation as fetched this session
is authoritative — nothing here was filled in from unverified recollection.

## Base URL and utilities used

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
```

| Utility | Endpoint | Used for |
|---|---|---|
| ESearch | `esearch.fcgi` | Text query → list of PMIDs |
| ESummary | `esummary.fcgi` | PMIDs → document summaries (DocSum) |
| EFetch | `efetch.fcgi` | PMIDs → full records (abstract text or XML) |

ELink, EPost, EInfo, ESpell, ECitMatch, EGQuery exist but are not used in Phase A.

## Authentication and identification

- **No API key required.** An optional free API key raises the rate limit (see below).
- **Politeness parameters** (not authentication, but NCBI-requested identification):
  - `tool` — identifies the calling application. Set from `NCBI_TOOL` env var, default
    `dana_dental_evidence`.
  - `email` — contact email. Set from `NCBI_EMAIL` env var. **Never hard-coded** — see
    `CONNECTOR_SECURITY.md`.
  - `api_key` — optional, from `NCBI_API_KEY` env var, if present.

## Rate limits (verified current, not assumed)

- **Without API key: 3 requests/second.**
- **With API key: 10 requests/second** (default enhanced tier).
- Confirmed via NLM Support Center documentation fetched this session; this matches the figures
  given in the release brief, so no correction was needed here — but the number was independently
  re-verified against current documentation rather than taken on the brief's word alone, per
  Phase 1's instruction.

## Response formats

- ESearch: `retmode=xml` (default) or `retmode=json`. **Note (live-tested this session):** a
  fetched example ESearch XML response matched the documented `<eSearchResult>` schema exactly
  (`<Count>`, `<RetMax>`, `<RetStart>`, `<IdList><Id>...</Id></IdList>`,
  `<TranslationSet>`, `<QueryTranslation>`). JSON mode was requested but not independently
  confirmed live this session (see `CONNECTOR_IMPLEMENTATION_DECISION.md`) — the client below
  requests `retmode=json` per documentation and includes an XML-fallback parser as a defensive
  measure, since the JSON response shape itself was not independently observed live.
- ESummary: `retmode=json` (v2 recommended, `version=2.0`) or XML DocSum.
- EFetch (PubMed): `retmode=xml` for structured records (MeSH terms, publication types, abstract,
  authors, journal); `retmode=abstract&rettype=text` for plain-text abstract display. The client
  uses XML mode for structured `EvidenceRecord` population, since abstract/text mode does not
  reliably expose MeSH terms or publication-type fields.

## Functions implemented (`connectors/pubmed/client.py`)

### `pubmed_search(query, date_range=None, study_type=None, max_results=20, sort=None)`
Calls ESearch. Builds the `term` parameter from `query` plus optional `mindate`/`maxdate` (from
`date_range`) and a publication-type filter (from `study_type`, mapped to PubMed's
`[Publication Type]` field tag — e.g. `"Randomized Controlled Trial"[Publication Type]`, never a
bare title-text guess). Returns a list of PMIDs plus the raw query translation NCBI returns, so
the actual interpreted search is auditable (feeds `search-log-template.md`).

### `pubmed_fetch(pmids)`
Accepts a single PMID or list. Calls EFetch (`retmode=xml`) to get full records, then ESummary as
a secondary cross-check for fields EFetch's XML sometimes omits (e.g. a clean publication date).
Returns a list of `EvidenceRecord`-shaped dicts (see `connectors/shared/`) with:
PMID, title, authors, journal, publication year/date, publication types, DOI (if present in the
`ArticleIdList`), abstract (if present), MeSH terms (if present).

**Never invents a missing field** — per Phase 13, a field EFetch/ESummary doesn't return is
`null`, not guessed or left implicit.

### `pubmed_search_systematic_reviews(query, **kwargs)`
Calls `pubmed_search` with `study_type` filters restricted to legitimate PubMed publication-type
tags: `"Systematic Review"[Publication Type]` and/or `"Meta-Analysis"[Publication Type]`.

**Does not classify by title text.** A result is only treated as a systematic review if PubMed's
own `PublicationType` metadata (returned in the EFetch XML `<PublicationTypeList>`) actually says
so — a title containing the words "systematic review" with a `PublicationType` of, say, "Journal
Article" or "Review" is reported with its actual publication type, not silently upgraded. This is
enforced in `parser.py`, not left to the caller.

### `pubmed_search_clinical_studies(query, designs=None, **kwargs)`
Supports `designs` values: `rct` → `"Randomized Controlled Trial"[Publication Type]`,
`controlled_trial` → `"Controlled Clinical Trial"[Publication Type]`, `cohort` →
`"Cohort Studies"[MeSH Terms]` (MeSH, since there is no clean Publication Type tag for cohort
studies), `observational` → a combination excluding RCT/controlled-trial tags.

**RCT disambiguation (Phase 3 requirement):** `models.py` defines `STUDY_DESIGN_RCT =
"Randomized Controlled Trial"` as a constant distinct from any dental-procedure vocabulary. The
parser never matches "RCT" as free text against an abstract or title to infer study design — design
classification comes only from PubMed's structured `PublicationType`/`MeSH` fields, which is the
same mechanism that prevents "root canal treatment" abstracts from being misclassified as
randomized-trial design: the structured field, not the acronym in the text, decides.

## Failure states surfaced (Phase 7 — implemented in `errors.py`)

`SUCCESS`, `ZERO_RESULTS`, `RATE_LIMITED` (HTTP 429 or NCBI's own throttling response),
`TIMEOUT`, `AUTH_ERROR` (malformed/rejected API key), `UPSTREAM_ERROR` (5xx), `PARSE_ERROR`
(response didn't match expected XML/JSON schema), `NOT_CONNECTED` (no attempt made — connector
map says not connected in this environment). See `CONNECTOR_FAILURE_MODEL.md` for the full
mapping to gateway-level messages.

## What was NOT independently live-verified this session

Per `CONNECTOR_IMPLEMENTATION_DECISION.md`: a fresh ESearch for this release's actual target
query, and a live EFetch/ESummary call for any PMID from it, were not achieved due to
`web_fetch`'s prior-search-result restriction. The schema above is built from official
documentation plus one confirmed-live example response (a different query, matching documented
shape exactly) — not from a fresh execution of this exact client against this exact question.

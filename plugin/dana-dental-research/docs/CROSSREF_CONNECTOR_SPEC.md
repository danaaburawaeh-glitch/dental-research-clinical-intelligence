# Crossref REST API Connector Specification — v0.4 Phase A

Verified against: `crossref.org/documentation/retrieve-metadata/rest-api/`,
`crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/`, the
`community.crossref.org` rate-limit announcement threads (Dec 2025 change), and live confirmation
this session of DOI resolution behavior (see `CONNECTOR_IMPLEMENTATION_DECISION.md`). Retrieved
2026-08-29.

## Base URL and endpoint used

```
https://api.crossref.org
```

| Endpoint | Used for |
|---|---|
| `/works/{doi}` | Single-record DOI lookup |
| `/works?query.bibliographic=...` | Candidate-match search from citation text |

## Access tiers (verified current)

Three access options exist; Phase A uses the first two only:

1. **Public** — no authentication or identification.
2. **Polite** — include contact email via `mailto` query parameter or in the `User-Agent` header.
   **Recommended and used by this connector** — configured from `CROSSREF_MAILTO` env var.
3. **Metadata Plus** — paid tier, API key via `Crossref-Plus-API-Token` header. **Not used in
   Phase A**, per the brief ("No paid Crossref API key is required for Phase A").

## Rate limits — verified current, explicitly NOT the stale figure

**Important correction applied per the brief's own instruction:** several developer guides and
older client libraries still document Crossref's rate limit as **50 requests/second**. This is
outdated. The actual current policy, per Crossref's own community-forum announcement (dated
2025-12-02, describing changes that took effect 2025-12-01):

| Pool | Rate limit (requests/second) | Concurrency limit |
|---|---|---|
| Public | 5 | 1 |
| Polite (via `mailto`) | 10 | 5 |

The connector's `rate_limit.py` is built against **these current numbers, not 50/sec.** The
concurrency limit (not just the rate limit) is also enforced — Crossref's announcement
specifically notes concurrency was newly limited alongside the per-second rate, and older client
code that only throttled requests/second without bounding concurrent in-flight requests would
under-throttle against the current policy.

## Single-record vs list/query requests

Per the brief's instruction to distinguish these: `crossref_lookup_doi()` (single-record,
`/works/{doi}`) and `crossref_search_bibliographic()` (list/query, `/works?query.bibliographic=`)
are implemented as separate functions with **independent rate-limit token buckets** in
`rate_limit.py`, since Crossref's documentation discusses the two request shapes distinctly (a
single-record DOI lookup is a much lighter operation than a filtered/paginated list query) even
though the currently-published numeric limits apply to the API as a whole rather than being
split by endpoint in the public documentation found this session. Treating them as separately
throttled internally is a conservative choice, not a documented requirement — flagged as such
rather than presented as a specific Crossref policy distinction that was independently confirmed.

## HTTP 429 / error handling

- **429 (Too Many Requests):** back off and retry, honoring a `Retry-After` header if present;
  otherwise exponential backoff starting at 1s, capped, bounded attempt count (see `retry.py`).
- **5xx (upstream error):** bounded exponential-backoff retry, distinct error code from 429
  (`UPSTREAM_ERROR` vs `RATE_LIMITED` — see `CONNECTOR_FAILURE_MODEL.md`), since these represent
  different failure conditions and should not be silently collapsed into one "it failed" state.
- Crossref's REST API documentation (per its GitHub-hosted `rest-api-doc`) also describes an
  `x-api-pool` response header indicating which pool served the request, and
  `X-Rate-Limit-Limit`/`X-Rate-Limit-Interval` headers when a limit is in effect — `client.py`
  reads these when present and logs them into the provenance record rather than only relying on
  the hard-coded table above, so the client adapts if Crossref advertises a different live limit
  than the currently-documented default.

## Functions implemented (`connectors/crossref/client.py`)

### `crossref_lookup_doi(doi)`
Calls `/works/{doi}`. Returns DOI, title, authors, container-title (journal/book), publication
date/year, publisher, type (e.g. `journal-article`) — each `null` if Crossref's record doesn't
include it, never guessed.

**Live-verified this session, via DOI resolution rather than the literal REST JSON endpoint** (see
`CONNECTOR_IMPLEMENTATION_DECISION.md`): DOI `10.1007/s00784-021-04289-6` was confirmed to resolve
to a real, live publisher record with title, authors (Smielak, Armata, Bojar), journal (*Clinical
Oral Investigations*), volume 26, pages 3049–3059, year 2022 — all matching what independent
citing sources report for the same DOI. This gives real confidence the DOI-lookup *concept* works
end-to-end for a real dental-evidence citation; it is not, however, confirmation that the literal
`api.crossref.org/works/{doi}` JSON response was obtained and parsed successfully this session —
that specific endpoint was not reachable via the available tools this session (see the
implementation-decision doc).

### `crossref_search_bibliographic(citation_text)`
Calls `/works?query.bibliographic=...`. Purpose: given a title/author/year string (e.g. extracted
from a PubMed record lacking a DOI, or from a user-supplied citation), find candidate DOI/metadata
matches. Returns a ranked list of candidates — **never auto-selects a single "best" match as
VERIFIED**; that judgment belongs to Phase 5's field-by-field comparison logic, not to this
function.

## Role in the architecture — metadata/citation verification, not primary evidence retrieval

Per Phase 10's explicit instruction: Crossref is **not** the primary evidence database. It has no
abstracts, no MeSH terms, no clinical-study metadata in the sense PubMed provides. Its role in
this system is exclusively **bibliographic metadata cross-check for citation verification**
(Phase 5's dual-source verification) and DOI-based full-text-link resolution where available.
`connector-capability-map.md` and the gateway file both label Crossref's v0.4 capability precisely
as "metadata/citation verification," not "full text" and not "literature search."

## Failure states surfaced

Same taxonomy as the PubMed connector (`SUCCESS`, `ZERO_RESULTS`, `RATE_LIMITED`, `TIMEOUT`,
`AUTH_ERROR`, `UPSTREAM_ERROR`, `PARSE_ERROR`, `IDENTIFIER_MISMATCH` — this last one specific to
Crossref's role in dual verification, raised when a Crossref record is retrieved but its title/
author/year/journal fields disagree with the PubMed record being checked against it, per Phase 5).

## What was NOT independently live-verified this session

The literal `api.crossref.org` JSON REST response (as opposed to DOI-resolution-via-publisher-page)
was not obtained — every direct attempt to fetch an `api.crossref.org` URL was blocked by
`web_fetch`'s prior-search-or-fetch-result restriction, and no search surfaced a literal
`api.crossref.org/works/...` URL as a clickable result this session. This is recorded plainly in
`CONNECTOR_IMPLEMENTATION_DECISION.md` and is why Crossref remains `NOT CONNECTED` in
`connector-capability-map.md` despite the genuine, real DOI-resolution evidence above.

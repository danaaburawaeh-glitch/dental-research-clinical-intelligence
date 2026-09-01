<!--
REFERENCE-ID: connector-capability-map
VERSION: 0.6.0
CANONICAL-OWNER: evidence-research (see /ARCHITECTURE_REFERENCE_MAP.md)
LAST-SYNCHRONIZED: 2026-08-31 (v0.6.0 Phase C)
This is a BUNDLED copy. Canonical owner: skills/evidence-research/references/connector-capability-map.md.
Re-synced from the canonical copy on 2026-08-30 for the v0.4.2 release.
v0.4 Phase A: ~~literature, ~~systematic-reviews, ~~journal-access now have BUILT implementations
(connectors/pubmed/, connectors/crossref/) — see the new "Implementation status" column. Built is
NOT the same as CONNECTED. Per Phase 19's own bar (implementation exists AND credentials
available AND a real API request succeeds AND response parsed successfully AND regression test
passes), and per CONNECTOR_IMPLEMENTATION_DECISION.md's honest account of what could and could
not be live-verified in this build environment, all seven placeholders remain NOT CONNECTED.
v0.4.1: Connector Reliability & Retraction Safety Patch — fixed retry-wiring, error-handling,
and rate-limiter defects (see CONNECTOR_RELIABILITY_AUDIT.md), added retraction/correction
metadata. Real subprocess-level integration testing (mocked network, actual client entry points)
now achieved — see the updated Implementation Ledger below. Status remains NOT CONNECTED for all
seven; bar 3 (a real request from this exact code against the live network) is still unmet, per
the same honest environment-limitation reasoning as v0.4.
v0.4.2: Retraction Semantics & Evidence Safety Patch — fixed two real directionality bugs in the
PubMed and Crossref retraction/correction parsers (a retraction NOTICE was being misclassified
as a retracted ARTICLE — see RETRACTION_DIRECTIONALITY_AUDIT.md), removed an unverified Crossref
`relation`-field assumption, and added an executable retraction gate
(connectors/shared/retraction_gate.py). None of this changes connector CONNECTED status — still
NOT CONNECTED for all seven, unchanged reasoning.
v1.1.0 (2026-09-01): Remote MCP integration. The Dental AI Research Remote MCP server
(https://dental-ai-research-mcp.onrender.com/mcp) is now declared in the plugin's .mcp.json and
provides a SECOND TRANSPORT to four already-CONNECTED sources. This changes NO status in the table
below: status is a property of the source, not of the transport used to reach it, and every source
listed CONNECTED was already CONNECTED in v1.0.2 over the plugin-local CLIs. Transport selection,
the T1/T2 behavioural differences, and the retraction-gate consequence are governed by
skills/evidence-research/references/retrieval-transports.md.
-->

# Connector Capability Map

This file separates three things now, not two: (A) documentation describing what a connector
*would* do, (B) an actual built implementation that has not been live-executed, and (C) an
actual, wired, live-tested, callable connector. Only (C) is ever marked `CONNECTED`. `start` and
`evidence-research` must check actual tool availability in the running environment before
treating any of the below as usable — never infer availability from this file's existence, nor
from the presence of implementation code, alone.

## Architecture note (v0.3, unchanged in v0.4)

These seven placeholders are **source-specific capability layers**, invoked through the
**Clinical Evidence Safe Search gateway** — see clinical-evidence-safe-search-gateway.md. This
map's status column is the single source of truth for whether a placeholder is actually
connected; the gateway file never overrides it.

| Placeholder | Purpose | Implementation status (v0.4 Phase A) | Current status |
|---|---|---|---|
| `~~clinical-guidelines` | Current recognised clinical guidelines (L1) | Not built — no aggregating API identified in Phase 17 research | **NOT CONNECTED** |
| `~~systematic-reviews` | Systematic review / meta-analysis databases (L2) | **Built and live-validated**: `connectors/pubmed/client.py search-systematic-reviews`, filtered on PubMed's own structured `PublicationType` field only (never title text). v0.4.5 fixed the filter to `("Systematic Review"[Publication Type] OR "Meta-Analysis"[Publication Type])` — it previously omitted Meta-Analysis, silently dropping meta-analyses not also tagged Systematic Review. | **CONNECTED — PubMed filtered retrieval.** Bar 3 met 2026-08-31 (see Live Validation Record). Do not imply PubMed's systematic-review filter is equivalent to, or a substitute for, Cochrane coverage — Cochrane/CENTRAL remains completely unwired. |
| `~~literature` | General biomedical/dental literature search (L2-L4) | **Built and live-validated**: `connectors/pubmed/client.py search` / `fetch`, `connectors/pubmed/{parser,models,rate_limit,errors}.py`. | **CONNECTED — PubMed/NCBI.** Bar 3 met 2026-08-30 (see Live Validation Record). Runs unauthenticated (3 req/s) unless `NCBI_API_KEY` is set. |
| `~~clinical-trials` | Trial registries | **Built and live-validated (v0.5.0 Phase B)**: `connectors/clinical_trials/client.py search` / `fetch` against ClinicalTrials.gov API v2 (deprecated classic API not used). Registry data only — never published evidence. | **CONNECTED — ClinicalTrials.gov API v2.** Bar 3 met 2026-08-31 (see Live Validation Record). A registry record is NOT evidence an intervention works — see registry-vs-published-evidence.md and the routing rules in clinical-evidence-safe-search-gateway.md. |
| `~~journal-access` | Metadata / citation verification (re-scoped, v0.4) | **Built and live-validated**: `connectors/crossref/client.py lookup-doi` / `search-bibliographic`, `connectors/crossref/{parser,models,rate_limit,errors}.py`. | **CONNECTED — METADATA/CITATION VERIFICATION via Crossref.** Bar 3 met 2026-08-30 (see Live Validation Record). Never describe as "CONNECTED — FULL TEXT" — Crossref does not provide full text. See `connectors/crossref/models.py`. |
| `~~manufacturer-ifu` | Manufacturer instructions-for-use documents (IFU) | Not touched in Phase A | **NOT CONNECTED** |
| `~~regulatory-saudi` | SFDA Saudi regulatory status lookup (REG) | **Built (v0.6.0 Phase C)**: `connectors/sfda/client.py` — OAuth client-credentials + registered medical-device / drug product lookup, against the real developer.sfda.gov.sa API programme. Gateway host and paths are environment configuration, never hard-coded, because SFDA discloses them only to registered applications. | **NOT CONNECTED — AUTH REQUIRED.** SFDA requires a registered application; no credentials are configured in this environment, so bar 3 (a real request succeeding) is unmet. Every unavailable outcome maps to REQUIRES VERIFICATION — never to "not approved". See SFDA_CONNECTOR_VALIDATION.md and saudi-regulatory-gate.md. |

## Transport note (v1.1.0)

Every CONNECTED source below is now reachable over **two transports**:

- **T1 — Remote MCP:** server `dental-ai-research` (`.mcp.json`). Claude Code registers it as
  `plugin:dana-dental-research:dental-ai-research`, so the runtime tools are
  `mcp__plugin_dana-dental-research_dental-ai-research__search_pubmed`,
  `…__search_systematic_reviews`, `…__verify_citation`, `…__search_clinical_trials`.
  **Identify them by suffix, not by a hard-coded prefix** — see retrieval-transports.md.
- **T2 — Plugin-local Python CLIs** invoked via the Bash tool (`connectors/*/client.py`).

Prefer T1 when it is available; fall back to T2; use T2 for everything T1 does not expose
(record fetch, trial fetch, the executable retraction gate, dedup, linkage, SFDA). T1 and T2 hit
the same upstream APIs, so agreement between them is **not** independent corroboration. Full rule:
`retrieval-transports.md`. A transport being unavailable is a retrieval failure, never a status
downgrade — see the Runtime availability rule below.

## Implementation Ledger — precisely what "Built" means and doesn't mean

For `~~literature`, `~~systematic-reviews`, and `~~journal-access`, per Phase 19's five-point bar:

| Bar (Phase 19) | `~~literature` / `~~systematic-reviews` (PubMed) | `~~journal-access` (Crossref) |
|---|---|---|
| 1. Implementation exists | YES, and (v0.4.1) confirmed to actually run as a real subprocess entry point (`python3 pubmed/client.py --help` succeeds) — this specifically caught and fixed a relative-import bug that would have crashed every real invocation in v0.4. | YES, same subprocess confirmation. |
| 2. Credentials/config available if required | N/A — neither requires credentials to function (both work at a lower rate limit without a key/mailto) | N/A |
| 3. A real API request succeeds | **PARTIAL, improved in v0.4.1.** The target API was confirmed live via `web_fetch` in v0.4. In v0.4.1, the actual client code's request path (retry-wrapped `_http_get`) was exercised against a **mocked** network layer (`urllib.request.urlopen` monkeypatched) and confirmed to make the correct real function calls, retry correctly, and handle failures cleanly — this proves the code's *logic* is correct end-to-end, but a mock is still not a live network response. Bash sandbox still has no network access this session. | **PARTIAL, improved in v0.4.1.** Same reasoning — `crossref_lookup_doi`'s actual request path was exercised against a mocked network layer and confirmed correct. The literal `api.crossref.org` REST endpoint was still not reached by any tool this session. |
| 4. Response parsed successfully | **YES, against real data** (unchanged from v0.4) — parser tested against live-captured ESearch XML. v0.4.1 additionally tests the parser against schema-correct retraction/correction XML. | **YES, against realistic data** (unchanged from v0.4), plus v0.4.1 retraction/correction JSON. |
| 5. Regression test passes | v0.4: `connector-hallucination-safety-tests.md`. v0.4.1: `v0.4.1-reliability-regression-tests.md` — 15/15 scenarios genuinely executed (not reviewed-only), including real subprocess-level retry, error-handling, and rate-limiter-spacing tests. | Same. |

**Conclusion: bar not fully met for either connector — both remain `NOT CONNECTED`.** v0.4.1
meaningfully strengthens bars 1, 3 (partially), and 5 compared to v0.4 — the client code is now
proven correct against a realistic mocked network, not just against isolated unit tests of its
sub-components — but bar 3's core requirement (a real request against the actual live network)
remains unmet for the same, unchanged reason: this build environment's code-execution tool has
no network access. Everything else is either satisfied or satisfied via the closest verifiable
proxy available in this
environment, documented rather than glossed over.

## Live Validation Record — bar 3 satisfied (v0.4.5, macOS)

This section exists because the "When a placeholder becomes connected" rule below requires the date
and method of the live test to be recorded in the same change that flips a status.

**Environment:** macOS (Darwin 24.6.0), operator's own machine — NOT the original build sandbox. The
network restriction documented in LIVE_CONNECTIVITY_TESTS.md was an artefact of that sandbox and does
not apply here.

**Method:** the packaged client code itself was executed as a real subprocess. No `web_fetch`, no
browser tool, no mock, no simulated response.

| Date | Command | Result |
|---|---|---|
| 2026-08-30 | `pubmed/client.py search --query "porcelain veneers survival systematic review"` | `SUCCESS`, count 37, 10 real PMIDs. NCBI-side `query_translation` returned — proof of a real server round-trip. |
| 2026-08-30 | `pubmed/client.py fetch --pmids 42607000` | `SUCCESS`. DOI `10.5005/jp-journals-10024-3981`, publication types `['Journal Article','Systematic Review']`, `is_retracted: false`. |
| 2026-08-30 | `crossref/client.py lookup-doi --doi 10.5005/jp-journals-10024-3981` | `SUCCESS`. Live `api.crossref.org` record returned and parsed. |
| 2026-08-30 | `shared/citation_verifier.py` (PubMed x Crossref) | `VERIFIED` — title/authors/journal/year/doi all agree. |
| 2026-08-30 | `shared/retraction_gate.py` | Record routed to `included`; `excluded` and `flagged` empty. |
| 2026-08-31 | `pubmed/client.py search-systematic-reviews --query "porcelain veneers survival"` (post-fix) | `SUCCESS`, count 36 (was 34 pre-fix). Filter confirmed in NCBI's own `query_translation`. |

**What the v0.4.5 filter fix recovered.** Fetching all 36 hits identified two records tagged
`Meta-Analysis` WITHOUT `Systematic Review` — unreachable by the pre-fix filter: PMID 30677113
(`['Journal Article','Meta-Analysis','Review']`) and PMID 9611940 (`['Journal Article','Meta-Analysis']`).

**Credentials at validation time:** `NCBI_API_KEY`, `NCBI_EMAIL` and `CROSSREF_MAILTO` were all unset.
Both connectors therefore ran unauthenticated/non-polite. This did not cause failure at this volume,
but bar 2 is satisfied only in the "no credentials required to function" sense.

**Scope limit.** These three placeholders are CONNECTED. `~~clinical-guidelines`, `~~clinical-trials`,
`~~manufacturer-ifu` and `~~regulatory-saudi` remain **NOT CONNECTED** — no implementation exists for
any of them, and nothing in v0.4.5 changes that. ClinicalTrials.gov is explicitly still deferred.

## SOURCE-UPDATE-CONFLICT — SFDA regulatory database claim (unchanged from v0.3.1)

CORE and the authoritative M3 both currently state or imply that SFDA has no public queryable
database. Phase 17 research found SFDA now publishes an OAuth-secured open-data API. Recorded
here as `SOURCE-UPDATE-CONFLICT`, for review during M4 (still out of scope). `~~regulatory-saudi`
remains `NOT CONNECTED`; do not assert "no Saudi regulatory database exists" as settled fact.

### Phase B addendum — `~~clinical-trials` live validation (v0.5.0, 2026-08-31)

Same method as above: the packaged client executed as a real subprocess on Claude Code / macOS
against `https://clinicaltrials.gov/api/v2` (service-reported `apiVersion` 2.0.5). No web search,
no browser tool, no mock.

| Test | Command | Result |
|---|---|---|
| 1. Search | `clinical_trials/client.py search --condition "dental implants" --max-results 5` | `SUCCESS`, totalCount 1350, 5 real NCT IDs |
| 2. Fetch | `fetch --nct-id NCT00226148` | `SUCCESS`. COMPLETED, INTERVENTIONAL, EARLY_PHASE1, enrolment 92 ACTUAL, sponsor University of Aarhus, eligibility parsed |
| 3. Status filter | `search --condition "dental caries" --status RECRUITING` | `SUCCESS`, all 5 returned records `RECRUITING` |
| 4. Zero result | `search --condition "zzqxdental unobtainium periodontal flurbotron"` | `ZERO_RESULTS` with the explicit "not proof no trials exist" meaning |
| 5. Results-aware | `fetch --nct-id NCT00607022` | `has_results: true`, class B, results posted 2018-07-27, 1 outcome measure, adverse-event data present |
| 6. Linkage | `fetch --nct-id NCT00782171` → PubMed → Crossref | 3 `RESULT` PMIDs; PMID 18416725 fetched via the existing PubMed connector; `TRIAL ↔ PUBLICATION LINK VERIFIED`; Crossref `SUCCESS`; citation verifier `VERIFIED`; dedup 2 records → 1 independent study |

Regression suite: `connectors/clinical_trials/tests/test_clinical_trials.py` — **50/50 assertions
pass** covering all 20 required scenarios (network mocked for determinism).

**Scope limit.** `~~clinical-trials` is CONNECTED for REGISTRY RETRIEVAL. It is not a source of
published evidence and must never be used as one. `~~clinical-guidelines`, `~~manufacturer-ifu`
and `~~regulatory-saudi` remain NOT CONNECTED — no implementation exists for any of them, and
M4/SFDA is not started.

### Phase C addendum — `~~regulatory-saudi` (v0.6.0, 2026-08-31)

**Status: NOT CONNECTED — AUTH REQUIRED.** This is an honest negative, not a failure of the phase.

What was verified live: the SFDA developer portal (`developer.sfda.gov.sa`, HTTP 200) is real and
publishes five API products — Registered Medical Device, Registered Drug, Registered Food,
Registered Cosmetic, and OAuth. The medical-device service documents keyword search and product
listing, `application/json`, Bearer-token security, data source "Ghad System". The OAuth service
documents a client-credentials grant (consumer key as username, consumer secret as password) with
tokens expiring within 24 hours.

What could NOT be verified: the API gateway hostname and concrete request paths, which SFDA
discloses only to a registered application (public docs use `api.example.com.sa` placeholders).
The connector therefore takes every URL from environment configuration and **invents no endpoint**.
With no configuration it performs no request and reports `NOT_CONNECTED_AUTH_REQUIRED`.

The Saudi open-data portal (`open.data.gov.sa`) was also probed as a possible unauthenticated
route; its WAF rejects programmatic requests, so no credential-free live path exists.

**To connect:** register an app at developer.sfda.gov.sa, then set `SFDA_CLIENT_ID`,
`SFDA_CLIENT_SECRET`, `SFDA_TOKEN_URL`, `SFDA_API_BASE_URL` and the service path variable. Status
becomes `CONNECTED — SFDA` only after a real request succeeds, a real record parses, and provenance
is preserved.

**The other four Saudi bodies have no connector at all.** SCFHS, MOH, SDAIA/PDPL and CST claims are
`REQUIRES VERIFICATION` by default, routed to the named body — see
`saudi-regulatory-source-priority.md`.

### v1.1.0 addendum — Remote MCP transport live validation (2026-09-01)

**Method:** direct JSON-RPC calls to `https://dental-ai-research-mcp.onrender.com/mcp` over
streamable HTTP from the operator's machine. No mock, no browser tool, no simulated response.

| Test | Call | Result |
|---|---|---|
| 1. Handshake | `initialize` | HTTP 200, protocol `2025-06-18`, serverInfo `dental-ai-research` v1.0.0, no authentication required |
| 2. Tool discovery | `tools/list` | 4 tools: `search_pubmed`, `search_systematic_reviews`, `verify_citation`, `search_clinical_trials` |
| 3. Literature | `search_pubmed{query:"porcelain veneers survival", max_results:2}` | `ok:true`, `SUCCESS`, `total_matched` 431, real PMIDs with DOI + abstract (e.g. PMID 42629625, DOI 10.1111/clr.70160) |
| 4. Systematic reviews | `search_systematic_reviews{query:"porcelain veneers survival"}` | `ok:true`, `SUCCESS`, `total_matched` 36 — matches the T2 post-fix count of 36 recorded above |
| 5. Citation verification | `verify_citation{doi:"10.5005/jp-journals-10024-3981"}` | `NOT_VERIFIED` — Crossref and PubMed both returned the record but disagree on year (`metadata_match.year:false`); both sources named in `source_provenance`. Correct behaviour under citation-verification.md: the disagreement is surfaced, not silently repaired |
| 6. Trial registry | `search_clinical_trials{query:"dental implants", max_results:2}` | `ok:true`, `SUCCESS`, `total_matched` 1351 (T2 recorded 1350 on 2026-08-31), real NCT IDs, `evidence_caveat` present |
| 7. Nonsense query | `search_pubmed{query:"zzqxdental unobtainium periodontal flurbotron"}` | `SUCCESS`, `total_matched` 149,830 — **T1 does not phrase-quote**, where T2 returned `ZERO_RESULTS`. A non-zero T1 count is not evidence of a relevant match; see retrieval-transports.md difference 1 |
| 8. Bad argument | `search_clinical_trials{condition:…}` | JSON-RPC error −32602, unexpected keyword — schema uses `query`, not `condition`. Server validates rather than guessing |

**What this validation does and does not establish.** It establishes that T1 is live, unauthenticated,
schema-correct, and returns real upstream identifiers. It does **not** add a source, does not change
any status, and does **not** supply retraction/correction metadata — T1 records carry no
`is_retracted` / `record_role`, so the mandatory retraction gate still runs over T2.

## Runtime availability rule (v0.4.5.1)

`CONNECTED` in this file means bar 3 has been satisfied — the packaged code made a real request
successfully in a real environment. It does **not** guarantee connectivity in every environment,
and it never licenses assuming a request will succeed.

- Network availability is a **runtime** property. Invoke the connector and read the `status` field
  it returns; the clients never raise and never fabricate.
- Some sandboxes block outbound hosts (the original v0.4 build environment returned `HTTP 403`
  `x-deny-reason: host_not_allowed`). That is a property of the environment, not of the connector.
- Never state "no network access" as a universal fact, and never state the opposite either.
- A connectivity failure in a `CONNECTED` connector is reported as a retrieval failure
  (`TIMEOUT` / `UPSTREAM_ERROR`) — it must **not** be silently downgraded to `NOT CONNECTED`
  behaviour, and must never be answered from memory. The `NOT CONNECTED` required-behaviour rules
  below (no simulated retrieval, `(UNVER)` marking, provide a runnable search strategy instead)
  apply to a failed live attempt as well.

## Status rule

A placeholder's status must read exactly `NOT CONNECTED` in this file unless a real, callable tool
is actually installed, reachable, AND live-tested successfully in the current environment — never
mark `CONNECTED` speculatively, because a future version is expected to have it, because
documentation confirms the target API is live, or because an implementation has been built and
unit-tested against real or realistic data. All of those are necessary groundwork; none of them
individually or together substitute for bar 3 above (a real request from the actual client code
succeeding in the running environment).

## Required behaviour while a placeholder is `NOT CONNECTED`

- Do not simulate retrieval through that placeholder.
- Do not present remembered/training-derived content as if it were retrieved this session.
- Mark any recalled item `(UNVER)` per `citation-verification.md`.
- Provide a ready, runnable search strategy (database, terms, filters) instead of fabricated
  results.
- For `~~regulatory-saudi` specifically: state "Regulatory verification required" per
  `saudi-regulatory-claim-gate.md` (quality-control) — never assert the specific legal/regulatory
  provision as settled, and never assert that no Saudi regulatory database exists.

## When a placeholder becomes connected

Update this row's status to `CONNECTED`, name the actual tool/connector, record the date and
method of the live test that satisfied bar 3 above, and update `LAST-SYNCHRONIZED` on both bundled
copies (`skills/start/references/` and `skills/evidence-research/references/`) in the same change.
An implementation being built, documented, and unit-tested — as `~~literature`,
`~~systematic-reviews`, and `~~journal-access` now are — is necessary but explicitly insufficient
for `CONNECTED` status on its own.

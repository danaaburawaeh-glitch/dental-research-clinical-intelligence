<!--
REFERENCE-ID: retrieval-transports
VERSION: 1.1.0
CANONICAL-OWNER: evidence-research (see /ARCHITECTURE_REFERENCE_MAP.md)
LAST-SYNCHRONIZED: 2026-09-01 (v1.1.0 — Remote MCP integration)
New in v1.1.0. Before this release there was exactly one retrieval transport (plugin-local Python
CLIs invoked via the Bash tool). There are now two, and this file is the single source of truth for
which one is used when. It does NOT change any connector's CONNECTED status — status is owned by
connector-capability-map.md and is a property of the SOURCE, not of the transport that reaches it.
-->

# Retrieval Transports

A *source* (`~~literature`, `~~journal-access`, …) is what evidence comes from. A *transport* is
how this plugin reaches it. As of v1.1.0 the same four connected sources are reachable over two
transports, and the distinction must never be collapsed:

| Transport | What it is | Availability |
|---|---|---|
| **T1 — Remote MCP** | The hosted **Dental AI Research Remote MCP** server, `https://dental-ai-research-mcp.onrender.com/mcp` (streamable HTTP, no authentication), declared in the plugin's `.mcp.json` as server `dental-ai-research`. Exposes four tools: `search_pubmed`, `search_systematic_reviews`, `verify_citation`, `search_clinical_trials`. | Present as MCP tools when the plugin's MCP server is enabled and reachable. **Runtime tool names are `mcp__plugin_dana-dental-research_dental-ai-research__<tool>`** — Claude Code registers a plugin-provided server as `plugin:<plugin-name>:<server-name>` and derives the tool prefix from that, so the bare server name alone is *not* the prefix. Match on the tool suffix (`__search_pubmed`, `__search_systematic_reviews`, `__verify_citation`, `__search_clinical_trials`), never on a hard-coded prefix. |
| **T2 — Plugin-local CLIs** | `connectors/pubmed/client.py`, `connectors/crossref/client.py`, `connectors/clinical_trials/client.py` and `connectors/shared/*.py`, invoked via the Bash tool. | Present whenever the plugin files are installed and `python3` is available. |

## Transport selection rule

1. **Check which transports actually exist in the running environment.** Never assume. T1 exists
   only if the four dental research MCP tools are listed — their names end in `__search_pubmed`,
   `__search_systematic_reviews`, `__verify_citation`, `__search_clinical_trials`, normally
   prefixed `mcp__plugin_dana-dental-research_dental-ai-research__`. **Check by suffix.** A prefix
   that does not match the expected string is not evidence the transport is missing; the absence of
   all four tool suffixes is. T2 exists only if the connector files are present.
2. **Prefer T1** for `search_pubmed` / `search_systematic_reviews` / `verify_citation` /
   `search_clinical_trials`-shaped retrieval when it is available. It requires no local Python, no
   path resolution, and no local API-key configuration.
3. **Fall back to T2** when T1 is absent or returns a transport-level failure. T2 remains fully
   supported and is **not** deprecated.
4. **T2 is required — T1 cannot substitute — for anything the remote tools do not expose:**
   - `connectors/pubmed/client.py fetch` (full record fetch by PMID, including
     `<DataBankList>` NCT linkage)
   - `connectors/clinical_trials/client.py fetch` (single-trial detail, results-posted data,
     eligibility, sponsor)
   - `connectors/shared/retraction_gate.py` (the executable retraction/correction gate — **step 5
     of the evidence-research workflow, which is mandatory and has no remote equivalent**)
   - `connectors/shared/deduplication.py`, `trial_publication_linkage.py`,
     `citation_verifier.py` (structured `EvidenceRecord` pipeline stages)
   - `connectors/sfda/client.py`
5. **Never run both transports for the same query to manufacture a second source.** T1 and T2 reach
   the *same* upstream APIs (NCBI E-utilities, Crossref REST, ClinicalTrials.gov API v2). Two
   agreeing results from two transports are **one** retrieval, not independent corroboration.
6. **A transport failure is a retrieval failure**, reported per `docs/CONNECTOR_FAILURE_MODEL.md`
   (`TIMEOUT` / `UPSTREAM_ERROR`). It is never a downgrade to `NOT CONNECTED`, never "no evidence
   found", and never grounds for answering from memory. If T1 fails, try T2 before reporting.

## Reading a T1 (remote MCP) response

Each tool returns a JSON text block. Contract, verified live 2026-09-01:

- `ok: true` + `status: "SUCCESS"` — records retrieved.
- `ok: false` — **a retrieval failure, not a finding of "no evidence."** The server's own
  instructions state this explicitly. Route it through `absence-of-evidence.md`.
- `verify_citation` returns `verification_status` of `VERIFIED` / `PARTIALLY_VERIFIED` /
  `NOT_VERIFIED`, plus `metadata_match` (per-field booleans) and `source_provenance` naming which
  of Crossref/PubMed were actually consulted. This maps directly onto `citation-verification.md`'s
  three-state standard, including its rule that a PubMed↔Crossref field disagreement is reported,
  never silently repaired — the remote server returns `NOT_VERIFIED` with the disagreeing fields
  named, which is the correct behaviour, not an error.
- `search_clinical_trials` returns an `evidence_caveat` field. It is not decoration: a registry
  record is not evidence an intervention works. Carry it per
  `quality-control`'s `registry-vs-published-evidence.md`.

## Known behavioural differences between T1 and T2

These are real, verified differences. Do not paper over them.

1. **Query handling — T1 does not phrase-quote.** A nonsense multi-word query
   (`"zzqxdental unobtainium periodontal flurbotron"`) returns `ZERO_RESULTS` from T2 but
   `SUCCESS` with ~149,830 loosely-matched records from T1, because the terms are OR-expanded by
   PubMed rather than searched as a phrase. **Consequence: a non-zero T1 count is not evidence
   that the query matched anything relevant.** Inspect the returned titles before reporting a
   count, and never quote a T1 `total_matched` as a measure of evidence volume on a specific
   question without doing so.
2. **T1 returns no `query_translation`.** T2's PubMed client surfaces NCBI's own query translation;
   T1 does not, so the executed strategy is less auditable. When the exact executed query must be
   logged (`templates/search-log-template.md`), prefer T2.
3. **T1 records are not `EvidenceRecord` objects.** They do not carry `is_retracted`,
   `is_corrected`, `record_role` or `related_notices`. **T1 results therefore cannot enter workflow
   step 5's retraction gate directly** — see the gate rule below.
4. **T1 has no credential configuration.** `NCBI_API_KEY`, `NCBI_EMAIL` and `CROSSREF_MAILTO` apply
   to T2 only; the remote server's own rate limits and politeness settings are outside this
   plugin's control.
5. **T1 is a third-party-hosted service** on a platform that idles inactive instances, so a first
   call after idle may be slow or time out. Retry once, then fall back to T2.

## Retraction-gate rule (hard)

Workflow step 5 (`connectors/shared/retraction_gate.py`) is **mandatory and unchanged**. Because T1
returns no retraction/correction metadata (difference 3 above):

- A record retrieved over T1 that will back a clinical claim must have its retraction status
  established before synthesis — re-fetch it over T2 (`pubmed/client.py fetch --pmids …`) and run
  the gate.
- If T2 is unavailable, the record is disclosed as **retraction-status unchecked** and cannot be
  presented as a gated, synthesis-eligible source. It is never silently treated as `included`.
- T1 convenience never buys an exemption from the gate. This is the one place where preferring T1
  costs something, and the cost is paid explicitly, not hidden.

## Sources that no transport reaches

Cochrane/CENTRAL, Embase and Scopus are `NOT IMPLEMENTED` on both transports. The remote server's
own instructions say so. `search_systematic_reviews` is PubMed's structured Publication Type filter
only and must never be presented as a Cochrane search.

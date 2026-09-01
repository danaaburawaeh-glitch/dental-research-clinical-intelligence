# Changelog — v1.0.2 → v1.1.0

**Release:** Remote MCP integration
**Date:** 2026-09-01

## Summary

The already-live **Dental AI Research Remote MCP** server is now integrated into the plugin as a
second retrieval transport. No source was added, no connector status changed, and no governance
rule was relaxed.

## What changed

### 1. The MCP server is declared (`.mcp.json`)

```json
{
  "mcpServers": {
    "dental-ai-research": {
      "type": "http",
      "url": "https://dental-ai-research-mcp.onrender.com/mcp"
    }
  }
}
```

Previously `{"mcpServers": {}}`. Streamable HTTP, no authentication. Four tools:
`search_pubmed`, `search_systematic_reviews`, `verify_citation`, `search_clinical_trials`.

### 2. New canonical reference — `retrieval-transports.md`

`skills/evidence-research/references/retrieval-transports.md` is the single source of truth for
which transport reaches which source:

- **T1 — Remote MCP**, preferred when the environment exposes it. Runtime tool names are
  `mcp__plugin_dana-dental-research_dental-ai-research__<tool>` (Claude Code derives the prefix
  from the server id `plugin:<plugin>:<server>`); the skills match them **by suffix**, never by a
  hard-coded prefix.
- **T2 — Plugin-local Python CLIs** (`connectors/*/client.py` via the Bash tool), the fallback,
  **not deprecated**, and still **required** for record fetch, trial fetch, the executable
  retraction gate, deduplication, trial↔publication linkage and SFDA.

### 3. Source status vs transport availability — now explicitly separated

`CONNECTED` describes a **source**. A transport being absent or failing is a **retrieval failure**
(`TIMEOUT`/`UPSTREAM_ERROR`), never a `CONNECTED` → `NOT CONNECTED` downgrade, and never grounds
for answering from memory. Recorded in both copies of `connector-capability-map.md` and in
`start`'s capability-check step.

### 4. Three hard rules carried into the skills

- **No double-counting.** T1 and T2 reach the same upstream APIs (NCBI, Crossref,
  ClinicalTrials.gov). Two agreeing results are **one** retrieval, never independent corroboration.
- **The retraction gate is not waived.** T1 records carry no `is_retracted` / `is_corrected` /
  `record_role` / `related_notices`. A T1 record backing a clinical claim is re-fetched over T2 for
  workflow step 5, or is carried forward explicitly marked **retraction-status unchecked** and may
  not be presented as a gated, synthesis-eligible source.
- **A T1 count is not evidence volume.** T1's `search_pubmed` does not phrase-quote; a nonsense
  four-word query returned 149,830 OR-expanded matches where the local connector returned
  `ZERO_RESULTS`. Records are inspected before any count is reported.

### 5. Live validation (2026-09-01)

All four tools called directly over JSON-RPC — no mock, no browser tool. Handshake, tool discovery,
literature search, systematic-review search, citation verification, trial search, a nonsense-query
probe and an invalid-argument probe. Full table in `connector-capability-map.md`, section
"v1.1.0 addendum — Remote MCP transport live validation".

Notable: `verify_citation` on DOI `10.5005/jp-journals-10024-3981` returned `NOT_VERIFIED` because
Crossref and PubMed disagree on publication year. That is the **correct** behaviour under
`citation-verification.md` — the disagreement is surfaced with the field named, not silently
repaired.

### 6. Files touched

| File | Change |
|---|---|
| `.mcp.json` | remote MCP server declared |
| `.claude-plugin/plugin.json` | version 1.1.0, description names both transports, `mcp` keyword |
| `../../.claude-plugin/marketplace.json` | version 1.1.0, description and tags |
| `skills/evidence-research/references/retrieval-transports.md` | **new** — canonical transport rules |
| `skills/evidence-research/references/connector-capability-map.md` | transport note + live validation addendum |
| `skills/start/references/connector-capability-map.md` | re-synced identically |
| `skills/evidence-research/SKILL.md` | transport selection in step 3; MCP record shape in step 4; MCP `verify_citation` mapping in step 6 |
| `skills/evidence-research/references/clinical-evidence-safe-search-gateway.md` | transport decision at gateway steps 5–7 |
| `skills/start/SKILL.md` | capability check updated — the `.mcp.json`-is-empty statement is now marked historical |
| `README.md` | retrieval-transports section, version 1.1.0 |
| `clinical/tests/test_docs_consistency.py` | version assertion → 1.1.0; **11 new checks (35–45)** covering the MCP integration, including the runtime tool-naming rule |

## What did NOT change

- No connector status. `~~clinical-guidelines`, `~~manufacturer-ifu` remain `NOT CONNECTED`;
  `~~regulatory-saudi` remains `NOT CONNECTED — AUTH REQUIRED`.
- Cochrane/CENTRAL, Embase and Scopus remain `NOT IMPLEMENTED` on **both** transports.
  `search_systematic_reviews` is PubMed's structured Publication Type filter only and must never be
  presented as a Cochrane search.
- The evidence-research workflow's step order, the retraction gate, the citation-verification
  standard, the numeric gate, the safety veto and the author-identity policy are all unchanged.

## Verification

All seven suites pass: **341/341** (was 330/330; +11 MCP-integration checks).

```
clinical/tests/test_clinical_layer.py          60/60
clinical/tests/test_clinical_completion.py     66/66
clinical/tests/test_protocol_approval.py       24/24
clinical/tests/test_identity_policy.py         46/46
clinical/tests/test_docs_consistency.py        45/45
connectors/clinical_trials/tests/…             50/50
connectors/sfda/tests/…                        50/50
```

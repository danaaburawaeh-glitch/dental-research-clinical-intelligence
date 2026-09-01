# Release Notes — v1.1.0

**Dental Research & Clinical Intelligence by Dr. Dana**
Plugin identifier `dana-dental-research` · Designed by Dr. Dana Abu Rawaeh

A **minor release** of v1.0.2. Integrates the live **Dental AI Research Remote MCP** server as a
second retrieval transport. No new evidence source, no connector status change, no relaxation of
any clinical or governance rule.

## What changed

**The remote MCP server is now declared.** `plugin/dana-dental-research/.mcp.json` — empty in every
prior release — now declares:

```json
{ "mcpServers": { "dental-ai-research": {
    "type": "http",
    "url": "https://dental-ai-research-mcp.onrender.com/mcp" } } }
```

Streamable HTTP, no authentication, four tools: `search_pubmed`, `search_systematic_reviews`,
`verify_citation`, `search_clinical_trials`.

**Source and transport are now separate concepts.** `CONNECTED` describes a *source*
(`~~literature`, `~~journal-access`, …). It is now reachable two ways:

| Transport | Covers |
|---|---|
| **Remote MCP** — tools ending `__search_pubmed`, `__search_systematic_reviews`, `__verify_citation`, `__search_clinical_trials` (runtime prefix `mcp__plugin_dana-dental-research_dental-ai-research__`) | `~~literature`, `~~systematic-reviews`, `~~journal-access`, `~~clinical-trials` |
| **Plugin-local Python CLIs** — `connectors/*/client.py` via Bash | the same four, **plus** record fetch, trial fetch, the executable retraction gate, deduplication, trial↔publication linkage, SFDA |

The remote transport is preferred when the environment exposes it; the local connectors are the
fallback and are **not** deprecated. A missing or failing transport is a *retrieval failure*, never
a `CONNECTED` → `NOT CONNECTED` downgrade, and never a licence to answer from memory.

**Three safety rules were written into the skills, not assumed.**

1. **No double-counting.** Both transports call the same upstream APIs, so agreement between them
   is one retrieval, never independent corroboration.
2. **The retraction gate is not waived.** Remote-MCP records carry no retraction/correction
   metadata, so a record backing a clinical claim is re-fetched locally for the gate, or is carried
   forward explicitly marked **retraction-status unchecked** and may not be presented as a gated,
   synthesis-eligible source.
3. **A remote result count is not evidence volume.** The remote `search_pubmed` does not
   phrase-quote; a nonsense four-word query returned 149,830 OR-expanded matches where the local
   connector returned `ZERO_RESULTS`. Records are inspected before a count is reported.

**New canonical reference.** `skills/evidence-research/references/retrieval-transports.md` owns the
transport rules. `evidence-research` loads it; `start`, the safe-search gateway and both copies of
the connector capability map point to it.

## Live validation — 2026-09-01

All four tools were called directly over JSON-RPC from the operator's machine. No mock, no browser
tool, no simulated response: handshake (`initialize`, protocol `2025-06-18`), tool discovery,
literature search (431 matches, real PMIDs and DOIs), systematic-review search (36 matches — same
count the local connector records), trial search (1,351 matches, real NCT IDs, evidence caveat
present), citation verification, a nonsense-query probe, and an invalid-argument probe. Full table
in the connector capability map.

`verify_citation` on DOI `10.5005/jp-journals-10024-3981` returned `NOT_VERIFIED` because Crossref
and PubMed disagree on publication year. That is the correct behaviour: the disagreement is
surfaced with the field named, not silently repaired.


## Installation validation (2026-09-01)

Validated by a **fresh isolated install** into a throwaway `CLAUDE_CONFIG_DIR`, so no existing
installation was touched:

- `claude plugin install dana-dental-research@dana-dental` → installed, v1.1.0, enabled.
- `claude plugin details` → **MCP servers (1) `dental-ai-research`**, Skills (9).
- `claude mcp list` → `plugin:dana-dental-research:dental-ai-research:
  https://dental-ai-research-mcp.onrender.com/mcp (HTTP) — ✔ Connected`.
- A session loading the packaged v1.1.0 artifact exposed **exactly four** tools and executed
  `search_systematic_reviews` (`porcelain veneers`) followed by `verify_citation` against a real
  PMID and DOI.

**At no point was the connector URL entered manually** — it is discovered from the plugin's bundled
`.mcp.json`.

**One defect was found and fixed during this validation.** The pre-release drafts told the skills to
look for `mcp__dental-ai-research__*`. The real runtime name is
`mcp__plugin_dana-dental-research_dental-ai-research__<tool>`, because Claude Code registers a
plugin-provided server as `plugin:<plugin-name>:<server-name>` and derives the tool prefix from
that id. A skill checking the wrong name would have concluded the remote transport was absent and
silently fallen back to the local connectors — the same class of defect v1.0.2 fixed in `/start`.
The skills now **match these tools by suffix** rather than by a hard-coded prefix, so a future
naming change cannot silently disable the transport.

## What did not change

Clinical logic · clinical safety · prompts · treatment planning · evidence hierarchy · the DEL-7
tags · the retraction gate · the numeric gate · the safety veto · governance · identity policy ·
connector code · connector status · Clinical Protocol v1.3 · all nine skills.

`~~clinical-guidelines` and `~~manufacturer-ifu` remain **NOT CONNECTED**; `~~regulatory-saudi`
remains **NOT CONNECTED — AUTH REQUIRED**. Cochrane/CENTRAL, Embase and Scopus remain
**NOT IMPLEMENTED** on *both* transports — `search_systematic_reviews` is PubMed's structured
Publication Type filter only and must never be presented as a Cochrane search.

Zero connector `.py` files were modified. The only Python change is in
`clinical/tests/test_docs_consistency.py`: the version assertion, plus eight new checks (35–42)
that hold the MCP integration to the statements above.

## Verification

All seven regression suites pass: **341/341 assertions** (was 330/330 — the eleven new checks are
the MCP-integration consistency checks 35–45).

```
clinical/tests/test_clinical_layer.py             60/60
clinical/tests/test_clinical_completion.py        66/66
clinical/tests/test_protocol_approval.py          24/24
clinical/tests/test_identity_policy.py            46/46
clinical/tests/test_docs_consistency.py           45/45
connectors/clinical_trials/tests/…                50/50
connectors/sfda/tests/test_saudi_governance.py    50/50
```

Detailed diff: [`plugin/dana-dental-research/docs/CHANGELOG_v1.0.2_to_v1.1.0.md`](../plugin/dana-dental-research/docs/CHANGELOG_v1.0.2_to_v1.1.0.md)

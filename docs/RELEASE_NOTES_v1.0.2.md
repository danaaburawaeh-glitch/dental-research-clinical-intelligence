# Release Notes — v1.0.2

**Dental Research & Clinical Intelligence by Dr. Dana**
Plugin identifier `dana-dental-research` · Designed by Dr. Dana Abu Rawaeh

A **patch release** of v1.0.1. Fixes connector path resolution and capability reporting.
No feature, clinical or governance change.

## What changed

**Plugin path resolution.** The documented way to invoke the connector clients used
`${CLAUDE_PLUGIN_ROOT}` unguarded. That variable is substituted into plugin-declared hooks,
commands and MCP configuration, but is not exported into the Bash environment used for the ad-hoc
commands `evidence-research` issues — so on a clean install the documented command failed with
`[Errno 2] No such file or directory`. The invocation line now keeps `CLAUDE_PLUGIN_ROOT` as the
primary path and falls back to the most-recent *valid* installed plugin directory, selected
version-aware so that `1.0.10` correctly outranks `1.0.9`.

**Capability reporting in `/start`.** The capability check could be satisfied by looking for MCP
tools. This plugin's connectors are plugin-local Python CLIs invoked through the Bash tool, and its
bundled `.mcp.json` is empty by design — so an MCP-shaped check reported every research source as
unavailable no matter how healthy it was. PubMed, which is connected and working, was reported
`NOT CONNECTED`, and sources of differing status were grouped into a single row. `/start` now
states its detection procedure: read the connector capability map first, report each source
separately, and distinguish `NOT IMPLEMENTED` from `NOT CONNECTED` from a runtime retrieval failure.

**Version metadata** updated to 1.0.2.

## What did not change

Clinical logic · clinical safety · prompts · treatment planning · evidence hierarchy · governance ·
identity policy · connector code · connector states · Clinical Protocol v1.3 · scientific content ·
all nine skills · every reference file. No connector was added, removed or re-scoped.

Zero connector `.py` files were modified. The only Python change in this release is the version
assertion inside `clinical/tests/test_docs_consistency.py`.

## Connector status

Unchanged by this patch — it corrects how status is *reported*, not what is *connected*.

| Source | Status |
|---|---|
| PubMed / NCBI | **CONNECTED AND WORKING** |
| Systematic-review retrieval | **CONNECTED AND WORKING** — via PubMed `PublicationType` filtering |
| Crossref | **CONNECTED AND WORKING** — metadata / citation verification only, never full text |
| ClinicalTrials.gov API v2 | **CONNECTED AND WORKING** — registry retrieval only, not published evidence |
| Cochrane / CENTRAL | **NOT IMPLEMENTED** — no connector exists in this plugin |
| Embase | **NOT IMPLEMENTED** — no connector exists in this plugin |
| Scopus | **NOT IMPLEMENTED** — no connector exists in this plugin |
| SFDA | **NOT CONNECTED — AUTH REQUIRED** |

PubMed's systematic-review filter is **not** a substitute for Cochrane/CENTRAL coverage, and a
ClinicalTrials.gov registry record is **not** evidence that an intervention works.

## Impact on existing installations

Connectors already worked when invoked with a resolved path; the defects caused under-reporting,
not incorrect clinical output. The governance layer fails safe — a connector believed unavailable
yields `(UNVER)` marking plus a runnable search strategy, never fabricated citations. Updating is
recommended but no existing installation is unsafe.

## Validation

All seven regression suites pass: **330/330 assertions**. Public API health, the full evidence
path (retrieval → fetch → Crossref → citation verification → retraction gate → provenance) and
`/start` capability reporting were re-verified live against this release.

Full technical detail: [`CHANGELOG_v1.0.1_to_v1.0.2.md`](../plugin/dana-dental-research/docs/CHANGELOG_v1.0.1_to_v1.0.2.md)

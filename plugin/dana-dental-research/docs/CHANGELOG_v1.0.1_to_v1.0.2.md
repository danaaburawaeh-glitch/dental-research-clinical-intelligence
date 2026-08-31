# Changelog — v1.0.1 → v1.0.2 (connector detection & path resolution patch)

Patch release. **No clinical logic, evidence logic, connector code, connector state, Clinical
Protocol v1.3 content, safety rule, identity policy, prompt, treatment-planning rule, evidence
hierarchy or scientific content was changed.** No connector was added, removed or re-scoped.

## Why

Two defects were found by a read-only connector diagnostics pass on the installed public v1.0.1
release. Neither affected clinical output — the governance layer fails safe, treating a connector
believed unavailable as `(UNVER)` plus a runnable search strategy rather than fabricating results
— but together they caused the system to understate its own retrieval capability.

**Defect 1 — path resolution.** Every documented invocation of the connector clients used
`${CLAUDE_PLUGIN_ROOT}` unguarded. That variable is substituted into plugin-declared hooks,
commands and MCP configuration; it is **not** exported into the Bash tool environment used for the
ad-hoc commands `evidence-research` issues. On a clean install the documented command therefore
failed:

```
python3 "${CLAUDE_PLUGIN_ROOT}/connectors/pubmed/client.py" search ...
can't open file '/connectors/pubmed/client.py': [Errno 2] No such file or directory
```

**Defect 2 — capability detection.** `start`'s capability check could be satisfied by looking for
MCP tools. This plugin's connectors are plugin-local Python CLIs and its bundled `.mcp.json` is
empty by design, so an MCP-shaped check reports every research source as unavailable regardless of
actual health. Combined with defect 1, PubMed — which is connected and working — was reported
`NOT CONNECTED`, and four sources of three different statuses were collapsed into one row.

## Changed

**`skills/evidence-research/SKILL.md`** (line 44) — the connector invocation example now guards
the variable and resolves a fallback:

- `CLAUDE_PLUGIN_ROOT` remains the **primary** path; when set, it passes through unchanged.
- The fallback selects the most-recent **valid** install: the glob targets
  `connectors/pubmed/client.py`, so an incomplete or corrupt version directory can never be chosen.
- Selection is **version-aware**. `sort -V` is applied to the isolated version field, not the whole
  path — sorting whole paths misorders `0.4.5` against `0.4.5.2` because `/` collates against `.`,
  which would pick `1.0.5` over `1.0.5.1`. This project has shipped four-part versions, so the
  distinction is load-bearing.
- The cache root honours `CLAUDE_CONFIG_DIR` before defaulting to `$HOME/.claude`. Without
  this, an installation under a custom config directory would fall back to a *different,
  older* copy under `~/.claude` and run it silently — a wrong-version failure rather than a
  clean miss.
- Verified against synthetic caches: `1.0.8/1.0.9/1.0.10/1.0.11` → `1.0.11`; `1.0.9/1.0.10` →
  `1.0.10`; `1.0.4/1.0.5/1.0.5.1` → `1.0.5.1`; a `9.9.9` directory with no client is rejected;
  an empty cache returns empty without error; an explicitly set variable still wins.

**`skills/start/SKILL.md`** (§2) — the capability check now states the detection procedure it
already implied. Read `connector-capability-map.md` first and report its status column; the
connectors are Bash-invoked Python CLIs, not MCP servers, so absent `mcp__*` tools prove nothing;
report every source separately; `NOT IMPLEMENTED` (no connector exists) is distinct from
`NOT CONNECTED` and from a runtime retrieval failure on a connected source.

**Version metadata** — `1.0.1` → `1.0.2` in the plugin manifest, the marketplace manifest, and the
corresponding assertion in `clinical/tests/test_docs_consistency.py`.

## Connector status — unchanged by this patch

This patch changes how status is *reported*, never what is *connected*. The capability map's
status column is unchanged in substance.

| Source | Status |
|---|---|
| PubMed / NCBI (`~~literature`) | CONNECTED |
| Systematic-review retrieval (`~~systematic-reviews`) | CONNECTED — PubMed `PublicationType` filter |
| Crossref (`~~journal-access`) | CONNECTED — metadata / citation verification only, never full text |
| ClinicalTrials.gov API v2 (`~~clinical-trials`) | CONNECTED — registry retrieval only, not published evidence |
| Cochrane / CENTRAL | **NOT IMPLEMENTED** — no connector exists; PubMed's SR filter is not a substitute |
| Embase | **NOT IMPLEMENTED** — no connector exists |
| Scopus | **NOT IMPLEMENTED** — no connector exists |
| SFDA (`~~regulatory-saudi`) | **NOT CONNECTED — AUTH REQUIRED** |
| `~~clinical-guidelines`, `~~manufacturer-ifu` | NOT CONNECTED — not built |

## Validation

All seven regression suites pass unchanged: 330/330 assertions. Zero `.py` files changed other
than the single version assertion in the docs-consistency test.

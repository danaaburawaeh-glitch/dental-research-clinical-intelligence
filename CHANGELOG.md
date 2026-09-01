# Changelog

## v1.1.0 — remote MCP integration

Added:

- The live **Dental AI Research Remote MCP** server (`dental-ai-research`,
  `https://dental-ai-research-mcp.onrender.com/mcp`, streamable HTTP, no auth) is declared in the
  plugin's `.mcp.json` and is now the preferred retrieval transport for `~~literature`,
  `~~systematic-reviews`, `~~journal-access` and `~~clinical-trials`. The plugin-local Python
  connectors remain the fallback and are not deprecated.
- `skills/evidence-research/references/retrieval-transports.md` — new canonical rules separating a
  *source* (what evidence comes from) from a *transport* (how the plugin reaches it), with the
  transport-selection order and the verified behavioural differences between the two.
- Eleven new consistency checks (35–45) holding the integration to those rules, including the
  runtime tool-naming rule found by the fresh-install validation.

Unchanged:

- No connector status changed — status is a property of the source, not the transport. A missing or
  failing transport is a retrieval failure, never a `NOT CONNECTED` downgrade.
- The mandatory retraction gate is not waived: remote-MCP records carry no retraction/correction
  metadata, so a record backing a clinical claim is re-fetched over the local connector for the
  gate, or is marked retraction-status unchecked and cannot be presented as synthesis-eligible.
- Both transports call the same upstream APIs, so agreement between them is one retrieval, never
  independent corroboration.
- Cochrane, Embase and Scopus remain **not implemented** on both transports; SFDA remains
  **not connected — auth required**. No clinical logic, safety, governance or identity change.
  Zero connector `.py` files modified.

Full notes: [`docs/RELEASE_NOTES_v1.1.0.md`](docs/RELEASE_NOTES_v1.1.0.md)

## v1.0.2 — connector detection & path resolution patch

Fixed:

- PubMed connector incorrectly reported as disconnected in `/start`. The capability check could be
  satisfied by looking for MCP tools; these connectors are plugin-local Python CLIs and the bundled
  `.mcp.json` is empty by design, so the check reported every research source as unavailable
  regardless of actual health.
- `evidence-research` path resolution when `CLAUDE_PLUGIN_ROOT` is unset. The documented invocation
  failed with `[Errno 2]` on a clean install; the variable remains the primary path, with a
  version-aware fallback to the most-recent valid installed plugin directory.
- Capability reporting now separates PubMed, systematic-review retrieval, Crossref,
  ClinicalTrials.gov, Cochrane, Embase, Scopus and SFDA accurately, and distinguishes
  `NOT IMPLEMENTED` from `NOT CONNECTED` from a runtime retrieval failure.

No changes to clinical logic, clinical safety, prompts, treatment planning, evidence hierarchy,
governance or identity policy. No connector added, removed or re-scoped. Cochrane, Embase and
Scopus remain **not implemented**; SFDA remains **not connected — auth required**. All seven
regression suites pass unchanged: 330/330 assertions.

Full notes: [`docs/RELEASE_NOTES_v1.0.2.md`](docs/RELEASE_NOTES_v1.0.2.md)

## v1.0.1 — privacy patch

The maintainer's personal email address removed from all tracked repository content before public
distribution. Contact fields that structurally require an address now use a GitHub noreply address;
three historical documents had the literal address redacted with their meaning preserved.

**Functionally identical to v1.0.0.** No clinical logic, evidence logic, connector code, connector
state, Clinical Protocol v1.3 content, safety rule, identity policy or scientific content changed.
All seven regression suites pass unchanged.

v1.0.0 artifacts are preserved outside this repository and are not distributed, because their
manifest still contains the personal address.

Full notes: [`docs/RELEASE_NOTES_v1.0.1.md`](docs/RELEASE_NOTES_v1.0.1.md)

## v1.0.0 — first production release

Validated production release. **0 P0 blockers · 0 P1 blockers.**

**Evidence engine** — live PubMed/NCBI, Crossref and ClinicalTrials.gov API v2 connectors, DEL-7
evidence tagging, dual-source citation verification, an executable retraction and correction gate,
and trial-to-publication linkage that refuses to count a trial and its own paper as two studies.

**Clinical intelligence layer** — case-state model with provenance tagging, the 14-check red-flag
sweep as executable code, phased treatment planning with five blocking gates, a categorical
prognosis engine across five axes, and a non-overridable safety veto in the output path.

**Saudi governance layer** — four-state regulatory gate, PDPL patient-data rules including the
clinical-to-marketing firewall, and a strict separation of clinical evidence from legal permission.

**Author identity policy** — the designer is never a clinical, scientific, regulatory or protocol
source; the name appears in the product name and creator attribution only. Enforced in code.

**Clinical Protocol v1.3 — APPROVED.** All eight previously open items closed.

Known non-blocking items carried into release: product/IFU register not yet populated · laboratory
register not yet populated · protocol signature outstanding · SFDA authentication not configured.

The complete engineering history — every version from v0.3 forward, with per-release changelogs,
migration audits, connector specifications and validation records — ships inside the plugin at
`plugin/dana-dental-research/docs/`.

Full release notes: [`docs/RELEASE_NOTES_v1.0.0.md`](docs/RELEASE_NOTES_v1.0.0.md)

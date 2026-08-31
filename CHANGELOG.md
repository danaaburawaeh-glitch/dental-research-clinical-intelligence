# Changelog

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

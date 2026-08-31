# Changelog — v0.9.1 → v0.9.2 (documentation release-blocker patch)

Documentation only. **No clinical logic, connector code, Evidence Engine, Saudi governance,
identity policy or Clinical Protocol content changed.** The sole objective was the single P1
blocker from final v1.0 production validation.

## Fixed — the P1

`docs/UNRESOLVED_GAPS.md` stated *"No connector is actually wired. Every one of the seven `~~`
placeholders remains NOT CONNECTED"* in the present tense, under a "v0.3" title, with no historical
marking. False since v0.4.5 and contradicting `connector-capability-map.md`.

The file is restructured into **Part A — current release state** and **Part B — historical /
resolved**. No historical fact was deleted; 13 entries moved to Part B, each marked RESOLVED,
SUPERSEDED or HISTORICAL. Part A now opens with the authoritative connector table.

## Also fixed

- **Old gap 1 (CLINICAL-PROTOCOL-08)** → **H01, RESOLVED** by Clinical Protocol v1.3 APPROVED, with
  the historical explanation preserved.
- **Numbering** — unique `G01`–`G28` and `H01`–`H13`. The duplicate `14` is gone; the NCT-linkage
  item, previously triplicated across gaps 15/22/31/38, is now the single `G06`.
- **Register IDs `P1`–`P9` → `E1`–`E9`**, removing a collision with the `P0`–`P3` severity scheme
  that made "P1" mean either *release blocker* or *enhancement one*.
- **Two further stale titles** found by the §6 package-wide scan and bannered as historical:
  `EVIDENCE_ENGINE_ARCHITECTURE.md` and `PACKAGE_VALIDATION.md`, both titled "— v0.3".

## Classification of current gaps

**4 P2** — Appendix B empty (G01), Annex E empty (G02), protocol signature outstanding (G03),
`~~regulatory-saudi` AUTH REQUIRED (G04). **24 P3.** No current gap is P0 or P1.

## Added

`clinical/tests/test_docs_consistency.py` — 30 assertions. Permitted by the brief as a
documentation-consistency test. It enforces the rule whose breach caused the blocker, and
cross-checks the gaps file against both capability-map copies so they cannot drift apart silently
again.

## Unchanged

`connectors/` and every `clinical/*.py` module byte-identical to v0.9.1. All five prior regression
suites unchanged and passing. Connector states, Clinical Protocol v1.3 status and the identity
policy are untouched.

# Changelog — v0.4 → v0.4.1 (Connector Reliability & Retraction Safety Patch)

> **HISTORICAL RECORD — SUPERSEDED IN PART (v0.4.5.1).** Statements below about the packaged
> connectors having no live network access, or not having been executed live, describe the
> ORIGINAL BUILD SANDBOX at the time of that release. They are not current and must not be read
> as universal facts about the connectors. The packaged PubMed and Crossref clients have since
> made real live requests successfully on Claude Code / macOS (2026-08-30/31). Runtime
> connectivity is environment-dependent and must be checked at invocation. Authoritative current
> status: "Live Validation Record" in `connector-capability-map.md`.

**Type:** Patch release. **Scope:** runtime reliability fixes and retraction/correction safety
for the connector layer built in v0.4 Phase A. No new external connectors, no M3 Evidence Engine
architecture changes, no new knowledge migration.

## Bugs fixed

1. **Retry/backoff was written but not wired into the real request path.** `shared/retry.py`'s
   `with_backoff()` existed and was unit-tested in v0.4, but both `pubmed/client.py` and
   `crossref/client.py` called `urllib.request.urlopen()` directly. Fixed: both clients' real
   `_http_get()` now route through `with_backoff()`. Proven with real subprocess-style
   integration tests (mocked network, actual client functions), not just the standalone utility.

2. **A second, previously undetected bug found while fixing (1):** `pubmed/parser.py` and
   `crossref/parser.py` used relative imports (`from .errors import ...`) inconsistent with every
   other file in the codebase's absolute-import convention. This would have crashed
   `pubmed/client.py`/`crossref/client.py` on their very first real invocation as standalone
   scripts — exactly how they're actually meant to run. Never caught in v0.4 because all v0.4
   testing imported these modules as package submodules, never ran the actual entry-point
   scripts. Fixed; confirmed by literally running `python3 pubmed/client.py --help` and
   `python3 crossref/client.py --help` as real subprocesses.

3. **Network-level exceptions could leak as raw tracebacks instead of clean JSON failure
   objects.** Fixed: `pubmed_search`, `pubmed_fetch`, `crossref_lookup_doi`,
   `crossref_search_bibliographic` now guarantee they never raise — every failure path (retry
   exhaustion, HTTP error, parse error, or any unexpected exception) is caught and converted to
   the documented status-taxonomy JSON contract. CLI `_main()` functions add a second, outer
   safety net.

4. **Rate limiters permitted an initial burst above the configured rate.** The v0.4 token-bucket
   implementation started full, allowing up to `rate_per_second` requests with zero wait before
   throttling kicked in. Replaced with `SpacingRateLimiter`, a strict-interval/leaky-bucket design
   with no upfront burst allowance — proven correct with a fully mocked clock (no real waiting),
   confirming both that it never bursts and that it doesn't over-throttle when real time has
   already elapsed.

## New: retraction/correction safety

- `EvidenceRecord` extended with `publication_status`, `is_retracted`, `is_corrected`,
  `related_notices`, `retraction_source` — all default `None`, never guessed.
- Both parsers extract retraction/correction signals from **structured metadata only**
  (PubMed's `PublicationTypeList`/`CommentsCorrectionsList`; Crossref's `update-to`/`relation`) —
  never inferred from title text.
- New file: `skills/evidence-research/references/retraction-correction-gate.md` — a retracted
  record is excluded from synthesis (`RETRACTED — EXCLUDED FROM SYNTHESIS`), never used as
  supporting clinical evidence, regardless of its citation-verification status. A corrected
  record: the correction is identified and preferred where resolvable, with provenance for both
  preserved. An unchecked record (`publication_status: None`) is disclosed as unchecked, never
  silently treated as clean — this distinction is the single most important design decision in
  this feature, see `RETRACTION_CORRECTION_SPEC.md`.
- Integrated into `citation-verification.md` (canonical + quality-control bundled copy),
  `evidence-research/SKILL.md` (new workflow step 7a), and `quality-control/SKILL.md`.

## New: executable citation verifier

- `connectors/shared/citation_verifier.py` — the dual-source VERIFIED/PARTIALLY_VERIFIED/
  UNVERIFIED/IDENTIFIER_MISMATCH decision (previously only a Markdown instruction in
  `citation-verification.md`) is now real, callable, unit-tested code. Also has a CLI entry point.
  7 scenarios tested, including the exact real Smielak et al. bibliographic data → correctly
  classified `VERIFIED`.

## New: deduplication conflict detection

- `connectors/shared/deduplication.py` rewritten: a shared DOI or PMID no longer auto-merges on
  its own. If two records share a DOI (or PMID) but substantively disagree on title, or share a
  PMID but carry conflicting DOIs, this is now `FLAGGED_CONFLICT` and the records are kept
  separate — never silently merged. A dedicated cross-check pass specifically catches the
  same-PMID-different-DOI case, which would otherwise never be compared (same-DOI and different-
  DOI records land in different groups under the primary DOI-preferred keying). All 4 required
  scenarios tested (same-DOI/conflicting-title, same-PMID/conflicting-DOI, same-title-year/
  different-authors, legitimate online-first/issue-year merge), plus the original v0.4 regression
  test re-confirmed with zero behavior change for the legitimate-merge case.

## Regression tests

`skills/evidence-research/tests/v0.4.1-reliability-regression-tests.md` — 15 required scenarios,
**all 15 genuinely executed** (not reviewed-only) as real Python assertions this session, several
as true subprocess-level integration tests against the actual client entry points.

## Live connector status — unchanged, correctly so

**No connector reaches `CONNECTED` in this release.** This build environment's code-execution
tool (`bash_tool`) still has no network access — the same constraint documented in v0.4's
`CONNECTOR_IMPLEMENTATION_DECISION.md`. What changed is the *quality of evidence* behind
`NOT CONNECTED`: v0.4.1's mocked-network integration tests prove the client code's logic is
correct end-to-end (not just its isolated sub-components), which is real, valuable groundwork —
but a mock is still not a live network response, and `connector-capability-map.md`'s
Implementation Ledger says so explicitly rather than rounding this up to `CONNECTED`. Per the
patch's own Live Status Rule: `web_search`/`web_fetch` success (used in v0.4) was never treated
as proof the packaged Python connector itself is connected, and that discipline is unchanged here.

## Files changed

- `connectors/pubmed/client.py`, `connectors/pubmed/parser.py`, `connectors/pubmed/rate_limit.py`
- `connectors/crossref/client.py`, `connectors/crossref/parser.py`, `connectors/crossref/rate_limit.py`
- `connectors/shared/models.py`, `connectors/shared/deduplication.py`
- `connectors/shared/citation_verifier.py` (new)
- `skills/evidence-research/references/citation-verification.md` (canonical + quality-control bundled copy)
- `skills/evidence-research/references/connector-capability-map.md` (canonical + start bundled copy)
- `skills/evidence-research/references/retraction-correction-gate.md` (new)
- `skills/evidence-research/SKILL.md`
- `skills/quality-control/SKILL.md`
- `skills/evidence-research/tests/v0.4.1-reliability-regression-tests.md` (new)
- `.claude-plugin/plugin.json` (version 0.4.1)
- `docs/CONNECTOR_RELIABILITY_AUDIT.md`, `docs/RETRACTION_CORRECTION_SPEC.md`,
  `docs/PACKAGE_VALIDATION_v0.4.1.md`, `docs/CHANGELOG_v0.4_to_v0.4.1.md` (this file) — all new.

## Unchanged

All Evidence Engine content untouched: `del7-evidence-hierarchy.md`,
`evidence-quality-appraisal.md`, `evidence-synthesis.md`, `absence-of-evidence.md`,
`evidence-conflict-resolution.md`, `clinical-applicability.md`,
`clinical-evidence-safe-search-gateway.md`'s core architecture, `numeric-evidence-gate.md`,
`claim-strength-governor.md`, all templates, `evidence-regression-tests.md` (v0.3),
`connector-hallucination-safety-tests.md` (v0.4), `PUBMED_CONNECTOR_SPEC.md`,
`CROSSREF_CONNECTOR_SPEC.md`, `CONNECTOR_SECURITY.md`, `CONNECTOR_FAILURE_MODEL.md`,
`CONNECTOR_IMPLEMENTATION_DECISION.md`, `LIVE_CONNECTIVITY_TESTS.md`. All other skills
(`clinical-case`, `clinical-governance`, `esthetic-prosthodontics`,
`scientific-problem-selection`, `triage`, `treatment-plan-audit`) untouched.

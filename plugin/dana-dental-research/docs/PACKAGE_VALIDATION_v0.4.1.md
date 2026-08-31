# Package Validation — v0.4.1 (Connector Reliability & Retraction Safety Patch)

> **HISTORICAL RECORD — SUPERSEDED IN PART (v0.4.5.1).** Statements below about the packaged
> connectors having no live network access, or not having been executed live, describe the
> ORIGINAL BUILD SANDBOX at the time of that release. They are not current and must not be read
> as universal facts about the connectors. The packaged PubMed and Crossref clients have since
> made real live requests successfully on Claude Code / macOS (2026-08-30/31). Runtime
> connectivity is environment-dependent and must be checked at invocation. Authoritative current
> status: "Live Validation Record" in `connector-capability-map.md`.

## 1. Python code — syntax, real subprocess execution, and unit/integration tests

**Result: PASS.** Every `.py` file under `connectors/` compiles cleanly. Beyond v0.4's static
syntax checks, v0.4.1 additionally confirms all three CLI entry points (`pubmed/client.py`,
`crossref/client.py`, `shared/citation_verifier.py`) run as real subprocesses (`--help` exits 0)
— this specifically caught and fixed a relative-import bug that would have crashed every real
invocation in v0.4 (see `CONNECTOR_RELIABILITY_AUDIT.md` Finding 1).

25+ genuine executed assertions across this session, spanning: retry-wiring integration tests
(mocked `urllib.request.urlopen`, confirming the actual client functions retry correctly and
recover, or cleanly exhaust and report a status — never a raw traceback), rate-limiter spacing
tests (mocked monotonic clock, confirming no burst), retraction/correction parser tests (schema-
correct constructed XML/JSON for both connectors), citation-verifier tests (7 scenarios,
including the real Smielak et al. bibliographic data), and deduplication conflict-detection tests
(4 required scenarios plus the original v0.4 regression case re-confirmed with no behavior
change).

## 2. Manifest and structure

**Result: PASS.** `.claude-plugin/plugin.json` valid JSON, `version: "0.4.1"`. `.mcp.json`
unchanged (`{"mcpServers": {}}`). Structure unchanged from v0.4 (`.claude-plugin/`, `.mcp.json`,
`.env.example`, `connectors/`, `docs/`, `skills/`).

## 3. 9/9 skills present

**Result: PASS.**

## 4. Reference/template/test paths resolve

**Result: PASS.** Including the new `retraction-correction-gate.md` reference and
`v0.4.1-reliability-regression-tests.md` test file, both correctly cited from
`evidence-research/SKILL.md`.

## 5. Bundled-copy synchronization

**Result: PASS.** `citation-verification.md` (evidence-research ↔ quality-control) verified
byte-identical. `connector-capability-map.md` (evidence-research ↔ start) verified identical
except the two files' own canonical-vs-bundled header lines, which are intentionally different by
design — confirmed via direct diff, exactly 2 lines differ and they are the expected header lines.

## 6. Evidence Engine content not touched by v0.4.1 — confirmed unchanged

**Result: PASS.** Per this patch's own scope limit ("Do NOT change M3 Evidence Engine
architecture"), only the files listed in `CHANGELOG_v0.4_to_v0.4.1.md`'s "Files changed" section
were modified. `del7-evidence-hierarchy.md`, `evidence-quality-appraisal.md`,
`evidence-synthesis.md`, `absence-of-evidence.md`, `evidence-conflict-resolution.md`,
`clinical-applicability.md`, `numeric-evidence-gate.md`, `claim-strength-governor.md`, all
templates, and both prior test files (`evidence-regression-tests.md`,
`connector-hallucination-safety-tests.md`) are untouched.

## 7. All connectors still NOT CONNECTED

**Result: PASS.** Verified by direct grep: every occurrence of the string `CONNECTED` in
`connector-capability-map.md` that isn't part of `NOT CONNECTED` is an instructional/conditional
sentence (e.g. "only (C) is ever marked CONNECTED", "never mark CONNECTED speculatively") — no
status claim anywhere asserts a connector is actually connected. This holds despite v0.4.1's
substantially stronger evidence base (real subprocess-level mocked-network integration tests) —
the Implementation Ledger records this improvement precisely without rounding it up to
`CONNECTED`.

## 8. Bugs found and fixed — disclosed, not hidden

Both real bugs found during this patch's own work (the relative-import crash, and the initial
absence of a retry-wiring integration test that would have caught it sooner) are documented in
`CONNECTOR_RELIABILITY_AUDIT.md` rather than silently fixed and left unmentioned. This mirrors
the same disclosure standard applied to the `journals_match` bug found during v0.4's own testing.

## 9. What this document does NOT and cannot establish

Same limitation as v0.4, unchanged: no live network execution occurred in this build session
(this sandbox's `bash_tool` has no network access). Mocked-network integration tests prove the
client code's *logic* is correct end-to-end; they do not and cannot prove the code succeeds
against the real, live PubMed or Crossref APIs. That remains the one gap between this package's
current state and a genuine `CONNECTED` status — stated plainly here as in every other document
in this release.

## Overall result

**PASS**, for everything a static-plus-mocked-network build process can actually establish. The
patch's 4 findings are all fixed and proven with real executed tests; one additional real bug
was found and fixed in the process; retraction/correction safety and an executable citation
verifier are added and tested; no connector status was inflated.

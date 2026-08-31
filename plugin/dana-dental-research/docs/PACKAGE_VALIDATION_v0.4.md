# Package Validation — v0.4 (Phase A)

Static validation only — see `docs/LIVE_CONNECTIVITY_TESTS.md` for what was and wasn't verified
against live APIs, and `docs/CONNECTOR_IMPLEMENTATION_DECISION.md` for the environment constraint
governing all of it. This document does not and cannot claim live connectivity — see Package
Validation's own limits, stated plainly in each section below.

## 1. Python code — syntax and unit tests

**Result: PASS.** Every `.py` file under `connectors/` compiles cleanly
(`python3 -m py_compile`). A combined run of 12 core assertions spanning `identifiers.py`,
`normalization.py`, `deduplication.py`, `models.py`, `retry.py`, and both connectors' `parser.py`
modules passes in full — including the two real bugs found and fixed in `normalization.py`
during this build (see `CHANGELOG_v0.3.1_to_v0.4.md`). This is genuine executed verification, not
a claim of correctness by inspection alone.

## 2. Manifest and structure

**Result: PASS.** `.claude-plugin/plugin.json` is valid JSON, `version: "0.4.0"`. `.mcp.json`
unchanged from v0.3.1 (`{"mcpServers": {}}` — no fake servers added, matching the brief's explicit
instruction). Top-level shape: `.claude-plugin/`, `.mcp.json`, `.env.example`, `connectors/`,
`docs/`, `skills/` — the new `connectors/` and `.env.example` are additions outside the
auto-scanned plugin component directories (`skills/`, `commands/`, `agents/`, `hooks/`), so their
presence is inert to plugin discovery, same reasoning as `docs/`'s inertness established in
`PACKAGE_VALIDATION_v0.3.1.md`.

## 3. 9/9 skills present

**Result: PASS.** All nine skill directories retain a valid `SKILL.md`, unchanged in count from
v0.3.1.

## 4. Reference/template/test paths resolve

**Result: PASS.** Every `references/*.md`, `templates/*.md`, `tests/*.md` path cited in
`evidence-research/SKILL.md` (including the two new v0.4 test-file and gateway/connector-map
citations) resolves to an actual file. No orphans found.

## 5. Bundled-copy synchronization

**Result: PASS.** `citation-verification.md` (evidence-research ↔ quality-control),
`evidence-directness.md` (evidence-research ↔ quality-control ↔ clinical-governance),
`evidence-source-separation.md` (clinical-governance ↔ evidence-research), and
`connector-capability-map.md` (evidence-research ↔ start) all verified byte-identical (except each
file's own canonical-vs-bundled header line, which is intentionally different by design) via
direct `diff` after the v0.4 edits. The two files actually changed this release
(`citation-verification.md`, `connector-capability-map.md`) were synced to every location that
bundles them; the files left untouched this release remain in the synced state established in
v0.3/v0.3.1.

## 6. Evidence Engine content not touched by v0.4 — confirmed unchanged

**Result: PASS.** `skills/evidence-research/references/del7-evidence-hierarchy.md`,
`evidence-quality-appraisal.md`, `evidence-synthesis.md`, `absence-of-evidence.md`,
`evidence-conflict-resolution.md`, `clinical-applicability.md`,
`clinical-evidence-safe-search-gateway.md`'s pre-existing sections, `numeric-evidence-gate.md`,
`claim-strength-governor.md`, all templates, and `evidence-regression-tests.md` (the v0.3 15
scenarios) — none of these were rewritten wholesale; only `citation-verification.md`,
`connector-capability-map.md`, `clinical-evidence-safe-search-gateway.md` (appended sections),
`SKILL.md` (targeted edits to steps 3/7 and the intro/regression-coverage sections), and
`quality-control/SKILL.md` (targeted edits to the Evidence section) were modified, all
additively/precisely rather than as rewrites, per the brief's "Do NOT change the Evidence Engine
content [beyond what Phase A requires]" instruction from the v0.3.1 patch (carried forward as a
governing principle here since v0.4 has its own narrow, named scope too).

## 7. All connectors still NOT CONNECTED

**Result: PASS.** `connector-capability-map.md` (both copies) lists all seven placeholders as
`NOT CONNECTED`, including the three with new Phase A implementations. No file in the package
asserts a different status. Verified by direct grep — every `CONNECTED` occurrence outside the
literal string `NOT CONNECTED` is an instructional/conditional sentence (e.g. "never mark
CONNECTED speculatively"), not a status claim.

## 8. Secrets

**Result: PASS.** `.env.example` contains placeholders only (`NCBI_API_KEY=`, `NCBI_TOOL=
dana_dental_evidence`, `NCBI_EMAIL=`, `CROSSREF_MAILTO=`). No real API key, email, or credential
value appears anywhere in `connectors/`, `docs/`, `skills/`, `.claude-plugin/plugin.json`, or
`.mcp.json` — confirmed by direct review of every new/modified file this release, per
`CONNECTOR_SECURITY.md`.

## 9. What this document does NOT and cannot establish

Per `LIVE_CONNECTIVITY_TESTS.md`: this package's Python connector code has not been executed
against a live network anywhere in this build process. Static validation (this document) confirms
the package is syntactically correct, internally consistent, well-structured, and that its
non-network-dependent logic is genuinely tested and correct. It does not and cannot confirm the
connector code succeeds against the real, live PubMed or Crossref APIs — that requires an
environment with actual network access, which this build environment does not have for its
code-execution tool.

## Overall result

**PASS**, for everything a static, sandboxed build process can actually establish. The one
substantive gap — live network execution — is not a validation failure but a stated, honest
environment limitation, carried through consistently across every document in this release rather
than glossed over in any one of them.

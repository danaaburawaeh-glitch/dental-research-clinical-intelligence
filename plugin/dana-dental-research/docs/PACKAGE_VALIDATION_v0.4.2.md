# Package Validation — v0.4.2 (Retraction Semantics & Evidence Safety Patch)

## 1. Python code — syntax, subprocess execution, and directionality tests

**Result: PASS.** Every `.py` file compiles cleanly. All four CLI entry points
(`pubmed/client.py`, `crossref/client.py`, `shared/citation_verifier.py`,
`shared/retraction_gate.py`) run as real subprocesses (`--help` exits 0).

All 15 required Section 7 scenarios genuinely executed: 7 PubMed directionality tests (including
the exact `RetractionOf` bug scenario), 3 Crossref directionality tests (including the exact
`update-to`-retraction bug scenario, adapted to the real, verified field names per
`CROSSREF_RELATIONSHIP_MAP.md`), and 5 retraction-gate tests (plus a sanity check that every
record lands in exactly one output bucket). Both literal Section 6 tests (PubMed 500 retry,
Crossref 429 retry) executed exactly, correcting two v0.4.1 entries that had been mislabeled as
plain "Executed" when they were actually equivalent-path substitutions.

**A design bug in this patch's own first draft was found and fixed during testing**: the initial
directionality rewrite left `is_retracted`/`record_role` as `None` for ordinary checked articles
instead of `False`/`"article"`. Caught by a regression test, fixed, re-verified.

**An end-to-end pipeline test** (parser output fed directly into the gate) confirms the full
retraction-detection-to-exclusion pipeline works correctly, not just each piece in isolation.

## 2. Regression — zero breakage from v0.4.1

**Result: PASS.** Re-ran all 15 of v0.4.1's own regression scenarios (retry wiring, error
handling, rate-limiter spacing, citation verifier, deduplication conflict detection) against the
v0.4.2 codebase — zero behavior change. The parser rewrites were scoped to
`_parse_retraction_correction()` in both connectors and did not touch retry, rate-limiting,
citation verification, or deduplication logic; this is confirmed by test, not merely asserted by
scope description.

## 3. Manifest and structure

**Result: PASS.** `.claude-plugin/plugin.json` valid JSON, `version: "0.4.2"`. `.mcp.json`
unchanged. Structure unchanged from v0.4.1.

## 4. 9/9 skills present; reference/template/test paths resolve

**Result: PASS.** Including the two new docs (`PUBMED_CORRECTION_RELATIONSHIP_MAP.md`,
`CROSSREF_RELATIONSHIP_MAP.md`), the new test file
(`v0.4.2-directionality-regression-tests.md`), and the updated `retraction-correction-gate.md`
reference.

## 5. Bundled-copy synchronization

**Result: PASS.** `citation-verification.md` (unchanged this patch) still synced.
`connector-capability-map.md` (header updated this patch) re-synced to the `start` bundle —
verified via diff: exactly the expected canonical-vs-bundled header lines differ, content
otherwise identical.

## 6. Evidence Engine content not touched by v0.4.2 — confirmed unchanged

**Result: PASS.** Per this patch's scope limit ("Do NOT modify the Evidence Engine
architecture"), only the files listed in `CHANGELOG_v0.4.1_to_v0.4.2.md`'s "Files changed"
section were modified. `del7-evidence-hierarchy.md`, `evidence-quality-appraisal.md`,
`evidence-synthesis.md`, `absence-of-evidence.md`, `evidence-conflict-resolution.md`,
`clinical-applicability.md`, `numeric-evidence-gate.md`, `claim-strength-governor.md`, all
templates, `citation_verifier.py`, `deduplication.py`, `retry.py`, both rate limiters, and all
three prior test files' non-corrected content are untouched.

## 7. All connectors still NOT CONNECTED

**Result: PASS.** Verified by direct grep — the one line containing "CONNECTED" outside
"NOT CONNECTED" is the changelog-style header note stating plainly that this patch "does not
change connector CONNECTED status — still NOT CONNECTED for all seven" (a sentence spanning two
lines). No status claim anywhere asserts a connector is actually connected. This patch does not
touch live connectivity at all — the retraction/correction fixes are orthogonal to connection
status.

## 8. Real re-verification, disclosed — not just re-stated confidence

Unlike a patch that could have simply implemented the review's Section 3 instructions as
written, this patch's Crossref fix required going back to primary documentation and discovering
that v0.4.1's `relation`-field assumption had no documented basis, and that the `update-to` field
it did correctly identify was being read backwards. Both findings are disclosed in
`RETRACTION_DIRECTIONALITY_AUDIT.md` and `CROSSREF_RELATIONSHIP_MAP.md` rather than silently
folded into a fix that only addressed the specifically-named bug.

## Overall result

**PASS.** All required deliverables present, all required tests genuinely executed (not
reviewed-only), zero regressions, two additional real bugs found and fixed beyond what was
originally flagged, and the regression-accounting integrity issue from v0.4.1 corrected rather
than left standing.

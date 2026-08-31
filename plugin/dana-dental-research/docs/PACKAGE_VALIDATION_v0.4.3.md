# Package Validation — v0.4.3 (Evidence Pipeline Ordering Patch)

## 1. Scope compliance — zero connector code changed

**Result: PASS, verified by direct diff, not just scope description.** `diff -rq` between
`v0.4.2-build/connectors/` and `v0.4.3-build/connectors/` (after clearing `__pycache__`
bytecode-cache artifacts, which differ only by compilation timestamp and are not source) reports
**zero differences.** Every `.py` file — both parsers, both clients, all rate limiters, the
retraction gate, the citation verifier, deduplication, retry, identifiers, normalization,
provenance, models — is byte-for-byte identical to v0.4.2. This directly confirms the brief's
"Do NOT modify connector code" and "Do NOT change retraction semantics" constraints were honored,
not merely asserted.

## 2. The ordering fix — verified programmatically, not just by inspection

**Result: PASS.** A Python script parses the corrected `SKILL.md`'s `## Workflow` section and
confirms: the retraction-gate step (5) has a lower number than both the study-classification step
(7) and the DEL-7-tagging step (8); no sub-numbered steps (e.g. the old `"7a."`) remain; no stale
"before step 4" contradiction remains; steps are exactly 1 through 16, strictly increasing, no
gaps or duplicates. This is the same test used as regression scenario 6 — re-run here as a final
confirmation, not a separate weaker check.

## 3. Pipeline-order regression tests — all 6 required scenarios executed

**Result: PASS.** See `v0.4.3-pipeline-order-regression-tests.md` for full detail: 5 substantive
scenarios (retracted-article exclusion, retraction-notice flagging, clean-article pass-through,
expression-of-concern flagging, unresolved-correction flagging) plus the static document test.
All reuse v0.4.2's unchanged gate/parser logic — they pass without any code change being
necessary, which is the expected and correct outcome for a pure document-ordering patch, not a
coincidence.

## 4. Manifest and structure

**Result: PASS.** `.claude-plugin/plugin.json` valid JSON, `version: "0.4.3"`. `.mcp.json`
unchanged. No new top-level directories or files beyond the required deliverable docs and the one
new test file.

## 5. 9/9 skills present; reference/template/test paths resolve

**Result: PASS.** Including the new `v0.4.3-pipeline-order-regression-tests.md` file, correctly
cited from the updated `SKILL.md` regression-coverage section.

## 6. quality-control update

**Result: PASS.** The explicit pipeline-order check (Retrieval → Retraction gate → Evidence
classification, with the stated critical-failure condition) is present in
`quality-control/SKILL.md`, positioned directly after the existing retraction-gate check section
it extends.

## 7. All connectors still NOT CONNECTED

**Result: PASS.** Verified by direct grep of `connector-capability-map.md` — unchanged from
v0.4.2, since this patch does not touch connectivity at all. No status claim anywhere asserts a
connector is connected.

## 8. Honest disclosure of an in-process test correction

This patch's own static workflow-order test initially flagged a false positive (an explanatory
sentence describing the *old*, now-fixed "7a" numbering, not a live contradiction) because the
first version of the test checked the whole file rather than scoping to the active `## Workflow`
section. Corrected before being reported as passing, and disclosed in both
`PIPELINE_ORDERING_AUDIT.md`'s implicit test design and the regression-test file itself, rather
than silently fixed and re-run without comment.

## Overall result

**PASS.** The contradiction described in the brief is confirmed to have existed exactly as
described, is now fixed, and the fix is verified both by a programmatic document check and by
substantive gate-behavior tests — with zero connector code touched, confirmed by direct diff
rather than by assertion.

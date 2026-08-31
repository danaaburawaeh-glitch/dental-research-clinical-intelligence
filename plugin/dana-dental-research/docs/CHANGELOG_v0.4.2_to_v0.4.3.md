# Changelog — v0.4.2 → v0.4.3 (Evidence Pipeline Ordering Patch)

**Type:** Patch release. **Scope:** document-ordering fix only. No connector code touched, no
new connectors, no knowledge migration, no retraction semantics changes.

## The bug

`skills/evidence-research/SKILL.md`'s numbered workflow positioned the executable retraction gate
as step "7a" — after study classification (step 4), DEL-7 tagging (step 4, same step), quality
appraisal (step 5), directness (step 6), and citation verification (step 7). But step 7a's own
body text stated the gate must run "before study classification and DEL-7 tagging (step 4
below)." A reader following the numbered list in order would classify and DEL-7-tag every
retrieved record — including retracted ones — before ever reaching the step meant to remove them
first. See `PIPELINE_ORDERING_AUDIT.md` for the full analysis.

## The fix

Full renumbering of the workflow to 16 steps, matching the required pipeline order:

1. Formulate evidence question
2. Select source class / retrieval order
3. Retrieve through Clinical Evidence Safe Search Gateway
4. **Normalize retrieved records and parse retraction/correction metadata** (new explicit step —
   this was previously implicit, described only inside connector specs)
5. **Apply executable retraction/correction gate** (moved from "7a" to its correct position)
6. Citation verification (moved before classification, per the required pipeline)
7. Study-design classification
8. DEL-7 tagging (split into its own step, was previously merged with step 7's classification)
9. Evidence-quality appraisal
10. Directness assessment
11. Numeric evidence gate
12. Absence-of-evidence / conflict handling
13. Evidence synthesis
14. Clinical applicability
15. Claim-strength calibration
16. Output mode formatting (folded into the numbered list; the detailed mode table remains as
    supporting content immediately after)

No step's underlying logic changed — this is a pure reordering plus two small pieces of new
connective text (step 4's explanation, and step 5's text carried over near-verbatim from the old
7a). Every reference file the workflow cites is unchanged.

## Hard safety rule — restated explicitly in the corrected workflow

No record with `is_retracted == True` may reach study-design classification, DEL-7
supporting-evidence classification, the DIRECT or INDIRECT buckets, or clinical synthesis. It may
remain only in provenance/audit as `RETRACTED — EXCLUDED FROM SYNTHESIS`. This was already true
of the gate's *logic* in v0.4.2 — this patch makes the *document* say so unambiguously as well,
closing the gap where the numbered list itself contradicted the rule.

## quality-control update

Added an explicit pipeline-order check: **Retrieval → Retraction gate → Evidence classification**,
with a stated critical failure if classification or synthesis occurred before retraction status
was checked — independent of whether the eventual classification was itself correct. A retracted
record classified before being caught by the gate, then correctly excluded afterward, is still a
critical failure under this check, because the ordering guarantee was violated regardless of the
final outcome.

## Regression tests — all 6 required scenarios executed

`skills/evidence-research/tests/v0.4.3-pipeline-order-regression-tests.md` — 5 substantive gate
scenarios (retracted article excluded before reaching the classification pool, retraction notice
flagged before classification, clean article passes through to classification, expression of
concern flagged before synthesis, unresolved correction flagged before synthesis) plus 1 static
test that parses the corrected `SKILL.md` and programmatically confirms the retraction-gate step
number is lower than both the classification and DEL-7-tagging step numbers, with no stale
sub-numbered steps or "before step 4"-style contradictions remaining, and steps 1-16 present with
no gaps or duplicates.

**Disclosed candidly:** the static test's first version flagged a false positive (an explanatory
sentence in the new intro note that legitimately mentions the *old* "7a" numbering while
describing the fix) because it checked the whole file instead of scoping to the active workflow
section. The test was corrected before being reported as passing — noted here rather than
silently fixed, since a test that needed adjustment is worth being honest about.

## What was NOT done — stated plainly, consistent with prior patches' disclosure standard

The *ordering guarantee* is now unambiguous in the document, and quality-control has an explicit
check for a live violation of it — but nothing in this patch adds a structural pipeline harness
that would make skipping the gate mechanically impossible (e.g. a single orchestrating script
calling each stage's executable module in sequence). This is the same acknowledged gap
`RETRACTION_DIRECTIONALITY_AUDIT.md` (v0.4.2) already named, and it remains open — this patch
fixes the document's internal consistency (a real, meaningful fix, since a contradictory document
is actively misleading), not the deeper structural-enforcement question, which was outside this
patch's explicit scope ("very small workflow-ordering patch").

## Files changed

- `skills/evidence-research/SKILL.md` — workflow renumbered 1-16; intro note updated; stale
  step-number cross-references fixed.
- `skills/quality-control/SKILL.md` — pipeline-order check added.
- `skills/evidence-research/tests/v0.4.3-pipeline-order-regression-tests.md` (new).
- `.claude-plugin/plugin.json` — version 0.4.3.
- `docs/PIPELINE_ORDERING_AUDIT.md`, `docs/PACKAGE_VALIDATION_v0.4.3.md`,
  `docs/CHANGELOG_v0.4.2_to_v0.4.3.md` (this file) — all new.

## Unchanged

Every connector file, every parser, `retraction_gate.py`, `citation_verifier.py`,
`deduplication.py`, `retry.py`, both rate limiters, every DEL-7/directness/appraisal/synthesis
reference file's content, all prior test files, `.mcp.json`, `.env.example`. **No connector
reaches `CONNECTED` status** — this patch does not touch connectivity at all.

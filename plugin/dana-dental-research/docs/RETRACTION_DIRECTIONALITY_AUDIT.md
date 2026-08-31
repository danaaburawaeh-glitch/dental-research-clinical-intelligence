# Retraction Directionality Audit — v0.4.2

## Finding 1: PubMed RetractionIn/RetractionOf collapsed (confirmed accurate)

v0.4.1's `_parse_retraction_correction()` had:
```python
if ref_type in ("RetractionIn", "RetractionOf"):
    is_retracted = True
```
This is wrong for `RetractionOf`. Per PubMed's actual semantics (see
`PUBMED_CORRECTION_RELATIONSHIP_MAP.md`): `RetractionIn` means the current record HAS a
retraction (correctly sets `is_retracted = True`); `RetractionOf` means the current record IS a
retraction notice FOR another record (should NOT set `is_retracted = True` — the notice itself
was never retracted). The same collapse applied to `ErratumIn`/`ErratumFor`.

**Fixed:** `PUBMED_REFTYPE_SEMANTICS`, an explicit dict keyed by exact `RefType` string, each
mapped to its own `(sets_is_retracted, sets_is_corrected, record_role)` tuple — direct lookup,
no shared branches for paired types. **Proven** with all 7 required directionality tests
(Section 7, tests 1-7), including the exact `RetractionOf` scenario the review named — confirmed
`is_retracted: False`, `record_role: "retraction_notice"`.

## Finding 2: `record_role` added as a separate axis (confirmed necessary)

Extended `EvidenceRecord` with `record_role` (values: `article`, `retraction_notice`,
`correction_notice`, `erratum_notice`, `expression_of_concern_notice`, `corrected_republication`,
`unknown`, or `None` if unclassified). Kept genuinely separate from `is_retracted`/`is_corrected`
— a retraction notice's `record_role` is `"retraction_notice"` while its `is_retracted` is
`False`, exactly the distinction the review specified: *"A retraction notice is not the same
thing as a retracted article."*

## Finding 3: Crossref generic `relation` substring matching (confirmed unsafe — and a further
finding beyond what was flagged)

The review correctly flagged `if "retract" in relation_type: is_retracted = True` as unsafe
substring matching. Re-verifying Crossref's actual documentation for this patch went one step
further and found **no evidence that `is-retracted-by`/`is-retraction-of` are real values in
Crossref's documented `relation` controlled vocabulary at all** — the real values found
(`is-preprint-of`, `has-preprint`, `isVersionOf`, etc.) are about versions/preprints, not
retraction signaling. **v0.4.1's `relation`-based check was built on an unverified assumption
about field semantics — the same "infer from name similarity" failure mode this patch exists to
eliminate, that had already occurred once, undetected, before this patch.**

**A second, independent bug was found in the process**, beyond what the review's Section 3
described: v0.4.1's `update-to` handling (the field it DID correctly identify as real and
documented) was itself checked in the wrong direction. Real, verified Crossref documentation
(a published blog tutorial with actual JSON examples) confirms `update-to` and `updated-by` are
a **directional pair**: `update-to` appears on the record that IS the update/notice itself;
`updated-by` appears on the record that HAS BEEN updated by another record. v0.4.1 checked only
`update-to` and treated its presence as evidence the current record was retracted — backwards
from what `update-to` actually means.

**Fixed:** `CROSSREF_UPDATE_SEMANTICS`, keyed by `(direction, type)` tuples, covering both
`update-to` and `updated-by` with their correct, opposite meanings. The generic `relation` field
is no longer touched by retraction/correction logic at all. **Proven** with all 3 required
Crossref directionality tests (Section 7, tests 8-10), including the exact `update-to`-retraction
scenario — confirmed `is_retracted: False`, `record_role: "retraction_notice"` when the current
record IS an `update-to` retraction notice, and `is_retracted: True` when a different record
carries an `updated-by` retraction entry.

## Finding 4: executable retraction gate (built as requested)

`connectors/shared/retraction_gate.py`, `apply_retraction_gate()` — takes a list of records,
returns `{included, excluded, flagged}`. Retracted articles are excluded; notice records
(including retraction notices specifically) are flagged as contextual, never treated as clinical
supporting evidence; unresolved corrections are flagged; expressions of concern are flagged for
heightened caution. **Proven** with all 5 required tests (Section 7, tests 11-15) plus a sanity
check confirming every input record lands in exactly one output bucket, never dropped or
duplicated.

## Finding 5: pipeline integration (done, still Markdown-instruction-level for the *ordering*
guarantee)

`evidence-research/SKILL.md` step 7a now specifies the gate runs on the retraction/correction-
parsed records **before** study classification and DEL-7 tagging, with each of the three output
buckets given explicit handling instructions. `quality-control/SKILL.md` adds the exact critical-
failure statement requested: `is_retracted == True` AND the record was used to support a clinical
claim.

**What was NOT done, stated plainly:** the *ordering guarantee* (retraction gate runs before
DEL-7/classification, on every retrieval, without exception) is enforced by instructing Claude's
workflow via `SKILL.md`, not by a hard pipeline harness that would make skipping the gate
structurally impossible. This is the same category of limitation the reviewer originally
identified for citation verification in v0.4.1 (governance logic in Markdown vs. an executable
function) — v0.4.2 makes the *classification and filtering logic* executable
(`apply_retraction_gate()`), but the *guarantee that it's always called, in the right order* is
still a workflow instruction, not a structural enforcement. A future patch could wrap
`evidence-research`'s retrieval-to-synthesis pipeline in a single orchestrating script that calls
each stage's executable module in sequence, making the ordering itself unbypassable — not done
here, to keep this patch scoped to what was explicitly requested (retraction semantics and
evidence safety, not a full pipeline-orchestration rewrite, which the brief's own scope limits
("Do NOT modify the Evidence Engine architecture") argue against attempting here anyway).

## Corrected regression-test accounting (Section 6)

v0.4.1's own regression report mislabeled two equivalent-path tests as plain "Executed." Both are
corrected in `v0.4.1-reliability-regression-tests.md` (inline correction, preserving the original
reasoning) and the literal scenarios have now been run exactly — see
`v0.4.2-directionality-regression-tests.md`.

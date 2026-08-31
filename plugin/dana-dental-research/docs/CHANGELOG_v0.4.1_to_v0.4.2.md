# Changelog — v0.4.1 → v0.4.2 (Retraction Semantics & Evidence Safety Patch)

**Type:** Patch release. **Scope:** retraction/correction directionality fixes and an executable
evidence gate for the connector layer. No new connectors, no M3 Evidence Engine architecture
changes, no new knowledge migration.

## Bugs fixed

1. **PubMed `RetractionIn`/`RetractionOf` (and `ErratumIn`/`ErratumFor`,
   `CorrectedAndRepublishedIn`/`CorrectedAndRepublishedFrom`, `ExpressionOfConcernIn`/
   `ExpressionOfConcernFor`) were collapsed into the same meaning.** `RetractionOf` means the
   current record IS a retraction notice for another record — it does not mean the current
   record was itself retracted. v0.4.1 set `is_retracted = True` for both directions of the
   pair. Fixed with an explicit `PUBMED_REFTYPE_SEMANTICS` lookup table (direct lookup, no
   shared branches) — see `PUBMED_CORRECTION_RELATIONSHIP_MAP.md`. Proven with all 7 required
   directionality tests, including the exact `RetractionOf` scenario.

2. **Crossref's generic `relation` field was checked with unsafe substring matching
   (`"retract" in relation_type`), and — a further finding beyond what was flagged — the values
   it was checking for (`is-retracted-by`, etc.) were never confirmed to actually exist in
   Crossref's documented `relation` vocabulary.** Re-verifying Crossref's real documentation this
   session found no evidence for those specific values; the real, confirmed relation-type values
   are about versions/preprints, not retractions. **Removed entirely** — see
   `CROSSREF_RELATIONSHIP_MAP.md`, "A finding from re-verification."

3. **Crossref's `update-to` field was checked in the wrong direction.** Real, verified Crossref
   documentation (a published tutorial with actual JSON examples) confirms `update-to` and
   `updated-by` are a directional pair: `update-to` appears on the record that IS the notice;
   `updated-by` appears on the record that WAS updated by another record. v0.4.1 checked only
   `update-to` and treated it as evidence the current record was retracted — backwards. Fixed
   with `CROSSREF_UPDATE_SEMANTICS`, keyed by `(direction, type)`. Proven with all 3 required
   Crossref directionality tests, including the exact `update-to`-retraction scenario.

4. **A bug in this patch's own first-draft fix, caught during testing:** the initial
   directionality rewrite left `is_retracted`/`record_role` as `None` for ordinary, checked
   articles instead of the correct `False`/`"article"`, inconsistent with the established
   "checked-and-clean vs. never-checked" distinction. Found and fixed before proceeding, via a
   regression test that expected the correct default.

5. **v0.4.1's own regression-test accounting mislabeled two equivalent-path tests as plain
   "Executed."** ("PubMed 500" was actually tested via the Crossref 503 case; "Crossref 429" was
   actually tested via the 503 variant.) Corrected inline in
   `v0.4.1-reliability-regression-tests.md`, and the literal scenarios were subsequently run
   exactly in `v0.4.2-directionality-regression-tests.md`.

## New: `record_role` — a separate axis from `is_retracted`/`is_corrected`

`EvidenceRecord` extended with `record_role` (`"article"` | `"retraction_notice"` |
`"correction_notice"` | `"erratum_notice"` | `"expression_of_concern_notice"` |
`"corrected_republication"` | `"unknown"` | `None`). A retraction notice has
`record_role: "retraction_notice"` and `is_retracted: False` — it is not itself a retracted
article. This distinction is the central fix of this patch.

## New: executable retraction gate

`connectors/shared/retraction_gate.py`, `apply_retraction_gate()` — takes a list of records,
returns `{included, excluded, flagged}`. Retracted articles excluded with
`RETRACTED — EXCLUDED FROM SYNTHESIS`; notice records (including retraction notices) flagged as
contextual, never treated as clinical supporting evidence; unresolved corrections flagged with
`CORRECTION EXISTS — VERIFY CURRENT VERSION`; expressions of concern flagged with
`EXPRESSION OF CONCERN — USE WITH HEIGHTENED CAUTION`. All 5 required tests pass, plus a sanity
check confirming every input record lands in exactly one output bucket. An end-to-end test
(parser output fed directly into the gate) confirms the full pipeline works correctly — a parsed
retraction notice is flagged, not excluded as if it were itself retracted.

## Integrated into the pipeline

- `evidence-research/SKILL.md` step 7a rewritten: the gate now runs on retraction/correction-
  parsed records **before** study classification and DEL-7 tagging, with each of the three output
  buckets given explicit handling instructions.
- `quality-control/SKILL.md`: added the explicit critical-failure statement —
  `is_retracted == True` AND the record was used to support a clinical claim.
- `retraction-correction-gate.md` updated to document the `record_role` axis and point to the
  executable module as the enforcement mechanism (the file remains the canonical rule
  description).

## What was NOT done — stated plainly

- The *ordering guarantee* (the gate always runs, in the right order, on every retrieval) is
  still enforced via workflow instruction in `SKILL.md`, not a structural pipeline harness that
  would make skipping it impossible. Same category of limitation the original review identified
  for citation verification before v0.4.1's `citation_verifier.py` — this patch makes the
  *classification and filtering logic* executable, not the *guarantee it's always invoked*. Noted
  as a gap for a future patch, not attempted here given the "Do NOT modify the Evidence Engine
  architecture" scope limit.
- `updated-by`'s exact JSON shape was not independently confirmed with a literal captured example
  the way `update-to` was (a description of its existence and direction was confirmed, but not a
  raw JSON example) — implemented per the documented, described structure, flagged as
  slightly lower-confidence than `update-to` itself in `CROSSREF_RELATIONSHIP_MAP.md`.
- Retracted/corrected records reachable only via unknown, unclassified `RefType`/`update-to`
  `type` values are preserved in `related_notices` but not acted upon by the gate — this is
  intentional (per Section 3's explicit instruction not to classify unknown types), not an
  oversight, but it does mean a genuinely retracted paper using a PubMed `RefType` or Crossref
  `type` value not in the current mapping tables would not be caught. The mapping tables cover
  every value found in official documentation this session; expanding them further would need
  either more documentation or live data to discover additional real values.

## Files changed

- `connectors/pubmed/parser.py` — `_parse_retraction_correction()` rewritten with
  `PUBMED_REFTYPE_SEMANTICS`.
- `connectors/crossref/parser.py` — `_parse_retraction_correction()` rewritten with
  `CROSSREF_UPDATE_SEMANTICS`; generic `relation` field check removed.
- `connectors/shared/models.py` — `record_role` field added.
- `connectors/shared/retraction_gate.py` (new).
- `skills/evidence-research/references/retraction-correction-gate.md` — updated for
  `record_role` axis and executable enforcement.
- `skills/evidence-research/references/connector-capability-map.md` (canonical + `start` bundled
  copy) — header updated, no status changes.
- `skills/evidence-research/SKILL.md` — step 7a rewritten.
- `skills/quality-control/SKILL.md` — critical-failure statement added.
- `skills/evidence-research/tests/v0.4.1-reliability-regression-tests.md` — two mislabeled
  entries corrected inline.
- `skills/evidence-research/tests/v0.4.2-directionality-regression-tests.md` (new).
- `.claude-plugin/plugin.json` — version 0.4.2.
- `docs/RETRACTION_DIRECTIONALITY_AUDIT.md`, `docs/PUBMED_CORRECTION_RELATIONSHIP_MAP.md`,
  `docs/CROSSREF_RELATIONSHIP_MAP.md`, `docs/PACKAGE_VALIDATION_v0.4.2.md`,
  `docs/CHANGELOG_v0.4.1_to_v0.4.2.md` (this file) — all new.

## Unchanged

Everything not listed above: all other skills, all Evidence Engine content, `citation_verifier.py`,
`deduplication.py`, `retry.py`, both rate limiters, `CONNECTOR_SECURITY.md`,
`CONNECTOR_FAILURE_MODEL.md`, `PUBMED_CONNECTOR_SPEC.md`, `CROSSREF_CONNECTOR_SPEC.md`,
`.env.example`, `.mcp.json`. **No connector reaches `CONNECTED` status** — unchanged reasoning
from v0.4/v0.4.1, this patch does not touch live connectivity at all.

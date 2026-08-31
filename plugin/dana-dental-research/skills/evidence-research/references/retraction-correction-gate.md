<!--
REFERENCE-ID: retraction-correction-gate
VERSION: 0.4.2
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-08-30
New in v0.4.1 — Connector Reliability & Retraction Safety Patch, Section 4.
v0.4.2: the rules described here are now EXECUTABLE — see connectors/shared/retraction_gate.py
and evidence-research/SKILL.md step 7a. This file remains the canonical description of the
rules; the Python module is the enforcement mechanism, not a duplicate spec. v0.4.2 also adds
the record_role axis (a retraction NOTICE is not the same as a retracted ARTICLE — see
PUBMED_CORRECTION_RELATIONSHIP_MAP.md / CROSSREF_RELATIONSHIP_MAP.md) and fixes a real
directionality bug in v0.4.1's parsers that had this backwards for several RefType/update-to
pairs.
-->

# Retraction / Correction Gate

Loaded by: evidence-research, citation-verification.md (as a required check), quality-control.

## Why this exists

A citation being retrievable, verifiable, and correctly DEL-7 tagged says nothing about whether
it has since been retracted or corrected. A retracted paper can still resolve on PubMed and
Crossref, still have a valid DOI, still pass dual-source citation verification on its original
fields — and still be actively wrong. This gate is a separate check, run in addition to citation
verification, not a substitute for it.

## Where the signal comes from — structured metadata only

- **PubMed:** `PublicationTypeList` may directly contain `Retracted Publication`.
  `CommentsCorrectionsList/CommentsCorrections` entries with `RefType` in `RetractionIn`,
  `RetractionOf`, `ErratumIn`, `ErratumFor`, `CorrectedAndRepublishedIn`,
  `ExpressionOfConcernIn` link to the specific notice (by PMID and/or free-text source).
- **Crossref:** the `update-to` field (type: `retraction`, `correction`, `erratum`,
  `clarification`, `removal`, `addendum`) and/or the `relation` field
  (`is-retracted-by`/`has-retraction`, `is-corrected-by`, etc.).

**Never infer retraction or correction from title text, abstract wording, or any unstructured
signal.** A title containing the word "retracted" (e.g. a paper *about* retraction practices) is
not itself a retracted paper — see `connectors/pubmed/parser.py`'s
`_parse_retraction_correction()` and the equivalent in `connectors/crossref/parser.py`, both of
which check only the structured fields above.

## Three states, and the honest distinction between them

`EvidenceRecord.publication_status` is one of:

- **`"retracted"`** — structured metadata confirms a retraction.
- **`"corrected"`** — structured metadata confirms a correction/erratum, and no retraction.
- **`"active"`** — structured metadata WAS checked (publication types and/or relation/
  update-to fields were present in the retrieved record) and found no retraction or
  correction signal.
- **`None`** — the check could not be meaningfully performed at all (the retrieved record
  carried no publication-type or relation/update-to data to check). **This is distinct from
  `"active"` and must never be silently treated as equivalent to it** — `None` means "unchecked,"
  not "checked and clean."

## The record_role axis (v0.4.2) — separate from is_retracted/is_corrected

`record_role` answers "what IS this record" (an article, or a notice about another record),
which is a different question from "is the article this record describes retracted/corrected."
A retraction notice has `record_role: "retraction_notice"` and `is_retracted: False` — **the
notice itself was not retracted; it describes the retraction of a different record.** Conflating
these (treating a retraction notice as if it were a retracted article) was a real bug in v0.4.1,
fixed in v0.4.2 — see `PUBMED_CORRECTION_RELATIONSHIP_MAP.md` and `CROSSREF_RELATIONSHIP_MAP.md`
for the exact directional signal-by-signal mapping.

## The critical evidence gate — now executable (v0.4.2)

Implemented in `connectors/shared/retraction_gate.py`, `apply_retraction_gate()`. Given a list of
records, it returns three buckets — every input record lands in exactly one:

- **`excluded`** — `is_retracted: True`. Not used as supporting clinical evidence:

  ```
  RETRACTED — EXCLUDED FROM SYNTHESIS
  ```

  The record may still be mentioned — e.g. "a 2019 study initially reported X but was retracted
  in 2021 for [reason if known]" — as a factual, historical note, but never as a citation backing
  a clinical claim.

- **`flagged`** — a notice record (`record_role` in the notice-role set — a retraction notice is
  never itself clinical supporting evidence, even though it isn't "retracted" in the
  `is_retracted` sense), an unresolved correction (`CORRECTION EXISTS — VERIFY CURRENT VERSION`),
  or an expression of concern (`EXPRESSION OF CONCERN — USE WITH HEIGHTENED CAUTION`, never
  treated as strong supporting evidence without explicit review).

- **`included`** — passes through cleanly, or (for a resolved correction) is the corrected
  version with the original preserved as `superseded_record` for provenance.

If `is_corrected` is `True` and a corrected version can be resolved (by the PMID/DOI in
`related_notices`), the gate prefers it and links back to the original — do not silently
substitute one for the other without preserving that linkage.

If `publication_status` is `None` for a consequential citation: state that retraction/correction
status could not be checked from the retrieved metadata, per the same "state the gap, don't
silently assume clean" principle governing every other honesty rule in this plugin. (The gate
itself passes an unchecked record through to `included`, since there is no signal to act on —
the disclosure obligation is separate, and sits with citation-verification.md / the workflow
step that presents the citation.)

## Relationship to citation-verification.md

This gate is independent of VERIFIED/PARTIALLY VERIFIED/UNVERIFIED status. A citation can be
`VERIFIED` (its bibliographic fields are confirmed accurate) and simultaneously `retracted` (the
paper itself has been withdrawn) — these are different axes and must both be checked and both be
reported. `citation-verification.md`'s QC check now includes a retraction-gate check as a
required step, not an optional add-on.

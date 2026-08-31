# Retraction / Correction Specification — v0.4.1 Section 4

## Data model

`EvidenceRecord` (`connectors/shared/models.py`) extended with five new fields, all defaulting to
`None`:

| Field | Type | Meaning |
|---|---|---|
| `publication_status` | `"active"` \| `"retracted"` \| `"corrected"` \| `None` | `None` means the check could not be performed (no structured data to check) — never conflated with `"active"` |
| `is_retracted` | `bool` \| `None` | `None` only when unchecked |
| `is_corrected` | `bool` \| `None` | `None` only when unchecked |
| `related_notices` | `list[dict]` \| `None` | Each `{type, pmid/doi, source_text/label}` |
| `retraction_source` | `"pubmed"` \| `"crossref"` \| `None` | Which connector's metadata established a retraction/correction flag |

## PubMed source fields (structured only)

1. `PublicationTypeList` may directly contain the value `Retracted Publication` — the single
   strongest, most explicit PubMed signal.
2. `CommentsCorrectionsList/CommentsCorrections` elements, each with a `RefType` attribute.
   Types checked: `RetractionIn`, `RetractionOf` (→ retracted), `ErratumIn`, `ErratumFor`,
   `CorrectedAndRepublishedIn` (→ corrected), `ExpressionOfConcernIn` (recorded as a notice but
   does not by itself set `is_retracted`/`is_corrected` — an expression of concern is neither).
   Each matching element's linked `PMID` and free-text `RefSource` are captured into
   `related_notices`.

Implementation: `connectors/pubmed/parser.py`, function `_parse_retraction_correction()`.

## Crossref source fields (structured only)

1. `update-to` — a list of `{DOI, type, label, updated}` objects. `type` values checked:
   `retraction` (→ retracted), `correction`/`erratum`/`clarification` (→ corrected).
2. `relation` — a dict keyed by relation type (e.g. `is-retracted-by`, `has-retraction`,
   `is-corrected-by`). Any key containing `"retract"` sets `is_retracted`; any key containing
   `"correct"` or `"erratum"` sets `is_corrected`.

Implementation: `connectors/crossref/parser.py`, function `_parse_retraction_correction()`.

## The "unchecked vs. clean" distinction — the most important design decision here

If neither `PublicationTypeList` nor `CommentsCorrectionsList` (PubMed) / neither `update-to` nor
`relation` (Crossref) is present at all in the retrieved record, `publication_status` is `None`
— **not** `"active"`. This is deliberate: a record that was actually checked and found clean
(`"active"`) is different, evidentially, from a record where the check couldn't be performed at
all. Silently defaulting an unchecked record to `"active"` would be exactly the kind of false
"checked and clean" claim the rest of this plugin's honesty rules exist to prevent — see
`retraction-correction-gate.md`'s explicit statement of this distinction.

## The evidence gate

Implemented as a documentation-level rule in `retraction-correction-gate.md` (not executable code
in this patch — see Unresolved Gaps): if `is_retracted` is `True` for any record entering
`evidence-synthesis.md`'s DIRECT or INDIRECT buckets, it is excluded with
`RETRACTED — EXCLUDED FROM SYNTHESIS` rather than used as supporting evidence. If `is_corrected`
is `True` (and not retracted), the corrected version is identified and preferred where a
resolvable identifier exists, with provenance for both preserved.

## What was tested (see `v0.4.1-reliability-regression-tests.md` tests 8, 9)

- A schema-correct PubMed record with `Retracted Publication` in its `PublicationTypeList` and a
  linked `RetractionIn` notice → correctly parsed as `is_retracted: True`,
  `publication_status: "retracted"`, notice PMID captured.
- A schema-correct PubMed record with only an `ErratumIn` notice → correctly parsed as
  `is_corrected: True`, `is_retracted: False`, `publication_status: "corrected"`.
- A schema-correct PubMed record with normal `PublicationTypeList` and no correction notices →
  correctly parsed as `publication_status: "active"`.
- A PubMed record with no publication-type data at all → correctly parsed as
  `publication_status: None`.
- Equivalent Crossref cases via `update-to` (`retraction` and `erratum` types) and the
  no-data-present case.

## What was NOT done in this patch — stated plainly

- **The evidence gate itself is not executable code** — it's a Markdown rule in
  `retraction-correction-gate.md` that evidence-research's workflow is instructed to follow, the
  same category of "governance logic in Markdown, not a function" the reviewer flagged for
  citation verification (and which Section 5 addressed for citation verification specifically,
  via `citation_verifier.py`). A future patch could similarly extract this into an executable
  `retraction_gate.py` that takes a list of `EvidenceRecord`s and returns the filtered/flagged
  set — not done here, to keep this patch scoped to what was explicitly requested.
- **No live retraction data was retrieved or tested against a real retracted paper.** All test
  data is schema-correct constructed XML/JSON, matching documented PubMed/Crossref structures,
  not live-captured examples of an actual retracted dental paper (no live network access this
  session — unchanged constraint from v0.4).
- **PubMed's `ExpressionOfConcernIn`/`ExpressionOfConcernFor` are captured in `related_notices`
  but do not set either `is_retracted` or `is_corrected`.** An expression of concern is neither a
  retraction nor a correction — it's a signal that the record deserves scrutiny, which is
  preserved in the notices list for a human or downstream process to consider, but is
  deliberately not force-classified into either boolean flag.

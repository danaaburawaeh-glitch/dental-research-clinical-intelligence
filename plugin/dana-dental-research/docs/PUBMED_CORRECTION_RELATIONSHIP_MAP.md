# PubMed Correction/Retraction Relationship Map — v0.4.2

Source: NLM/MEDLINE `CommentsCorrectionsList` documentation and `PublicationTypeList` controlled
vocabulary, cross-checked against real-world `RefType` usage patterns. Every mapping below is a
**directional** relationship — the `RefType` attribute names look similar in pairs
(`XIn`/`XFor`) but mean opposite things, and v0.4.1 collapsed several of these pairs incorrectly.
This document exists specifically so that collapse never happens again silently.

## The core distinction

A `CommentsCorrections` element with `RefType="RetractionIn"` says: *"a retraction notice exists,
and it is IN [the linked PMID]"* — i.e., **this current record has been retracted**, and the
linked PMID is the retraction notice.

A `CommentsCorrections` element with `RefType="RetractionOf"` says: *"this current record IS a
retraction OF [the linked PMID]"* — i.e., **this current record IS the retraction notice
itself**, and the linked PMID is the article being retracted.

These are opposite roles. v0.4.1 set `is_retracted = True` for both, which was wrong for
`RetractionOf` — a retraction notice is not itself a retracted article.

## Exact mapping table

| `RefType` | What it means for the CURRENT record | `is_retracted` | `is_corrected` | `record_role` |
|---|---|---|---|---|
| `RetractionIn` | Current record has been retracted; link points to the notice | `True` | — | `article` (unchanged — it's still an article, just a retracted one) |
| `RetractionOf` | Current record IS the retraction notice; link points to the retracted article | `False` | — | `retraction_notice` |
| `ErratumIn` | Current record has a published erratum/correction; link points to the erratum | — | `True` | `article` |
| `ErratumFor` | Current record IS the erratum notice itself; link points to the article it corrects | — | `False` | `erratum_notice` |
| `CorrectedAndRepublishedIn` | Current record was corrected and republished as a new record; link points to the republished version | — | `True` | `article` (superseded — the republished version is preferred) |
| `CorrectedAndRepublishedFrom` | Current record IS the corrected republication; link points to the original, superseded record | — | `False` | `corrected_republication` |
| `ExpressionOfConcernIn` | Current record has a published expression of concern; link points to it | — | — | `article` (flagged — see below) |
| `ExpressionOfConcernFor` | Current record IS the expression-of-concern notice itself; link points to the article of concern | — | — | `expression_of_concern_notice` |

`PublicationTypeList` direct values (the most authoritative PubMed signal, when present):

| `PublicationType` value | Meaning | `is_retracted` | `record_role` |
|---|---|---|---|
| `Retracted Publication` | This record IS a retracted article | `True` | `article` |
| `Retraction of Publication` | This record IS a retraction notice | `False` | `retraction_notice` |

## What "flagged" means for expression-of-concern (neither retracted nor corrected)

An expression of concern is neither a retraction nor a correction — it's a signal that the
record deserves heightened scrutiny while an investigation is ongoing or unresolved. Per v0.4.2
Section 4, this does not set `is_retracted` or `is_corrected`, but is preserved in
`related_notices` and triggers a distinct caution flag at the retraction-gate level
(`EXPRESSION OF CONCERN — USE WITH HEIGHTENED CAUTION`), never silently treated as either "clean"
or "retracted."

## Unknown/unlisted RefType values

Any `RefType` not in the table above (PubMed's controlled vocabulary includes others not
relevant to retraction/correction semantics, e.g. `CommentIn`/`CommentOn`, `UpdateIn`/`UpdateOf`)
is preserved verbatim in `related_notices` with its raw `RefType` string, but never used to set
`is_retracted`, `is_corrected`, or a specific `record_role` — per the explicit instruction not to
infer semantics from name similarity. An unrecognized type is data worth keeping, not a basis for
classification.

## Implementation

`connectors/pubmed/parser.py`, `PUBMED_REFTYPE_SEMANTICS` dict + `_parse_retraction_correction()`
— the dict is the single source of truth; the function does a direct lookup, never pattern
matching or substring checks on the `RefType` string.

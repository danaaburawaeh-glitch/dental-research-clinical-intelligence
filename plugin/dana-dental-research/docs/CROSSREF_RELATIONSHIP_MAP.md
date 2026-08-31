# Crossref Relationship Map — v0.4.2

## A finding from re-verification, disclosed up front

v0.4.1's Crossref retraction/correction logic checked the generic `relation` field for keys
containing the substrings `"retract"` or `"correct"`/`"erratum"` (e.g. an assumed
`is-retracted-by` value), in addition to the `update-to` field. Re-verifying Crossref's actual
documentation for this patch (fetched from `crossref.org` and `support.crossref.org`, plus a
real, published REST API example from a Crossref blog post) found **no documented evidence that
`is-retracted-by`/`is-retraction-of` are real values in Crossref's `relation` controlled
vocabulary.** The `relation` field's documented, real values are things like `is-preprint-of`,
`has-preprint`, `isVersionOf`, `is-referenced-by` — version/preprint/citation relationships, not
retraction signaling. The v0.4.1 code was checking for a mechanism that doesn't appear to be how
Crossref actually signals retractions — exactly the "infer semantics from name similarity"
mistake this patch was commissioned to eliminate, and it turns out v0.4.1 had already made a
version of it independently. **This is fixed in v0.4.2: the generic `relation`-substring check is
removed entirely.**

## The real, documented mechanism: `update-to` + `updated-by` (a directional pair)

Confirmed via a real, published Crossref REST API JSON example (Crossref's own tutorial and blog
post on Retraction Watch integration, `crossref.gitlab.io/tutorials/get-rw-metadata/` and
`crossref.org/blog/retraction-watch-retractions-now-in-the-crossref-api/`):

- **`update-to`** appears on the record that **IS the update/notice itself**. Each entry:
  `{"updated": {date-parts, date-time, timestamp}, "DOI": "<the DOI this record updates>",
  "type": "retraction"|"correction"|"erratum"|"clarification"|"removal"|"addendum"|
  "expression_of_concern", "source": "publisher"|"retraction-watch", "label": "Retraction"}`.
  A record carrying `update-to` with `type: "retraction"` **IS the retraction notice** — it is
  not itself a retracted article.

- **`updated-by`** appears on the record that **HAS BEEN updated** (retracted/corrected/etc.) by
  another record. This is the reverse direction. A record carrying `updated-by` with a
  `type: "retraction"` entry **IS the retracted article** — the linked DOI is its retraction
  notice.

**v0.4.1 checked only `update-to` and treated it as evidence the current record was retracted —
backwards from its actual, documented meaning.** This is fixed in v0.4.2.

## Exact mapping table

| Field on current record | `type` value | Meaning for CURRENT record | `is_retracted` | `is_corrected` | `record_role` |
|---|---|---|---|---|---|
| `updated-by` entry | `retraction` | Current record has been retracted; linked DOI is the notice | `True` | — | `article` |
| `update-to` entry | `retraction` | Current record IS the retraction notice; linked DOI is the retracted work | `False` | — | `retraction_notice` |
| `updated-by` entry | `correction`/`erratum`/`clarification` | Current record has a correction; linked DOI is the notice | — | `True` | `article` |
| `update-to` entry | `correction`/`erratum`/`clarification` | Current record IS the correction notice; linked DOI is the corrected work | — | `False` | `correction_notice`/`erratum_notice` (per type) |
| `updated-by` entry | `expression_of_concern` | Current record has an expression of concern; linked DOI is the notice | — | — | `article` (flagged) |
| `update-to` entry | `expression_of_concern` | Current record IS the expression-of-concern notice | — | — | `expression_of_concern_notice` |
| `update-to` or `updated-by` | `removal`/`addendum`/anything else not listed above | Preserved in `related_notices` verbatim | — | — | not classified |

## What was NOT done

**`updated-by` was not independently, directly confirmed live this session** the way `update-to`
was (the published tutorial explicitly describes `updated-by` appearing on "a record that has an
update," contrasted with `update-to` on "a record that represents an update to another one," but
the exact field name and shape shown in the walkthrough is described rather than shown as raw
JSON in the search results retrieved). The `update-to` shape IS confirmed via a real, verbatim
JSON example from Crossref's own blog. `updated-by` is treated here as documented-but-not-
independently-JSON-confirmed — implemented per the described structure (mirroring `update-to`'s
confirmed shape), flagged as slightly lower-confidence than `update-to` itself, and worth a
direct live check once network access is available.

## Unknown relation types — preserved, never classified

Per Section 3's explicit instruction: any `update-to`/`updated-by` entry whose `type` is not in
the table above is preserved verbatim in `related_notices` (including its raw `type` string and
linked DOI) but never converted into `is_retracted` or `is_corrected`. The generic `relation`
field (non-update-mechanism relationships like `is-preprint-of`) is not touched by retraction/
correction logic at all in v0.4.2 — it was never a confirmed signal for this purpose.

## Implementation

`connectors/crossref/parser.py`, `CROSSREF_UPDATE_TYPE_SEMANTICS` dict (keyed by `(direction,
type)` where direction is `"update-to"` or `"updated-by"`) + `_parse_retraction_correction()` —
direct lookup only, no substring matching anywhere in this logic.

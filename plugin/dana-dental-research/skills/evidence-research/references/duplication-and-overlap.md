<!--
REFERENCE-ID: duplication-and-overlap
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
New in v1.2. Executable implementation: `evidence/overlap.py`, building on
`connectors/shared/deduplication.py`.
-->

# Duplication and Overlap

Loaded by: evidence-research, quality-control.

Stops the same finding from being counted twice, without deleting evidence to achieve it.

## Four distinct things, routinely conflated

| Type | What it is | Merge? |
|---|---|---|
| **DUPLICATE_RECORD** | The same paper retrieved twice — two connectors, two queries | Yes, on a strong identifier with agreeing titles |
| **SAME_STUDY_MULTIPLE_REPORTS** | One trial published as several papers — primary report, longer follow-up, subgroup analysis | **No** — cluster and count once |
| **UPDATED_SYSTEMATIC_REVIEW** | A later review superseding an earlier one on the same question | **No** — prefer the update, retain the original |
| **OVERLAPPING_META_ANALYSIS** | Two reviews pooling substantially the same primary studies | **No** — prefer the broader, retain the other |

Only the first is a duplicate in the bibliographic sense. The other three are real, separate
publications whose *evidence* overlaps. Counting them as independent inflates the apparent weight
of the evidence base; deleting them loses information.

## Counting rule

**Each overlap cluster contributes ONE independent study**, however many papers it produced.
Every paper keeps its citation and its row in the evidence table.

## Preferred, and retained

Prefer the newest or highest-quality synthesis — **but preserve older relevant evidence when it
materially changes interpretation.** A 2024 review that excluded the long-follow-up cohort a 2016
review included does not supersede it; it answers a narrower question more recently. Recency is
not quality (`source-hierarchy-and-ranking.md`).

So every finding carries `preferred` **and** `retained`, and `supersedes_entirely` is set only
when an update explicitly states it replaces the earlier version. Nothing is deleted.

## Detection signals — structured only

- **Same study:** a shared trial registration identifier. Topic similarity is never used — two
  papers about the same intervention are not thereby the same trial.
- **Updated review:** same title stem, later year, and explicit update wording in the title.
- **Overlapping syntheses:** ≥50% of the smaller review's included primary studies shared, where
  the caller established what each review included.

## Bibliographic de-duplication is delegated

`connectors/shared/deduplication.py` keeps the v0.4.1 strong-identifier discipline: a shared DOI
with substantively disagreeing titles is a `FLAGGED_CONFLICT` and the records are kept separate,
never silently merged. A strong-identifier match that disagrees on substance is more likely a
data-quality problem than a genuine duplicate.

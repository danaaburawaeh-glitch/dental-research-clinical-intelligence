<!--
REFERENCE-ID: duplication-and-overlap
VERSION: 1.2.0-rc
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


## Cohort overlap assessment (v1.2 RC)

Registration-identifier clustering is exact and safe, and it is blind to the commonest real
overlap in dentistry: two retrospective reports of the same patient cohort, from the same unit,
years apart, with no registration identifier anywhere.

`evidence/overlap.py`'s `assess_cohort_overlap()` grades the suspicion instead of resolving it:

| Level | Reached when | Independent studies |
|---|---|---|
| **CONFIRMED_OVERLAP** | an explicit shared identifier, or a linkage stated in one of the records | 1 |
| **PROBABLE_OVERLAP** | ≥2 strong features agree, with ≥1 supporting feature | 1 (pending verification) |
| **POSSIBLE_OVERLAP** | 1 strong feature with weaker corroboration, or ≥3 supporting features | **not established** |
| **NO_OVERLAP_SIGNAL** | nothing above — including shared authorship alone | 2 |

**Strong features:** shared institution · study-period overlap · identical sample size.
**Supporting features:** same intervention/material · same country or site · same population
description · same follow-up window · nested sample size.
**Recorded but never counted:** shared authors.

### The rules

- **CONFIRMED is never reached by accumulating circumstantial features**, however many. It
  requires an identifier or a stated linkage.
- **Shared authorship alone is never an overlap signal.** Research groups publish repeatedly on
  their own subject with different patients; treating co-authorship as sufficient would collapse
  every productive unit into a single study. It is reported, and it does not count.
- **POSSIBLE and PROBABLE reduce the confidence available for pooled interpretation. Neither
  deletes a study.** Both citations are preserved in every case; `deletes_a_study` is a property
  that is always False, so the guarantee is testable rather than merely stated.
- **POSSIBLE leaves the independent-study count unresolved** rather than guessing one or two —
  the honest answer is that it is not established.
- **Every assessment names the features that triggered it**, three-valued (agrees / differs / not
  established), so "we could not tell" is never scored as "no".

### Worked case (real, from validation)

PMID 22259802 (Beier 2012, Medical University Innsbruck, veneers placed 1987–2009, n=318) and
PMID 11203615 (Dumfahrt 2000, same institution, shared author, n=191). Shared institution +
overlapping study period + same intervention + same country + nested sample size →
**PROBABLE_OVERLAP**. Counted once; both citations retained; the overlap reported as probable,
not established.

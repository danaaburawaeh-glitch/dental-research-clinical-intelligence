<!--
REFERENCE-ID: source-hierarchy-and-ranking
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
New in v1.2. Executable implementation: `evidence/rank.py`. DEL-7 itself is unchanged and remains
canonically defined in del7-evidence-hierarchy.md.
-->

# Source Hierarchy and Ranking

Loaded by: evidence-research, quality-control.

**DEL-7 is preserved exactly.** This file adds only the ordering rules that sit on top of it.

## Recency never automatically outranks methodological quality

Sorting by date is the default behaviour of every retrieval interface in existence, PubMed's
included. A results list sorted newest-first is read as best-first, and a 2025 narrative review
lands above a 2014 meta-analysis for no reason other than the calendar. The pull toward
date-ordering is structural, not a lapse of judgement.

So `evidence/rank.py` **does not accept publication year as a sort key**; `sort_by_recency()`
exists only to raise `NotImplementedError` and explain why.

## The ordering actually used

1. **DEL-7 tier**, adjusted one step for directness (below)
2. **Certainty**
3. **Directness**
4. **Recency** — only among sources equal on all three, and flagged in the output when applied

## The directness adjustment

INDIRECT or UNKNOWN directness costs **one tier position**, for ordering purposes only. This is
how `evidence-conflict-resolution.md`'s requirement — that directness can outweigh a raw tier
advantage — becomes expressible.

One step, not more. A DIRECT case report still does not outrank a partially direct systematic
review; the adjustment lets directness break a near-tie, not overturn the hierarchy. **The DEL-7
tag itself is never changed** — only the position in the list.

## Tier inversions are reported

Where a lower-tier source ends up ranked above a higher-tier one, the ordering names both and
gives the reason. A ranking that inverts the hierarchy silently is worse than one that does not
invert it at all.

## Off-ladder tags are separated, not sorted low

(LAB) · (IFU) · (REG) · (KOL) · (JUDG) · (OPS) · (UNVER) are listed separately from the clinical
ordering. They are not weak clinical evidence — they are not clinical evidence. Placing a bench
study "below L4 but above nothing" in a list a reader scans as a ranking of clinical evidence
invites exactly the reading the laboratory firewall forbids.

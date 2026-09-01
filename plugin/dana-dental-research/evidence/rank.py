"""
evidence/rank.py  —  SOURCE HIERARCHY AND ORDERING (v1.2)

Preserves DEL-7 exactly as `del7-evidence-hierarchy.md` defines it, and adds one rule the v1.2
brief makes explicit: **recency never automatically outranks methodological quality.**

WHY THIS NEEDS ENFORCING IN CODE
--------------------------------
Sorting by date is the default behaviour of every retrieval interface in existence, including
PubMed's own. A results list sorted newest-first is read as best-first, and a 2025 narrative
review lands above a 2014 meta-analysis for no reason other than the calendar. The pull toward
date-ordering is structural, not a lapse of judgement, so `rank()` simply does not accept a
publication year as a sort key — `sort_by_recency()` exists only to raise and explain.

THE ORDERING ACTUALLY USED
--------------------------
    1. DEL-7 tier            what kind of source it is
    2. Certainty             how much confidence the body of evidence justifies
    3. Directness            whether it answers THIS question
    4. (tie-break) recency   only among sources equal on all three, and flagged when applied

Directness feeds in twice: once as a one-step adjustment to the tier (see
`RankedItem.effective_tier`), and once as the final ordering key.

Directness can legitimately outrank tier — a highly applicable cohort study can be worth more
for a specific question than an indirect systematic review, exactly as
`evidence-conflict-resolution.md` requires. `rank()` reports the ordering it produced along with
the reasoning, so a tier inversion is visible rather than silent.
"""
import _paths  # noqa: F401

import certainty as ce
import directness as dr

# DEL-7 tiers in descending order of standing as a SOURCE TYPE. Non-clinical tags sit outside
# the clinical ladder entirely rather than at its bottom — they are not weak clinical evidence,
# they are not clinical evidence.
DEL7_ORDER = ("L1", "L2", "L3", "L4")
OUTSIDE_CLINICAL_LADDER = ("LAB", "IFU", "REG", "KOL", "JUDG", "OPS", "UNVER")

_TIER_RANK = {tag: len(DEL7_ORDER) - i for i, tag in enumerate(DEL7_ORDER)}
_CERTAINTY_RANK = {ce.HIGH: 4, ce.MODERATE: 3, ce.LOW: 2, ce.VERY_LOW: 1, ce.NOT_ASSESSABLE: 0}
_DIRECTNESS_RANK = {dr.DIRECT: 3, dr.PARTIALLY_DIRECT: 2, dr.UNKNOWN: 1, dr.INDIRECT: 0}

RECENCY_RULE = (
    "Recency is not quality. A newer publication does not outrank an older one on date alone; "
    "publication year is used only to break a tie between sources equal on DEL-7 tier, "
    "certainty and directness, and its use is flagged when it happens."
)


class RankedItem:
    def __init__(self, record_id, del7_tag, certainty_rating, directness_verdict,
                 publication_year=None, design=None):
        self.record_id = record_id
        self.del7_tag = del7_tag
        self.certainty_rating = certainty_rating
        self.directness_verdict = directness_verdict
        self.publication_year = publication_year
        self.design = design

    @property
    def on_clinical_ladder(self):
        return self.del7_tag in _TIER_RANK

    @property
    def effective_tier(self):
        """
        The DEL-7 tier, adjusted by directness.

        `evidence-conflict-resolution.md` requires that directness can outweigh a raw tier
        advantage — an indirect systematic review does not answer a specific clinical question
        better than a directly applicable cohort study. A strict tier-first ordering makes that
        impossible to express, so a source that does not answer the question costs one tier step:

            INDIRECT or UNKNOWN directness  ->  one tier lower, for ordering purposes only

        One step, not more. A DIRECT case report still does not outrank a partially direct
        systematic review; the penalty lets directness break a near-tie, not overturn the
        hierarchy. The DEL-7 tag itself is never changed — only the position in this list — and
        every resulting inversion is reported by `rank()`.
        """
        base = _TIER_RANK.get(self.del7_tag, 0)
        if self.directness_verdict in (dr.INDIRECT, dr.UNKNOWN):
            return max(base - 1, 0)
        return base

    def key(self):
        return (self.effective_tier,
                _CERTAINTY_RANK.get(self.certainty_rating, 0),
                _DIRECTNESS_RANK.get(self.directness_verdict, 0))

    def to_dict(self):
        return {"record_id": self.record_id, "del7_tag": self.del7_tag,
                "certainty": self.certainty_rating, "directness": self.directness_verdict,
                "publication_year": self.publication_year,
                "on_clinical_ladder": self.on_clinical_ladder}


def sort_by_recency(items):
    """Deliberately unavailable."""
    raise NotImplementedError(
        "Ranking evidence by publication date is not supported. " + RECENCY_RULE +
        " Use rank(), which orders by DEL-7 tier, certainty and directness.")


def rank(items):
    """
    items: list of RankedItem.

    Returns {"ranked": [...], "off_ladder": [...], "tier_inversions": [...],
             "recency_tiebreaks": [...]}.

    Off-ladder sources (LAB/IFU/REG/KOL/JUDG/OPS/UNVER) are separated out rather than sorted
    into the clinical ordering, so nothing places a bench study "below L4 but above nothing" in
    a list a reader will scan as a ranking of clinical evidence.
    """
    on_ladder = [i for i in items if i.on_clinical_ladder]
    off_ladder = [i for i in items if not i.on_clinical_ladder]

    ordered = sorted(on_ladder, key=lambda i: i.key(), reverse=True)

    recency_tiebreaks = []
    # Apply recency only within groups identical on all three real criteria.
    final = []
    group = []
    last_key = None
    for item in ordered + [None]:
        key = item.key() if item is not None else object()
        if last_key is not None and key != last_key and group:
            if len(group) > 1 and any(g.publication_year for g in group):
                group.sort(key=lambda g: g.publication_year or 0, reverse=True)
                recency_tiebreaks.append({
                    "record_ids": [g.record_id for g in group],
                    "note": ("These sources are equal on DEL-7 tier, certainty and directness. "
                             "Publication year was used only to order them among themselves. "
                             + RECENCY_RULE),
                })
            final.extend(group)
            group = []
        if item is not None:
            group.append(item)
            last_key = key
    final.extend(group)

    tier_inversions = []
    for i, higher in enumerate(final):
        for lower in final[i + 1:]:
            if _TIER_RANK.get(higher.del7_tag, 0) < _TIER_RANK.get(lower.del7_tag, 0):
                tier_inversions.append({
                    "ranked_above": higher.record_id, "ranked_below": lower.record_id,
                    "note": (f"{higher.record_id} ({higher.del7_tag}) is ranked above "
                             f"{lower.record_id} ({lower.del7_tag}) because its certainty "
                             f"({higher.certainty_rating}) and directness "
                             f"({higher.directness_verdict}) are higher. A DEL-7 tier advantage "
                             f"does not settle relevance to this specific question — state this "
                             f"reasoning in the output rather than presenting the order bare."),
                })

    return {"ranked": final, "off_ladder": off_ladder, "tier_inversions": tier_inversions,
            "recency_tiebreaks": recency_tiebreaks, "recency_rule": RECENCY_RULE}

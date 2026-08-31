<!--
REFERENCE-ID: evidence-directness
VERSION: 0.3
CANONICAL-OWNER: evidence-research (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-08-29
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
v0.3: DEL-7 tag definitions now live canonically in del7-evidence-hierarchy.md — this file
retains only the directness/match-rating mechanics. See also clinical-applicability.md for the
two additional applicability dimensions (feasibility-locally, patient-fit) this file does not
cover, and evidence-conflict-resolution.md for how directness modifies interpretation when two
DEL-7 tiers disagree.
-->

# Evidence Directness Engine

Loaded by: evidence-research, quality-control.

## Purpose
DEL-7 evidence level alone is not sufficient. High-level evidence (e.g. L2 systematic review) can
still be indirect for the specific clinical question being asked.

## For each meaningful evidence item, classify
1. DEL-7 level (L1/L2/L3/L4/LAB/IFU/REG/JUDG/OPS/KOL/UNVER — see del7-evidence-hierarchy.md).
2. Directness: DIRECT / PARTIALLY DIRECT / INDIRECT, relative to the actual clinical question.
3. Match ratings, each HIGH / MODERATE / LOW (comparator may be N/A):
   - Population match
   - Intervention match
   - Comparator match
   - Outcome match
   - Timeframe match
   - Setting/applicability match

## Worked example
A systematic review of porcelain veneers in general may be L2. If the actual question is
"minimal-prep veneers surviving beyond 10 years" and the review pools mixed preparation designs and
shorter follow-ups, the correct tagging is:
L2, PARTIALLY DIRECT or INDIRECT (population/intervention/timeframe match: LOW-MODERATE), not "L2,
direct proof."

## Hard rule
Never silently upgrade indirect evidence to direct proof. State the directness and match ratings
alongside the DEL-7 tag whenever the evidence item materially supports a consequential claim.

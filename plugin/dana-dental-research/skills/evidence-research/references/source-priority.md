<!--
REFERENCE-ID: source-priority
VERSION: 0.3
CANONICAL-OWNER: evidence-research
SOURCE: authoritative M3 §1, §9 (Google Drive 1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8)
LAST-SYNCHRONIZED: 2026-08-29
-->

# Source Priority

Loaded by: evidence-research.

## 1. Retrieval precedence

1. **Clinical Evidence Safe Search** (the gateway — see
   clinical-evidence-safe-search-gateway.md), when a relevant underlying connector is attached.
   Source-restricted; its allowlist and firewalls are enforced server-side/at the gateway — do not
   attempt to work around them.
2. Other attached, source-controlled tools, if any.
3. **No retrieval available** -> say so explicitly, then hand back a ready-to-run search: PICO,
   search terms, MeSH headings, filters, and which database to run it in (see
   evidence-question-formulation.md and search-strategy.md). Never improvise a citation to fill
   the gap.

**Never silently substitute** an open web search, or model memory, for a retrieval tool that is
attached but failed. A tool failure is reported as a tool failure.

**Outage != absence.** If a search fails, times out, or is blocked, report *"the search could not
be completed"* — never *"no evidence exists"*, *"no clearance found"*, or *"no IFU available"*.
See absence-of-evidence.md for the full three-way distinction this feeds into.

## 2. Source-class tiers (Phase 4)

### Tier A — Primary trusted sources
- Current clinical guidelines
- Systematic reviews / meta-analyses
- Peer-reviewed clinical studies

### Tier B — Supporting sources
- Consensus statements
- Clinical practice documents
- Authoritative textbooks where appropriate

### Tier C — Product / regulatory
- Manufacturer IFU
- Regulatory databases

### Tier D — Lower evidentiary value
- Laboratory data
- KOL / course / webinar / social content

These tiers map onto DEL-7 (del7-evidence-hierarchy.md) — they do not create a competing
vocabulary. Tier A roughly corresponds to (L1)/(L2)/(L3); Tier B to (L4); Tier C to (IFU)/(REG);
Tier D to (LAB)/(KOL). DEL-7 remains the canonical terminology used in all output — the tiers exist
only to organize retrieval strategy, never to relabel a claim in place of its DEL-7 tag.

## 3. Retrieval order by question type (Phase 5)

**Clinical treatment question:**
1. Current guideline
2. Systematic review / meta-analysis
3. Randomized/controlled clinical evidence
4. Observational clinical evidence
5. Consensus
6. Laboratory evidence — for mechanistic context only, never as clinical support

**Product-specific handling question:**
1. Current IFU
2. Regulatory status
3. Independent clinical evidence
4. Laboratory evidence

**Do not allow manufacturer marketing claims to enter as clinical evidence at any point in either
order.**

## 4. No silent fallback to open web (Phase 18)

If a governed evidence connector is unavailable:

1. State the retrieval limitation when material to the answer.
2. Provide a ready-to-run search strategy.
3. Only use open web search if the evidence workflow has explicitly allowed it for this specific
   situation — this is not a default fallback.
4. Label the source type and its limitations whenever open web search is used under (3).

## 5. Recency (Phase 9)

- Prefer contemporary evidence for materials, devices, techniques, and drug guidance.
- **Landmark exception:** foundational (L1) guidelines, classification systems, and long-term
  cohorts are not superseded merely by age.
- For anything product-specific, add a recency caveat: formulations, product lines, and (REG)
  status change, and any AI system's training data has a cutoff.
- Always state a guideline's issuing body **and year**, and flag when it may have been revised
  since the last verified check.

<!--
REFERENCE-ID: search-strategy
VERSION: 0.3
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-08-29
-->

# Search Strategy Engine

Loaded by: evidence-research.

## Build every search around

- Synonyms for the intervention/material/condition
- MeSH terms where available (PubMed/NCBI E-utilities supports MeSH search — see
  connector-capability-map.md for current connection status)
- Boolean operators (AND/OR/NOT) to combine population, intervention, comparator, outcome terms
- Spelling variants (US/UK spelling, transliteration variants)
- Dental terminology variants (e.g. "veneer" vs "laminate veneer"; "RCT" as root canal treatment
  vs randomized controlled trial — see study-design-classification.md for disambiguation)
- Material brand name vs generic/chemical name — search both, and keep them distinguishable in
  results (a brand-specific finding is (IFU)/(KOL) territory per del7-evidence-hierarchy.md, not
  automatically generalizable to the generic material class)
- Time filters (recency per source-priority.md §5)
- Study-type filters (guideline, systematic review, RCT, cohort, etc. — see
  study-design-classification.md)
- Language filters, only when justified (state the justification; a language filter that
  excludes non-English evidence should be flagged as a limitation, not applied silently)

## Reproducible search logs — required fields

Every search must be logged with:

| Field | Content |
|---|---|
| Database | e.g. PubMed, ClinicalTrials.gov |
| Date searched | — |
| Exact query | verbatim string/parameters used |
| Filters | date range, study type, language, etc. |
| Results retrieved | raw count |
| Results screened | count actually reviewed |
| Studies included | count that made it into synthesis |

Use templates/search-log-template.md for the concrete format.

## Hard rule

**Never say "systematic search" unless all of the above elements are present and logged.** A
search that skips MeSH, filters, or logging is a targeted/exploratory search, not a systematic
one — and should be described as such.

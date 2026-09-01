<!--
REFERENCE-ID: search-strategy
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
v1.2: PICO-aware query construction and the two structural rules against over-broad OR
expansion. Executable implementation: `evidence/search_builder.py`.
-->

# Search Strategy Engine

Loaded by: evidence-research.

## The two structural rules (v1.2)

v1.1.0's own live validation recorded the failure these prevent (connector-capability-map.md, T1
test 7): the query `zzqxdental unobtainium periodontal flurbotron` returned **149,830 matches**
over the remote transport, because the terms were OR-expanded rather than phrase-searched. A large
result count on a nonsense phrase is not a body of evidence; it is the search falling apart
quietly, in the one direction that looks like success.

1. **OR within a concept, AND between concepts.** Synonyms of "veneer" are alternatives to each
   other. "Veneer" and "survival" are not. A flat OR across concepts retrieves everything about
   either — which is why an over-broad query returns six figures of results and a reviewer
   concludes the topic is well studied.

2. **Multi-word free-text terms are phrase-quoted.** `"minimally invasive veneer"` is one concept;
   `minimally AND invasive AND veneer` is three.

`evidence/search_builder.py` builds queries this way by construction and flags a top-level OR as
a CRITICAL warning. It also warns when a single concept carries more than eight alternatives —
not a limit, but a prompt to check they are genuine synonyms of one idea rather than related but
different concepts.

## Keep the user's own concept visible

The clinician's own words survive verbatim into the search log as `user_concept`, next to the
built query and next to PubMed's own `query_translation`. A reader needs to see whether the
question they asked is the question that was searched — a translated MeSH string alone hides the
answer to that.

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
| User's own terms | verbatim, as the question was asked |
| Exact query | verbatim string/parameters used |
| PubMed's translation | `query_translation` as returned, proving the search actually ran |
| Filters | date range, study type, language, etc. |
| Results retrieved | raw count |
| Results screened | count actually reviewed |
| Studies included | count that made it into synthesis |
| Connector status | SUCCESS / ZERO_RESULTS / TIMEOUT / … per CONNECTOR_FAILURE_MODEL.md |

Use templates/search-log-template.md for the concrete format.

## Hard rule

**Never say "systematic search" unless all of the above elements are present and logged.** A
search that skips MeSH, filters, or logging is a targeted/exploratory search, not a systematic
one — and should be described as such.

`SearchStrategy.is_systematic` implements this: it requires at least one MeSH term, at least one
filter, a date searched, and all three counts. Anything short of that renders as
`targeted/exploratory` in the log, automatically.

A **language filter** without a stated justification is flagged. It excludes evidence and is
declared as a limitation, never applied silently.

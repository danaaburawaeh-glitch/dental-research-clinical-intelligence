# CHANGELOG — v1.1.0 → v1.2.0

**Released:** 2026-09-02 · **Dental AI Evidence Intelligence Engine**
**Status: RELEASED.** Merged to `main`, tagged `v1.2.0`.

## What changed, in one line

The system stopped treating "the citation is real" as an answer to "is this good evidence?"

## The architectural change

Six stages are now separate, and enforced as separate in code:

```
RETRIEVAL -> VERIFICATION -> APPRAISAL -> CERTAINTY -> SYNTHESIS -> CLINICAL APPLICABILITY
```

Each of these collapses into the one before it under pressure, and each collapse is one plausible
sentence away. `evidence/pipeline.py` makes the boundaries load-bearing: a stage cannot run before
its predecessor, and synthesis refuses records that have not cleared verification and certainty.

## New: `evidence/` (16 modules, 3 test suites, 1 benchmark)

### Citation Verification 2.0 — `evidence/citation_verification.py`

Four states became seven, across two axes that are both always reported:

- **Bibliographic:** VERIFIED · VERIFIED_WITH_METADATA_DISCREPANCY · PARTIALLY_VERIFIED ·
  NOT_VERIFIED
- **Publication integrity:** ACTIVE · RETRACTED · CORRECTED · EXPRESSION_OF_CONCERN · UNCHECKED

Integrity dominates the headline state; the bibliographic reading is preserved in its own field.

**The year rule.** A disagreement confined to online-first vs print/issue year, with DOI, title,
authors and journal all matching, is now `VERIFIED_WITH_METADATA_DISCREPANCY` — not
`NOT_VERIFIED`. v1.1.0's own live validation hit this case (T1 test 5): a real record with a real
DOI was reported `NOT_VERIFIED` because Crossref and PubMed disagreed on the year. That was wrong
in substance and it taught the reader to discount the verifier, which is worse than the original
error. The discrepancy is still reported in full, with both values and both source names, and is
resolved neither way.

**No single verification score.** Seven components (`DOI_MATCH`, `PMID_MATCH`, `TITLE_MATCH`,
`AUTHOR_MATCH`, `JOURNAL_MATCH`, `YEAR_MATCH`, `RETRACTION_STATUS`) stay individually visible. A
scalar would be read as a quality measure and would flatten the distinction between
NOT_COMPARABLE (an absence) and MISMATCH (a conflict).

### Study design classification — `evidence/study_design.py`

Eighteen designs, classified from PubMed's controlled PublicationType and MeSH vocabularies, never
from free text for the load-bearing designs. Every classification carries provenance: REPORTED
(structured field) / INFERRED (free text, with a mandatory recorded basis) / UNKNOWN. A
classification with UNKNOWN provenance receives no supporting-evidence DEL-7 tier.

Registry records are classified `Clinical trial registry record` and carry
**REGISTRY ONLY — NOT EVIDENCE OF EFFICACY** permanently.

One documented addition to the brief's vocabulary: `Cohort study (direction not reported)`, used
when and only when PubMed establishes a cohort design without establishing its direction. Choosing
a direction would be an invention; collapsing to "Other" would lose the (L3) mapping.

### Evidence appraisal — `evidence/appraisal.py`

Fourteen fields, each holding a value **and** its provenance. An INFERRED value without a stated
basis is refused at construction; a value with UNKNOWN provenance is refused; a bare value cannot
be passed at all. Completeness is reported as counts and a named list of what is missing — never a
percentage, which reads as a grade.

Formal tools are refused rather than approximated: `risk_of_bias()` will not attach RoB 2,
ROBINS-I, AMSTAR 2 or QUADAS-2 when the tool does not apply to the design, or when the tool's own
required domains were not supplied.

### Certainty engine — `evidence/certainty.py`

HIGH / MODERATE / LOW / VERY LOW / **NOT ASSESSABLE**, from GRADE's domains and starting points.
Three conservative properties:

1. **It never upgrades.** GRADE's upgrade criteria need a full-text reading this system does not
   perform; applying them from an abstract raises confidence on a guess.
2. **Missing domains produce NOT ASSESSABLE**, never a default. It also cross-checks the appraisal
   — a domain cannot be judged over a field the appraisal records as UNKNOWN.
3. **Laboratory, computational and registry records are off the scale**, not at the bottom of it.

A systematic review of non-randomized studies starts LOW, not HIGH; where what a review pooled was
not established, the result is NOT ASSESSABLE.

`AUTHOR-REPORTED GRADE` is a separate channel, requiring a named outcome and an attribution. The
system's own rating is labelled `DENTAL AI STRUCTURED CERTAINTY ASSESSMENT` and the word GRADE is
never attached to it.

### Directness — `evidence/directness.py`

Six dimensions (population, procedure, material, comparison, outcome, follow-up), four verdicts
(DIRECT / PARTIALLY DIRECT / INDIRECT / UNKNOWN), one documented aggregation rule. LOW dominates
UNKNOWN: a known mismatch is a finding, an unknown is an absence, and a finding outranks an
absence. Laboratory, computational and registry records are capped at INDIRECT, with the cap
reported rather than silent.

### Systematic review intelligence — `evidence/sr_extraction.py`

Fourteen review-level fields, with **NOT REPORTED** (the source was read and does not state it)
kept distinct from **NOT AVAILABLE** (the source was not read at that depth). No connector in this
plugin supplies full text, so NOT AVAILABLE is the default, and a field marked as full-text-sourced
is refused while `full_text_retrieved` is False.

### Duplication and overlap — `evidence/overlap.py`

Four distinct relationships, only the first of which is a merge candidate: duplicate record ·
same study reported in multiple papers · updated systematic review · overlapping meta-analyses.
Each cluster counts as **one** independent study. Nothing is deleted — every finding carries
`preferred` **and** `retained`, because an older synthesis can still materially change
interpretation.

### Numeric evidence gate — `evidence/numeric_gate.py`

The rule was already written; this makes it executable. The gate scans the **finished text** of a
Clinical Bottom Line and fails it on any survival %, failure %, risk ratio, odds ratio, hazard
ratio, mean difference or confidence interval that is not registered against a retrieved, verified
source. Numeric hallucination is not a reasoning failure that better instructions fix — "veneer
survival is approximately 95% at 10 years" is the most fluent sentence available on the subject,
and a rule competing against fluency loses. A gate that scans the output competes against nothing.

### Conflicting evidence — `evidence/conflict.py`

EVIDENCE CONFLICT objects carrying both sources in full, five comparison dimensions each answered
(including "not established"), a candidate explanation, and what would settle it. **The module
provides no averaging or pooling function at all** — that absence is the design, and a test asserts
it. A conflict is also distinguished from a difference in evidence quality: where one side is
materially weaker, that is a quality note, not an equal counterweight.

### Search quality — `evidence/search_builder.py`

PICO-aware construction with two structural rules: **OR within a concept, AND between concepts**,
and **multi-word terms phrase-quoted**. This addresses the defect v1.1.0's own validation recorded
(T1 test 7): a nonsense phrase returned 149,830 matches because the terms were OR-expanded. The
user's own words survive verbatim into the log as `user_concept`, and `is_systematic` refuses the
word "systematic" for a search without MeSH terms, filters and complete counts.

### Ranking — `evidence/rank.py`

DEL-7 tier, certainty, directness. **Publication year is not an accepted sort key**;
`sort_by_recency()` exists only to raise and explain. Directness costs an indirect source one tier
position — one step, enough to break a near-tie, not enough to overturn the hierarchy — and every
resulting inversion is reported with its reasoning.

### Claim–evidence linking — `evidence/claim_link.py`

Every consequential claim binds to five links at the claim itself: citation · verification state ·
study type · certainty · directness. A VERIFIED citation with LOW or NOT ASSESSABLE certainty and
no stated limitation is flagged, because the verification state would otherwise be read as
strength.

### Evidence table, bottom line, output modes

`evidence_table.py` — fourteen columns, no cell ever blank (NOT REPORTED / NOT AVAILABLE /
NOT ASSESSED are distinct). `bottom_line.py` — seven sections, all rendered including the empty
ones, with sections 1 and 2 gated by certainty and directness rather than by citation status; a
claim that does not meet the bar is **moved**, with the reason stated. `output_modes.py` — five
modes with section contracts, and identical gates across all five: a shorter mode is not a
less-checked one.

## Bug fixed in the shared layer

`connectors/shared/normalization.py` — `authors_overlap()` took the last token of an author string
as the surname unconditionally. PubMed renders "Smith J"; Crossref renders "John Smith". The last
token of the former is "J", which matches no Crossref surname, so genuine PubMed × Crossref pairs
systematically failed on the author component. A new `surname()` helper drops trailing initials
tokens and handles both renderings and compound surnames in either order. This was found by the
v1.2 test suite and affects v1.1 behaviour too.

## What did NOT change

- **The four MCP tool contracts.** `search_pubmed`, `search_systematic_reviews`,
  `verify_citation`, `search_clinical_trials` are untouched. Appraisal reasoning lives in the
  plugin's skill layer; the MCP server stays a retrieval service and has not become a clinical
  decision engine.
- **`.mcp.json`** — unchanged.
- **Connector status.** No source added, none upgraded. Cochrane/CENTRAL, Embase and Scopus remain
  NOT IMPLEMENTED; `~~clinical-guidelines`, `~~manufacturer-ifu` and `~~regulatory-saudi` remain
  NOT CONNECTED.
- **DEL-7.** Preserved exactly. `evidence/rank.py` reads the hierarchy; it does not redefine it.
- **The clinical layer.** `clinical/` is unchanged. All 241 of its existing checks pass.
- **The nine skills.** All nine remain; no clinical feature was added or removed. Six skills'
  reference sets were updated for the v1.2 evidence rules.

## Validation

| Suite | Checks | Result |
|---|---|---|
| `evidence/tests/test_safety_nonnegotiable.py` | 65 | PASS |
| `evidence/tests/test_evidence_engine.py` | 115 | PASS |
| `evidence/tests/test_benchmark.py` | 54 | PASS |
| `clinical/tests/test_clinical_layer.py` | 60 | PASS |
| `clinical/tests/test_clinical_completion.py` | 66 | PASS |
| `clinical/tests/test_identity_policy.py` | 46 | PASS |
| `clinical/tests/test_protocol_approval.py` | 24 | PASS |
| `clinical/tests/test_docs_consistency.py` | 45 | PASS |
| `connectors/clinical_trials/tests/test_clinical_trials.py` | 50 | PASS |
| `connectors/sfda/tests/test_saudi_governance.py` | 50 | PASS |

All executed, none reviewed-only, no network.

## Benchmark

38 dental evidence questions across ten domains (prosthodontics, esthetic dentistry, veneers,
implants, adhesive dentistry, periodontics, endodontics, orthodontics, digital dentistry, AI in
dentistry), with thirteen deliberate trap types executed against the engine.

**Every identifier in the benchmark is a synthetic `FIXTURE-`.** No PMID, DOI or NCT ID appears in
the file, and three tests assert this. A validation set that seeds realistic-looking identifiers
into the repository creates precisely the artefact the engine exists to prevent — a plausible
citation with nothing behind it, available for any later reader to lift into an output.

## Release status

**RELEASED as v1.2.0.** Manifest version `1.2.0`.

Two further rounds of work followed the initial build and are included in this release: four
defects found by real-world evidence validation (see the commit history), and the two release
blockers closed in the release candidate — T1/T2 citation-verification parity and graded cohort
overlap detection. The remote MCP server was deployed separately at v1.1.0 / verification
contract 1.1.

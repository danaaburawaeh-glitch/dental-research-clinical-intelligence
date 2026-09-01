# Dental Research & Clinical Intelligence v1.2.0

**The Evidence Intelligence Engine.**

v1.1 could find and verify a paper. v1.2 can tell you what that paper is worth — and, just as
importantly, when it cannot tell you.

---

## The rule this release is built around

> **A bibliographically VERIFIED citation does NOT mean strong evidence.**

Verification answers one narrow question: is this reference real and correctly described? It says
nothing about how well the study was conducted, how much confidence the evidence justifies, or
whether it answers your question at all. Those are three further assessments, and each can fail
independently.

v1.2 separates six stages and enforces the separation in code, so a result from one can never
stand in for a result from another:

```
RETRIEVAL → VERIFICATION → APPRAISAL → CERTAINTY → SYNTHESIS → CLINICAL APPLICABILITY
```

In practice this means the system will now decline to call something well established when the
evidence does not support it — including when the citation behind it is perfectly verified.

---

## New capabilities

**Citation Verification 2.0** — seven states across two axes (bibliographic accuracy, and
publication integrity), replacing the previous three. Seven comparison components stay
individually visible; no single opaque score is produced.

**`VERIFIED_WITH_METADATA_DISCREPANCY`** — a new state for the common case where a record's
PubMed and Crossref years differ by one year, because the journal published it online in one
calendar year and in an issue the next. Identity is confirmed; only the date differs. Both years
are reported with their source, and neither is ever silently replaced. A gap beyond that
documented one-year tolerance is *not* given the benign explanation — it is reported as
unexplained.

**Evidence quality appraisal** — fourteen fields, each carrying its provenance: REPORTED (with
its source), INFERRED (with a mandatory stated basis), or UNKNOWN. Missing data stays missing.
Formal instruments (RoB 2, ROBINS-I, AMSTAR 2, QUADAS-2) are named only where they apply to the
design and their required domains were actually available.

**Structured certainty assessment** — HIGH / MODERATE / LOW / VERY LOW / NOT ASSESSABLE.
Conservative by construction: it never upgrades, unestablished domains produce NOT ASSESSABLE
rather than a default rating, and laboratory and registry records are off the clinical scale
entirely. **This is not GRADE.** Where a paper's own authors performed GRADE, their rating is
reported separately and attributed to them; this system never asserts one on their behalf.

**Systematic-review intelligence** — structured extraction of what a review reports, keeping
NOT REPORTED (the source was read and does not state it) distinct from NOT AVAILABLE (the source
was not read at that depth).

**Evidence directness** — six dimensions (population, procedure, material, comparison, outcome,
follow-up) aggregating to DIRECT / PARTIALLY DIRECT / INDIRECT / UNKNOWN. Laboratory,
computational and trial-registry records are capped at INDIRECT for any claim about patients.

**Numeric evidence gate** — scans the finished Clinical Bottom Line. Any survival or failure
percentage, risk ratio, odds ratio, hazard ratio, risk difference, mean difference, absolute risk
reduction, NNT or confidence interval that is not registered against a retrieved, verified source
fails the output. Numerical values are never reconstructed from memory.

**Retraction / correction gate** — runs before study classification, so a retracted record is
never classified as usable evidence even transiently. Retraction, correction and
expression-of-concern are three distinct states; an expression of concern is never reported as a
retraction.

**Conflicting-evidence handling** — where comparable sources disagree, an EVIDENCE CONFLICT is
produced naming both, the dimensions along which they differ, a candidate explanation, and what
would settle it. Conflicting estimates are never averaged into a middle value that appears in
neither source.

**Standardized evidence table** — fourteen columns, and no cell is ever blank: NOT REPORTED,
NOT AVAILABLE and NOT ASSESSED are three different statements.

**Clinical Bottom Line** — seven sections, all rendered including the empty ones. "Well
established" and "reasonably supported" are gated by certainty and directness, not by citation
status; a claim that does not meet the bar is moved down with the reason stated.

**Cohort overlap detection** — NO_OVERLAP_SIGNAL / POSSIBLE / PROBABLE / CONFIRMED, graded from
named features. CONFIRMED requires an explicit shared identifier or a stated linkage and is never
reached by accumulating circumstantial features. Shared authorship alone is never an overlap
signal. No study is ever deleted, and both citations are always preserved.

**Improved PubMed search construction** — PICO-aware queries: OR within a concept, AND between
concepts, with multi-word terms phrase-quoted. This prevents the over-broad OR expansion that
returns six figures of results on a query that matches nothing relevant. Your own words are
preserved verbatim in the search log next to the built query.

---

## Remote research server

The hosted Dental AI Research MCP server was updated to v1.1.0 (verification contract 1.1) so it
returns the same citation semantics as the local evidence layer. A caller no longer has to know
which transport answered in order to interpret a verdict.

The four research tools are unchanged: `search_pubmed`, `search_systematic_reviews`,
`verify_citation`, `search_clinical_trials`.

---

## What is NOT included

Stated plainly, because a research tool that overstates its coverage is worse than one with less
of it:

- **Cochrane / CENTRAL — NOT integrated.** The systematic-review search is a PubMed publication-
  type filter. It is not a Cochrane search and must not be described as one.
- **Embase — NOT integrated.**
- **Scopus — NOT integrated.**
- **Full text — not retrieved.** No connector in this plugin supplies it. Crossref provides
  bibliographic metadata only. This is why certainty assessments frequently return NOT
  ASSESSABLE: from abstracts alone, risk of bias, heterogeneity and publication bias cannot be
  established, and the system says so rather than guessing.
- **Clinical guidelines connector — NOT CONNECTED.**
- **Manufacturer IFU connector — NOT CONNECTED.**
- **SFDA regulatory connector — NOT CONNECTED (authentication required).** Saudi regulatory
  questions return REQUIRES VERIFICATION routed to the named body.

Connected sources: PubMed/NCBI, Crossref (metadata and citation verification), and
ClinicalTrials.gov API v2 (registry records only — a registration is not evidence of efficacy).

---

## Upgrading from v1.1

No action required, and no breaking change to how the plugin is invoked. The nine skills are
unchanged in name and purpose. Clinical logic is unchanged.

The visible difference is that the system is more willing to say what it does not know. Outputs
that v1.1 would have stated plainly may now carry an explicit certainty of NOT ASSESSABLE, or
appear under "what remains uncertain" rather than "what is well established". That is the
intended behaviour, not a regression.

---

## Validation

773 automated checks, all executed, none reviewed-only: 656 in the plugin (evidence engine,
safety prohibitions, benchmark, clinical layer, connectors) and 117 in the research server.

The engine was additionally validated end-to-end against live PubMed, Crossref and
ClinicalTrials.gov on a real clinical question about ceramic veneer survival. That exercise found
four defects in the engine's own gates, which were fixed before release.

---

*Dental Research & Clinical Intelligence by Dr. Dana. Designed by Dr. Dana Abu Rawaeh.*
*Clinical decision support for qualified professionals. It does not replace clinical judgement,
and it is not a substitute for a human legal, regulatory or clinical review.*

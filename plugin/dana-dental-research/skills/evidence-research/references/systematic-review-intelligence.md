<!--
REFERENCE-ID: systematic-review-intelligence
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
New in v1.2. Executable implementation: `evidence/sr_extraction.py`.
-->

# Systematic Review Intelligence

Loaded by: evidence-research.

Structured extraction of what a systematic review or meta-analysis actually reports.

## Fields extracted, where available

number of included studies · study designs included · total participants · intervention ·
comparator · follow-up · primary outcomes · pooled effect estimates · confidence intervals ·
heterogeneity · risk-of-bias method · GRADE method · publication bias assessment ·
major limitations

## Two kinds of blank — never one

| Marker | Means |
|---|---|
| **NOT REPORTED** | The source was read and does not state this. A finding about the review. |
| **NOT AVAILABLE** | The source was not read at this depth. A finding about our retrieval. |

**No connector in this plugin supplies full text.** Crossref provides metadata; PubMed provides
abstracts and structured metadata. So `NOT AVAILABLE` is the default for every field unless the
full text was genuinely obtained, and `evidence/sr_extraction.py` refuses to accept a field
marked as full-text-sourced while `full_text_retrieved` is False.

## Why this is the module most at risk of fabrication

A review's abstract typically states its headline: how many studies, a pooled estimate, sometimes
an I² value. It typically does **not** state its risk-of-bias instrument's per-domain findings,
its funnel-plot inspection, its full participant total, or its limitations.

The failure mode is specific and predictable: an abstract-derived extraction gets completed from
plausible knowledge of how such reviews are usually reported, and the resulting table looks like a
full-text extraction. Every number in it would be real-sounding and unsourced.

Two rules follow:

1. **If the full text is unavailable, do not fabricate these fields.** Return NOT REPORTED or
   NOT AVAILABLE.
2. **Do not parse numbers out of abstract prose automatically.** Reading "34 studies were
   included" from an abstract and recording it as REPORTED produces a confidently wrong table when
   the sentence was "34 studies were screened". Extraction is an explicit act by whoever actually
   read the source, and it carries their provenance.

## Provenance on every extracted field

`REPORTED` (with its source: abstract / full text / registry) · `INFERRED` (with a mandatory
stated basis) · `UNKNOWN`. An INFERRED value without a basis is refused at construction — without
one it is indistinguishable from an invention.

## Numeric fields

Study counts, participant totals, pooled estimates, confidence intervals and heterogeneity
statistics feed the Numeric Evidence Gate. Any of them appearing in a Clinical Bottom Line must
trace to a retrieved, verified source — see `numeric-evidence-gate.md`.

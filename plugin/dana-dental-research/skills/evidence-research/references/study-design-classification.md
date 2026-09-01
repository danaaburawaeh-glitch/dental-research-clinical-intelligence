<!--
REFERENCE-ID: study-design-classification
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
v1.2: fixed design vocabulary, classification provenance, and the structured-metadata-first
rule. Executable implementation: `evidence/study_design.py`.
-->

# Study Design Classification

Loaded by: evidence-research.

## The design vocabulary (v1.2, fixed)

Guideline · Systematic review · Meta-analysis · Randomized controlled trial ·
Prospective cohort · Retrospective cohort · Cohort study (direction not reported) ·
Case-control · Cross-sectional · Diagnostic accuracy study · In-vitro · Finite element ·
Case series · Case report · Narrative review · Expert opinion ·
**Clinical trial registry record** · Other

Two notes on the list itself:

- **"Cohort study (direction not reported)"** is a documented addition. PubMed's structured
  fields frequently establish that a study is a cohort study without establishing its direction.
  Choosing one would be an invention; collapsing to "Other" would lose the (L3) mapping a cohort
  study legitimately earns.
- **Animal studies and consensus statements** map to `Other` with a stated `design_detail`.
  An animal study additionally carries the laboratory firewall.

## Registry records

A **Clinical trial registry record** carries, permanently and in every output:

> **REGISTRY ONLY — NOT EVIDENCE OF EFFICACY**

It is a registration, not a study report. It is never rated on the certainty scale, is capped at
INDIRECT, and may not support an efficacy claim whatever its registered design field says. See
`registry-vs-published-evidence.md`.

## Structured metadata first — free text never, for the load-bearing designs

PubMed's PublicationType and MeSH vocabularies are controlled fields assigned by indexers. A
title or abstract is prose written to persuade. Where they disagree, the structured field wins.

Every classification therefore carries its **provenance**:

| Provenance | Means |
|---|---|
| **REPORTED** | From a controlled structured field (PublicationType / MeSH / registry) |
| **INFERRED** | From free text, with the matched phrase recorded as its mandatory basis |
| **UNKNOWN** | Nothing available to classify on — the design is not guessed |

An INFERRED classification without a stated basis is refused at construction. A classification
with UNKNOWN provenance receives no supporting-evidence DEL-7 tier: an unnamed design cannot earn
a tier.

State the design explicitly whenever a study is cited — this feeds directly into the DEL-7 tag
(del7-evidence-hierarchy.md §1) and the directness/quality appraisal steps
(evidence-directness.md, evidence-quality-appraisal.md).

## Disambiguation — mandatory

**RCT is ambiguous in dentistry and must never be used without disambiguation:**
- Randomized Controlled Trial (a study design — maps toward (L3))
- Root Canal Treatment (a clinical procedure — not a study design at all)

When either meaning is possible from context, spell it out on first use in any output. Do not
rely on the reader inferring which sense is meant from surrounding text alone.

**In code this is absolute:** the randomized-trial classification is derived only from PubMed's
structured PublicationType field. The letters "RCT" appearing in a title or abstract never
produce it — see `evidence/study_design.py` and `connectors/pubmed/models.py`.

## Classification precedes DEL-7 tagging

This file's output (a named design) is an input to del7-evidence-hierarchy.md §1's tag-assignment
table — a study cannot be correctly DEL-7 tagged without first correctly naming its design. A
"review" with no stated search method is a narrative review (-> L4), not a systematic review
(-> L2), regardless of what the source itself calls it.

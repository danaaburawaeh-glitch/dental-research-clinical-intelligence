<!--
REFERENCE-ID: evidence-intelligence-architecture
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
New in v1.2. Executable implementation: `evidence/pipeline.py`.
-->

# Evidence Intelligence Architecture — the six stages

Loaded by: evidence-research, quality-control.

v1.2 turns the research retrieval system into an evidence intelligence engine by separating six
things that were previously allowed to run together:

```
RETRIEVAL  ->  VERIFICATION  ->  APPRAISAL  ->  CERTAINTY  ->  SYNTHESIS  ->  APPLICABILITY
```

| Stage | Answers | Never answers |
|---|---|---|
| **RETRIEVAL** | Does the record exist, and was it fetched? | Whether it is any good |
| **VERIFICATION** | Is the citation accurate, and does the paper still stand? | How strong the finding is |
| **APPRAISAL** | How well was the study conducted, and what was not established? | How confident to be overall |
| **CERTAINTY** | How much confidence does this body of evidence justify? | Whether it applies to this patient |
| **SYNTHESIS** | What does the assembled evidence say, conflicts included? | Whether to do it here |
| **APPLICABILITY** | Does it apply to this patient, in this setting? | Whether it is lawful — that is the regulatory gate |

## Why the separation is enforced in code

Every one of these collapses into the one before it under pressure, and each collapse is a single
plausible sentence away:

- Retrieval becomes evidence — *"PubMed returned 431 results on this."*
- Verification becomes appraisal — *"the citation checks out, so the finding stands."*
- Appraisal becomes certainty — *"large sample, therefore reliable."*
- Certainty becomes applicability — *"high certainty, therefore do it for this patient."*

None of them announces itself. So `evidence/pipeline.py` makes the boundaries load-bearing: a
stage cannot run before its predecessor, `synthesise()` refuses records that have not passed
verification and certainty, and `stage_report()` shows which stage every conclusion came from.

## The rule the whole architecture exists to enforce

> **A bibliographically VERIFIED paper must never automatically be treated as strong evidence.**

Verification is stage two of six. Four further assessments stand between a real citation and a
clinical recommendation, and each can fail independently.

## Ordering guarantee (inherited from v0.4.3)

The retraction gate runs **inside VERIFICATION, before study classification and DEL-7 tagging**.
A retracted record must never be classified as usable evidence even transiently — see
`PIPELINE_ORDERING_AUDIT.md`. `test_safety_nonnegotiable.py` checks the ordering behaviourally,
not just the document.

## Where a retrieval count sits

A retrieval count is not an evidence count. `pipeline.retrieve()` reports both: how many records
were returned, and how many independent studies they reduce to after overlap detection
(`duplication-and-overlap.md`). Two papers reporting one trial are one study; a review and its
own update are one synthesis.

# Evidence Engine Architecture — v0.3 (HISTORICAL)

> **HISTORICAL DOCUMENT — describes v0.3.** Retained for the record. It is not a statement about the current release. For current connector status, the Clinical Protocol status and the live gap list, see `UNRESOLVED_GAPS.md` (Part A) and `connector-capability-map.md`.

## Layers, top to bottom

```
User evidence question
        |
        v
evidence-research/SKILL.md          (orchestrator — 13-step workflow, output-mode router)
        |
        v
evidence-question-formulation.md    (PICO/PECO/PIRD/SPIDER/PICo router)
        |
        v
source-priority.md                  (Tier A-D, retrieval order by question type, recency, no-
                                      silent-fallback)
        |
        v
clinical-evidence-safe-search-gateway.md   (ORCHESTRATOR/GATEWAY — formulates, selects, enforces
        |                                    firewalls, invokes, returns status, hands off downstream)
        v
connector-capability-map.md         (SOURCE-SPECIFIC CAPABILITY LAYERS — the seven ~~ placeholders;
                                      canonical CONNECTED/NOT CONNECTED status)
        |
        v
   [retrieved evidence, or a structured retrieval limitation]
        |
        v
study-design-classification.md  -->  del7-evidence-hierarchy.md  -->  evidence-quality-appraisal.md
        |                                                                       |
        v                                                                       v
evidence-directness.md  <----------------------------------------  citation-verification.md
        |                                                                       |
        v                                                                       v
absence-of-evidence.md (if applicable)          numeric-evidence-gate.md (bundled, clinical-governance)
        |                                                                       |
        +---------------------------+---------------------------+--------------+
                                     v
                    evidence-conflict-resolution.md (if sources disagree)
                                     |
                                     v
                          evidence-synthesis.md (four-bucket output)
                                     |
                                     v
                       clinical-applicability.md (case-specific rating)
                                     |
                                     v
              claim-strength-governor.md (bundled, clinical-governance — final calibration)
                                     |
                                     v
                   Output mode: QUICK / STANDARD / DEEP EVIDENCE REVIEW
```

## Why this shape

The authoritative M3 (v0.4) reads as one continuous protocol, but its content splits naturally
into three kinds of file:

1. **Orchestration** — question formulation, retrieval order, the gateway. These decide *what
   to do and in what order*, and stay thin (per the "SKILL.md should orchestrate, not be a
   textbook" instruction).
2. **Classification and appraisal** — DEL-7 tagging, directness, quality appraisal, study design.
   These are the substantive judgment-heavy content, and are where most of the genuinely new
   material from the audit landed (evidence-quality-appraisal.md, absence-of-evidence.md,
   evidence-conflict-resolution.md, clinical-applicability.md were all new in v0.3).
3. **Gating** — citation verification, numeric evidence gate, claim strength governor. These are
   pass/fail checks applied to output regardless of how the evidence was retrieved, and two of the
   three (numeric-evidence-gate.md, claim-strength-governor.md) remain canonically owned by
   clinical-governance and are only bundled here, unchanged, per the existing architecture.

## What deliberately sits outside this plugin's v0.3 scope

- **CLINICAL-PROTOCOL-08** and its Appendix A reference-reuse mechanics — deferred, tracked in
  deferred-knowledge-dependencies.md, not reconstructed.
- **M4/M5/Rosenstiel/full clinical protocol** — untouched per the v0.3 brief. The
  `~~regulatory-saudi` SOURCE-UPDATE-CONFLICT finding (SFDA now has a real open-data API) is
  recorded for M4 review, not acted on here.
- **Actual connector wiring** — nothing in this release claims a connector is `CONNECTED`. Phase
  17 research established real, documented, mostly-free APIs exist for PubMed, Crossref, Semantic
  Scholar, OpenAlex, ClinicalTrials.gov, and (with procurement) Cochrane, plus a real SFDA
  open-data API — but "documented and feasible" is not "wired and reachable in this running
  environment," and connector-capability-map.md's status column is the only place that
  distinction is allowed to be recorded as `CONNECTED`.

## File-count summary

- 1 canonical evidence-vocabulary file (del7-evidence-hierarchy.md) replacing the previously
  scattered DEL-7 restatements.
- 2 gateway/routing files (clinical-evidence-safe-search-gateway.md, source-priority.md).
- 1 question-formulation file, 1 search-strategy file, 1 study-design-classification file.
- 5 genuinely new judgment files (evidence-quality-appraisal.md, absence-of-evidence.md,
  evidence-conflict-resolution.md, clinical-applicability.md, evidence-synthesis.md).
- 3 refined existing files (evidence-directness.md, citation-verification.md,
  evidence-source-separation.md).
- 1 connector map (updated) + 1 deferred-dependency tracker (new) + 2 bundled clinical-governance
  gates (unchanged).
- 5 templates, 1 regression test file (15 scenarios).

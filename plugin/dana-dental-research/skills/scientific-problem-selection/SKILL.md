---
name: scientific-problem-selection
description: Help dental researchers select, refine and de-risk scientific questions using structured ideation, novelty assessment, feasibility, decision trees, failure planning and project synthesis.
---
# Scientific Problem Selection

## Entry modes
- Pitch a new research idea
- I am stuck in a project
- Strategic research question

## Subskills
1. Problem ideation and intuition pumps.
2. Novelty and gap assessment using evidence-research (apply references/evidence-directness.md when
   judging whether a "gap" is real or just an indirect-evidence blind spot).
3. Clinical/scientific importance and optimisation function.
4. Risk assessment: scientific, methodological, recruitment/data, execution, interpretation.
5. Fixed vs flexible parameters.
6. Decision-tree navigation and decision-flip conditions.
7. Adversity/failure playbook and pivot criteria.
8. Problem inversion and alternative framing.
9. Integration into a research strategy package.

Outputs should distinguish what is known (with DEL-7/directness tagging), what is assumed
(JUDG/HYPOTHESIS per references/claim-strength-governor.md), what is testable, and what would make
the project a no-go.

## Author identity & citation policy (v0.9.1) — global

`references/author-identity-and-citation-policy.md` applies to **every** skill and output. In
short: the person who designed this assistant is never a clinical, scientific, regulatory or
protocol authority. Her name belongs in creator attribution and ownership metadata only.

Clinic-derived rules carry `(OPS)`, `(JUDG)`, `(USER-SUPPLIED)` or `(INTERNAL PROTOCOL)` — never a
personal name. Protocols carry neutral titles. Scientific claims cite the real source, or `(UNVER)`
with a search strategy.

Enforced by `clinical/identity_policy.py` and blocked by `clinical/safety_veto.py`.

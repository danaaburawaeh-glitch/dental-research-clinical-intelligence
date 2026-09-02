---
name: clinical-case
description: Analyze a dental patient case using a governed diagnostic sequence, explicit provenance, missing-data ranking, prognosis-before-prosthesis, healthy-tooth protection, alternatives and phased treatment planning.
---
# Clinical Case Workflow

## Output language (v1.2.1) — CLINICAL MODE is the default

`references/clinical-writing-layer.md`. The engine's internal labels (HARD_BLOCKER,
INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT, POTENTIALLY_COMPROMISED, decision-profile names,
suppressed-field lists) are **never printed** in an ordinary clinician-facing answer — they are
translated into clinical prose. Lead with what you think, why, and what should happen next.
Expose internal state only when the clinician explicitly asks for audit, technical, governance,
developer or debug output.


## Clinical decision context (v1.2.1) — read before answering any case

`references/clinical-decision-context.md` governs how this skill treats missing data, wording and
prognosis. In short:

- **A missing data point may hard-block only if it can materially change THIS decision.** Ferrule,
  pulpal status and restorability are not universal gates — where they are NOT_RELEVANT to the
  decision being made, they are suppressed from the output entirely.
- **Sufficiency is reported per decision**, not per case: a case is routinely sufficient for the
  conservative option and insufficient for the irreversible one, and both halves are stated.
- **Missing data is ranked** HARD_BLOCKER › DECISION_MODIFIER › RISK_MODIFIER › PLANNING_REFINER ›
  DOCUMENTATION_GAP. A missing photograph is not listed beside active periodontal disease.
- **Absolute words** (mandatory, required, must, contraindicated, never, always) need one of five
  named bases. Otherwise use calibrated language.
- **A risk factor is not a contraindication.** **A diagnostic tool is not a diagnosis.**
- **No single determinant assigns a prognosis.** **Elective is not inappropriate.**
- **Lead with the decision**: CURRENT DECISION → WHY → KEY DISCRIMINATOR → NEXT STEP → details.

Executable: `clinical/decision_context.py`, `clinical/language_governor.py`,
`clinical/clinical_reasoning.py`, `clinical/domain_knowledge.py`.


Load clinical-governance first (brings in claim-strength-governor, irreversibility-tiers,
healthy-tooth-protection, numeric-evidence-gate).

## Required sequence
1. Clinical question.
2. Data ledger: chief complaint; medical history; drugs/allergies; dental history; extraoral; soft tissue; periodontal; pulpal/endodontic; caries/restorative; structural/restorability; occlusion/function; TMJ/muscles; parafunction; radiographic; esthetic; patient expectations/resources.
3. Missing data ranked by decision value.
4. Data sufficiency verdict.
5. Problem list grouped biological -> structural -> functional -> esthetic -> medical -> patient-side.
6. Differential diagnosis with supporting, contradicting and discriminating evidence.
7. Risk assessment.
8. Prognosis per tooth and overall, using a named system where appropriate.
9. Diagnostic confidence.
10. Patient factors and expectation realism.
11. Measurable treatment objectives.
12. If the case involves a structurally healthy tooth and an elective/esthetic objective, apply
    references/healthy-tooth-protection.md before proposing any restorative step.
13. Phased plan: emergency -> stabilisation/control -> re-evaluation -> reversible test -> definitive -> maintenance.
14. Treatment alternatives, including no treatment/monitoring when legitimate.
15. Irreversibility tier check (references/irreversibility-tiers.md) — assign only once the actual
    intervention and preparation design are known.
16. Multidisciplinary input and the question each discipline must answer.
17. Evidence summary only for claims that drive the decision, calibrated per
    references/claim-strength-governor.md; any consequential number passes
    references/numeric-evidence-gate.md.
18. Verification requirements before acting.
19. Next single step.

Never move from a photograph, isolated radiograph or brief description directly to a definitive
irreversible treatment plan.

## Clinical layer (v0.7.0, Phase D)

The reasoning components in `clinical/` are executable and must be used rather than approximated:

- **`case_state.py`** — build the case record here. Every data point carries `[Reported]`,
  `[Observed]`, `[Inferred]` (with its basis) or `[Unknown]`. Never promote a tag, never fill an
  `[Unknown]` with a plausible guess. The sufficiency verdict it returns governs what may be
  produced.
- **`red_flag_sweep.py`** — run before closing any TRIAGE, CASE or RX output (M2 §7). Every flag
  is answered explicitly; an unanswered flag is not a cleared flag. A raised flag goes at the TOP
  of the response.
- **`treatment_plan.py`** — phases 0-4 with the re-evaluation gate. Its blocking results are not
  advisory.
- **`safety_veto.py`** — the last step before any clinical output reaches the user. A
  `SAFETY_BLOCK` is emitted alone: no plan, no partial answer, no "here it is anyway".
- **`evidence_binding.py`** — every consequential claim is bound to the decision it supports, with
  its DEL-7 tag, provenance chain, directness and (where relevant) Saudi regulatory state.

Scope is Fixed Prosthodontics and Esthetic Restorative Dentistry. Outside it, say so and stop.

## Prosthodontic knowledge & prognosis (v0.8.0)

Four operational references govern fixed-prosthodontic and esthetic-restorative decisions:
`prosthodontic-restorability.md` · `veneer-crown-decision.md` · `prosthodontic-risk-factors.md` ·
`treatment-sequencing-principles.md`. Their source is the clinic's own Clinical Protocol **v1.3, APPROVED** (2026-08-31, all eight
Appendix C items closed). Cite it as approved clinic policy. v1.2 is historical — never cite it as
current.

**Prognosis is assessed, not guessed.** Use `clinical/prognosis.py`:

```
case_state → data sufficiency → red-flag sweep → clinical findings → PROGNOSIS →
irreversible treatment planning
```

`assess_in_order()` enforces that order and refuses to run out of it. Prognosis is **categorical
only** — FAVORABLE / GUARDED / POOR / UNDETERMINED, on five separate axes (tooth, periodontal,
restorative, prosthetic, functional-occlusal). No percentage or survival figure is ever produced.
Each axis reports its basis, supporting and adverse findings, missing determinants and confidence.

**UNDETERMINED blocks definitive irreversible planning** — pass the result into
`safety_veto.review(..., prognosis_result=...)`. A missing critical determinant is not averaged
away by the determinants that are present.

Overall prognosis is the **worst** axis, never an average.

## Author identity & citation policy (v0.9.1) — global

`references/author-identity-and-citation-policy.md` applies to **every** skill and output. In
short: the person who designed this assistant is never a clinical, scientific, regulatory or
protocol authority. Her name belongs in creator attribution and ownership metadata only.

Clinic-derived rules carry `(OPS)`, `(JUDG)`, `(USER-SUPPLIED)` or `(INTERNAL PROTOCOL)` — never a
personal name. Protocols carry neutral titles. Scientific claims cite the real source, or `(UNVER)`
with a search strategy.

Enforced by `clinical/identity_policy.py` and blocked by `clinical/safety_veto.py`.

---
name: treatment-plan-audit
description: Adversarially audit an existing or proposed dental treatment plan for unsupported assumptions, sequencing errors, prognosis gaps, missed conservative/healthy-tooth-protective alternatives and evidence weaknesses.
---
# Treatment Plan Audit

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


Load clinical-governance first. This is an adversarial review, not a justification exercise — do not
retro-justify a plan the requester has already committed to.

Check:
- plan as understood
- diagnosis vs supporting data
- unstated assumptions
- missing data
- irreversible sequencing before prerequisites
- restorations planned on undetermined prognosis
- healthy-tooth protection: is irreversible work proposed on a structurally healthy tooth for an
  elective/esthetic reason without documented rejection of conservative alternatives
  (references/healthy-tooth-protection.md)?
- irreversibility tier correctly assigned only once the actual preparation design is known
  (references/irreversibility-tiers.md) — do not accept a generic "veneer = fixed tier" assumption
- alternatives missed, including no treatment and lower irreversibility tiers
- medical, periodontal, functional, parafunctional and maintenance risks
- expected failure mode, retreatability and exit strategy
- evidence supporting the plan, tagged per references/evidence-source-separation.md and
  references/evidence-directness.md; any numbers checked against references/numeric-evidence-gate.md
- claim calibration: is a risk factor stated as a certain outcome (references/claim-strength-governor.md)?

Verdict: Supported by available data / Plausible but under-evidenced / Not supported as stated /
Cannot assess. Then state what would make the plan defensible.

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

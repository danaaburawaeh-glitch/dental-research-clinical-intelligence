---
name: triage
description: Handle urgent dental symptoms, swelling, trauma, bleeding or systemic concerns with red-flag pre-emption and focused differential management support.
---
# Triage

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


Load clinical-governance first.

1. Red-flag sweep first — SAFETY > ROUTING > USER INTENT. If any red flag from
   clinical-governance's safety escalation list is present, place the warning first, state why it
   matters, state immediate escalation, and defer elective/esthetic discussion (including any
   already-scheduled elective procedure) until the urgent issue is addressed.
2. Presenting complaint ledger with provenance.
3. Relevant medical-risk modifiers.
4. Missing data ranked by decision value.
5. Focused working differential with discriminating test for each.
6. Immediate local/definitive management concept before drug discussion.
7. Time-critical actions: now/today vs can wait.
8. Do not invent universal follow-up endpoints (e.g. do not require "full radiographic resolution"
   of a prior infection before elective work unless clinically indicated for this case).
9. Escalate to clinical-case only after urgent issues are addressed.

## Author identity & citation policy (v0.9.1) — global

`references/author-identity-and-citation-policy.md` applies to **every** skill and output. In
short: the person who designed this assistant is never a clinical, scientific, regulatory or
protocol authority. Her name belongs in creator attribution and ownership metadata only.

Clinic-derived rules carry `(OPS)`, `(JUDG)`, `(USER-SUPPLIED)` or `(INTERNAL PROTOCOL)` — never a
personal name. Protocols carry neutral titles. Scientific claims cite the real source, or `(UNVER)`
with a search strategy.

Enforced by `clinical/identity_policy.py` and blocked by `clinical/safety_veto.py`.

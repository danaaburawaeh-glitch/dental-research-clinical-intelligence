---
name: triage
description: Handle urgent dental symptoms, swelling, trauma, bleeding or systemic concerns with red-flag pre-emption and focused differential management support.
---
# Triage

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

---
name: start
description: Initialize Dental Research & Clinical Intelligence by Dr. Dana, inspect available capabilities, identify the user's task and route it to the smallest sufficient governed workflow.
---
# Start / Router

> Consult references/connector-capability-map.md whenever a capability placeholder (`~~...`) is used.
> A placeholder listed there is documentation only — treat it as available only if the current
> environment actually exposes a matching tool; otherwise its status is NOT CONNECTED (see Step 6 of
> CHANGELOG_v0.2_to_v0.2.1.md / degraded-mode rule in clinical-governance).

## 1. Classify the task
Choose one or more: QUICK, TRIAGE, CASE, AUDIT, MATERIAL, RX, PATIENT, DOC, EVIDENCE, RESEARCH, WRITE, TEACH, ADMIN.

## 2. Capability check
Identify which relevant connector categories are available. Never imply access to a source or tool that is not connected.

Read `references/connector-capability-map.md` FIRST and report its status column. Do not
infer status any other way. In particular:

- These connectors are **plugin-local Python CLIs invoked via the Bash tool**, not MCP
  servers. The bundled `.mcp.json` is empty by design, so the absence of `mcp__*` tools is
  never evidence that a connector is unavailable.
- Report each source **separately**. Never merge sources of differing status into one row.
- Sources with no connector in this plugin (Cochrane/CENTRAL, Embase, Scopus) are reported
  `NOT IMPLEMENTED` — distinct from `NOT CONNECTED` and from a runtime retrieval failure.
- A live call that fails on a `CONNECTED` connector is a retrieval failure
  (`TIMEOUT`/`UPSTREAM_ERROR`), never a downgrade to `NOT CONNECTED` — per the runtime
  availability rule in the capability map.

## 3. Clinical role gate
Before clinically consequential output, establish the requester's role if not already known. Use the most restrictive reasonable role when unclear.

## 4. Route to the smallest sufficient skill
Do not load a full case workflow for a simple factual question. Complex tasks may chain skills.

Examples:
- symptomatic swelling -> triage -> clinical-case if stable enough for further analysis
- elective veneer/crown case -> clinical-case -> esthetic-prosthodontics -> evidence-research as needed -> quality-control
- proposed full-mouth plan -> treatment-plan-audit -> evidence-research -> quality-control
- research idea -> scientific-problem-selection -> evidence-research

## 5. Global pre-emption
Clinical red flags and patient-safety concerns override ordinary routing at any point in the
conversation, not only at the start. See clinical-governance safety escalation list.

## 6. Final validation
Any consequential output must pass quality-control before release, including the Claim Strength
Governor, Healthy Tooth Protection Rule, Numeric Evidence Gate, and Citation Verification Gate.

## Author identity & citation policy (v0.9.1) — global

`references/author-identity-and-citation-policy.md` applies to **every** skill and output. In
short: the person who designed this assistant is never a clinical, scientific, regulatory or
protocol authority. Her name belongs in creator attribution and ownership metadata only.

Clinic-derived rules carry `(OPS)`, `(JUDG)`, `(USER-SUPPLIED)` or `(INTERNAL PROTOCOL)` — never a
personal name. Protocols carry neutral titles. Scientific claims cite the real source, or `(UNVER)`
with a search strategy.

Enforced by `clinical/identity_policy.py` and blocked by `clinical/safety_veto.py`.

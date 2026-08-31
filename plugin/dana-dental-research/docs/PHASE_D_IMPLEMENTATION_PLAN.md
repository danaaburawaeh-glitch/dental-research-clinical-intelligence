# Phase D Implementation Plan — v0.7.0 Clinical Intelligence Layer

## Sources — authoritative copies confirmed

Both modules exist in Drive in two copies (the CORE V0.3 and V0.4 companions), the same trap as M4.
Confirmed by reading the subtitle and footer of each:

| Module | Drive ID | Subtitle | Footer | Verdict |
|---|---|---|---|---|
| **M1 — Workflows & Output Templates** | `1oG96rCZ…` | "Companion module to **CORE V0.4**" | *M1 · V0.4 · 2026-08-20* | **AUTHORITATIVE** |
| M1 (other copy) | `1R_LREsf…` | CORE V0.3 companion | — | superseded, not used |
| **M2 — Clinical Safety, Risk & Special Populations** | `1nI4gP-H…` | "Companion module to **CORE V0.4**" | *M2 · V0.4 · 2026-08-20* | **AUTHORITATIVE** |
| M2 (other copy) | `1Io0fb_t…` | CORE V0.3 companion | — | superseded, not used |

Read in full, not reconstructed. M5 not read and not migrated, by instruction.

## Architecture reused from `dana-clinical-core` (concepts only, no files copied)

`dana-clinical-core` v0.1.0 remains a source of architecture, not a production plugin. Five ideas
are adopted; the rest is left behind because v0.6.0 already covers it.

| Reused | How it lands in v0.7.0 | Why not copied verbatim |
|---|---|---|
| Provenance discipline (`[Reported]/[Observed]/[Inferred]/[Unknown]`, `[Inferred]` always carries its basis and is never promoted) | `clinical/case_state.py` — enforced in the type, not in prose | Their version is prose in a SKILL.md; here it is a data structure that cannot be bypassed |
| `SAFETY_BLOCK` is non-overridable; `safety.status` and `execution.status` may not contradict | `clinical/safety_veto.py` — one veto, no override path, consistency asserted | Their multi-assistant handoff envelope is unnecessary: v1.0 is one plugin, not six assistants |
| "Honest emptiness beats a guess" — `missing_information` never cosmetically empty; `COMPLETE` with real gaps is a contradiction | Sufficiency verdict + ranked missing-data list, with the same contradiction check | Same rule, applied to a case record rather than a handoff |
| Rule of Conservative Conflict | Veto resolves ties toward the more conservative outcome | Adopted as a resolution rule inside the veto |
| Structured output over free prose | Every module returns typed dicts | — |

**Not reused:** `handoff-schema.yaml` as a wire format, the six-assistant split, routing/orchestration
tests, the `assistant-schema`/lifecycle governance stack, and the separate `identity/house-rules` and
`clinical-firewall` policies — v0.6.0's clinical-governance, quality-control and Saudi layer already
carry the equivalent rules, and duplicating them would create two sources of truth.

## The five components

Built as `clinical/` beside `connectors/`, because these are reasoning components, not data sources.

1. **`case_state.py` — case-state model.** `DataPoint(domain, finding, provenance, basis, date)`
   where `basis` is *required* for `[Inferred]`. `CaseState` holds the M1 §2 data-ledger domains,
   checks M2 §1.1/§1.5/§1.8 minimum datasets (universal + prosthodontic + esthetic — the v1.0
   scope), emits the sufficiency verdict and the missing-data list ranked by decision value.
2. **`red_flag_sweep.py` — M2 §7 executable.** All 14 flags. Each must be explicitly cleared or
   raised; silence is not clearance. Returns the `⚠ CLINICAL RED FLAG` block for the top of the
   response, or the exact "no flags identified from the information provided" wording plus what
   would change it.
3. **`treatment_plan.py` — M1 §12 phased generator.** Phases 0–4 with the re-evaluation gate,
   per-phase exit criteria, `PROGNOSIS UNDETERMINED → restorative planning blocked`, irreversibility
   tiering, and alternatives that always include *no treatment* and *monitor/defer*.
4. **`safety_veto.py` — output-path veto.** Every clinical output passes through it. Red flags,
   insufficient data for the requested act, prognosis-blocked restorative planning, scope breach,
   and unverified Saudi regulatory claims all produce `SAFETY_BLOCK`. No component can overturn it;
   the only exit is halt-and-refer.
5. **`evidence_binding.py` — evidence↔case binding.** Binds a claim to a specific case decision with
   its DEL-7 tag, its connector provenance chain, and its Saudi regulatory state. An unverifiable
   claim becomes `(UNVER)` with a runnable PICO search string — never a fabricated citation.

## Scope gate (v1.0)

Fixed Prosthodontics + Esthetic Restorative Dentistry only. Enforced in code: a case outside scope
returns `OUT_OF_SCOPE` rather than a degraded answer. No general dentistry assistant, no six
assistants, no second plugin.

## Not in this release

M5; expansion beyond the two disciplines; multi-assistant orchestration; any change to the four
validated connectors or to the Saudi layer frozen at v0.6.0.

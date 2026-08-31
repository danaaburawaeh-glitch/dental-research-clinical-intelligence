# Changelog — v0.6.0 → v0.7.0 (FEATURE RELEASE — Phase D: Clinical Intelligence Layer)

## Headline

DANA becomes a prosthodontic clinical assistant. Five components in `clinical/`, migrated from
**M1 V0.4** and **M2 V0.4**, turn the evidence and governance stack into something that reasons
about a patient rather than about literature.

One integrated plugin. No second production plugin, no six assistants, no M5.

## Sources — authoritative copies confirmed before use

Both modules exist in Drive in two copies (CORE V0.3 and V0.4 companions), the same trap as M4.
Confirmed by subtitle and footer: **M1 `1oG96rCZ…`** and **M2 `1nI4gP-H…`**, both
"Companion module to CORE V0.4", both footed *V0.4 · 2026-08-20*. The V0.3 copies were not used.

## Architecture reused from `dana-clinical-core` — concepts, not files

Nothing was copied. Five ideas adopted: the provenance discipline, the non-overridable
`SAFETY_BLOCK` with its status-consistency rule, "honest emptiness beats a guess", the Rule of
Conservative Conflict, and structured-output-over-prose.

**Deliberately not reused:** the handoff wire format, the six-assistant split, the routing and
orchestration harnesses, and the separate `house-rules`/`clinical-firewall` policies — v0.6.0's
clinical-governance, quality-control and Saudi layers already carry the equivalent rules, and
duplicating them would create two sources of truth.

## Added — `clinical/`

| Module | Migrated from | Enforces |
|---|---|---|
| `case_state.py` | M1 §2/§3/§4, M2 §1 | Provenance tags with `[Inferred]` requiring its basis; minimum datasets for both in-scope disciplines; sufficiency verdict; missing data ranked by decision value |
| `red_flag_sweep.py` | M2 §7 | All 14 flags. Unanswered ≠ absent |
| `treatment_plan.py` | M1 §12/§13, M2 §5/§6 | Phases 0-4 + re-evaluation; prognosis, sequencing, failure-planning, alternatives and esthetic test-phase gates |
| `safety_veto.py` | CORE §15, M2, PDPL layer | One non-overridable block in the output path |
| `evidence_binding.py` | M3 + the four connectors | Claim bound to decision with DEL-7 tag, provenance, directness, regulatory state |

## Design decisions worth noting

**`[Inferred]` without a basis raises at construction.** An inference whose basis is not recorded
is indistinguishable from an invention, so it is refused where it is created rather than caught
later — or not caught at all.

**Some dataset items block by their nature, not by a caller's opinion.** The medical screen,
allergies, restorability, ferrule, abutment prognosis, pulpal status, parafunction and esthetic
expectation screening are marked intrinsically blocking, tied to the M2 sections that gate on them.
A caller may raise an item's decision value but **cannot lower** one of these. A separate rule
catches the case that individual ranks miss: more than half the minimum dataset absent is
INSUFFICIENT whatever the ranks say — a case with most of its dataset missing has been mentioned,
not examined.

**Silence is not clearance.** A red flag never answered is `NOT_ASSESSED`, and an incomplete sweep
cannot be reported as clear. The sweep deliberately does **not** infer answers from the case
record: inferring ABSENT from an incomplete history is the exact failure the module exists to
prevent.

**Blocked plan items are reported, not dropped.** A quietly shortened plan hides the problem; the
clinician sees which item was blocked and why.

**The veto does not score.** Checks are all binding — one clean result never cancels a block, and
a `SAFETY_BLOCK` cannot be reported as any other status (`assert_consistent`).

## Updated — skills

`clinical-case`, `esthetic-prosthodontics`, `treatment-plan-audit` and `clinical-governance` now
invoke the clinical layer rather than approximating it. `quality-control` gains eight clinical
checks; the release-blocking failure is emitting a plan, prescribing support or an efficacy claim
past a `SAFETY_BLOCK`, or presenting an `[Inferred]`/`[Unknown]` value as established.

## Tests

`clinical/tests/test_clinical_layer.py` → **60/60 pass**, no network. Prior suites unchanged and
still passing: ClinicalTrials.gov 50/50, Saudi governance 50/50.

## Not changed

All four connectors and the Saudi layer are byte-identical to v0.6.0. Connector states unchanged,
`~~regulatory-saudi` still NOT CONNECTED — AUTH REQUIRED.

## Not in this release

M5; any discipline beyond Fixed Prosthodontics and Esthetic Restorative Dentistry; multi-assistant
orchestration; the post-v1.0 connector register (P1-P9); the PubMed `<DataBankList>` limitation,
still carried forward.

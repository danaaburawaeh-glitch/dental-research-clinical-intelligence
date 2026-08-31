# Changelog — v0.2.1 → v0.3

**Type:** Minor version release. **Scope:** M3 — Evidence & Source Protocol migration and Evidence
Engine build-out only. M4, M5, Rosenstiel, and the full clinical protocol are untouched. v0.2.1
itself was not modified or overwritten — this is a new, separately packaged release.

## Source used

Authoritative M3 (CORE V0.4 companion), read in full from Google Drive
(`1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8`, dated 2026-08-20 / modified 2026-08-21), plus CORE
V0.4 (`1cR6GKQ0ixuopSgzsiYt-cHRaVVEs2KD1zepgm9j35K8`) for cross-reference. The older duplicate M3
(`1aAnLVdyTsVoUP2lympyrjBBwLLL2YgvzORp4rSADL1g`, CORE V0.3 companion) was checked and confirmed
stale/deprecated — its bracket vocabulary was never migrated. Full detail: `M3_MIGRATION_AUDIT.md`.

## New files

- `skills/evidence-research/references/del7-evidence-hierarchy.md` — canonical DEL-7 definitions,
  misassignment guidance, laboratory/manufacturer/regulatory firewalls (previously scattered
  across evidence-source-separation.md without the misassignment table or firewall detail).
- `skills/evidence-research/references/clinical-evidence-safe-search-gateway.md` — orchestration
  spec for the CESS gateway layer above the seven connector placeholders (Decision 1).
- `skills/evidence-research/references/deferred-knowledge-dependencies.md` — tracks
  CLINICAL-PROTOCOL-08 as a deferred dependency (Decision 2), so it isn't silently forgotten or
  silently reconstructed.
- `skills/evidence-research/references/source-priority.md` — retrieval precedence, Tier A-D
  mapping, retrieval order by question type, no-silent-fallback rule, recency rules.
- `skills/evidence-research/references/evidence-question-formulation.md` — PICO/PECO/PIRD/SPIDER/
  PICo router and material/device question shape.
- `skills/evidence-research/references/search-strategy.md` — search construction and required
  search-log fields.
- `skills/evidence-research/references/study-design-classification.md` — design taxonomy and the
  RCT (randomized controlled trial vs root canal treatment) disambiguation rule.
- `skills/evidence-research/references/evidence-quality-appraisal.md` — the single largest content
  gap identified in the audit; full appraisal discipline (risk of bias, sample size, follow-up,
  effect size + CI, named formal tools) that previously existed only as one workflow-step line.
- `skills/evidence-research/references/absence-of-evidence.md` — four-state distinction (nothing
  found / search failed / weak-indirect / genuine no-effect), previously only partially covered.
- `skills/evidence-research/references/evidence-conflict-resolution.md` — evidence-vs-evidence
  conflict handling, distinct from clinical-governance's Axis A/B safety-vs-evidence conflict.
- `skills/evidence-research/references/clinical-applicability.md` — adds feasibility-locally and
  patient-fit dimensions on top of evidence-directness.md's existing match ratings.
- `skills/evidence-research/references/evidence-synthesis.md` — structured nine-question synthesis
  algorithm; the four-bucket output structure (DIRECT/INDIRECT/EXTRAPOLATION/UNKNOWN) moved here
  from evidence-source-separation.md, which now points to it instead of duplicating it.
- `skills/evidence-research/templates/*` — 5 templates (pico, search-log, evidence-table,
  evidence-summary, clinical-bottom-line), none existed as dedicated files before.
- `skills/evidence-research/tests/evidence-regression-tests.md` — 15 required regression
  scenarios, none existed before.
- `docs/M3_MIGRATION_AUDIT.md`, `docs/REAL_CONNECTOR_STACK_RESEARCH.md`,
  `docs/EVIDENCE_ENGINE_ARCHITECTURE.md`, `docs/CONNECTOR_REQUIREMENTS.md`,
  `docs/PACKAGE_VALIDATION.md`, `docs/CHANGELOG_v0.2.1_to_v0.3.md` (this file).

## Updated files

- `skills/evidence-research/SKILL.md` — fully rebuilt as a 13-step orchestrator over the new
  reference set, plus the QUICK/STANDARD/DEEP output-mode router (previously an 11-step list
  referencing a smaller reference set).
- `skills/evidence-research/references/connector-capability-map.md` (canonical) and
  `skills/start/references/connector-capability-map.md` (bundled, re-synced) — restructured around
  the CESS gateway architecture; Phase 17 research findings folded in per connector; added the
  SFDA SOURCE-UPDATE-CONFLICT note.
- `skills/evidence-research/references/evidence-directness.md` — pointer updated to
  del7-evidence-hierarchy.md for tag definitions; cross-references to clinical-applicability.md
  and evidence-conflict-resolution.md added. Directness mechanics themselves unchanged (audit
  finding: KEEP).
- `skills/evidence-research/references/citation-verification.md` — added the
  guideline-recommendation-strength-preservation rule and the verified-reference-reuse-with-
  provenance principle (both from M3 §10, minus the file-08-specific mechanics — see deferred
  dependencies).
- `skills/evidence-research/references/evidence-source-separation.md` — DEL-7 tag table reduced to
  a summary pointing to the new canonical file; four-bucket structure now points to
  evidence-synthesis.md instead of duplicating it. Remains the quality-control-facing quick
  reference and stays bundled/canonical-owned by clinical-governance, unchanged in that respect.
- `skills/quality-control/SKILL.md` — Evidence section expanded from 4 bullet checks to a full
  checklist against every new evidence-research reference file (question formulation, retrieval
  provenance, study quality, absence handling, conflict handling, applicability, unsupported
  extrapolation) — Phase 21.

## Unchanged (carried forward as-is)

`clinical-case`, `clinical-governance`, `esthetic-prosthodontics`, `scientific-problem-selection`,
`triage`, `treatment-plan-audit` skills; `numeric-evidence-gate.md` and
`claim-strength-governor.md` bundled copies (still canonically owned by clinical-governance, no
M3 content required a change to either).

## Known findings not acted on in v0.3 (see docs/ for detail)

- **SOURCE-UPDATE-CONFLICT:** CORE/M3 state SFDA has no public queryable database; Phase 17 found
  SFDA now publishes an OAuth-secured open-data API for registered drugs/medical devices. Recorded
  for M4 review, not corrected here.
- **CLINICAL-PROTOCOL-08** dependency deferred, not resolved — see
  deferred-knowledge-dependencies.md.
- No connector is `CONNECTED`. All seven placeholders remain `NOT CONNECTED`; Phase 17 established
  real, documented APIs exist for most of them, which is a precondition for wiring, not wiring
  itself.

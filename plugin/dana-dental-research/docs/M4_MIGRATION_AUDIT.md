# M4 Migration Audit — Phase C

**Source read:** `M4 — Saudi Regulatory, Patient Data & Governance`, Google Drive doc
`1Z7uct0tq3D5zHa0ReajnGcbva-NHs359dhkDuZoz7Qc`, footer version **M4 · V0.4 · 2026-08-20**,
companion to CORE V0.4. Read in full, not reconstructed.

**Version selection.** Two M4 documents exist in Drive with the same title. The other
(`1mAuqFNlTLcY-…`, modified 06:08) is the **CORE V0.3** companion; this one (modified 06:59) is
the **CORE V0.4** companion and is the authoritative current version. The V0.3 copy was not used.

**Scope note.** M4's own framing governs this migration: it names *authorities, obligations and
checkpoints* and requires current requirements to be verified at point of use. It deliberately
states no rule text, thresholds or procedural detail. The migration preserves that posture — no
migrated file states a Saudi legal requirement as settled fact.

## Target files

- `SRG` = `skills/clinical-governance/references/saudi-regulatory-gate.md`
- `PDPL` = `skills/clinical-governance/references/saudi-data-privacy-pdpl.md`
- `SCG` = `skills/clinical-governance/references/saudi-clinical-governance.md`
- `SRSP` = `skills/clinical-governance/references/saudi-regulatory-source-priority.md`
- `QC` = `skills/quality-control/` (SKILL.md + references)
- `EXISTING` = `saudi-regulatory-claim-gate.md` (already in the plugin, v0.2.1)

## Audit

| § | Rule | Current plugin coverage | Target | Action |
|---|---|---|---|---|
| — | Not legal advice; verify at point of use; no rule text from memory | EXISTING states the principle | SRG | **KEEP** — restated as the gate's governing posture |
| 1 | Saudi baseline jurisdiction; state which jurisdiction applies; foreign standards for comparison only | Not covered | SRG | **NEW** |
| 1 | If clinician practises elsewhere, Saudi layer does not apply | Not covered | SRG | **NEW** |
| 2 | Six bodies (SFDA, SCFHS, MOH, SDAIA/PDPL, Law of Practising Healthcare Professions, CST) and their domains | Not covered | SRSP | **NEW** |
| 2 | Operating rule: name body + obligation, then "verify current requirements with [body]" | EXISTING has a weaker "Regulatory verification required" flag | SRG, SRSP | **REFINE** — bodies named explicitly |
| 3.1 | SFDA registration status for products; "SFDA status not verified" when undeterminable | Not covered | SRG | **NEW** |
| 3.2 | FDA/CE reported separately, labelled non-transferable | Not covered | SRG | **NEW** — becomes a hard rule |
| 3.3 | Clearance ≠ superiority (M3 §6) | Covered by `claim-strength-governor.md` | — | **KEEP** — cross-referenced, not duplicated |
| 3.4 | IFU governs handling; off-label flagged | Partially — `~~manufacturer-ifu` is NOT CONNECTED | SRG | **REFINE** — stated as a checkpoint, not a lookup |
| 3.5 | SFDA adverse-event / product-problem reporting pathway | Not covered | SRG | **NEW** |
| 3.6 | Grey-market / unregistered products — flag regulatory, warranty, liability | Not covered | SRG | **NEW** |
| 4 | Scope of practice; ask when classification unknown | Not covered | SCG | **NEW** |
| 4 | Protected specialist titles (SCFHS); never describe a clinician by an unconfirmed title | Not covered | SCG | **NEW** |
| 4 | Referral stated as requirement, not suggestion, when case exceeds scope | Not covered | SCG | **NEW** |
| 5.1 | Minimisation — enumerated identifiers; de-identified reference (CASE-YYYYMMDD-xx) | Not covered | PDPL | **NEW** |
| 5.2 | De-identification standard incl. EXIF, burned-in radiograph identifiers, DICOM tags, identifying rarity | Not covered | PDPL | **NEW** |
| 5.3 | AI input is PDPL processing; cross-border transfer flagged; de-identify by default; third-party disclosure needs lawful basis | Not covered | PDPL | **NEW** |
| 5.4 | Retention period mandated — verify, do not state; AI session is not the record | Not covered | PDPL | **NEW** |
| 5.5 | Research use is a separate purpose; treatment consent does not cover it; ethics committee decides the audit/research boundary | Not covered | PDPL | **NEW** — M5 §4 cross-ref recorded only, M5 not migrated |
| 6.1 | Treatment consent is a process; capacity; guardians; language; never produce a completed consent instrument | Not covered | SCG | **NEW** |
| 6.2 | Photography/publication consent separate, specific, informed, written, freely given, revocable, separately recorded | Not covered | PDPL | **NEW** |
| 7 | CLINICAL → MARKETING FIREWALL, all 7 hard rules incl. one-way directionality | Not covered | PDPL (consent/marketing) + SCG (directionality) | **NEW** — highest-exposure rule in M4 |
| 8 | Documentation posture: clinician owns output; no implied examination; no backdating; no legal strategy | Not covered | SCG | **NEW** |
| 9 | Change control, amendment authority, incident log | Partially — plugin has versioned changelogs | — | **CONFLICT (recorded, not resolved)** — see below |
| 10 | Onboarding points for clinic-team users | Not covered | — | **DEFERRED** — team-charter material, not a governed decision gate |
| 11.1 | Role gating table (5 roles) | Not covered | SCG | **NEW** |
| 11.2-11.6 | Shared-project entry rules, project-knowledge vs thread, onboarding, incident log, escalation path | Not covered | — | **DEFERRED** — workspace-operations material |

## Conflicts and deliberate deferrals

**CONFLICT — §9 amendment authority vs. plugin change control.** M4 §9 vests amendment authority
in Dr Dana Abu Rawaeh or a written delegate, requires a logged amendment trail and a maintained
incident log. The plugin has versioned changelogs but no incident log and no encoded amendment
authority. This is a governance-process gap, not a rule the plugin can enforce in an output.
Recorded in `UNRESOLVED_GAPS.md`; not resolved in Phase C.

**DEFERRED — §10 and §11.2-11.6.** These govern how a clinic team operates a shared workspace
(who may enter what, onboarding records, escalation paths). They are real M4 rules but they are
not decision gates DANA applies to an output, and Phase C was scoped to four reference files.
Recorded as carried-forward, not silently dropped.

**Not migrated by instruction:** M5, Rosenstiel, Clinical Protocol. §5.5's cross-reference to
M5 §4 is recorded in PDPL as a pointer only.

## Coverage result

Of 30 auditable M4 rules: **21 NEW**, **3 REFINE**, **2 KEEP** (already covered, cross-referenced
rather than duplicated), **1 CONFLICT** recorded, **3 DEFERRED** and recorded. No M4 rule was
dropped without an entry above.

# M3 Migration Audit — v0.2.1 → v0.3

**Source of truth used:** Google Drive file `1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8`
("M3 — Evidence & Source Protocol", CORE V0.4 companion, dated 2026-08-20, modified 2026-08-21).
Read in full — not reconstructed from memory.

**CORE cross-reference used:** Google Drive file `1cR6GKQ0ixuopSgzsiYt-cHRaVVEs2KD1zepgm9j35K8`
("DANA Dental Intelligence OS — CORE V0.4"), §9, §9.1, §10, §11 specifically.

**Old duplicate checked for version drift only:** Google Drive file
`1aAnLVdyTsVoUP2lympyrjBBwLLL2YgvzORp4rSADL1g` ("M3 — Evidence & Source Protocol", CORE V0.3
companion). **Not used as a source of rules** — see Finding 0 below.

**Current plugin state compared against:** `evidence-research/SKILL.md` and all six existing files
in `evidence-research/references/` (`citation-verification.md`, `claim-strength-governor.md`,
`connector-capability-map.md`, `evidence-directness.md`, `evidence-source-separation.md`,
`numeric-evidence-gate.md`).

---

## Finding 0 — the old duplicate is stale and uses a deprecated vocabulary

The older file (CORE V0.3 companion) tags evidence with a bracket vocabulary —
`[Guideline]`, `[SR/MA]`, `[RCT]`, `[Cohort]`, `[Case series]`, `[In vitro]`, `[Expert opinion]`,
`[Manufacturer]`, `[Regulatory]`, `[Low-tier]`, `[Unverified]` — that does **not** match DEL-7 and
does not appear anywhere in the current plugin. The authoritative M3 (V0.4) replaced this wholesale
with DEL-7 ((L1)–(L4), (IFU), (JUDG), (OPS), (LAB), (REG), (KOL), (UNVER)), which is what the current
plugin's `evidence-source-separation.md` and `evidence-directness.md` already use.

**Action: DEPRECATE the old duplicate outright.** It is not a migration source. It confirms the
plugin is already aligned with the *newer* vocabulary, not the older one — no rework needed on that
axis. Flagged here only so it is never picked up by mistake in a later phase.

---

## Migration inventory

| M3 §(v0.4) source section | Current plugin rule | Destination (v0.3 target) | Action | Notes |
|---|---|---|---|---|
| Header — "DEL-7 is the only source vocabulary" | Implicit; DEL-7 used consistently in `evidence-source-separation.md`, `evidence-directness.md` | `del7-evidence-hierarchy.md` (new, canonical) | MOVE + REFINE | Currently DEL-7's canonical text lives in CORE §9.1 and is *echoed* in two plugin files with no single canonical evidence-side owner. Give evidence-research a canonical `del7-evidence-hierarchy.md` that mirrors CORE §9.1 verbatim (CORE remains the defining source; this file is the operational copy DEL-7-consuming skills load). |
| §1 Retrieval precedence | `SKILL.md` step 2 lists 7 granular connector placeholders (`~~clinical-guidelines`, `~~systematic-reviews`, `~~literature`, `~~clinical-trials`, `~~journal-access`, `~~manufacturer-ifu`, `~~regulatory-saudi`) | `source-priority.md` + `connector-capability-map.md` | **CONFLICT** | M3 §1 describes retrieval as going through **one** consolidated tool — "Clinical Evidence Safe Search (source-restricted evidence API, when attached)" — with server-side allowlist/firewalls, then "other attached tools," then none. The plugin instead models **seven separate placeholder categories** with no single unifying tool. These are not obviously the same shape: is "Clinical Evidence Safe Search" meant to *replace* the seven placeholders as one connector, or is it a routing layer in front of them? **Do not resolve this by inference** (per M3's own §3.2 rule 4 on (OPEN) items). Recording as an explicit open question for you, not auto-resolving it — see "Unresolved gaps" below. |
| §1 "never silently substitute web search for a failed tool" / "outage ≠ absence" | Present in spirit (`connector-capability-map.md` "Required behaviour" section), not verbatim | `source-priority.md` | REFINE | Wording should be pulled in near-verbatim; current file states the behavior but not M3's precise phrasing distinction ("the search could not be completed" vs "no evidence exists"/"no clearance found"/"no IFU available"). |
| §2 PICO(T) framing + surrogate-outcome warning | `SKILL.md` step 1 references PICO/PECO/PIRD/SPIDER by name only, no dedicated logic | `evidence-question-formulation.md` (new) | MOVE (new build) | This is genuinely new structured content — not present as a reference file today. Surrogate-outcome warning ("surrogate-only evidence is (LAB), not (L3)") is a hard rule that isn't stated anywhere in the current plugin and should be pulled in exactly. |
| §3.1 DEL-7 tag table with "common misassignment to avoid" column | `evidence-source-separation.md` has the tag list (bare) | `del7-evidence-hierarchy.md` (new) | MERGE + REFINE | Current file lists tags and one-line meanings but omits the misassignment guidance ("a narrative review in a guideline-sounding journal is (L4), not (L1)", etc.) — this is exactly the kind of thing that prevents tagging drift and should be preserved verbatim. |
| §3.2 rule 1 — (JUDG) never becomes evidence | `evidence-source-separation.md` — "JUDG is not external evidence" | `del7-evidence-hierarchy.md` | KEEP (content already correct) | Already present, just needs to live in the new canonical file rather than only in `evidence-source-separation.md`. |
| §3.2 rule 2 — (IFU) never transfers between products | Not explicitly stated in current plugin | `del7-evidence-hierarchy.md` | MOVE (new) | Genuine gap — current plugin has an IFU-never-establishes-superiority rule but not the cross-product-transfer rule. |
| §3.2 rule 3 — (LAB) never crosses to clinical | `evidence-source-separation.md` — "LAB is not clinical evidence" | `del7-evidence-hierarchy.md` | KEEP | Already correct; M3 §4 (laboratory firewall) has substantially more detail — see next row. |
| §3.2 rule 4 — (OPEN) means Unknown, tied to "the clinic protocol" (file 08) | Not present — no concept of "file 08" / clinic protocol exists in the plugin architecture | — | **CONFLICT — do not migrate as written** | M3 §3.2 rule 4 and §3.4 both assume a specific artifact ("clinic protocol, file 08," marked مسودة عمل / معتمدة) that has no analogue in the plugin's file structure. Migrating this verbatim would introduce a dependency the plugin can't satisfy. The *general* principle — an (OPEN)/unresolved gap is never silently resolved by inference — is sound and should migrate. The clinic-protocol-specific machinery (file 08, Arabic draft/approved labels, Appendix A reference reuse in §10) should not. Flagging as CONFLICT rather than silently dropping it — this needs your call on whether "clinic protocol" maps to something in your Drive/plugin setup I haven't been shown yet. |
| §3.3 Axis A/B (patient safety, legal, autonomy outrank DEL-7) | Owned by `clinical-governance`, not `evidence-research` (per CORE §11) | clinical-governance (unchanged) | KEEP, out of scope | Correctly out of evidence-research's remit already — CORE says Axis A is settled before DEL-7 is consulted, and clinical-governance is the existing canonical owner for conflict resolution. No action needed in this plugin; noted for completeness only. |
| §3.4 Citing the clinic protocol / IFU-overrides-JUDG-number rule | Not present | — | **CONFLICT — same file-08 dependency as above** | Same issue as §3.2 rule 4. The IFU-governs-over-JUDG-number principle is sound and generalizable; the "file 08" citation mechanics are not portable without knowing what that file maps to in this architecture. |
| §4 Laboratory firewall — explicit bench-marker list + escape hatch for a clinical arm in the same paper | `evidence-source-separation.md` states the rule in one line, no marker list, no escape hatch | `del7-evidence-hierarchy.md` or new `evidence-quality-appraisal.md` | MOVE + REFINE (new detail) | The specific marker list (bond strength, thermocycling, FEA, microleakage, artificial saliva, surface roughness, in vitro colour stability, zone-of-inhibition) and the "escape hatch" (classify the clinical arm as (L3) if one exists in the same paper) are both new operational detail not in the current plugin. |
| §5 Manufacturer firewall — IFU governs its own domain / off-label flag / "could not be retrieved, say so" | Partially present via CORE §10, not detailed at evidence-research level | `del7-evidence-hierarchy.md` | MERGE | Off-label flagging and "do not paraphrase an unretrieved IFU from memory" are both real additions. |
| §6 Regulatory is a gate not a rank | `evidence-source-separation.md` — "Regulatory clearance (REG) is a gate, not evidence of superiority" | `del7-evidence-hierarchy.md` | KEEP | Already correctly captured at the core-principle level; M3's clearance-vs-approval-vs-registration distinction and the "SFDA has no public queryable database" caveat are additive detail worth folding in. |
| §7 Reading and reporting a study (design, sample size, follow-up, dropout, effect size + CI, funding, limitation; statistical-vs-clinical significance; wide CI spanning no effect; short follow-up ≠ longevity answer; small single-centre = hypothesis-generating; RR without AR is misleading; no informal pooling) | Not present as a dedicated reference; `SKILL.md` step 5 gestures at "capture design, population/sample, follow-up, effect size" in one line | `evidence-quality-appraisal.md` (new) | MOVE (new build) | This is the single largest genuine content gap found in the audit — a full structured appraisal discipline that currently exists only as a one-line workflow step. Maps directly to Phase 8. |
| §8 Absence of evidence — three distinct situations (searched-nothing-found / search-failed / weak-or-indirect) | `connector-capability-map.md` covers the search-failed case; the other two are not distinguished anywhere | `absence-of-evidence.md` (new) | MOVE (new build) | Current plugin conflates "nothing found" and "search failed" more than M3 does; M3's three-way split (plus "evidence exists but is weak/indirect") is materially more precise and should become its own file per Phase 12. |
| §9 Recency (contemporary preference, landmark exception, product recency caveat, guideline year + revision flag) | Not present | `source-priority.md` or `evidence-quality-appraisal.md` | MOVE (new) | New content; no current equivalent. |
| §10 Citation integrity | `citation-verification.md` — VERIFIED/PARTIALLY VERIFIED/UNVERIFIED, no fabrication, (UNVER) tagging | `citation-verification.md` (existing) | KEEP + REFINE | Strong overlap already — current file is well-aligned. Two additions from M3: (a) never paraphrase a guideline recommendation in a way that changes its strength ("may be considered" ≠ "is recommended"); (b) reuse of already-verified references from "clinic protocol file 08, Appendix A" — the second again depends on the undefined file-08 artifact (see Finding above); only (a) migrates cleanly. |
| §11 Applicability (population/setting/directness/feasibility-locally/patient-fit match) | `evidence-directness.md` covers population/intervention/comparator/outcome/timeframe/setting match ratings | `clinical-applicability.md` (new) + `evidence-directness.md` (existing) | MERGE + MOVE | Current `evidence-directness.md` already covers most of this well. M3's "feasibility locally" (REG-registered in this jurisdiction + OPS permits it) and "patient fit" (cost, maintenance, compliance) are two additional applicability dimensions not currently captured — these map to Phase 13's dedicated `clinical-applicability.md`, which should reference (not duplicate) `evidence-directness.md`. |
| §12 Conflicting evidence (state what each side shows, DEL-7 tag, likely explanation, what it means for the decision, what would settle it; JUDG-vs-L1-L4 conflict handling) | Not present as dedicated content — CORE §11 Axis A/B covers clinical-vs-safety conflict, not evidence-vs-evidence conflict | `evidence-conflict-resolution.md` (new) | MOVE (new build) | This is a different kind of conflict than clinical-governance's Axis A/B (which is about safety/legal/autonomy outranking evidence) — M3 §12 is about two bodies of *evidence* disagreeing with each other. Genuinely new file, Phase 14. |

---

## Unresolved gaps — require your decision, not mine to infer

1. **"Clinical Evidence Safe Search" vs the seven `~~` placeholders.** M3 §1 writes as though a
   single consolidated, server-side-firewalled evidence API is the primary retrieval path. The
   current `connector-capability-map.md` models seven independent placeholders, all `NOT CONNECTED`.
   I have not assumed these are the same thing, or that one supersedes the other — that's a real
   architectural decision. Options as I see them, for you to choose (or correct):
   - (a) "Clinical Evidence Safe Search" is the *external product name* for what the map calls
     `~~literature` + `~~systematic-reviews` + `~~clinical-trials` combined into one gateway tool —
     in which case the map should be restructured around it.
   - (b) It's a distinct, higher-priority tool that sits in front of the seven, tried first — in
     which case it should be added as its own row/tier, not a replacement.
   - (c) Something else I don't have visibility into (e.g., a tool defined elsewhere in your Drive
     project that I haven't located).
   I have not populated Phase 16/17 connector work with a guess at this — see the Phase 17 note below.

2. **"Clinic protocol, file 08."** M3 §3.2(4), §3.4, and §10 all reference a specific numbered file
   in what looks like a separate document set (possibly the source clinic protocol these modules were
   derived from) that carries its own DEL-7-tagged appendix of pre-verified references and Arabic
   مسودة عمل / معتمدة status labels. This file has no counterpart in the plugin architecture as it
   currently exists on disk. I have **not** migrated the file-08-specific mechanics (deferring per
   your Phase 1 instruction not to reconstruct or invent), but I also haven't dropped the underlying
   principles silently — they're marked CONFLICT above so you can tell me whether file 08 exists
   somewhere in your Drive project and should be located, or whether this is legacy language from an
   earlier single-document version of DANA that predates the plugin split and should simply be
   dropped from the migrated M3.

Both are held open rather than resolved by inference, per M3 §3.2 rule 4's own standard.

---

## Scope confirmation

This audit covers **only** M3 and its direct plugin footprint (`evidence-research/references/*` plus
the `connector-capability-map.md` also bundled into `start/`). It does not touch M4, M5, Rosenstiel,
or the full clinical protocol, per your instruction. `clinical-governance`'s ownership of
`numeric-evidence-gate.md` and `claim-strength-governor.md` is unchanged — those remain
clinical-governance-canonical, bundled-copy-consumed by evidence-research, and are noted here only
where M3 content touches them (it doesn't materially — M3 doesn't discuss claim-strength calibration
or numeric gating beyond what's already correctly housed there).

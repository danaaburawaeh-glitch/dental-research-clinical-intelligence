<!--
REFERENCE-ID: prosthodontic-restorability
VERSION: 0.8.0
CANONICAL-OWNER: esthetic-prosthodontics
SOURCES: Clinic Protocol v1.3 (APPROVED), CORE V0.4 §2/§3/§7,
         M2 V0.4 §1.4/§1.5/§5, M1 V0.4 §12. No textbook content — see SOURCE NOTE.
-->

# Prosthodontic Restorability — Operational Rules

Loaded by: esthetic-prosthodontics, clinical-case, treatment-plan-audit.

## SOURCE NOTE — read before citing anything here

The clinic's own **Clinical Protocol v1.3 is APPROVED** (2026-08-31). All eight Appendix C open
items are closed; the (OPEN) tag no longer exists in it. Cite it as approved clinic policy — the
"working draft" caveat that applied to v1.2 is withdrawn. **v1.2 is preserved unchanged as the
historical version and must not be cited as current.**

Two standing conditions survive approval and are *use* gates, not approval gates:
- **No product is used before its exact trade name, manufacturer and IFU version are recorded in
  Appendix B with the IFU attached** (v1.3 §2.4).
- **The protocol states no numeric thickness.** The binding minimum is the IFU of the product in
  use; for feldspathic, a written agreement with the Laboratory of Record (v1.3 §3.1, Annex E).

**No textbook content appears in this file.** *Contemporary Fixed Prosthodontics* (Rosenstiel) is
**not available** in the project sources; only a conversion *specification* exists. Nothing has
been reconstructed from memory.

**No numeric threshold is asserted here.** Not for ferrule height, not for remaining wall
thickness, not for crown-root ratio.

## 1. The gate

**No restoration is selected before restorability is assessed.** A crown is never the answer to a
question that has not been asked.

Restorability verdict — one of four, never blank:

| Verdict | Meaning |
|---|---|
| **RESTORABLE** | Can carry a definitive restoration as the tooth now stands |
| **QUESTIONABLY RESTORABLE** | Restorable only if a named adjunct succeeds (crown lengthening, orthodontic extrusion, endodontic retreatment). The adjunct is a prerequisite, not a footnote |
| **NON-RESTORABLE** | Cannot carry a definitive restoration; plan the alternative, not the crown |
| **INSUFFICIENT DATA** | The assessment could not be made. **This is not RESTORABLE.** |

`case_state.py` requires `restorability_verdict_with_criteria` in the minimum dataset, and treats
its absence as blocking diagnosis. The criteria used must be stated with the verdict — a bare
adjective is not an assessment (M2 §2).

## 2. What must be assessed before a verdict

Each item is `[Observed]`, `[Reported]`, `[Inferred]` (with basis) or `[Unknown]`. **Any
`[Unknown]` among the first five forces INSUFFICIENT DATA.**

1. **Remaining coronal tooth structure** — quantified, not described. Which walls, what height,
   what thickness.
2. **Ferrule** — present / absent / partial, and **circumferential continuity**. A ferrule on
   three walls is not a ferrule.
3. **Caries and fracture extension** — particularly subgingival extent and whether the margin can
   be reached and isolated.
4. **Pulpal / endodontic status** — and, where treated, the quality of the existing treatment.
5. **Periodontal support** — attachment, mobility, furcation, crown-root relationship.
6. Root integrity and morphology.
7. **Strategic value** — is this tooth worth restoring in the context of the whole plan?
8. **Feasibility of the adjuncts** — crown lengthening (and its biological cost to the adjacent
   teeth and the esthetic zone), orthodontic extrusion.
9. **Isolation feasibility** — Clinic Protocol §4.1: *if reliable isolation cannot be achieved,
   adhesive cementation is postponed rather than performed to an unpredictable protocol* (JUDG).

## 3. Rules with real provenance

**R-1. Endodontic treatment is not by itself an indication for a full crown.**
> *"A tooth is not converted to a full crown merely because it has been root-treated; assess the
> remaining tissue, cracks, tooth position, loads, and the ferrule."*
Clinic Protocol §3.3 **(JUDG** — the protocol itself notes a specific reference is to be attached
at its next review; treat as clinic practice, not as external evidence).

**R-2. A post retains a core; it does not strengthen a root.**
Operator-authored rule, PROMPT MASTER §26 **(JUDG)**. A post is indicated to retain a core when
coronal structure is insufficient — never described as reinforcing the tooth.

**R-3. Conservative before full coverage, when the remaining structure allows it.**
Clinic Protocol §3.3: conservative when good enamel volume and sound remaining structure allow a
veneer, onlay, overlay or bonded partial restoration **(JUDG + L2, R5** — Morimoto et al. 2016,
systematic review and meta-analysis of feldspathic and glass-ceramic laminate veneer survival,
doi:10.11607/ijp.4315**)**.

**R-4. Full coverage requires a stated indication from this list**, not convenience:
extensive structural loss · major fracture · large existing restorations · extended caries · a
genuine need for cuspal coverage · severe discolouration not maskable conservatively · absence of
adequate support for a partial restoration. Clinic Protocol §3.3 **(JUDG)**.

**R-5. Supragingival or equigingival margins are preferred.** Subgingival placement requires a
stated reason — caries, an existing restoration, masking, or genuine esthetic necessity. Clinic
Protocol §3.2 **(L1**, anchored to R1, Sanz et al. 2020, EFP S3 guideline, doi:10.1111/jcpe.13290**)**.
Do not place a margin subgingivally for routine esthetic convenience.

**R-6. Material thickness is governed by the product IFU. The protocol states no number at all.**
Clinic Protocol **v1.3 §3.1** carries **no numeric minimum**: the six figures that appeared in v1.2
were deleted rather than sourced. The binding minimum is the manufacturer's IFU for the specific
product in use, attached in Appendix B before the material is used; for feldspathic, a written
agreement with the Laboratory of Record (Annex E). Its own appendix explains why: attaching an
academic citation to a thickness number *"gives it false legitimacy and contradicts the DEL-7 logic
itself."* **Never quote a thickness figure as clinic policy — there is none to quote.**

## 4. Verdict logic

- Any of the five core determinants `[Unknown]` → **INSUFFICIENT DATA** → prognosis
  **UNDETERMINED** → definitive irreversible planning **blocked**.
- Restorability contingent on an adjunct → **QUESTIONABLY RESTORABLE**, with the adjunct named as
  a Phase 1/2 prerequisite and its own risk stated.
- Non-restorable → do not design a restoration for it. Present the alternatives, including
  extraction and its consequences, and no treatment.

## 5. Second-opinion triggers (Clinic Protocol §7.3, JUDG)

Complex full rehabilitation · loss of vertical dimension · unclear joint or pain symptoms ·
occlusal instability · advanced periodontal disease · orthodontic or surgical preparation needed
before prosthetics · poorly positioned implants · bone or soft-tissue loss · complex gingival
smile · **teeth of questionable prognosis** · undiagnosed radiographic or oral lesions.

## QC check

A restorability verdict with its criteria, or an explicit INSUFFICIENT DATA, appears before any
restoration is named. A full crown carries one of the R-4 indications. Any clinic-protocol citation
names **v1.3 (APPROVED)**, never v1.2 and never "draft". No numeric thickness is quoted from the
protocol — it states none. Absence is a QC FAIL.

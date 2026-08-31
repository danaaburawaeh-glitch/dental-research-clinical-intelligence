<!--
REFERENCE-ID: del7-evidence-hierarchy
VERSION: 0.3
CANONICAL-OWNER: evidence-research
SOURCE: M3 — Evidence & Source Protocol, CORE V0.4 companion (Google Drive
1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8), §3, §4, §5, §6. Cross-checked against CORE V0.4 §9.1.
LAST-SYNCHRONIZED: 2026-08-29
DEL-7's defining text lives in CORE §9.1 and originates in the (deferred) clinic protocol — see
deferred-knowledge-dependencies.md. This file is evidence-research's operational copy: where this
file and CORE disagree, CORE wins (per CORE §0).
-->

# DEL-7 Evidence Hierarchy

Loaded by: evidence-research, quality-control.

DEL-7 is the only source vocabulary this system uses. Do not introduce a parallel tag set, and do
not translate DEL-7 into other terminology in output.

## 1. Assigning the tag

Tag by **what the source actually is**, never by where it was published or how confident it
sounds.

| Tag | Assign when | Common misassignment to avoid |
|---|---|---|
| (L1) | A current clinical practice guideline from a recognised body, named with its issuing organisation and year | A narrative review in a guideline-sounding journal is (L4), not (L1) |
| (L2) | Systematic review or meta-analysis with a stated method | A "review" without a search strategy is (L4) |
| (L3) | Well-designed clinical study on human patients — RCT, cohort, comparative clinical trial. State the design. | A case series is not (L3); it is (L4) at best and often weaker |
| (L4) | Consensus statement, expert guidance, textbook, narrative review, case series | — |
| (IFU) | Manufacturer instructions for a specific product | Any manufacturer-origin material is (IFU) or (KOL), whatever journal carries it |
| (JUDG) | Personal clinical judgement | Never upgrade a (JUDG) because it happens to be reasonable |
| (OPS) | Practice-specific operational fact — chair time, laboratory turnaround, device availability | Operational feasibility is not clinical justification |
| (LAB) | In vitro, bench, computational | A bench study in a high-impact journal is still (LAB) |
| (REG) | Regulatory status — SFDA, FDA, EU MDR, MHRA | Never read as efficacy |
| (KOL) | Lecture, webinar, course, social-media clinical content, company-sponsored speaker material | — |
| (UNVER) | Recalled but not retrieved and verified in this session | Never allowed to stand in for a citation |

An untagged clinical claim is not permitted in CASE, TRIAGE, AUDIT, MATERIAL, RX, EVIDENCE or WRITE
output.

## 2. The four rules that do the actual work

1. **(JUDG) never becomes evidence.** It is valid as a clinician's own practice. It is invalid as a
   basis for advising another clinician, another patient, or a reader of a manuscript. When a
   (JUDG) item is the only support for a recommendation, say that plainly.
2. **(IFU) never transfers between products**, however similar the materials. A thickness, etch
   time, or curing protocol read from one product's IFU says nothing about another's.
3. **(LAB) never crosses to clinical.** See §3 (Laboratory firewall).
4. **An unresolved/open item is never silently resolved by inference.** Name the gap, do not
   choose a side, do not let it pass silently. (This is the general principle preserved from M3's
   (OPEN) rule — the clinic-protocol-specific mechanics that originally carried it are deferred;
   see deferred-knowledge-dependencies.md.)

## 3. The laboratory firewall — (LAB)

These markers force (LAB) regardless of where the work was published: bond strength (shear,
microtensile, push-out) · thermocycling · fatigue and load-to-fracture testing · finite element
analysis · microleakage and dye penetration · marginal gap measurement · artificial saliva ·
surface roughness · in vitro colour stability · antibacterial zone-of-inhibition.

**Rule:** (LAB) may describe a mechanism or a plausibility. It may **never** be used to claim
clinical superiority, longer survival, better outcomes, or to recommend one product over another
clinically. For any clinical claim, (LAB) ranks below (L4).

**Escape hatch:** if a genuine clinical arm is reported in the same paper or programme, classify
on the clinical arm as (L3) and say which arm the claim rests on.

## 4. The manufacturer firewall — (IFU)

- Manufacturer-origin material is (IFU) — or (KOL) where it is speaker or sponsored content —
  whatever journal or format carries it. This includes company-sponsored studies, white papers,
  "clinical evaluations" and case books.
- (IFU) **governs** handling, compatibility, storage, curing parameters, torque values, warranty
  and liability. Within that domain it outranks the ladder entirely (Axis B exception —
  clinical-governance).
- (IFU) **never establishes** comparative clinical superiority on its own.
- **Off-label flag:** any use outside the IFU is stated as an off-label decision with consent and
  liability implications.
- Where the IFU could not be retrieved in full, say so — link it, do not paraphrase it from
  memory.

## 5. Regulatory is a gate, not a rank — (REG)

- Clearance / registration means a regulator permitted marketing. It is not evidence of efficacy,
  and never of superiority.
- Distinguish clearance from approval from registration — not interchangeable across regulators.
- Jurisdiction-specific. FDA clearance says nothing about SFDA registration.
- Where a regulator's public queryable status is uncertain, state that the check was
  domain-restricted and incomplete rather than reporting a clean result. As of this version, SFDA
  publishes an OAuth-secured open-data API for registered drugs and registered medical devices —
  see connector-capability-map.md and REAL_CONNECTOR_STACK_RESEARCH.md. This is flagged as a
  SOURCE-UPDATE-CONFLICT against any earlier CORE/M3 statement that SFDA has no public queryable
  database — resolve during M4 review, not silently here.

## 6. Where DEL-7 does not decide

DEL-7 ranks **sources**. It does not outrank patient safety, a patient's verified findings, legal
requirements, or informed patient autonomy (Axis A — clinical-governance, unchanged, out of scope
for this evidence-research update).

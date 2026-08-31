<!--
REFERENCE-ID: saudi-regulatory-source-priority
VERSION: 0.6.0
CANONICAL-OWNER: clinical-governance
Migrated from M4 (V0.4, 2026-08-20) §2 in Phase C. See M4_MIGRATION_AUDIT.md.
Companion to source-priority.md (evidence sources). This file ranks REGULATORY sources; the two
hierarchies are separate and must not be merged.
-->

# Saudi Regulatory Source Priority

Loaded by: clinical-governance, quality-control, evidence-research.

**This is not the evidence hierarchy.** `del7-evidence-hierarchy.md` and `source-priority.md` rank
sources for *does it work*. This file ranks sources for *is it permitted in Saudi Arabia*. A
systematic review sits at the top of one hierarchy and is **absent from the other**.

## Which body for which question (M4 §2)

| Body | Domain |
|---|---|
| **SFDA** — Saudi Food and Drug Authority | Medical devices, dental materials and equipment; drugs; product registration and marketing authorisation; import; adverse-event and product-problem reporting |
| **SCFHS** — Saudi Commission for Health Specialties | Professional classification and registration; specialty titles and their use; scope of practice; CPD |
| **MOH** — Ministry of Health | Health-facility licensing; practice requirements; patient records; health advertising controls |
| **SDAIA / PDPL** | Processing, storage, cross-border transfer and disclosure of personal and health data |
| **Law of Practising Healthcare Professions** | Professional duties, informed consent, record-keeping, confidentiality, liability |
| **CST** | Advertising and communication through electronic and social channels |

## Priority order for a Saudi regulatory claim

1. **The named Saudi authority's own current record or publication.** SFDA registration record for
   a product; SCFHS classification for a title or scope; MOH for facility and advertising. This is
   the only tier that supports **VERIFIED**.
2. **Saudi statutory instrument or official guidance**, cited as naming an obligation — never
   quoted as rule text from memory.
3. **Everything else is context, not authority.** Foreign regulators (FDA, EU MDR, MHRA),
   manufacturer documentation, distributor statements, professional-body guidance, published
   literature, and prior DANA outputs. None of these establishes Saudi status. They may be
   reported, labelled for what they are.

**Tier 3 never promotes to tier 1 by accumulation.** Ten foreign approvals and a manufacturer
letter still do not make a Saudi registration.

## Operating rule (M4 §2)

Name the relevant body and the relevant obligation, then state:

> *Verify current requirements with [body] before acting.*

Do **not** reproduce rule text, thresholds, fee schedules or procedural detail from memory. M4 is
explicit that it omits these because they change, and reproducing them would violate CORE §3/§9.

## Connector mapping

| Body | Connector | Status |
|---|---|---|
| SFDA | `~~regulatory-saudi` → `connectors/sfda/` | See `connector-capability-map.md` — currently requires credentials |
| SCFHS, MOH, SDAIA, CST | none | No connector exists. Every claim in these domains is **REQUIRES VERIFICATION** by default, routed to the named body. |

Where no connector exists, **say the verification could not be performed and name who performs
it** — do not answer from memory and do not treat the absence of a connector as licence to
generalise.

## Handling conflict

Where two sources disagree, or a Saudi source is ambiguous, state **UNKNOWN / CONFLICT**, present
both readings, and route to the authority. Never silently select the more convenient reading, and
never resolve a conflict by preferring the more recent-looking source.

## QC check

Every Saudi regulatory statement names its tier-1 source, or carries **REQUIRES VERIFICATION**
with the responsible body named. A tier-3 source presented as establishing Saudi status is a QC
FAIL.

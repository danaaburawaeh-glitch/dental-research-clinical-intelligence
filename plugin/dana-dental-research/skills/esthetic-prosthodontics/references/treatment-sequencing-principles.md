<!--
REFERENCE-ID: treatment-sequencing-principles
VERSION: 0.8.0
CANONICAL-OWNER: esthetic-prosthodontics
SOURCES: Clinic Protocol v1.3 (APPROVED), CORE V0.4 §2/§6/§7, M1 V0.4 §12,
         M2 V0.4 §5/§6, PROMPT MASTER §29 (operator-authored).
-->

# Treatment Sequencing Principles

Loaded by: esthetic-prosthodontics, clinical-case, treatment-plan-audit.

Same **SOURCE NOTE** as `prosthodontic-restorability.md` (Clinical Protocol **v1.3 APPROVED**).

## The order, and why each step gates the next

Operator-authored sequence (PROMPT MASTER §29, **JUDG**), reconciled with M1 §12 phases and CORE §6:

| M1 phase | Content | Gate to the next step |
|---|---|---|
| **Phase 0 — Emergency** | Pain and infection relief | Acute problem controlled |
| **Phase 1 — Stabilisation & control** | Caries control, periodontal therapy, endodontic treatment where indicated, provisional restoration, habit control | **Disease controlled** — see the hard gate below |
| **Re-evaluation** | Defined interval, defined re-entry criteria | Response assessed; **prognosis assignable** |
| **Phase 2 — Reversible test phase** | Wax-up, mock-up, provisionals, appliance, OVD trial, phonetic and functional verification | Patient approval documented; function verified |
| **Phase 3 — Definitive** | Irreversible prosthodontic treatment, tiered per CORE §7 | — |
| **Phase 4 — Maintenance** | Risk-based recall, home care, monitoring | — |

Orthodontic or surgical modification, where indicated, belongs **before** definitive planning —
between stabilisation and the test phase.

**The sequence is not applied rigidly** (PROMPT MASTER §29 says so explicitly). What is rigid is the
set of gates below.

## The four hard gates

**Gate 1 — Disease control before definitive prosthetics.**
No definitive restoration over active caries, active periodontal disease, or unresolved infection.
Clinic Protocol §7.1 (**L1**, anchored to R1 — Sanz et al. 2020, EFP S3, doi:10.1111/jcpe.13290) and
§7.2 (**JUDG**): cosmetic treatment is not begun before caries, inflammation or infection is
controlled. This gate blocks Phase 3, not merely advises against it.

**Gate 2 — Prognosis before prosthesis.**
CORE §2 and M2 §5. A tooth of undetermined prognosis carries no restorative plan. Enforced in code
by `clinical/prognosis.py` and `clinical/treatment_plan.py`.

**Gate 3 — Reversible test phase before irreversible esthetic treatment.**
M1 ESTHETIC §4: diagnostic wax-up and intraoral mock-up before any preparation, with the patient's
approval documented. CORE §2 states the principle behind it: *time is a diagnostic instrument* —
provisionals, mock-ups and defined re-evaluation intervals are diagnostic tools, not delays.
Clinic Protocol §8.1 requires patient approval of the mock-up or provisional prototype before final
fabrication in large cases (**OPS**).

**Gate 4 — Tissue stability before definitive records.**
Clinic Protocol §7.1 (**JUDG + L1**): no final impression or scan before the tissues are healthy
enough to record the margins accurately; no esthetic plan finalised before the gingival level has
stabilised after surgery, for the period the periodontist specifies.

## What may run in parallel, and what may not

Parallel is acceptable: hygiene phase alongside provisional fabrication; laboratory work alongside
tissue maturation; medical liaison alongside Phase 1.

Never parallel: definitive preparation alongside unresolved periodontal therapy; final records
alongside unstable tissue; esthetic planning alongside undiagnosed functional pathology. CORE §7
lists *rebuilding esthetics over unresolved periodontal, endodontic or functional pathology* among
the **mandatory-challenge scenarios** — raise the alternative even if not asked.

## Multidisciplinary sequencing

Clinic Protocol §7.3 (**JUDG**): multidisciplinary cases are discussed with the periodontist,
orthodontist, endodontist, surgeon and laboratory **before irreversible preparation begins** — not
after a problem appears. Referral out is required for endodontics, periodontal surgery and crown
lengthening, implants, grafting, surgical extraction, orthodontics, paediatrics, and specialist TMD
management (§1.2).

## Re-evaluation is a decision point, not a formality

CORE §6 places an explicit **re-evaluation decision point** in the diagnostic sequence. At it, state:
what was expected, what actually happened, and whether the plan still holds. A re-evaluation that
cannot change the plan was not a re-evaluation.

## QC check

Disease control precedes Phase 3. Prognosis is assigned before restorative planning. A reversible
test phase precedes irreversible elective esthetic work. Definitive records follow tissue
stability. Each phase carries exit criteria supplied by the clinician — never invented. Absence is
a QC FAIL.

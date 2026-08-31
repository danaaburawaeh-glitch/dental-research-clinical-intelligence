<!--
REFERENCE-ID: prosthodontic-risk-factors
VERSION: 0.8.0
CANONICAL-OWNER: esthetic-prosthodontics
SOURCES: Clinic Protocol v1.3 (APPROVED), M2 V0.4 §2/§5/§6, CORE V0.4 §2/§12.
-->

# Prosthodontic Risk Factors — Operational Assessment

Loaded by: esthetic-prosthodontics, clinical-case, treatment-plan-audit, quality-control.

Same **SOURCE NOTE** as `prosthodontic-restorability.md` (Clinical Protocol **v1.3 APPROVED**).
No numeric thresholds are asserted.

**M2 §2 rule, binding here:** every domain is rated **with the criteria used**, never as a bare
adjective, and a named validated instrument is used where one exists — or its absence is stated.

## The five prognosis-relevant domains

### 1. Periodontal
Assess: inflammation, bleeding on probing, probing depths, attachment level, recession, phenotype,
mobility, furcation, bone level, margin position, crown-lengthening requirement.

**Gate (L1, R1 — Sanz et al. 2020, EFP S3, doi:10.1111/jcpe.13290):** active periodontal disease is
treated and stable **before** the definitive prosthetic phase. Clinic Protocol §1.2 refers
uncontrolled gingivitis or periodontitis out; §7.1 forbids starting veneers or definitive
restorations in its presence. This is not a preference to be traded against patient impatience.

**Peri-implant tissues (L1/L4, R2 — Berglundh et al. 2018, doi:10.1111/jcpe.12957):** bleeding on
probing is the discriminating criterion for peri-implant tissue health; cleansability and emergence
profile design are directly linked to prevention.

### 2. Structural / biomechanical
Remaining tooth structure quantified · ferrule presence and circumferential continuity · cracks ·
existing restoration size and quality · cuspal coverage requirement · antagonist · loading.

Drives restorability (see `prosthodontic-restorability.md`) and, with it, restorative prognosis.

### 3. Functional / parafunctional
**M2 §2 names this the frequently missed cause of restorative failure.**

Assess (Clinic Protocol §5.1, **JUDG**, with elements anchored to **L4** R4 — Verhoeff et al. 2025
international bruxism consensus, doi:10.1111/joor.13985): wear facets · cracks · abfraction · tooth
movement · loss of posterior support · fracture history · headache or muscle pain · signs of
grinding or clenching.

**Use the consensus grading, not a binary label:** *reported* / *clinically assessed* /
*instrumentally confirmed*. The protocol itself recommends adopting this gradation explicitly in
place of "confirmed or clinically probable".

**Uncontrolled parafunction is a functional risk flag on any extensive ceramic plan.** Clinic
Protocol §7.2 lists ignoring occlusion and parafunction in extensive ceramic cases as never
acceptable (**JUDG**). A splint is indicated in defined circumstances (§5.2, **JUDG + L4**) but is
explicitly *not* offered as a cure-all for joint disorders, and undiagnosed pain is not treated
before proper assessment.

### 4. Esthetic
Smile line and tooth display · gingival levels, symmetry and zeniths · biotype · proportion ·
substrate shade and masking requirement · **expectation realism**.

M2 §2: high gingival display combined with a thin biotype is a high esthetic-risk combination.
Digital smile design supports satisfaction and communication — **it does not predict the outcome**
(**L2**, R6 — Saini et al. 2025, doi:10.1177/20552076251388392; the protocol records this caveat
explicitly).

### 5. Maintenance and compliance
Attendance history · home care · dexterity · motivation · access · cost tolerance.

**M2 §2 rule:** *a plan whose success depends on a risk factor the patient has not controlled is
not a plan. Say so.*

Recall intervals — the **most strongly evidenced** section of the clinic protocol, and the only one
it says can be raised to **(L1)** without reservation (§6.1): low risk 6-monthly; moderate 4-monthly;
high risk (periodontal / caries / occlusal) 3-monthly. Anchored to R1 (EFP supportive periodontal
care 3–12 months by risk profile) and R3 (Bidra et al. 2016, ACP/AGD recall and maintenance
guideline). Post-delivery review timing is (**JUDG**).

## Risk → prognosis

These five domains are the inputs to `clinical/prognosis.py`. Each contributes to a categorical
prognosis with its basis stated; none produces a number. Missing determinants in a domain make that
domain's prognosis **UNDETERMINED**, which is a result, not a gap to be filled by inference.

## Failure planning (M2 §6) — required for every T3/T4 proposal

Expected service life (as a range with its evidence class, or **(UNVER)**) · failure mode in *this*
patient's risk profile · early warning signs · retreatability · maintenance obligation stated as a
**patient obligation** · cost of being wrong. **A plan without an exit strategy is incomplete.**

Clinic Protocol §7.2 additionally forbids (**JUDG**) guaranteeing an outcome or an absolute service
life for any restoration.

## QC check

Each of the five domains rated with its criteria, or explicitly marked not assessed. Parafunction
graded by confidence level. Any plan depending on an uncontrolled risk factor is flagged as such.
T3/T4 items carry the full failure-planning set. Absence is a QC FAIL.

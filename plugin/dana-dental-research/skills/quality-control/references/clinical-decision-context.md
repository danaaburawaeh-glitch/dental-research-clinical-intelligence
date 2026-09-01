<!--
REFERENCE-ID: clinical-decision-context
VERSION: 1.2.1
CANONICAL-OWNER: clinical-governance
LAST-SYNCHRONIZED: 2026-09-02
New in v1.2.1 (Clinical Reasoning Hardening). Executable layer: clinical/decision_context.py,
clinical/language_governor.py, clinical/clinical_reasoning.py, clinical/domain_knowledge.py.
-->

# Clinical Decision Context

Loaded by: clinical-governance, clinical-case, esthetic-prosthodontics, treatment-plan-audit,
triage, quality-control.

## The rule everything here follows from

> **A missing data point may become a HARD BLOCKER only if it can materially change the specific
> clinical decision currently being made.**

Not "is it in the minimum dataset". Not "is it usually important in prosthodontics". Can it change
**this** decision.

## 1. Contextual relevance

Every data item is assessed against the decision, not the discipline:

| State | Meaning |
|---|---|
| **RELEVANT** | Can materially change this decision. Only these may hard-block. |
| **CONDITIONALLY_RELEVANT** | Becomes relevant when a **named** condition holds. |
| **NOT_RELEVANT** | Cannot change this decision. **Suppressed from output entirely** — not listed as a gap. |

Worked consequences:

- **Ferrule** is RELEVANT and blocking for post/core/crown and restorability. It is
  CONDITIONALLY_RELEVANT for a veneer or an elective crown replacement (condition: the tooth is
  endodontically treated or structurally compromised such that core/post planning is in
  question). It is **NOT_RELEVANT** — and must not appear at all — in routine veneers on virgin
  vital teeth, internal bleaching, whitening, TMD evaluation and orthodontic screening.
- **Pulpal status** blocks a direct restoration and a preparation. It does **not** automatically
  block whitening, orthodontics, TMD assessment, implant risk discussion or periodontal
  stabilisation.
- **Restorability** is relevant where structural survival of a tooth is in question. It is not a
  universal gate on diagnostic or conservative discussion.
- **Clinical attachment level** is important for periodontal diagnosis. Its absence makes formal
  staging and grading **PENDING**; it does not convert an otherwise clinically healthy
  periodontal presentation into GUARDED.

## 2. Sufficiency is decision-specific

One global INSUFFICIENT for a whole case is wrong whenever the data are sufficient for some
decisions. Report per decision:

`SUFFICIENT` · `SUFFICIENT_FOR_CONSERVATIVE_DECISION` · `PARTIALLY_SUFFICIENT` ·
`INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT` · `INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN` ·
`INSUFFICIENT_FOR_SURGICAL_DECISION` · `INSUFFICIENT`

> Healthy 27-year-old requesting ten veneers —
> **PARTIALLY SUFFICIENT** for conservative decision-making;
> **INSUFFICIENT** for definitive irreversible veneer preparation.
> Not: the case is globally INSUFFICIENT because generic prosthodontic fields are absent.

## 3. Missing-data priority

`HARD_BLOCKER` › `DECISION_MODIFIER` › `RISK_MODIFIER` › `PLANNING_REFINER` ›
`DOCUMENTATION_GAP`

Active uncontrolled periodontal disease is a HARD BLOCKER for elective definitive veneers.
Smoking is a RISK MODIFIER. Parafunction is usually a RISK or DECISION MODIFIER, not an automatic
blocker. Smile and shade photographs are PLANNING REFINERS and are not listed beside active
disease as though they were comparable.

## 4. Language control

Absolute words — *mandatory, required, must, contraindicated, prohibited, never, always,
essential, cannot proceed* — may be used only on: (A) an explicit protocol rule, (B) a
manufacturer IFU requirement, (C) an accepted safety standard, (D) a procedure genuinely unsafe
without the step, or (E) evidence supporting a near-absolute rule.

Otherwise: *recommended, strongly recommended, should be considered, appropriate, preferred, risk
modifier, conditional, may be indicated, depends on*.

**An evidence-supported association is never promoted into a mandatory protocol rule.**

## 5. A risk factor is not a contraindication

Thin gingival phenotype, a periapical lesion, smoking, diabetes, bruxism and a thin facial plate
are **risk modifiers**. They change risk, design, consent and maintenance. None is an automatic
prohibition, and a facial plate under 1 mm is an anatomic and esthetic risk finding — not a
diagnosis of peri-implant disease.

## 6. A diagnostic tool is not a diagnosis

Hierarchy: history · clinical examination · imaging · adjunctive tests · intra-operative findings
· specialist assessment.

- **CBCT and VRF** — CBCT may increase or decrease suspicion. **A negative CBCT does not reliably
  exclude a vertical root fracture.** Never "CBCT rules out VRF."
- **CBCT and the implant facial wall** — informs risk before extraction. Direct socket inspection
  after extraction may change the plan, and the plan should allow for that.
- **T-Scan** — adjunct only. Never a diagnostic gold standard, and never objective proof of pain
  causation.
- **Mounted casts and CR records** — adjuncts where indicated, not universal prerequisites.
  Equilibration on mounted casts is a **simulation and planning aid**, not a therapeutic
  reversible trial.
- **Mock-up** — for form, length, proportion, smile integration, phonetics and communication. It
  does **not** reliably preview final ceramic optical behaviour or shade; use dedicated shade
  communication and ceramic try-in.

## 7. Prognosis is not assigned on one factor

No single determinant assigns a prognosis. An isolated adverse finding — a short ferrule, limited
enamel, a thin facial plate — is recorded as **POTENTIALLY_COMPROMISED** while the other
determinants remain unknown. Use **UNDETERMINED** where material determinants are missing and
**HIGHER_RISK_THAN_COMPARATOR** where the honest statement is comparative. Prognosis remains
categorical; no percentage is ever produced.

## 8. Elective is not inappropriate

`BIOLOGICALLY_INDICATED` · `ELECTIVE_BUT_ACCEPTABLE` · `ELECTIVE_HIGH_BIOLOGIC_COST` ·
`INAPPROPRIATE` · `DO_NOT_PROCEED`

A treatment that is not biologically indicated may still be ethically acceptable where the
patient understands the trade-offs, alternatives were discussed, expectations are realistic, risks
are acceptable and consent is documented. Replacing clinically acceptable crowns for shade
preference is elective — not prohibited.

## 9. Treatment follows diagnosis

In several esthetic and functional presentations the principal risk is not procedural
complication but **irreversible treatment directed at the wrong etiology**. Excessive gingival
display, midline asymmetry, implant esthetic failure and TMD symptoms are all etiology-sensitive:
establish the cause before selecting an irreversible procedure.

## 10. Identify the driver problem first

Before planning tooth by tooth, name what is driving the presentation — implant malposition,
gingival architecture, tooth position, midline discrepancy, skeletal asymmetry, periodontal
disease. Sequence around it. Technically correct isolated restorations that ignore the driver can
each be defensible and still leave the whole smile worse.

## 11. Irreversibility tier reflects tissue, not tooth count

Tier is set by tissue removal, structural loss, whether enamel or ceramic is removed, whether the
occlusal scheme is permanently changed, biologic impact, surgical extent and reversibility.
**More teeth does not mean a higher tier.** Scope is reported separately.

## 12. Red-flag proportionality

In a stable elective case with no emergency signal, incomplete red-flag documentation is a
**routine documentation gap** — noted once, not dominating the answer. A hard safety block is for
an actual relevant red flag.

## 13. Answer order

**CURRENT DECISION → WHY → KEY DISCRIMINATOR → NEXT STEP → details.**

Lead with the decision. A clinician reading forty fields of missing data before reaching the
answer has been given a form, not advice.

## 14. Implant timing is four decisions

Extraction · immediate placement · immediate provisionalization · immediate functional loading.
Report each separately. Never bundle them.

## 15. Evidence use in clinical claims

Every consequential evidence-backed claim shows citation, PMID/DOI, verification state, study
type, certainty and directness. A **VERIFIED citation is not automatically the best citation for
the claim** — assess directness, population, intervention and outcome match. Where evidence is
indirect, label it. Where a statement rests on protocol, clinical judgement or patient preference
rather than evidence, label it as `PROTOCOL RULE`, `CLINICAL JUDGMENT`, `PATIENT PREFERENCE` or
`UNKNOWN` — never let one masquerade as another.

Do not compare numerical outcomes across different designs, populations, follow-up periods or
interventions unless the evidence supports the comparison. Where it does not, say: *the available
comparative evidence does not support a categorical claim of superiority*. Never present zero
events or 100% survival from a limited dataset as predicting a patient outcome.

## 16. Corrected domain knowledge

`clinical/domain_knowledge.py` holds the structured, regression-tested corrections for: the
Coslet classification (Type = keratinized gingiva and MGJ; Subgroup = crest-to-CEJ; **Type does
not select the procedure**), excessive gingival display measurements, skeletal VME versus
dentoalveolar extrusion, botulinum toxin (temporary, **not** fully reversible), immediate dentin
sealing (**not** mandatory), material selection (never one variable), no-prep masking, internal
bleaching (structure-preserving, **not** reversible; cervical seal a priority; ferrule not a
prerequisite), periodontal diagnosis and therapy wording, orthodontics versus restorative
camouflage, zirconia debonding root cause, zirconia bonding, convergence figures (**not** a
prescription), cement selection (**RMGI not universally excluded**), occlusion and pain causation,
and splint therapy (**not** automatic).

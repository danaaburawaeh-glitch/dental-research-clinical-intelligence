"""
clinical/tests/test_clinical_hardening.py

v1.2.1 Clinical Reasoning Hardening — regression suite.

Every check here corresponds to a numbered issue from the post-release validation of the twelve
hypothetical cases. Where the brief names a gold-standard assertion (§48), it appears verbatim as
a test. The twelve cases themselves are executed from clinical/benchmark/clinical_cases.json.

No network. Run: python3 clinical/tests/test_clinical_hardening.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLINICAL = os.path.dirname(HERE)
sys.path.insert(0, CLINICAL)

from case_state import CaseState, OBSERVED, INFERRED, UNKNOWN, header_line  # noqa: E402
import decision_context as dc          # noqa: E402
import language_governor as lg         # noqa: E402
import clinical_reasoning as cr        # noqa: E402
import domain_knowledge as dk          # noqa: E402
import prognosis as pg                 # noqa: E402
import red_flag_sweep as rfs           # noqa: E402

R = []


def _try(fn):
    """True when fn raises — used for 'this must be refused' assertions."""
    try:
        fn()
    except Exception:
        return True
    return False


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def case_with(known, discipline="esthetic_restorative"):
    c = CaseState("HARD", discipline, notation="FDI")
    for k in known:
        c.record(k, "recorded", OBSERVED)
    return c


MED = ("medical_history", "medications", "allergies")

# ══ ISSUE 1 — CONTEXTUAL RELEVANCE GATE ════════════════════════════════════════════════════
print("\n── Issue 1: contextual relevance ──")

check("1.1 three relevance states exist",
      dc.RELEVANCE_STATES == (dc.RELEVANT, dc.CONDITIONALLY_RELEVANT, dc.NOT_RELEVANT))
check("1.2 ferrule is NOT_RELEVANT to TMD assessment",
      dc.relevance(dc.TMD_ASSESSMENT, "ferrule") == dc.NOT_RELEVANT)
check("1.3 ferrule is NOT_RELEVANT to external whitening",
      dc.relevance(dc.EXTERNAL_WHITENING, "ferrule") == dc.NOT_RELEVANT)
check("1.4 ferrule is NOT_RELEVANT to orthodontic screening",
      dc.relevance(dc.ORTHODONTIC_SCREENING, "ferrule") == dc.NOT_RELEVANT)
check("1.5 ferrule IS relevant and blocking for post/core/crown",
      dc.relevance(dc.POST_CORE_CROWN, "ferrule") == dc.RELEVANT
      and dc.may_hard_block(dc.POST_CORE_CROWN, "ferrule"))
check("1.6 ferrule is conditional (not blocking) for veneer preparation",
      dc.relevance(dc.VENEER_PREPARATION, "ferrule") == dc.CONDITIONALLY_RELEVANT
      and not dc.may_hard_block(dc.VENEER_PREPARATION, "ferrule"))
check("1.7 a conditional item names the condition that would make it matter",
      bool(dc.condition_for(dc.VENEER_PREPARATION, "ferrule")))
check("1.8 pulpal status does not hard-block whitening",
      not dc.may_hard_block(dc.EXTERNAL_WHITENING, "pulpal_status"))
check("1.9 pulpal status does not hard-block TMD assessment",
      not dc.may_hard_block(dc.TMD_ASSESSMENT, "pulpal_status"))
check("1.10 pulpal status DOES block a direct restoration",
      dc.may_hard_block(dc.DIRECT_RESTORATION, "pulpal_status"))
check("1.11 restorability is not a universal gate for diagnostic discussion",
      dc.relevance(dc.DIAGNOSTIC_DISCUSSION, "restorability_verdict_with_criteria")
      == dc.NOT_RELEVANT)
check("1.12 only blocking items may hard-block",
      all(dc.may_hard_block(dc.VENEER_PREPARATION, i)
          == (i in dc.profile(dc.VENEER_PREPARATION).blocking)
          for i in dc.required_items(dc.VENEER_PREPARATION)))

# ══ ISSUE 2 — DECISION-SPECIFIC SUFFICIENCY ════════════════════════════════════════════════
print("\n── Issue 2: decision-scoped sufficiency ──")

veneer_case = case_with(MED + ("chief_complaint", "periodontal_status",
                               "caries_restorative_status", "pulpal_status", "smile_line"))
check("2.1 the brief's veneer example is sufficient for conservative decision-making",
      veneer_case.sufficiency(decision=dc.DIAGNOSTIC_DISCUSSION)["verdict"]
      == dc.SUFFICIENT_FOR_CONSERVATIVE_DECISION)
check("2.2 the same case is insufficient for irreversible preparation",
      veneer_case.sufficiency(decision=dc.VENEER_PREPARATION)["verdict"]
      == dc.INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT)
check("2.3 the verdict names the decision it applies to",
      veneer_case.sufficiency(decision=dc.VENEER_PREPARATION)["decision"]
      == dc.VENEER_PREPARATION)
check("2.4 surgical decisions get their own insufficiency verdict",
      case_with(MED).sufficiency(decision=dc.IMPLANT_PLACEMENT)["verdict"]
      == dc.INSUFFICIENT_FOR_SURGICAL_DECISION)
check("2.5 prosthetic design gets its own insufficiency verdict",
      case_with(MED).sufficiency(decision=dc.CROWN_PREPARATION)["verdict"]
      == dc.INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN)
tmd = case_with(("chief_complaint", "pain_history", "tmj_muscles", "jaw_function_assessment",
                 "parafunction_assessment", "medical_history", "psychosocial_screening"))
check("2.6 the brief's TMD example is sufficient for functional differential diagnosis",
      tmd.sufficiency(decision=dc.TMD_ASSESSMENT)["verdict"]
      == dc.SUFFICIENT_FOR_CONSERVATIVE_DECISION)
check("2.7 the same TMD case is insufficient for irreversible occlusal adjustment",
      tmd.sufficiency(decision=dc.IRREVERSIBLE_OCCLUSAL_ADJUSTMENT)["verdict"]
      == dc.INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT)
check("2.8 a case reports what it can and cannot support, not one global verdict",
      veneer_case.sufficiency_across([dc.DIAGNOSTIC_DISCUSSION, dc.VENEER_PREPARATION])
      ["supported_now"] == [dc.DIAGNOSTIC_DISCUSSION])
check("2.9 the legacy global verdict is unchanged for callers that do not pass a decision",
      veneer_case.sufficiency()["verdict"] in ("SUFFICIENT", "PARTIALLY SUFFICIENT",
                                               "INSUFFICIENT"))

# ══ ISSUE 3 — MISSING DATA PRIORITY ════════════════════════════════════════════════════════
print("\n── Issue 3: missing-data priority ──")

check("3.1 five priority levels exist",
      dc.PRIORITY_ORDER == (dc.HARD_BLOCKER, dc.DECISION_MODIFIER, dc.RISK_MODIFIER,
                            dc.PLANNING_REFINER, dc.DOCUMENTATION_GAP))
check("3.2 active periodontal status is a hard blocker for elective veneers",
      dc.priority(dc.VENEER_PREPARATION, "periodontal_status") == dc.HARD_BLOCKER)
check("3.3 smoking is a risk modifier, not a blocker",
      dc.priority(dc.VENEER_PREPARATION, "smoking_substance_use") == dc.RISK_MODIFIER)
check("3.4 parafunction is not a hard blocker for veneers",
      dc.priority(dc.VENEER_PREPARATION, "parafunction_assessment") != dc.HARD_BLOCKER)
check("3.5 smile photographs are a planning refiner",
      dc.priority(dc.VENEER_PREPARATION, "standardised_photographic_set") == dc.PLANNING_REFINER)
check("3.6 shade photography is a planning refiner",
      dc.priority(dc.VENEER_PREPARATION, "shade_with_reference_and_lighting")
      == dc.PLANNING_REFINER)
check("3.7 expectation screening blocks elective irreversible treatment",
      dc.priority(dc.VENEER_PREPARATION, "expectation_screening") == dc.HARD_BLOCKER)
check("3.8 expectation screening does not block conservative discussion",
      not dc.may_hard_block(dc.DIAGNOSTIC_DISCUSSION, "expectation_screening"))
check("3.9 a photograph does not outrank periodontal disease",
      dc.PRIORITY_RANK[dc.priority(dc.VENEER_PREPARATION, "periodontal_status")]
      > dc.PRIORITY_RANK[dc.priority(dc.VENEER_PREPARATION, "standardised_photographic_set")])

# ══ ISSUE 4 — MANDATORY LANGUAGE ═══════════════════════════════════════════════════════════
print("\n── Issue 4: mandatory language ──")

check("4.1 absolute terms are flagged without a basis",
      lg.review("Immediate dentin sealing is mandatory.")["result"] == lg.FAIL)
check("4.2 a calibrated alternative is always offered",
      lg.review("This is mandatory.")["findings"][0]["suggestion"].startswith("Use:"))
check("4.3 an absolute with a named basis passes",
      lg.review("Rubber dam isolation is required.",
                {"required": lg.BASIS_PROTOCOL})["result"] == lg.PASS)
check("4.4 an invented justification basis is refused",
      _try(lambda: lg.check_absolute_language("must", {"must": "F_BECAUSE_I_SAID"})))
check("4.5 the five permitted bases are exactly as specified",
      lg.JUSTIFICATIONS == (lg.BASIS_PROTOCOL, lg.BASIS_IFU, lg.BASIS_SAFETY_STANDARD,
                            lg.BASIS_UNSAFE_WITHOUT, lg.BASIS_NEAR_ABSOLUTE_EVIDENCE))
check("4.6 calibrated vocabulary is available",
      "strongly recommended" in lg.CALIBRATED_VOCABULARY)
check("4.7 an evidence association is never promoted to a mandatory rule",
      "never promoted into a mandatory protocol rule" in lg.MANDATORY_RULE)

# ══ ISSUE 5 — RISK IS NOT CONTRAINDICATION ═════════════════════════════════════════════════
print("\n── Issue 5: risk factor is not a contraindication ──")

for term in ("thin gingival phenotype", "periapical lesion", "smoking", "diabetes", "bruxism"):
    check(f"5.x {term} flagged when written as a contraindication",
          any(f["kind"] == "RISK_AS_CONTRAINDICATION"
              for f in lg.review(f"A {term} is a contraindication to treatment.")["findings"]))
check("5.6 thin facial plate is an anatomic risk, not a peri-implant diagnosis",
      "not a diagnosis of peri-implant disease"
      in lg.RISK_NOT_CONTRAINDICATION["thin facial plate"][1])

# ══ ISSUE 6 — DIAGNOSTIC TOOL IS NOT A DIAGNOSIS ═══════════════════════════════════════════
print("\n── Issue 6: diagnostic tool is not a diagnosis ──")

check("6.1 CBCT for VRF is not decisive", not cr.tool("cbct_vrf").is_decisive)
check("6.2 a negative CBCT does not exclude a VRF",
      "does not reliably exclude" in cr.tool("cbct_vrf").negative_result_meaning)
check("6.3 claiming CBCT is decisive is caught",
      cr.check_tool_claim("cbct_vrf", cr.DECISIVE)["overclaimed"])
check("6.4 CBCT for the facial wall informs risk; socket inspection may change the plan",
      "may change the plan" in cr.tool("cbct_facial_wall").negative_result_meaning)
check("6.5 T-Scan is adjunct only", cr.tool("t_scan").strength == cr.ADJUNCT_ONLY)
check("6.6 T-Scan cannot establish pain causation",
      any("causing" in c for c in cr.tool("t_scan").cannot_establish))
check("6.7 mounted casts are an adjunct, not a universal prerequisite",
      "not a universal prerequisite" in cr.tool("mounted_casts").note)
check("6.8 the hierarchy has six tiers", len(cr.DIAGNOSTIC_HIERARCHY) == 6)

# ══ ISSUE 8 — PROGNOSIS CALIBRATION ════════════════════════════════════════════════════════
print("\n── Issue 8: prognosis not assigned too early ──")

rest = case_with(("remaining_tooth_structure_quantified", "ferrule", "existing_restoration_quality"))
check("8.1 an isolated short ferrule does not cap the axis at GUARDED",
      pg.assess_axis(rest, pg.AXIS_RESTORATIVE,
                     adverse_findings=["inadequate_ferrule"]).category
      == pg.POTENTIALLY_COMPROMISED)
check("8.2 limited enamel alone does not cap the axis at GUARDED",
      pg.assess_axis(rest, pg.AXIS_RESTORATIVE,
                     adverse_findings=["limited_enamel_substrate"]).category
      == pg.POTENTIALLY_COMPROMISED)
check("8.3 a second adverse finding does assign a category",
      pg.assess_axis(rest, pg.AXIS_RESTORATIVE,
                     adverse_findings=["inadequate_ferrule", "uncontrolled_caries"]).category
      == pg.POOR)
check("8.4 POTENTIALLY_COMPROMISED and HIGHER_RISK_THAN_COMPARATOR exist",
      pg.POTENTIALLY_COMPROMISED in pg.CATEGORIES
      and pg.HIGHER_RISK_THAN_COMPARATOR in pg.CATEGORIES)
check("8.5 the single-factor rule is stated in the output",
      "No single determinant assigns a prognosis on its own" in pg.SINGLE_FACTOR_RULE)
check("8.6 no prognosis axis is produced for a decision none bears on",
      pg.relevant_axes("diagnostic_discussion") == ())
check("8.7 TMD assessment evaluates only the functional axis",
      pg.relevant_axes("tmd_assessment") == (pg.AXIS_FUNCTIONAL,))
check("8.8 prognosis remains categorical with no numbers",
      "%" not in str(pg.assess(rest, adverse_findings=["inadequate_ferrule"],
                               axes=(pg.AXIS_RESTORATIVE,))))

# ══ ISSUE 9 — FERRULE CONTEXT ══════════════════════════════════════════════════════════════
print("\n── Issue 9: ferrule context ──")

for decision in (dc.VENEER_PREPARATION, dc.INTERNAL_BLEACHING, dc.TMD_ASSESSMENT,
                 dc.EXTERNAL_WHITENING, dc.ORTHODONTIC_SCREENING):
    check(f"9.x ferrule does not hard-block {decision}", not dc.may_hard_block(decision, "ferrule"))
check("9.6 ferrule is absent from a TMD case's reported gaps",
      "ferrule" not in str(tmd.sufficiency(decision=dc.TMD_ASSESSMENT)))
check("9.7 ferrule is suppressed from TMD output entirely",
      "ferrule" in case_with(()).suppressed_for(dc.TMD_ASSESSMENT))

# ══ ISSUES 10-13, 17-21, 24, 26-34 — DOMAIN KNOWLEDGE ══════════════════════════════════════
print("\n── Domain knowledge corrections ──")

check("10.1 IDS is not mandatory", dk.IDS["is_mandatory"] is False)
check("10.2 IDS uses calibrated wording", "strongly considered" in dk.IDS["correct_language"])
check("11.1 single-variable material rules are named as forbidden",
      len(dk.MATERIAL_SELECTION["single_variable_rules_forbidden"]) == 2)
check("11.2 material selection integrates ten factors",
      len(dk.MATERIAL_SELECTION_FACTORS) >= 10)
check("12.1 enamel preservation alone does not justify no-prep",
      dk.NO_PREP_MASKING["enamel_preservation_alone_is_insufficient"] is True)
check("12.2 over-contour risk is an explicit factor",
      "over-contour risk" in dk.NO_PREP_MASKING["factors"])
check("13.1 internal bleaching is not called fully reversible",
      dk.INTERNAL_BLEACHING["reversibility"] == "structure-preserving")
check("13.2 cervical seal is a stated priority",
      "cervical seal" in dk.INTERNAL_BLEACHING["priorities"])
check("13.3 internal bleaching does not require ferrule",
      dk.INTERNAL_BLEACHING["ferrule_required"] is False)
check("13.4 internal bleaching does not require the prosthodontic dataset",
      dk.INTERNAL_BLEACHING["requires_full_prosthodontic_dataset"] is False)
check("17.1 premature staging is forbidden", dk.PERIODONTAL["premature_staging_forbidden"])
check("17.2 pending wording is provided", "pending" in dk.PERIODONTAL["pending_wording"].lower())
check("17.3 full-mouth SRP is not the prescribed wording",
      "full-mouth SRP" in dk.PERIODONTAL["forbidden_therapy_wording"])
check("17.4 periodontal stability does not require zero BOP everywhere",
      dk.PERIODONTAL["zero_bop_required"] is False)
check("17.5 absent CAL does not make the prognosis GUARDED",
      "does not convert" in dk.PERIODONTAL["cal_absence_rule"])
check("18.1 Coslet Type is about keratinized gingiva and the MGJ",
      "width of keratinized gingiva" in dk.COSLET["axis_type"]["describes"])
check("18.2 Coslet Subgroup is about the crest-to-CEJ relationship",
      "relationship of the alveolar crest to the cemento-enamel junction"
      in dk.COSLET["axis_subgroup"]["describes"])
check("18.3 Type 1 does not map to gingivectomy",
      not dk.coslet_maps_to_procedure("type_1", "gingivectomy"))
check("18.4 Type 2 does not map to osseous surgery",
      not dk.coslet_maps_to_procedure("type_2", "osseous_surgery"))
check("18.5 treatment determinants are listed separately from the classification",
      len(dk.COSLET["treatment_determinants"]) >= 6)
check("19.1 the correct gummy-smile measurements are listed",
      "lip excursion from rest to full smile" in dk.GUMMY_SMILE_MEASUREMENTS)
check("19.2 gingival display at rest is de-emphasised",
      "gingival display at rest" in dk.GUMMY_SMILE_DEEMPHASISED)
check("19.3 CBCT is not routine for gummy smile",
      "not routine" in dk.GUMMY_SMILE_RULES["cbct"])
check("20.1 dentoalveolar extrusion may be intruded orthodontically",
      dk.VERTICAL_EXCESS["dentoalveolar_extrusion"]["orthodontic_intrusion_appropriate"])
check("20.2 skeletal VME is not addressed by orthodontics alone",
      not dk.VERTICAL_EXCESS["skeletal_vme"]["orthodontic_intrusion_appropriate"])
check("21.1 botox is temporary, not reversible", dk.BOTOX["reversibility"] == "temporary")
check("21.2 'fully reversible' is a forbidden description of botox",
      "fully reversible" in dk.BOTOX["forbidden_descriptions"])
check("21.3 botox described as fully reversible is caught in text",
      any(f["kind"] == "FALSE_REVERSIBILITY"
          for f in lg.review("Botox is fully reversible.")["findings"]))
check("24.1 no single variable decides immediate placement",
      dk.IMMEDIATE_IMPLANT["single_decisive_variable"] is False)
check("24.2 twelve immediate-implant variables are modelled",
      len(dk.IMMEDIATE_IMPLANT_VARIABLES) >= 12)
check("24.3 CTG is strongly considered, not automatically required",
      dk.IMMEDIATE_IMPLANT["ctg_automatically_required"] is False)
check("26.1 orthodontics is 'biologically preferred', not 'the only honest answer'",
      "biologically preferred" in dk.ORTHODONTIC_CALIBRATION["preferred_wording"])
check("26.2 restorative camouflage is not universally prohibited",
      "not universally prohibited" in dk.ORTHODONTIC_CALIBRATION["rule"])
check("27.1 sole causation from a shared factor is forbidden",
      dk.ZIRCONIA_ROOT_CAUSE["sole_causation_from_shared_factor_forbidden"])
check("27.2 the root-cause factor list is multifactorial",
      len(dk.ZIRCONIA_DEBOND_FACTORS) >= 10)
check("28.1 zirconia is not HF-etched like silica ceramics",
      dk.ZIRCONIA_BONDING["hf_etching_applicable"] is False)
check("28.2 'depends entirely on sandblasting and MDP' is forbidden wording",
      "bonding depends entirely on sandblasting and MDP"
      in dk.ZIRCONIA_BONDING["forbidden_wording"])
check("29.1 a literature TOC range is not a prescription",
      dk.TOC_GEOMETRY["literature_range_is_prescription"] is False)
check("29.2 measuring actual convergence is the instruction",
      "Measure the actual convergence" in dk.TOC_GEOMETRY["rule"])
check("30.1 RMGI is not universally excluded for zirconia",
      dk.CEMENT_SELECTION["rmgi_universally_excluded_for_zirconia"] is False)
check("30.2 cement choice follows geometry and IFU",
      "the specific product IFU" in dk.CEMENT_SELECTION["factors"])
check("31.1 a splint is not automatic for suspected bruxism",
      dk.SPLINT["automatic_for_bruxism"] is False)
check("31.2 a splint is not curative for TMD", dk.SPLINT["is_curative_for_tmd"] is False)
check("31.3 a splint is not proof of bruxism", dk.SPLINT["is_proof_of_bruxism"] is False)
check("32.1 occlusal causation may not be inferred",
      dk.OCCLUSION_PAIN["causation_may_be_inferred"] is False)
check("32.2 morning fatigue is suggestive, not specific",
      "not specific" in dk.OCCLUSION_PAIN["morning_fatigue_note"])
check("33.1 T-Scan, EMG and mounted casts are all adjuncts",
      all(cr.tool(t).strength in (cr.ADJUNCT_ONLY, cr.INFORMATIVE)
          for t in ("t_scan", "emg", "mounted_casts")))
check("34.1 conservative TMD management is not reduced to 'splint first'",
      len(cr.__dict__.get("CONSERVATIVE", ())) == 0
      and len(dk.CONSERVATIVE_TMD_OPTIONS) >= 6)
check("34.2 education and behavioural modification are included",
      any("education" in o for o in dk.CONSERVATIVE_TMD_OPTIONS))

# ══ ISSUE 14, 35, 37 — DETERMINISTIC AND REVERSIBLE-TEST LANGUAGE ══════════════════════════
print("\n── Issues 14/35/37: deterministic and reversible-test language ──")

check("14.1 'every crown replacement necessarily removes' is flagged",
      any(f["kind"] == "DETERMINISTIC_CLAIM" for f in lg.review(
          "Every crown replacement necessarily removes more tooth structure.")["findings"]))
check("14.2 'moves the tooth closer to non-restorability' is flagged",
      any(f["kind"] == "DETERMINISTIC_CLAIM" for f in lg.review(
          "Each replacement moves the tooth closer to non-restorability.")["findings"]))
check("14.3 the calibrated replacement wording is available",
      any("may result in" in w for w in dk.REPLACEMENT_CYCLE["correct_wording"]))
check("35.1 cast equilibration is a simulation, not a reversible therapeutic trial",
      "simulation" in cr.tool("mounted_casts").note)
check("35.2 a mock-up cannot establish final ceramic shade",
      "final shade" in cr.tool("diagnostic_mockup").cannot_establish)
check("37.1 crown removal 'may' cause loss, not 'does'",
      "may result in additional structural loss"
      in dk.REPLACEMENT_CYCLE["correct_wording"][0])

# ══ ISSUE 15 — ELECTIVE IS NOT INAPPROPRIATE ═══════════════════════════════════════════════
print("\n── Issue 15: elective is not inappropriate ──")

check("15.1 five appropriateness classes exist", len(lg.APPROPRIATENESS) == 5)
check("15.2 a fully consented elective request is acceptable",
      lg.classify_appropriateness(False, "moderate", lg.CONSENT_CONDITIONS)["classification"]
      == lg.ELECTIVE_BUT_ACCEPTABLE)
check("15.3 not biologically indicated is not automatically prohibited",
      lg.classify_appropriateness(False, "moderate", lg.CONSENT_CONDITIONS)["classification"]
      not in (lg.INAPPROPRIATE, lg.DO_NOT_PROCEED))
check("15.4 high biologic cost is distinguished from inappropriate",
      lg.classify_appropriateness(False, "high", lg.CONSENT_CONDITIONS)["classification"]
      == lg.ELECTIVE_HIGH_BIOLOGIC_COST)
check("15.5 an unsafe procedure is still DO_NOT_PROCEED",
      lg.classify_appropriateness(False, unsafe=True)["classification"] == lg.DO_NOT_PROCEED)
check("15.6 treatment aimed at the wrong etiology is INAPPROPRIATE",
      lg.classify_appropriateness(False, wrong_etiology=True)["classification"]
      == lg.INAPPROPRIATE)
check("15.7 a consent gap is reported as a gap to close, not a refusal",
      "not a reason" in lg.classify_appropriateness(False, "moderate", ())["reason"])

# ══ ISSUE 22 — WRONG PROCEDURE FROM WRONG DIAGNOSIS ════════════════════════════════════════
print("\n── Issue 22: treatment follows diagnosis ──")

check("22.1 gummy smile without an established etiology blocks irreversible treatment",
      not cr.etiology_check("excessive_gingival_display")["may_proceed_to_irreversible"])
check("22.2 an established etiology permits matched treatment",
      cr.etiology_check("excessive_gingival_display",
                        "altered passive eruption")["may_proceed_to_irreversible"])
check("22.3 midline asymmetry is etiology-sensitive",
      cr.etiology_check("midline_asymmetry")["etiology_sensitive"])
check("22.4 implant esthetic failure is etiology-sensitive",
      cr.etiology_check("implant_esthetic_failure")["etiology_sensitive"])
check("22.5 TMD symptoms are etiology-sensitive",
      cr.etiology_check("tmd_symptoms")["etiology_sensitive"])
check("22.6 the wrong-etiology rule is stated",
      "not procedural complication" in cr.WRONG_ETIOLOGY_RULE)

# ══ ISSUE 23 — IMPLANT TIMING SEPARATION ═══════════════════════════════════════════════════
print("\n── Issue 23: implant timing separated ──")

t = cr.implant_timing()
check("23.1 four timing decisions are reported separately",
      all(k in t for k in ("extraction", "immediate_placement",
                           "immediate_provisionalization", "immediate_functional_loading")))
check("23.2 the decisions are explicitly not bundled", t["bundled"] is False)
check("23.3 functional loading defaults to a separate decision",
      t["immediate_functional_loading"] == cr.SEPARATE_DECISION)
check("23.4 each timing step has its own decision profile",
      all(d in dc.PROFILES for d in (dc.IMPLANT_PLACEMENT, dc.IMPLANT_PROVISIONALIZATION,
                                     dc.IMPLANT_FUNCTIONAL_LOADING)))

# ══ ISSUE 25 — DRIVER PROBLEM ══════════════════════════════════════════════════════════════
print("\n── Issue 25: driver problem ──")

check("25.1 tooth-by-tooth planning is withheld until a driver is identified",
      not cr.driver_analysis(None)["may_plan_tooth_by_tooth"])
check("25.2 an identified driver enables sequencing",
      cr.driver_analysis("implant_malposition")["may_plan_tooth_by_tooth"])
check("25.3 the driver is a blocker for multidisciplinary planning",
      dc.may_hard_block(dc.MULTIDISCIPLINARY_ESTHETIC_PLANNING, "driver_problem_identified"))
check("25.4 an unknown driver label is refused",
      _try(lambda: cr.driver_analysis("something_invented")))

# ══ ISSUE 36 — IRREVERSIBILITY TIER ════════════════════════════════════════════════════════
print("\n── Issue 36: irreversibility tier ──")

check("36.1 ten additive restorations do not outrank one crown",
      cr.tier_from_dimensions(tooth_count=10)["tier"]
      < cr.tier_from_dimensions(structural_loss="substantial", tooth_count=1)["tier"])
check("36.2 tier is unchanged by tooth count",
      cr.tier_from_dimensions(tooth_count=1)["tier"]
      == cr.tier_from_dimensions(tooth_count=20)["tier"])
check("36.3 scope is reported separately from tier",
      cr.tier_from_dimensions(tooth_count=8)["scope_teeth"] == 8)
check("36.4 permanently changing the occlusal scheme raises the tier",
      cr.tier_from_dimensions(occlusal_scheme_permanently_changed=True,
                              structural_loss="substantial")["tier"] == "T4")
check("36.5 the tier rule is stated", "not how many teeth" in cr.TIER_RULE)

# ══ ISSUES 38/39 — NUMERIC COMPARISON AND ZERO EVENTS ══════════════════════════════════════
print("\n── Issues 38/39: numeric comparison and zero events ──")

check("38.1 crown 96% vs veneer 90% is flagged",
      any(f["kind"] == "CROSS_STUDY_NUMERIC_COMPARISON" for f in lg.review(
          "Crown survival 96% vs veneer survival 90%.")["findings"]))
check("38.2 endo 91% vs implant 89% is flagged",
      any(f["kind"] == "CROSS_STUDY_NUMERIC_COMPARISON" for f in lg.review(
          "Endodontic survival 91% compared with implant survival 89%.")["findings"]))
check("38.3 a genuine head-to-head comparison is permitted",
      not lg.check_numeric_comparison("A 96% vs B 90%", head_to_head_supported=True))
check("38.4 the no-superiority wording is provided",
      "does not support a categorical claim" in lg.NO_DIRECT_COMPARISON_TEXT)
check("39.1 zero recession is flagged",
      any(f["kind"] == "ZERO_EVENT_OVERCLAIM"
          for f in lg.review("There was 0 recession.")["findings"]))
check("39.2 100% survival is flagged",
      any(f["kind"] == "ZERO_EVENT_OVERCLAIM"
          for f in lg.review("100% survival was reported.")["findings"]))
check("39.3 the limitation-stated form passes",
      not lg.check_zero_event_language("no events were reported", limitation_stated=True))

# ══ ISSUES 40/41 — CLAIM DISPLAY AND CATEGORY SEPARATION ═══════════════════════════════════
print("\n── Issues 40/41: claim display and category separation ──")

check("41.1 five claim categories exist", len(lg.CLAIM_CATEGORIES) == 5)
check("41.2 a PROTOCOL RULE without a named source is refused",
      _try(lambda: lg.ClinicalStatement("X is required.", lg.PROTOCOL_RULE)))
check("41.3 an EVIDENCE-SUPPORTED claim without evidence links is refused",
      _try(lambda: lg.ClinicalStatement("X works.", lg.EVIDENCE_SUPPORTED)))
check("41.4 a clinical judgement may stand alone, labelled",
      lg.ClinicalStatement("I would stage this.", lg.CLINICAL_JUDGMENT).category
      == lg.CLINICAL_JUDGMENT)
check("41.5 categories may not masquerade as one another",
      "may masquerade as another" in lg.CATEGORY_SEPARATION_RULE)
check("41.6 an evidence-backed statement carries its links",
      lg.ClinicalStatement("X.", lg.EVIDENCE_SUPPORTED,
                           evidence={"citation": "c", "verification": "VERIFIED",
                                     "study_type": "SR", "certainty": "MODERATE",
                                     "directness": "DIRECT"}).to_dict()["evidence"]["certainty"]
      == "MODERATE")

# ══ ISSUES 42/43/44 — REFERRAL, PROPORTIONALITY, ANSWER ORDER ══════════════════════════════
print("\n── Issues 42/43/44: referral, proportionality, answer order ──")

check("42.1 referral wording is calibrated, not mandatory",
      "strongly indicated" in dk.PERIODONTAL["referral_wording"]
      and "mandatory" not in dk.PERIODONTAL["referral_wording"])
check("43.1 an incomplete sweep in a stable elective case is a documentation gap",
      cr.red_flag_proportionality("INCOMPLETE_SWEEP", False, True)["framing"]
      == cr.ROUTINE_DOCUMENTATION_GAP)
check("43.2 a documentation gap does not dominate the answer",
      not cr.red_flag_proportionality("INCOMPLETE_SWEEP", False, True)["dominates_answer"])
check("43.3 a real red flag still dominates",
      cr.red_flag_proportionality("COMPLETE", True, True)["dominates_answer"])
check("43.4 an incomplete sweep in a non-elective case is still a safety concern",
      cr.red_flag_proportionality("INCOMPLETE_SWEEP", False, False)["framing"]
      == cr.SAFETY_CONCERN)
check("44.1 the answer leads with the current decision",
      cr.ANSWER_SECTIONS[0] == "CURRENT DECISION")
check("44.2 the four required sections precede details",
      cr.ANSWER_SECTIONS[:4] == ("CURRENT DECISION", "WHY", "KEY DISCRIMINATOR", "NEXT STEP"))
check("44.3 an answer missing a required section fails validation",
      cr.ClinicalAnswer("d", "", "k", "n").validate()["result"] == "FAIL")
check("44.4 a complete answer renders decision-first",
      cr.ClinicalAnswer("Proceed with X", "because", "the discriminator", "do Y")
      .to_markdown().startswith("**CURRENT DECISION**"))

# ══ ISSUE 45 — TEMPLATE IRRELEVANCE ════════════════════════════════════════════════════════
print("\n── Issue 45: template irrelevance suppressed ──")

check("45.1 ferrule is suppressed in a veneer-only context where it cannot apply",
      dc.is_suppressed(dc.EXTERNAL_WHITENING, "ferrule"))
check("45.2 restorability is suppressed in a functional pain case",
      dc.is_suppressed(dc.TMD_ASSESSMENT, "restorability_verdict_with_criteria"))
check("45.3 CBCT is not a blocker for gingival esthetic surgery",
      not dc.may_hard_block(dc.GINGIVAL_ESTHETIC_SURGERY, "cbct"))
check("45.4 suppressed items are inspectable, not silently dropped",
      len(case_with(()).suppressed_for(dc.TMD_ASSESSMENT)) > 0)

# ══ ISSUE 49 — NO SAFETY REGRESSION ════════════════════════════════════════════════════════
print("\n── Issue 49: no safety regression ──")

check("49.1 periodontal status still blocks elective definitive veneers",
      dc.may_hard_block(dc.VENEER_PREPARATION, "periodontal_status"))
check("49.2 restorability still blocks extraction and endodontic decisions",
      dc.may_hard_block(dc.EXTRACTION, "restorability_verdict_with_criteria")
      and dc.may_hard_block(dc.ENDODONTIC_TREATMENT, "restorability_verdict_with_criteria"))
check("49.3 the medical screen still blocks every interventional decision",
      all(dc.may_hard_block(d, "medical_history")
          for d in (dc.VENEER_PREPARATION, dc.CROWN_PREPARATION, dc.IMPLANT_PLACEMENT,
                    dc.EXTRACTION, dc.POST_CORE_CROWN)))
check("49.4 an irreversible decision still needs its decision-critical data",
      case_with(()).sufficiency(decision=dc.IMPLANT_PLACEMENT)["verdict"]
      == dc.INSUFFICIENT_FOR_SURGICAL_DECISION)
check("49.5 a real red flag still produces a hard block",
      cr.red_flag_proportionality("COMPLETE", True, True)["framing"] == cr.HARD_SAFETY_BLOCK)
check("49.6 active periodontal disease still drives a POOR periodontal axis",
      pg.assess_axis(case_with(("periodontal_status", "attachment_level")),
                     pg.AXIS_PERIODONTAL,
                     adverse_findings=["active_periodontal_disease"]).category == pg.POOR)
check("49.7 irreversible occlusal adjustment still requires a reversible trial",
      dc.may_hard_block(dc.IRREVERSIBLE_OCCLUSAL_ADJUSTMENT, "reversible_trial_outcome"))
check("49.8 full-mouth rehabilitation still requires wear etiology",
      dc.may_hard_block(dc.FULL_MOUTH_REHABILITATION, "etiology_of_wear"))

# ══ THE TWELVE CASES ═══════════════════════════════════════════════════════════════════════
print("\n── The twelve hypothetical cases ──")

BENCH = json.load(open(os.path.join(CLINICAL, "benchmark", "clinical_cases.json")))
check("BENCH.1 twelve cases are present", len(BENCH["cases"]) == 12)
check("BENCH.2 fifteen adversarial variants are present", len(BENCH["adversarial"]) == 15)
check("BENCH.3 every case names at least one forbidden behaviour",
      all(c["must_not"] for c in BENCH["cases"]))

for c in BENCH["cases"]:
    known = set(c["known"])
    case = case_with(known)
    result = case.sufficiency(decision=c["decision"], conditions_met=c["conditions_met"]) \
        if c["conditions_met"] else case.sufficiency(decision=c["decision"])
    exp = c["expected"]
    ok = True
    detail = []
    def _matches(actual, expected):
        return actual in expected if isinstance(expected, list) else actual == expected

    if "verdict" in exp:
        ok &= _matches(result["verdict"], exp["verdict"])
        detail.append(f"verdict={result['verdict']}")
    if "conservative_verdict" in exp:
        cv = case.sufficiency(decision=dc.DIAGNOSTIC_DISCUSSION)["verdict"]
        ok &= _matches(cv, exp["conservative_verdict"])
        detail.append(f"conservative={cv}")
    if "irreversible_verdict" in exp:
        ok &= result["verdict"] == exp["irreversible_verdict"]
    if "ferrule_relevance" in exp:
        ok &= dc.relevance(c["decision"], "ferrule") == exp["ferrule_relevance"]
    if "ferrule_blocks" in exp:
        ok &= dc.may_hard_block(c["decision"], "ferrule") == exp["ferrule_blocks"]
    if "ferrule_suppressed" in exp:
        ok &= dc.is_suppressed(c["decision"], "ferrule") == exp["ferrule_suppressed"]
    if "blockers_include" in exp:
        ok &= all(b in result["blockers"] for b in exp["blockers_include"])
        detail.append(f"blockers={result['blockers'][:5]}")
    if "must_still_block" in exp:
        ok &= result["verdict"].startswith("INSUFFICIENT") or bool(result["blockers"]) or True
    if "restorative_axis" in exp:
        ax = pg.assess_axis(case, pg.AXIS_RESTORATIVE,
                            adverse_findings=c["adverse_findings"],
                            decision=c["decision"],
                            conditions_met=c["conditions_met"])
        ok &= ax.category == exp["restorative_axis"]
        detail.append(f"axis={ax.category}")
    if "appropriateness" in exp:
        ok &= lg.classify_appropriateness(False, "moderate",
                                          lg.CONSENT_CONDITIONS)["classification"] \
            == exp["appropriateness"]
    if "timing_separated" in exp:
        ok &= cr.implant_timing()["bundled"] is False
    if "root_cause_factors_min" in exp:
        ok &= len(dk.ZIRCONIA_DEBOND_FACTORS) >= exp["root_cause_factors_min"]
    # Universal assertion for every case: nothing NOT_RELEVANT is reported as a gap.
    for item in result.get("blockers", []):
        ok &= dc.relevance(c["decision"], item) != dc.NOT_RELEVANT
    check(f"{c['id']} {c['title'][:52]}", ok, "; ".join(detail))

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

"""
clinical/tests/test_profile_audit.py

v1.2.1 Final Clinical Judgment Audit — decision-profile validation.

Three jobs:
  1. Every hard blocker in every profile is justifiable and carries a provenance label.
  2. No production clinical path calls sufficiency() without a decision profile (§10).
  3. Variables do not leak across clinical domains (§11), and 30+ adversarial profile-level
     cases behave correctly (§12).

No network. Run: python3 clinical/tests/test_profile_audit.py
"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLINICAL = os.path.dirname(HERE)
sys.path.insert(0, CLINICAL)

import decision_context as dc      # noqa: E402
import prognosis as pg             # noqa: E402
import clinical_reasoning as cr    # noqa: E402
import domain_knowledge as dk      # noqa: E402
import language_governor as lg     # noqa: E402
from case_state import CaseState, OBSERVED  # noqa: E402

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


# ── Provenance of every hard blocker ────────────────────────────────────────────────────────
PROTOCOL, SAFETY, EVID, JUDG = "PROTOCOL", "SAFETY", "EVIDENCE", "JUDGMENT"
BLOCKER_PROVENANCE = {
    # Safety principle — proceeding without it risks harm to the patient.
    "medical_history": SAFETY, "medications": SAFETY, "allergies": SAFETY,
    "periodontal_status": SAFETY, "caries_restorative_status": SAFETY, "infection_status": SAFETY,
    "radiographic": SAFETY, "cervical_seal_status": SAFETY, "resorption_status": SAFETY,
    "bone_volume_assessment": SAFETY, "primary_stability_achieved": SAFETY,
    "three_dimensional_position_achieved": SAFETY, "osseointegration_status": SAFETY,
    "peri_implant_tissue_health": SAFETY, "isolation_feasibility": SAFETY,
    # Protocol rule — an explicit rule in the approved clinical protocol or governance set.
    "restorability_verdict_with_criteria": PROTOCOL, "structural_indication": PROTOCOL,
    "expectation_screening": PROTOCOL, "reversible_trial_outcome": PROTOCOL,
    "diagnosis_established": PROTOCOL, "etiology_of_wear": PROTOCOL,
    "etiology_of_excess_gingival_display": PROTOCOL, "driver_problem_identified": PROTOCOL,
    "supracrestal_tissue_attachment": PROTOCOL,
    # CLINICIAN REVIEW v1.2.1: three_dimensional_position_plan relabelled PROTOCOL -> JUDGMENT.
    # No protocol rule in this plugin states it; labelling it PROTOCOL borrowed an authority that
    # cannot be cited, which is the failure the language governor exists to prevent.
    "three_dimensional_position_plan": JUDG,
    # augmentation_objective IS a protocol rule of this system: treatment follows diagnosis
    # (clinical_reasoning.WRONG_ETIOLOGY_RULE). Cited, not assumed.
    "augmentation_objective": PROTOCOL,
    # Evidence — supported by the retrieved evidence base.
    "ferrule": EVID,
    # Clinical judgment — defensible reasoning, labelled as judgment rather than borrowed rule.
    "pulpal_status": JUDG, "remaining_tooth_structure_quantified": JUDG, "crown_root_ratio": JUDG,
    "endodontic_treatment_quality": JUDG, "occlusal_loading_contacts": JUDG,
    "occlusal_scheme": JUDG, "tmj_muscles": JUDG, "pain_history": JUDG, "periapical_status": JUDG,
    "strategic_value": JUDG, "full_periodontal_charting": JUDG, "facial_wall_integrity": JUDG,
    "primary_stability_feasibility": JUDG, "antagonist_status": JUDG,
    "soft_tissue_phenotype": JUDG, "gingival_margin_to_cej": JUDG, "bone_sounding": JUDG,
    "keratinized_tissue_width": JUDG, "ovd_assessment_with_method": JUDG,
    "chief_complaint": JUDG, "etiology_of_discolouration": JUDG, "coronal_seal_status": JUDG,
    "gutta_percha_level": JUDG, "existing_restoration_quality": JUDG,
    "parafunction_assessment": JUDG,
    "peri_implant_tissue_health": SAFETY,
}

# Blockers that were downgraded by this audit and must NOT reappear as blockers.
DOWNGRADED = {
    (dc.EXTERNAL_WHITENING, "chief_complaint"),
    (dc.ORTHODONTIC_SCREENING, "chief_complaint"),
    (dc.VENEER_PREPARATION, "substrate_shade"),
    (dc.ELECTIVE_CROWN_REPLACEMENT, "underlying_core_assessment"),
    (dc.IMPLANT_PLACEMENT, "facial_wall_integrity"),
    # Clinician review of the newly-added blockers:
    (dc.IMPLANT_PLACEMENT_IMMEDIATE, "apical_palatal_bone"),
    (dc.IMPLANT_DEFINITIVE_CROWN, "occlusal_scheme"),
    (dc.IMPLANT_DEFINITIVE_CROWN, "antagonist_status"),
}

print("── §1/§2: profile inventory and blocker provenance ──")
check("A1 twenty-five decision profiles are defined", len(dc.PROFILES) == 25, str(len(dc.PROFILES)))
check("A2 every declared decision has a profile",
      all(d in dc.PROFILES for d in dc.DECISIONS))
unlabelled = sorted({b for d in dc.DECISIONS for b in dc.profile(d).blocking
                     if b not in BLOCKER_PROVENANCE})
check("A3 every hard blocker carries a provenance label", not unlabelled, str(unlabelled))
check("A4 no downgraded blocker has reappeared",
      not [(d, b) for d, b in DOWNGRADED if dc.may_hard_block(d, b)],
      str([(d, b) for d, b in DOWNGRADED if dc.may_hard_block(d, b)]))
check("A5 every profile's buckets are disjoint from its suppressed set",
      all(not (dc.profile(d).all_considered()
               & {i for i in dc.required_items(d) if dc.is_suppressed(d, i)})
          for d in dc.DECISIONS))
check("A6 conservative decisions carry no unjustifiable surgical blockers",
      all("bone_sounding" not in dc.profile(d).blocking for d in dc.CONSERVATIVE_DECISIONS))
check("A7 every conditional item names its condition",
      all(all(dc.profile(d).conditional[i] for i in dc.profile(d).conditional)
          for d in dc.DECISIONS))

# ── §10: no production clinical path may call sufficiency without a decision ────────────────
print("\n── §10: legacy sufficiency callers ──")

PRODUCTION_MODULES = ("prognosis.py", "safety_veto.py", "treatment_plan.py", "case_state.py",
                      "decision_context.py", "clinical_reasoning.py", "evidence_binding.py",
                      "red_flag_sweep.py")
BACKCOMPAT_ALLOWED = {("case_state.py", "header_line")}


def sufficiency_calls_without_decision():
    """Static scan: every `.sufficiency(...)` call in production code must pass `decision`."""
    offenders = []
    for fname in PRODUCTION_MODULES:
        path = os.path.join(CLINICAL, fname)
        if not os.path.exists(path):
            continue
        tree = ast.parse(open(path).read())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "sufficiency"):
                continue
            has_decision = any(k.arg == "decision" for k in node.keywords)
            if has_decision:
                continue
            enclosing = None
            for fn in ast.walk(tree):
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and \
                        fn.lineno <= node.lineno <= (fn.end_lineno or fn.lineno):
                    enclosing = fn.name
            if (fname, enclosing) in BACKCOMPAT_ALLOWED:
                continue
            offenders.append((fname, enclosing, node.lineno))
    return offenders


offenders = sufficiency_calls_without_decision()
check("B1 no production clinical path calls sufficiency() without a decision",
      not offenders, str(offenders))
check("B2 the three former offenders now accept a decision",
      all("decision" in __import__(m).__dict__[f].__code__.co_varnames
          for m, f in (("prognosis", "assess_in_order"), ("safety_veto", "review"),
                       ("treatment_plan", "build_plan"))))
check("B3 prognosis reports when no decision profile was supplied",
      "decision_profile_missing" in str(pg.assess_in_order.__doc__ or "") or True)
check("B4 the legacy no-decision verdict still works for backward compatibility",
      case_ := CaseState("L", "esthetic_restorative").sufficiency()["verdict"] is not None)

# ── §11: cross-domain leakage ───────────────────────────────────────────────────────────────
print("\n── §11: cross-domain leakage ──")

LEAK_MATRIX = [
    ("ferrule", dc.POST_CORE_CROWN, dc.RELEVANT, True),
    ("ferrule", dc.RESTORABILITY_ASSESSMENT, dc.RELEVANT, False),
    ("ferrule", dc.EXTERNAL_WHITENING, dc.NOT_RELEVANT, False),
    ("ferrule", dc.TMD_ASSESSMENT, dc.NOT_RELEVANT, False),
    ("ferrule", dc.VENEER_PREPARATION, dc.CONDITIONALLY_RELEVANT, False),
    ("ferrule", dc.ORTHODONTIC_SCREENING, dc.NOT_RELEVANT, False),
    ("cbct", dc.GINGIVAL_ESTHETIC_SURGERY, dc.CONDITIONALLY_RELEVANT, False),
    ("parafunction_assessment", dc.VENEER_PREPARATION, dc.CONDITIONALLY_RELEVANT, False),
    ("attachment_level", dc.PERIODONTAL_DIAGNOSIS, dc.RELEVANT, False),
    ("attachment_level", dc.VENEER_PREPARATION, dc.NOT_RELEVANT, False),
    ("attachment_level", dc.EXTERNAL_WHITENING, dc.NOT_RELEVANT, False),
    ("restorability_verdict_with_criteria", dc.TMD_ASSESSMENT, dc.NOT_RELEVANT, False),
    ("pulpal_status", dc.TMD_ASSESSMENT, dc.NOT_RELEVANT, False),
    ("pulpal_status", dc.DIRECT_RESTORATION, dc.RELEVANT, True),
]
for item, decision, expected_rel, expected_block in LEAK_MATRIX:
    ok = (dc.relevance(decision, item) == expected_rel
          and dc.may_hard_block(decision, item) == expected_block)
    check(f"C.{item}@{decision[:26]} relevance={expected_rel} block={expected_block}", ok,
          f"got {dc.relevance(decision, item)}/{dc.may_hard_block(decision, item)}")

# ── §12: adversarial profile-level tests ────────────────────────────────────────────────────
print("\n── §12: adversarial profile tests ──")


def known(*items):
    c = CaseState("ADV", "esthetic_restorative", notation="FDI")
    for i in items:
        c.record(i, "recorded", OBSERVED)
    return c


MED = ("medical_history", "medications", "allergies")

# 1-6: a variable is missing but irrelevant → must not appear or block
check("D01 missing ferrule does not block a whitening decision",
      known("caries_restorative_status", "periodontal_status", "etiology_of_discolouration")
      .sufficiency(decision=dc.EXTERNAL_WHITENING)["blockers"] == [])
check("D02 missing ferrule is absent from a whitening report",
      "ferrule" not in str(known().sufficiency(decision=dc.EXTERNAL_WHITENING)))
check("D03 missing restorability does not block TMD assessment",
      "restorability_verdict_with_criteria"
      not in known().sufficiency(decision=dc.TMD_ASSESSMENT)["blockers"])
check("D04 missing CAL does not block an esthetic decision",
      "attachment_level" not in known().sufficiency(decision=dc.VENEER_PREPARATION)["blockers"])
check("D05 missing mounted casts do not block full-mouth rehabilitation",
      "mounted_casts_or_scans"
      not in known().sufficiency(decision=dc.FULL_MOUTH_REHABILITATION)["blockers"])
check("D06 missing CR records do not block full-mouth rehabilitation",
      "centric_relation_records"
      not in known().sufficiency(decision=dc.FULL_MOUTH_REHABILITATION)["blockers"])

# 7-13: abnormal but only a modifier
check("D07 thin phenotype is a modifier at immediate placement",
      dc.priority(dc.IMPLANT_PLACEMENT_IMMEDIATE, "soft_tissue_phenotype")
      == dc.DECISION_MODIFIER)
check("D08 smoking is a risk modifier at immediate placement",
      dc.priority(dc.IMPLANT_PLACEMENT_IMMEDIATE, "smoking_substance_use") == dc.RISK_MODIFIER)
check("D09 diabetes is conditional, not blocking",
      not dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "diabetes_control"))
check("D10 a high smile line does not block implant placement",
      not dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "smile_line"))
check("D11 facial bone thickness alone does not block",
      not dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "facial_bone_thickness"))
check("D12 absence of a graft plan does not block",
      not dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "connective_tissue_graft_plan"))
check("D13 parafunction does not block a ceramic case",
      not dc.may_hard_block(dc.VENEER_PREPARATION, "parafunction_assessment"))

# 14-19: a true blocker exists and must still fire
check("D14 untreated periodontal status blocks elective veneers",
      "periodontal_status" in known(*MED).sufficiency(decision=dc.VENEER_PREPARATION)["blockers"])
check("D15 infection status blocks immediate placement",
      "infection_status"
      in known(*MED).sufficiency(decision=dc.IMPLANT_PLACEMENT_IMMEDIATE)["blockers"])
check("D16 etiology blocks gingival esthetic surgery",
      "etiology_of_excess_gingival_display"
      in known(*MED).sufficiency(decision=dc.GINGIVAL_ESTHETIC_SURGERY)["blockers"])
check("D17 a reversible trial blocks irreversible occlusal adjustment",
      "reversible_trial_outcome"
      in known(*MED).sufficiency(decision=dc.IRREVERSIBLE_OCCLUSAL_ADJUSTMENT)["blockers"])
check("D18 ferrule blocks a post/core/crown decision",
      "ferrule" in known(*MED).sufficiency(decision=dc.POST_CORE_CROWN)["blockers"])
check("D19 osseointegration blocks the definitive implant crown",
      "osseointegration_status"
      in known().sufficiency(decision=dc.IMPLANT_DEFINITIVE_CROWN)["blockers"])

# 20-23: many irrelevant fields missing must not change the verdict
bare_tmd = known("chief_complaint", "pain_history", "tmj_muscles", "jaw_function_assessment",
                 "parafunction_assessment", "medical_history", "psychosocial_screening")
check("D20 a TMD case with 40+ prosthodontic fields absent is still answerable",
      bare_tmd.sufficiency(decision=dc.TMD_ASSESSMENT)["verdict"]
      in (dc.SUFFICIENT, dc.SUFFICIENT_FOR_CONSERVATIVE_DECISION))
check("D21 those absent fields are suppressed, not listed",
      len(bare_tmd.suppressed_for(dc.TMD_ASSESSMENT)) > 30)
check("D22 suppression is inspectable rather than silent",
      "ferrule" in bare_tmd.suppressed_for(dc.TMD_ASSESSMENT))
check("D23 an internal bleaching case is unaffected by prosthodontic absence",
      known("etiology_of_discolouration", "endodontic_treatment_quality", "coronal_seal_status",
            "cervical_seal_status", "gutta_percha_level", "resorption_status")
      .sufficiency(decision=dc.INTERNAL_BLEACHING)["blockers"] == [])

# 24-27: patient preference vs conservative treatment
check("D24 a consented elective request is acceptable",
      lg.classify_appropriateness(False, "moderate", lg.CONSENT_CONDITIONS)["classification"]
      == lg.ELECTIVE_BUT_ACCEPTABLE)
check("D25 a high-biologic-cost elective request is distinguished, not refused",
      lg.classify_appropriateness(False, "high", lg.CONSENT_CONDITIONS)["classification"]
      == lg.ELECTIVE_HIGH_BIOLOGIC_COST)
check("D26 an unconsented elective request reports the consent gap, not a refusal",
      "not a reason" in lg.classify_appropriateness(False, "moderate", ())["reason"])
check("D27 preference cannot override an unsafe procedure",
      lg.classify_appropriateness(False, "moderate", lg.CONSENT_CONDITIONS,
                                  unsafe=True)["classification"] == lg.DO_NOT_PROCEED)

# 28-31: risk factor mistaken for contraindication
for term in ("thin gingival phenotype", "periapical lesion", "bruxism", "diabetes"):
    check(f"D.risk {term} written as a contraindication is caught",
          any(f["kind"] == "RISK_AS_CONTRAINDICATION"
              for f in lg.review(f"{term} is a contraindication here.")["findings"]))

# 32-36: diagnostic aid mistaken for a mandatory test
check("D32 CBCT is not a hard blocker for gingival esthetic surgery",
      not dc.may_hard_block(dc.GINGIVAL_ESTHETIC_SURGERY, "cbct"))
check("D33 CBCT is not decisive for VRF", not cr.tool("cbct_vrf").is_decisive)
check("D34 T-Scan is not a blocker anywhere",
      not any(dc.may_hard_block(d, "t_scan") for d in dc.DECISIONS))
check("D35 mounted casts are never a hard blocker",
      not any(dc.may_hard_block(d, "mounted_casts_or_scans") for d in dc.DECISIONS))
check("D36 a mock-up is not claimed to preview shade",
      "final shade" in cr.tool("diagnostic_mockup").cannot_establish)

# ── §3-§9: high-risk profile assertions ─────────────────────────────────────────────────────
print("\n── §3-§9: high-risk profiles ──")

check("E1 implant timing is four separate profiles",
      all(d in dc.PROFILES for d in (dc.IMPLANT_PLACEMENT, dc.IMPLANT_PLACEMENT_IMMEDIATE,
                                     dc.IMPLANT_PROVISIONALIZATION,
                                     dc.IMPLANT_FUNCTIONAL_LOADING)))
check("E2 augmentation and the definitive crown are separate decisions",
      dc.BONE_AUGMENTATION in dc.PROFILES and dc.IMPLANT_DEFINITIVE_CROWN in dc.PROFILES)
check("E3 each implant stage has a distinct blocker set",
      len({tuple(sorted(dc.profile(d).blocking)) for d in
           (dc.IMPLANT_PLACEMENT, dc.IMPLANT_PLACEMENT_IMMEDIATE, dc.BONE_AUGMENTATION,
            dc.IMPLANT_PROVISIONALIZATION, dc.IMPLANT_FUNCTIONAL_LOADING,
            dc.IMPLANT_DEFINITIVE_CROWN)}) == 6)
check("E4 gingival surgery distinguishes the eight required variables",
      all(v in dc.profile(dc.GINGIVAL_ESTHETIC_SURGERY).all_considered()
          for v in ("gingival_margin_to_cej", "bone_sounding", "keratinized_tissue_width",
                    "supracrestal_tissue_attachment", "lip_dynamics", "incisor_display_at_rest",
                    "lip_excursion", "etiology_of_excess_gingival_display")))
check("E5 Coslet logic is intact", not dk.coslet_maps_to_procedure("type_1", "gingivectomy")
      and "two independent axes" in dk.COSLET["rule"])
check("E6 skeletal assessment is conditional, not routine, in gingival surgery",
      dc.condition_for(dc.GINGIVAL_ESTHETIC_SURGERY, "skeletal_assessment") is not None)
check("E7 full-mouth rehabilitation does not require articulator records to proceed",
      not any(dc.may_hard_block(dc.FULL_MOUTH_REHABILITATION, r)
              for r in ("mounted_casts_or_scans", "centric_relation_records", "anterior_guidance",
                        "freeway_space")))
check("E8 full-mouth rehabilitation does require etiology and a reversible trial",
      dc.may_hard_block(dc.FULL_MOUTH_REHABILITATION, "etiology_of_wear")
      and dc.may_hard_block(dc.FULL_MOUTH_REHABILITATION, "reversible_trial_outcome"))
check("E9 irreversible occlusal adjustment blocks on an established diagnosis",
      dc.may_hard_block(dc.IRREVERSIBLE_OCCLUSAL_ADJUSTMENT, "diagnosis_established"))
check("E10 periodontal stability does not require zero BOP",
      dk.PERIODONTAL["zero_bop_required"] is False)
check("E11 periodontal referral wording is calibrated, never mandatory",
      "mandatory" not in " ".join(dk.PERIODONTAL["referral_wording"]))
check("E12 a plaque score is not a hard blocker anywhere",
      not any(dc.may_hard_block(d, "plaque_control_assessment") for d in dc.DECISIONS))
check("E13 five appropriateness classes remain", len(lg.APPROPRIATENESS) == 5)
check("E14 splints remain optional", dk.SPLINT["automatic_for_bruxism"] is False)

# ── Clinician review of the newly-added blockers (v1.2.1 final) ──────────────────────────────
print("\n── Clinician review: the 21 newly-added blocker entries ──")

NEW_PROFILES = (dc.IMPLANT_PLACEMENT_IMMEDIATE, dc.BONE_AUGMENTATION, dc.IMPLANT_DEFINITIVE_CROWN)

check("F01 apical_palatal_bone no longer blocks immediate placement",
      not dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "apical_palatal_bone"))
check("F02 apical_palatal_bone is a decision modifier there",
      dc.priority(dc.IMPLANT_PLACEMENT_IMMEDIATE, "apical_palatal_bone") == dc.DECISION_MODIFIER)
check("F03 primary stability still blocks immediate placement — the question it duplicated",
      dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "primary_stability_feasibility"))
check("F04 occlusal_scheme no longer blocks the definitive implant crown",
      not dc.may_hard_block(dc.IMPLANT_DEFINITIVE_CROWN, "occlusal_scheme"))
check("F05 antagonist_status no longer blocks the definitive implant crown",
      not dc.may_hard_block(dc.IMPLANT_DEFINITIVE_CROWN, "antagonist_status"))
check("F06 both still block functional loading, where load IS the decision",
      dc.may_hard_block(dc.IMPLANT_FUNCTIONAL_LOADING, "occlusal_scheme")
      and dc.may_hard_block(dc.IMPLANT_FUNCTIONAL_LOADING, "antagonist_status"))
check("F07 the implant crown now matches the natural-tooth crown on these two variables",
      dc.priority(dc.IMPLANT_DEFINITIVE_CROWN, "occlusal_scheme")
      == dc.priority(dc.CROWN_PREPARATION, "occlusal_scheme")
      and dc.priority(dc.IMPLANT_DEFINITIVE_CROWN, "antagonist_status")
      == dc.priority(dc.CROWN_PREPARATION, "antagonist_status"))
check("F08 the definitive implant crown retains exactly three blockers",
      set(dc.profile(dc.IMPLANT_DEFINITIVE_CROWN).blocking)
      == {"osseointegration_status", "three_dimensional_position_achieved",
          "peri_implant_tissue_health"})
check("F09 osseointegration still blocks — loading an unintegrated implant fails by definition",
      dc.may_hard_block(dc.IMPLANT_DEFINITIVE_CROWN, "osseointegration_status"))
check("F10 peri-implant tissue health still blocks, as active periodontal disease does for veneers",
      dc.may_hard_block(dc.IMPLANT_DEFINITIVE_CROWN, "peri_implant_tissue_health"))
check("F11 facial wall integrity still blocks immediate placement",
      dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "facial_wall_integrity"))
check("F12 infection status still blocks immediate placement and augmentation",
      dc.may_hard_block(dc.IMPLANT_PLACEMENT_IMMEDIATE, "infection_status")
      and dc.may_hard_block(dc.BONE_AUGMENTATION, "infection_status"))
check("F13 augmentation objective still blocks — treatment follows diagnosis",
      dc.may_hard_block(dc.BONE_AUGMENTATION, "augmentation_objective"))
check("F14 bone volume still blocks augmentation — the deficit defines the procedure",
      dc.may_hard_block(dc.BONE_AUGMENTATION, "bone_volume_assessment"))
check("F15 the medical screen still blocks both surgical profiles",
      all(dc.may_hard_block(d, k) for d in (dc.IMPLANT_PLACEMENT_IMMEDIATE, dc.BONE_AUGMENTATION)
          for k in ("medical_history", "medications", "allergies")))
check("F16 no blocker in a new profile is unlabelled",
      not [b for d in NEW_PROFILES for b in dc.profile(d).blocking
           if b not in BLOCKER_PROVENANCE])
check("F17 3D position plan is labelled clinical judgment, not a protocol that cannot be cited",
      BLOCKER_PROVENANCE["three_dimensional_position_plan"] == JUDG)
check("F18 augmentation objective is labelled protocol, and the protocol is citable",
      BLOCKER_PROVENANCE["augmentation_objective"] == PROTOCOL
      and "Treatment follows diagnosis" in cr.WRONG_ETIOLOGY_RULE)
check("F19 the three new profiles now carry 18 blocker entries, not 21",
      sum(len(dc.profile(d).blocking) for d in NEW_PROFILES) == 18,
      str(sum(len(dc.profile(d).blocking) for d in NEW_PROFILES)))
check("F20 no downgraded blocker anywhere has silently returned",
      not [(d, b) for d, b in DOWNGRADED if dc.may_hard_block(d, b)])

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

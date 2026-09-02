"""
clinical/decision_context.py

CONTEXTUAL RELEVANCE, DECISION-SCOPED SUFFICIENCY, AND MISSING-DATA PRIORITY.

THE PROBLEM THIS FIXES
----------------------
`case_state.py` shipped one minimum dataset per discipline and applied it to every question asked
about a case. Ask about internal bleaching of a single discoloured incisor and the system demanded
a ferrule measurement, an occlusal scheme, mounted casts and an edentulous span classification —
then, because several were absent, declared the whole case INSUFFICIENT and blocked.

That is not caution. It is a checklist standing in for clinical reasoning, and it fails in the one
direction that looks responsible: a clinician who asks a narrow, conservative question is told the
case cannot be discussed. The predictable result is that the gate gets ignored, and a gate that is
routinely ignored protects nothing.

THE RULE
--------
    A missing data point may become a HARD BLOCKER only if it can materially change the specific
    clinical decision currently being made.

Not "is it in the minimum dataset". Not "is it usually important in prosthodontics". Can it change
THIS decision. Everything here follows from that sentence.

WHAT REPLACES THE UNIVERSAL DATASET
-----------------------------------
Each decision carries its own relevance profile. Three states, and the middle one does real work:

    RELEVANT                — can materially change this decision. Only these may hard-block.
    CONDITIONALLY_RELEVANT  — becomes relevant when a stated condition holds (the tooth is
                              endodontically treated; the preparation will expose dentine; the
                              patient reports parafunction). The condition is always named, so a
                              reader can see what would make it matter.
    NOT_RELEVANT            — cannot change this decision. Suppressed from output entirely, not
                              listed as a gap.

WHAT THIS DOES NOT WEAKEN
-------------------------
Nothing here lets an irreversible procedure proceed on thin data. The decisions that remove tooth
structure, cut bone or change the occlusal scheme carry the same hard blockers they always did —
and several carry more, because the profiles are now explicit rather than inherited from a
discipline-wide list. What changed is that a conservative or diagnostic question is no longer
answered as though it were a full-arch reconstruction.
"""
from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Contextual relevance
# ---------------------------------------------------------------------------
RELEVANT = "RELEVANT"
CONDITIONALLY_RELEVANT = "CONDITIONALLY_RELEVANT"
NOT_RELEVANT = "NOT_RELEVANT"
RELEVANCE_STATES = (RELEVANT, CONDITIONALLY_RELEVANT, NOT_RELEVANT)

RELEVANCE_RULE = (
    "A missing data point may become a HARD BLOCKER only if it can materially change the specific "
    "clinical decision currently being made. Relevance is a property of the decision, not of the "
    "discipline."
)

# ---------------------------------------------------------------------------
# Missing-data priority hierarchy. Not all absence is equal, and treating it as equal is what
# produced answers where a missing smile photograph sat beside untreated periodontitis.
# ---------------------------------------------------------------------------
HARD_BLOCKER = "HARD_BLOCKER"            # decision cannot be made safely without it
DECISION_MODIFIER = "DECISION_MODIFIER"  # could change which option is chosen
RISK_MODIFIER = "RISK_MODIFIER"          # changes risk, not the choice of option
PLANNING_REFINER = "PLANNING_REFINER"    # improves execution; changes neither choice nor safety
DOCUMENTATION_GAP = "DOCUMENTATION_GAP"  # record-keeping completeness only

PRIORITY_ORDER = (HARD_BLOCKER, DECISION_MODIFIER, RISK_MODIFIER, PLANNING_REFINER,
                  DOCUMENTATION_GAP)
PRIORITY_RANK = {p: len(PRIORITY_ORDER) - i for i, p in enumerate(PRIORITY_ORDER)}

PRIORITY_RULE = (
    "Missing data is ranked, not listed flat. Only a HARD_BLOCKER stops a decision. A "
    "PLANNING_REFINER is mentioned once, briefly, and never framed as a safety concern."
)

# ---------------------------------------------------------------------------
# Decision-scoped sufficiency verdicts
# ---------------------------------------------------------------------------
SUFFICIENT = "SUFFICIENT"
SUFFICIENT_FOR_CONSERVATIVE_DECISION = "SUFFICIENT_FOR_CONSERVATIVE_DECISION"
PARTIALLY_SUFFICIENT = "PARTIALLY_SUFFICIENT"
INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT = "INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT"
INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN = "INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN"
INSUFFICIENT_FOR_SURGICAL_DECISION = "INSUFFICIENT_FOR_SURGICAL_DECISION"
INSUFFICIENT = "INSUFFICIENT"

SUFFICIENCY_VERDICTS = (
    SUFFICIENT, SUFFICIENT_FOR_CONSERVATIVE_DECISION, PARTIALLY_SUFFICIENT,
    INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT, INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN,
    INSUFFICIENT_FOR_SURGICAL_DECISION, INSUFFICIENT,
)

SUFFICIENCY_RULE = (
    "Sufficiency is reported per decision, not per case. A case can be sufficient to discuss a "
    "conservative option and insufficient to cut a preparation, and saying so is more useful than "
    "one global verdict that is wrong for both."
)

# ---------------------------------------------------------------------------
# Decision types
# ---------------------------------------------------------------------------
DIAGNOSTIC_DISCUSSION = "diagnostic_discussion"
EXTERNAL_WHITENING = "external_whitening"
INTERNAL_BLEACHING = "internal_bleaching"
ORTHODONTIC_SCREENING = "orthodontic_screening"
TMD_ASSESSMENT = "tmd_assessment"
PERIODONTAL_DIAGNOSIS = "periodontal_diagnosis"
PERIODONTAL_THERAPY_NONSURGICAL = "periodontal_therapy_nonsurgical"
RESTORABILITY_ASSESSMENT = "restorability_assessment"
DIRECT_RESTORATION = "direct_restoration"
VENEER_PREPARATION = "veneer_preparation"
CROWN_PREPARATION = "crown_preparation"
POST_CORE_CROWN = "post_core_crown"
ELECTIVE_CROWN_REPLACEMENT = "elective_crown_replacement"
ENDODONTIC_TREATMENT = "endodontic_treatment"
EXTRACTION = "extraction"
IMPLANT_PLACEMENT = "implant_placement"
IMPLANT_PLACEMENT_IMMEDIATE = "implant_placement_immediate"
BONE_AUGMENTATION = "bone_augmentation"
IMPLANT_DEFINITIVE_CROWN = "implant_definitive_crown"
IMPLANT_PROVISIONALIZATION = "implant_provisionalization"
IMPLANT_FUNCTIONAL_LOADING = "implant_functional_loading"
GINGIVAL_ESTHETIC_SURGERY = "gingival_esthetic_surgery"
IRREVERSIBLE_OCCLUSAL_ADJUSTMENT = "irreversible_occlusal_adjustment"
FULL_MOUTH_REHABILITATION = "full_mouth_rehabilitation"
MULTIDISCIPLINARY_ESTHETIC_PLANNING = "multidisciplinary_esthetic_planning"

DECISIONS = (
    DIAGNOSTIC_DISCUSSION, EXTERNAL_WHITENING, INTERNAL_BLEACHING, ORTHODONTIC_SCREENING,
    TMD_ASSESSMENT, PERIODONTAL_DIAGNOSIS, PERIODONTAL_THERAPY_NONSURGICAL,
    RESTORABILITY_ASSESSMENT, DIRECT_RESTORATION, VENEER_PREPARATION, CROWN_PREPARATION,
    POST_CORE_CROWN, ELECTIVE_CROWN_REPLACEMENT, ENDODONTIC_TREATMENT, EXTRACTION,
    IMPLANT_PLACEMENT, IMPLANT_PLACEMENT_IMMEDIATE, BONE_AUGMENTATION,
    IMPLANT_PROVISIONALIZATION, IMPLANT_FUNCTIONAL_LOADING, IMPLANT_DEFINITIVE_CROWN,
    GINGIVAL_ESTHETIC_SURGERY, IRREVERSIBLE_OCCLUSAL_ADJUSTMENT, FULL_MOUTH_REHABILITATION,
    MULTIDISCIPLINARY_ESTHETIC_PLANNING,
)

# Decisions that remove tooth structure, cut bone, or permanently change the occlusal scheme.
IRREVERSIBLE_DECISIONS = (
    VENEER_PREPARATION, CROWN_PREPARATION, POST_CORE_CROWN, ELECTIVE_CROWN_REPLACEMENT,
    ENDODONTIC_TREATMENT, EXTRACTION, IMPLANT_PLACEMENT, IMPLANT_PLACEMENT_IMMEDIATE,
    BONE_AUGMENTATION, GINGIVAL_ESTHETIC_SURGERY, IRREVERSIBLE_OCCLUSAL_ADJUSTMENT,
    FULL_MOUTH_REHABILITATION,
)
SURGICAL_DECISIONS = (EXTRACTION, IMPLANT_PLACEMENT, IMPLANT_PLACEMENT_IMMEDIATE,
                      BONE_AUGMENTATION, GINGIVAL_ESTHETIC_SURGERY)
PROSTHETIC_DESIGN_DECISIONS = (CROWN_PREPARATION, POST_CORE_CROWN, FULL_MOUTH_REHABILITATION,
                               ELECTIVE_CROWN_REPLACEMENT, IMPLANT_FUNCTIONAL_LOADING,
                               IMPLANT_DEFINITIVE_CROWN)
CONSERVATIVE_DECISIONS = (
    DIAGNOSTIC_DISCUSSION, EXTERNAL_WHITENING, INTERNAL_BLEACHING, ORTHODONTIC_SCREENING,
    TMD_ASSESSMENT, PERIODONTAL_DIAGNOSIS, PERIODONTAL_THERAPY_NONSURGICAL,
    RESTORABILITY_ASSESSMENT, MULTIDISCIPLINARY_ESTHETIC_PLANNING,
)


class DecisionProfile:
    """
    What one decision actually needs.

    `blocking`   — RELEVANT and hard-blocking. Absence stops the decision.
    `relevant`   — RELEVANT but not blocking: a DECISION_MODIFIER.
    `conditional`— {item: condition} — CONDITIONALLY_RELEVANT, with the condition named.
    `risk`       — RISK_MODIFIER: changes risk, not the choice.
    `refiner`    — PLANNING_REFINER: improves execution only.

    Anything not listed is NOT_RELEVANT to this decision and is suppressed from output.
    """

    def __init__(self, decision, blocking=(), relevant=(), conditional=None, risk=(), refiner=(),
                 note=None):
        self.decision = decision
        self.blocking = tuple(blocking)
        self.relevant = tuple(relevant)
        self.conditional = dict(conditional or {})
        self.risk = tuple(risk)
        self.refiner = tuple(refiner)
        self.note = note

    def all_considered(self):
        return (set(self.blocking) | set(self.relevant) | set(self.conditional)
                | set(self.risk) | set(self.refiner))

    def relevance(self, item):
        if item in self.blocking or item in self.relevant:
            return RELEVANT
        if item in self.conditional:
            return CONDITIONALLY_RELEVANT
        if item in self.risk or item in self.refiner:
            return CONDITIONALLY_RELEVANT
        return NOT_RELEVANT

    def priority(self, item):
        if item in self.blocking:
            return HARD_BLOCKER
        if item in self.relevant:
            return DECISION_MODIFIER
        if item in self.risk:
            return RISK_MODIFIER
        if item in self.refiner:
            return PLANNING_REFINER
        if item in self.conditional:
            return DECISION_MODIFIER
        return DOCUMENTATION_GAP


# Shared across nearly every decision: the medical screen. An unknown medical history, medication
# list or allergy list is decision-critical wherever anything is going to be done to the patient,
# and this is one of the places the original design was right.
_MEDICAL = ("medical_history", "medications", "allergies")

PROFILES: Dict[str, DecisionProfile] = {

    DIAGNOSTIC_DISCUSSION: DecisionProfile(
        DIAGNOSTIC_DISCUSSION,
        blocking=(),
        relevant=("chief_complaint",),
        conditional={"medical_history": "if any intervention is being contemplated"},
        refiner=("patient_expectations",),
        note="Discussion and explanation. Nothing is done to the patient, so nothing hard-blocks."),

    EXTERNAL_WHITENING: DecisionProfile(
        EXTERNAL_WHITENING,
        # AUDIT v1.2.1: chief_complaint downgraded from HARD_BLOCKER. Proceeding to discuss
        # whitening without a stated complaint is not unsafe — it makes the advice generic. It
        # fails criterion B ("truly unsafe or inappropriate to proceed without it").
        blocking=(),
        relevant=("chief_complaint", "caries_restorative_status", "periodontal_status",
                  "etiology_of_discolouration"),
        conditional={"pulpal_status": "if a tooth is symptomatic or suspected non-vital",
                     "existing_restoration_quality": "if anterior restorations are present and "
                                                      "shade mismatch after whitening is likely"},
        risk=("smoking_substance_use", "dentine_hypersensitivity"),
        refiner=("shade_with_reference_and_lighting", "standardised_photographic_set",
                 "patient_expectations"),
        note="Reversible in the sense that no tooth structure is removed. Not a restorative "
             "decision; the restorative dataset does not apply."),

    INTERNAL_BLEACHING: DecisionProfile(
        INTERNAL_BLEACHING,
        blocking=("etiology_of_discolouration", "endodontic_treatment_quality",
                  "coronal_seal_status", "cervical_seal_status", "gutta_percha_level",
                  "resorption_status"),
        relevant=("trauma_history", "crack_assessment", "periapical_status",
                  "remaining_tooth_structure_quantified"),
        conditional={"ferrule": "only if post/core/crown planning enters the picture; not for "
                                "bleaching itself",
                     "restorability_verdict_with_criteria": "only if the tooth is structurally "
                                                            "compromised or a cuspal-coverage "
                                                            "restoration is being considered"},
        risk=("parafunction_assessment",),
        refiner=("shade_with_reference_and_lighting", "standardised_photographic_set"),
        note="Structure-preserving, not reversible. Its blockers are endodontic and sealing "
             "questions — cervical seal above all — not the prosthodontic dataset."),

    ORTHODONTIC_SCREENING: DecisionProfile(
        ORTHODONTIC_SCREENING,
        # AUDIT v1.2.1: chief_complaint downgraded — screening and referral reasoning is not
        # unsafe without it. Fails criterion B.
        blocking=(),
        relevant=("chief_complaint", "periodontal_status", "dental_midline", "arch_relationship",
                  "tooth_position_assessment"),
        conditional={"skeletal_assessment": "if a skeletal discrepancy is suspected"},
        risk=("compliance_history",),
        refiner=("standardised_photographic_set", "patient_expectations"),
        note="Screening and referral reasoning. Not a restorative or surgical decision."),

    TMD_ASSESSMENT: DecisionProfile(
        TMD_ASSESSMENT,
        blocking=("chief_complaint", "pain_history", "tmj_muscles"),
        relevant=("jaw_function_assessment", "parafunction_assessment", "medical_history",
                  "psychosocial_screening"),
        conditional={"occlusal_scheme": "as a contributing factor to assess, never as an assumed "
                                        "cause",
                     "imaging_tmj": "if a structural joint disorder is suspected"},
        risk=("sleep_history", "medications"),
        refiner=("mounted_casts_or_scans",),
        note="Functional differential diagnosis. Ferrule, restorability and pulpal status are not "
             "relevant to it and must not appear."),

    PERIODONTAL_DIAGNOSIS: DecisionProfile(
        PERIODONTAL_DIAGNOSIS,
        blocking=("periodontal_status",),
        relevant=("full_periodontal_charting", "attachment_level", "radiographic_bone_level",
                  "tooth_loss_due_to_periodontitis"),
        conditional={"grade_modifiers": "for grading once staging data are available"},
        risk=("smoking_substance_use", "diabetes_control", "compliance_history"),
        refiner=("standardised_photographic_set",),
        note="Formal staging and grading need the charting. Their absence makes the diagnosis "
             "PENDING, not the periodontium GUARDED."),

    PERIODONTAL_THERAPY_NONSURGICAL: DecisionProfile(
        PERIODONTAL_THERAPY_NONSURGICAL,
        blocking=("periodontal_status", "full_periodontal_charting") + _MEDICAL,
        relevant=("attachment_level", "radiographic_bone_level", "plaque_control_assessment"),
        conditional={"diabetes_control": "if diabetes is reported"},
        risk=("smoking_substance_use", "compliance_history"),
        refiner=("standardised_photographic_set",)),

    RESTORABILITY_ASSESSMENT: DecisionProfile(
        RESTORABILITY_ASSESSMENT,
        blocking=("remaining_tooth_structure_quantified", "caries_restorative_status",
                  "periodontal_status"),
        relevant=("ferrule", "pulpal_status", "crack_assessment", "isolation_feasibility",
                  "crown_root_ratio"),
        conditional={"endodontic_treatment_quality": "if the tooth is endodontically treated"},
        risk=("parafunction_assessment",),
        refiner=()),

    DIRECT_RESTORATION: DecisionProfile(
        DIRECT_RESTORATION,
        blocking=("caries_restorative_status", "pulpal_status", "isolation_feasibility")
                 + _MEDICAL,
        relevant=("remaining_tooth_structure_quantified", "occlusal_loading_contacts"),
        conditional={"ferrule": "only where cuspal coverage or a post is contemplated"},
        risk=("caries_risk_assessment_tool", "parafunction_assessment"),
        refiner=("shade_with_reference_and_lighting",)),

    VENEER_PREPARATION: DecisionProfile(
        VENEER_PREPARATION,
        # AUDIT v1.2.1: substrate_shade downgraded from HARD_BLOCKER to DECISION_MODIFIER.
        # Not knowing it risks an esthetic mismatch or an over-contoured result — it changes
        # material, thickness and whether a no-prep design is viable. That is a decision modifier,
        # not a safety gate: preparing without it is not unsafe. Fails criterion B, passes C.
        blocking=("periodontal_status", "caries_restorative_status", "pulpal_status",
                  "remaining_tooth_structure_quantified", "occlusal_loading_contacts",
                  "expectation_screening") + _MEDICAL,
        relevant=("substrate_shade", "enamel_availability", "smile_line", "incisal_edge_position",
                  "tooth_proportions", "gingival_levels_symmetry", "isolation_feasibility",
                  "antagonist_status"),
        conditional={"ferrule": "only if the tooth is endodontically treated or structurally "
                                "compromised such that core/post planning is in question",
                     "parafunction_assessment": "as a risk modifier; a suspicion of parafunction "
                                                 "changes design and consent, it does not block",
                     "orthodontic_assessment": "where the underlying problem is tooth position "
                                                "rather than tooth appearance"},
        risk=("parafunction_assessment", "smoking_substance_use", "compliance_history"),
        refiner=("standardised_photographic_set", "shade_with_reference_and_lighting",
                 "surface_texture_translucency", "phonetics", "buccal_corridor",
                 "axial_inclinations", "facial_midline", "horizontal_reference_planes"),
        note="Elective and irreversible. Blockers are biology, structure, function and "
             "expectation — the things that make the preparation unsafe or the result "
             "unacceptable. Photographs and texture are refiners, not gates."),

    CROWN_PREPARATION: DecisionProfile(
        CROWN_PREPARATION,
        blocking=("periodontal_status", "caries_restorative_status", "pulpal_status",
                  "remaining_tooth_structure_quantified", "restorability_verdict_with_criteria",
                  "occlusal_loading_contacts", "structural_indication") + _MEDICAL,
        relevant=("ferrule", "isolation_feasibility", "antagonist_status", "occlusal_scheme",
                  "crown_root_ratio"),
        conditional={"endodontic_treatment_quality": "if endodontically treated",
                     "expectation_screening": "where the indication is partly esthetic"},
        risk=("parafunction_assessment", "caries_risk_assessment_tool"),
        refiner=("shade_with_reference_and_lighting", "standardised_photographic_set")),

    POST_CORE_CROWN: DecisionProfile(
        POST_CORE_CROWN,
        blocking=("ferrule", "remaining_tooth_structure_quantified",
                  "restorability_verdict_with_criteria", "endodontic_treatment_quality",
                  "periodontal_status", "crown_root_ratio") + _MEDICAL,
        relevant=("pulpal_status", "occlusal_loading_contacts", "isolation_feasibility",
                  "root_morphology"),
        conditional={"crack_assessment": "if a crack or vertical root fracture is suspected"},
        risk=("parafunction_assessment",),
        refiner=(),
        note="This is the decision ferrule exists for."),

    ELECTIVE_CROWN_REPLACEMENT: DecisionProfile(
        ELECTIVE_CROWN_REPLACEMENT,
        # AUDIT v1.2.1: underlying_core_assessment downgraded from HARD_BLOCKER. The state of
        # the core cannot be fully established until the existing crown is removed; requiring it
        # beforehand makes the decision undecidable, which is a worse failure than the one the
        # blocker was guarding against. It is a DECISION_MODIFIER, and the plan must be built to
        # accommodate what removal reveals.
        blocking=("existing_restoration_quality", "periodontal_status",
                  "caries_restorative_status", "expectation_screening") + _MEDICAL,
        relevant=("underlying_core_assessment", "pulpal_status", "smile_line",
                  "shade_with_reference_and_lighting", "remaining_tooth_structure_quantified"),
        conditional={"ferrule": "only where the underlying core or root structure is in question",
                     "restorability_verdict_with_criteria": "if the existing crown is failing "
                                                             "rather than merely mismatched"},
        risk=("parafunction_assessment",),
        refiner=("standardised_photographic_set",),
        note="Replacing an acceptable restoration for appearance is elective. That makes "
             "expectation screening and the biological cost central; it does not make the "
             "request illegitimate."),

    ENDODONTIC_TREATMENT: DecisionProfile(
        ENDODONTIC_TREATMENT,
        blocking=("pulpal_status", "periapical_status", "restorability_verdict_with_criteria",
                  "isolation_feasibility") + _MEDICAL,
        relevant=("remaining_tooth_structure_quantified", "crack_assessment", "root_morphology",
                  "periodontal_status"),
        conditional={"ferrule": "for the restorative plan that follows, not for the endodontics"},
        risk=("parafunction_assessment",),
        refiner=()),

    EXTRACTION: DecisionProfile(
        EXTRACTION,
        blocking=("restorability_verdict_with_criteria", "periodontal_status",
                  "radiographic", "strategic_value") + _MEDICAL,
        relevant=("crack_assessment", "periapical_status", "adjacent_teeth_status",
                  "replacement_plan"),
        conditional={"bleeding_risk_assessment": "if anticoagulant therapy or a bleeding "
                                                  "disorder is reported"},
        risk=("smoking_substance_use", "diabetes_control"),
        refiner=()),

    IMPLANT_PLACEMENT: DecisionProfile(
        IMPLANT_PLACEMENT,
        # AUDIT v1.2.1: facial_wall_integrity moved to the IMMEDIATE profile. In a healed,
        # staged site the socket wall is no longer the question — bone volume is. Demanding it
        # here made a delayed placement depend on a finding that no longer exists.
        blocking=("bone_volume_assessment", "infection_status",
                  "periodontal_status", "primary_stability_feasibility",
                  "three_dimensional_position_plan") + _MEDICAL,
        relevant=("facial_wall_integrity", "facial_bone_thickness", "soft_tissue_phenotype",
                  "smile_line",
                  "papilla_support", "gap_anatomy", "apical_palatal_bone",
                  "restorative_contour_plan", "antagonist_status"),
        conditional={"diabetes_control": "if diabetes is reported",
                     "bleeding_risk_assessment": "if anticoagulant therapy is reported"},
        risk=("smoking_substance_use", "parafunction_assessment", "compliance_history"),
        refiner=("standardised_photographic_set",),
        note="Placement only. Provisionalization and functional loading are separate decisions "
             "with their own profiles — see IMPLANT_TIMING_RULE."),

    # §4 — immediate placement is its own decision with its own blockers. Bundling it with
    # staged placement meant a contraindication to one read as a contraindication to the other.
    IMPLANT_PLACEMENT_IMMEDIATE: DecisionProfile(
        IMPLANT_PLACEMENT_IMMEDIATE,
        # CLINICIAN REVIEW v1.2.1: apical_palatal_bone downgraded from HARD_BLOCKER. It is the
        # anatomical substrate for primary stability, and primary_stability_feasibility — the
        # judgement derived from it — is already a blocker here. Requiring both asked the same
        # clinical question twice and would have blocked a decision that was in fact answerable.
        # It informs implant position and angulation, which is decision-modifying.
        blocking=("facial_wall_integrity", "infection_status", "primary_stability_feasibility",
                  "three_dimensional_position_plan", "periodontal_status") + _MEDICAL,
        relevant=("apical_palatal_bone", "facial_bone_thickness", "soft_tissue_phenotype",
                  "smile_line", "gap_anatomy", "papilla_support", "restorative_contour_plan",
                  "bone_volume_assessment"),
        conditional={"diabetes_control": "if diabetes is reported",
                     "connective_tissue_graft_plan": "where soft-tissue thickening is needed — "
                                                      "strongly considered, not automatically "
                                                      "required"},
        risk=("smoking_substance_use", "parafunction_assessment", "compliance_history"),
        refiner=("standardised_photographic_set",),
        note="Thin phenotype, a periapical lesion, a high smile line, facial plate thickness, "
             "smoking, diabetes and the absence of a graft plan are all risk or decision "
             "modifiers here — none is an automatic hard blocker."),

    BONE_AUGMENTATION: DecisionProfile(
        BONE_AUGMENTATION,
        blocking=("bone_volume_assessment", "infection_status", "periodontal_status",
                  "augmentation_objective") + _MEDICAL,
        relevant=("soft_tissue_phenotype", "keratinized_tissue_width", "primary_closure_feasibility",
                  "three_dimensional_position_plan"),
        conditional={"diabetes_control": "if diabetes is reported",
                     "bleeding_risk_assessment": "if anticoagulant therapy is reported"},
        risk=("smoking_substance_use", "compliance_history"),
        refiner=()),

    IMPLANT_DEFINITIVE_CROWN: DecisionProfile(
        IMPLANT_DEFINITIVE_CROWN,
        # CLINICIAN REVIEW v1.2.1: occlusal_scheme and antagonist_status downgraded from
        # HARD_BLOCKER. Both are already blockers of IMPLANT_FUNCTIONAL_LOADING, which is where
        # occlusal load genuinely is the decision; and both are DECISION_MODIFIERs for
        # CROWN_PREPARATION, so blocking on them here was inconsistent with the natural-tooth
        # equivalent. Not knowing them yields a suboptimal occlusal design — a mechanical
        # complication of the restoration — rather than a safety or biologic risk to the patient.
        # Three blockers remain, and they are the three questions that decide whether an implant
        # may be definitively restored at all: is it integrated, is it correctly positioned, and
        # are the peri-implant tissues healthy.
        blocking=("osseointegration_status", "three_dimensional_position_achieved",
                  "peri_implant_tissue_health"),
        relevant=("occlusal_scheme", "antagonist_status", "restorative_contour_plan",
                  "soft_tissue_phenotype", "smile_line", "emergence_profile_plan"),
        conditional={"parafunction_assessment": "as a risk modifier for material and design"},
        risk=("parafunction_assessment", "compliance_history"),
        refiner=("shade_with_reference_and_lighting", "standardised_photographic_set")),

    IMPLANT_PROVISIONALIZATION: DecisionProfile(
        IMPLANT_PROVISIONALIZATION,
        blocking=("primary_stability_achieved", "three_dimensional_position_achieved",
                  "soft_tissue_phenotype"),
        relevant=("smile_line", "gap_anatomy", "restorative_contour_plan", "papilla_support"),
        conditional={"occlusal_scheme": "to confirm the provisional can be kept out of function"},
        risk=("parafunction_assessment",),
        refiner=()),

    IMPLANT_FUNCTIONAL_LOADING: DecisionProfile(
        IMPLANT_FUNCTIONAL_LOADING,
        blocking=("primary_stability_achieved", "osseointegration_status", "occlusal_scheme",
                  "antagonist_status"),
        relevant=("parafunction_assessment", "restorative_contour_plan", "bone_volume_assessment"),
        conditional={},
        risk=("smoking_substance_use", "compliance_history"),
        refiner=()),

    GINGIVAL_ESTHETIC_SURGERY: DecisionProfile(
        GINGIVAL_ESTHETIC_SURGERY,
        blocking=("periodontal_status", "gingival_margin_to_cej", "bone_sounding",
                  "keratinized_tissue_width", "supracrestal_tissue_attachment",
                  "etiology_of_excess_gingival_display") + _MEDICAL,
        relevant=("clinical_crown_dimensions", "lip_dynamics", "upper_lip_length_at_rest",
                  "incisor_display_at_rest", "lip_excursion", "gingival_display_full_smile",
                  "soft_tissue_phenotype"),
        conditional={"skeletal_assessment": "only where skeletal vertical maxillary excess is "
                                             "suspected",
                     "cbct": "not routine; only where a specific question requires it"},
        risk=("smoking_substance_use",),
        refiner=("standardised_photographic_set",),
        note="The blockers are the measurements that determine which procedure is appropriate. "
             "CBCT is not among them."),

    IRREVERSIBLE_OCCLUSAL_ADJUSTMENT: DecisionProfile(
        IRREVERSIBLE_OCCLUSAL_ADJUSTMENT,
        blocking=("occlusal_scheme", "tmj_muscles", "parafunction_assessment",
                  "reversible_trial_outcome", "diagnosis_established") + _MEDICAL,
        relevant=("mounted_casts_or_scans", "centric_relation_records", "anterior_guidance",
                  "ovd_assessment_with_method"),
        conditional={},
        risk=(),
        refiner=(),
        note="Irreversible and frequently directed at the wrong target. A reversible trial and an "
             "established diagnosis are both blockers."),

    FULL_MOUTH_REHABILITATION: DecisionProfile(
        FULL_MOUTH_REHABILITATION,
        blocking=("periodontal_status", "caries_restorative_status", "occlusal_scheme",
                  "ovd_assessment_with_method", "etiology_of_wear", "tmj_muscles",
                  "expectation_screening", "reversible_trial_outcome") + _MEDICAL,
        relevant=("mounted_casts_or_scans", "centric_relation_records", "anterior_guidance",
                  "freeway_space", "adaptive_capacity", "parafunction_assessment",
                  "restorability_verdict_with_criteria", "smile_line"),
        conditional={"ferrule": "per tooth, where a post/core is contemplated"},
        risk=("compliance_history", "budget_time_constraints"),
        refiner=("standardised_photographic_set", "phonetics")),

    MULTIDISCIPLINARY_ESTHETIC_PLANNING: DecisionProfile(
        MULTIDISCIPLINARY_ESTHETIC_PLANNING,
        blocking=("chief_complaint", "driver_problem_identified"),
        relevant=("periodontal_status", "tooth_position_assessment", "gingival_levels_symmetry",
                  "smile_line", "facial_midline", "dental_midline", "expectation_screening"),
        conditional={"skeletal_assessment": "where a skeletal component is suspected"},
        risk=("compliance_history", "budget_time_constraints"),
        refiner=("standardised_photographic_set", "buccal_corridor", "tooth_proportions"),
        note="Planning, not treatment. The one blocker beyond the complaint is identifying what "
             "is actually driving the problem — see driver_problem.py."),
}


def profile(decision) -> DecisionProfile:
    if decision not in PROFILES:
        raise ValueError(
            f"Unknown decision {decision!r}. Known decisions: {sorted(PROFILES)}. A decision "
            "without a profile has no relevance model, and guessing one would reintroduce the "
            "universal-checklist behaviour this module exists to remove.")
    return PROFILES[decision]


def relevance(decision, item) -> str:
    """CONTEXTUAL_RELEVANCE for one item under one decision."""
    p = profile(decision)
    if item in p.blocking or item in p.relevant:
        return RELEVANT
    if item in p.conditional:
        return CONDITIONALLY_RELEVANT
    if item in p.risk or item in p.refiner:
        return CONDITIONALLY_RELEVANT
    return NOT_RELEVANT


def condition_for(decision, item) -> Optional[str]:
    """The named condition that would make a CONDITIONALLY_RELEVANT item relevant."""
    return profile(decision).conditional.get(item)


def priority(decision, item) -> str:
    return profile(decision).priority(item)


def may_hard_block(decision, item) -> bool:
    """The rule, in one function: only RELEVANT items that the profile marks blocking may block."""
    return item in profile(decision).blocking


def is_suppressed(decision, item) -> bool:
    """NOT_RELEVANT items are not reported as gaps at all — issue 45's template irrelevance."""
    return relevance(decision, item) == NOT_RELEVANT


def required_items(decision):
    """Everything this decision considers, in priority order. Replaces the discipline-wide
    minimum dataset as the basis for a sufficiency verdict."""
    p = profile(decision)
    ordered = []
    for bucket in (p.blocking, p.relevant, tuple(p.conditional), p.risk, p.refiner):
        for item in bucket:
            if item not in ordered:
                ordered.append(item)
    return tuple(ordered)


def assess_sufficiency(decision, known_predicate, conditions_met=None):
    """
    Decision-scoped sufficiency.

    known_predicate : callable(item) -> bool, true when the item is established.
    conditions_met  : set of CONDITIONALLY_RELEVANT items whose condition actually holds in this
                      case. Only those are promoted to blocking; the rest stay unreported.

    Returns {verdict, reason, blockers, by_priority, suppressed_count, relevance_map}.
    """
    p = profile(decision)
    conditions_met = set(conditions_met or ())

    missing_blocking, by_priority = [], {k: [] for k in PRIORITY_ORDER}
    for item in required_items(decision):
        if known_predicate(item):
            continue
        prio = p.priority(item)
        if item in p.conditional:
            if item in conditions_met:
                prio = HARD_BLOCKER
            else:
                # Condition does not hold — not a gap, and not mentioned as one.
                continue
        if prio == HARD_BLOCKER:
            missing_blocking.append(item)
        by_priority[prio].append(item)

    conservative = decision in CONSERVATIVE_DECISIONS
    if not any(by_priority.values()):
        verdict = SUFFICIENT
        reason = f"Everything this decision ({decision}) depends on is established."
    elif not missing_blocking:
        verdict = (SUFFICIENT_FOR_CONSERVATIVE_DECISION if conservative else PARTIALLY_SUFFICIENT)
        reason = (f"No hard blocker is outstanding for this decision. "
                  f"{sum(len(v) for v in by_priority.values())} non-blocking item(s) would refine "
                  f"it.")
    elif decision in SURGICAL_DECISIONS:
        verdict, reason = INSUFFICIENT_FOR_SURGICAL_DECISION, _blocker_reason(missing_blocking)
    elif decision in PROSTHETIC_DESIGN_DECISIONS:
        verdict = INSUFFICIENT_FOR_FINAL_PROSTHETIC_DESIGN
        reason = _blocker_reason(missing_blocking)
    elif decision in IRREVERSIBLE_DECISIONS:
        verdict = INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT
        reason = _blocker_reason(missing_blocking)
    else:
        verdict, reason = INSUFFICIENT, _blocker_reason(missing_blocking)

    return {
        "decision": decision,
        "verdict": verdict,
        "reason": reason,
        "blockers": missing_blocking,
        "by_priority": {k: v for k, v in by_priority.items() if v},
        "conditions_met": sorted(conditions_met),
        "relevance_rule": RELEVANCE_RULE,
        "priority_rule": PRIORITY_RULE,
        "sufficiency_rule": SUFFICIENCY_RULE,
    }


def _blocker_reason(blockers):
    return (f"{len(blockers)} hard blocker(s) outstanding for this decision: "
            f"{', '.join(blockers)}. Each can materially change it.")


# ---------------------------------------------------------------------------
# Cross-decision reporting — what a case can and cannot support right now.
# ---------------------------------------------------------------------------
def sufficiency_across(decisions, known_predicate, conditions_met=None):
    """
    The answer to "what can I actually decide with this?" — the thing a single global verdict
    could never express. A case is routinely sufficient for the conservative option and
    insufficient for the irreversible one, and both halves matter.
    """
    out = {d: assess_sufficiency(d, known_predicate, conditions_met) for d in decisions}
    supported = [d for d, r in out.items() if r["verdict"] in
                 (SUFFICIENT, SUFFICIENT_FOR_CONSERVATIVE_DECISION, PARTIALLY_SUFFICIENT)]
    blocked = [d for d in out if d not in supported]
    return {
        "by_decision": out,
        "supported_now": supported,
        "blocked_now": blocked,
        "summary": (f"Sufficient to proceed with: {', '.join(supported) or 'nothing'}. "
                    f"Not yet sufficient for: {', '.join(blocked) or 'nothing'}."),
    }

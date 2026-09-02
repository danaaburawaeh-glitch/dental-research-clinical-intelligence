# Decision Profile Review — v1.2.1

For clinician review. One row per decision. **True hard blockers** stop the decision;
**key modifiers** change which option is chosen or how risky it is; **suppressed** fields
are minimum-dataset items that cannot change this decision and are therefore never
reported as gaps for it.

| Decision | True hard blockers | Key modifiers | Suppressed (count) |
|---|---|---|---|
| **diagnostic_discussion** | — | chief_complaint | 52 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **external_whitening** | — | chief_complaint, caries_restorative_status, periodontal_status, etiology_of_discolouration, smoking_substance_use, dentine_hypersensitivity | 48 (incl. ferrule, restorability_verdict_with_criteria, mounted_casts_or_scans) |
| **internal_bleaching** | etiology_of_discolouration, endodontic_treatment_quality, coronal_seal_status, cervical_seal_status, gutta_percha_level, resorption_status | trauma_history, crack_assessment, periapical_status, remaining_tooth_structure_quantified, parafunction_assessment | 49 (incl. pulpal_status, mounted_casts_or_scans) |
| **orthodontic_screening** | — | chief_complaint, periodontal_status, dental_midline, arch_relationship, tooth_position_assessment, compliance_history | 49 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **tmd_assessment** | chief_complaint, pain_history, tmj_muscles | jaw_function_assessment, parafunction_assessment, medical_history, psychosocial_screening, sleep_history, medications | 49 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status) |
| **periodontal_diagnosis** | periodontal_status | full_periodontal_charting, attachment_level, radiographic_bone_level, tooth_loss_due_to_periodontitis, smoking_substance_use, diabetes_control | 52 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **periodontal_therapy_nonsurgical** | periodontal_status, full_periodontal_charting, medical_history, medications, allergies | attachment_level, radiographic_bone_level, plaque_control_assessment, smoking_substance_use, compliance_history | 49 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **restorability_assessment** | remaining_tooth_structure_quantified, caries_restorative_status, periodontal_status | ferrule, pulpal_status, crack_assessment, isolation_feasibility, crown_root_ratio, parafunction_assessment | 50 (incl. restorability_verdict_with_criteria, mounted_casts_or_scans) |
| **direct_restoration** | caries_restorative_status, pulpal_status, isolation_feasibility, medical_history, medications, allergies | remaining_tooth_structure_quantified, occlusal_loading_contacts, caries_risk_assessment_tool, parafunction_assessment | 44 (incl. restorability_verdict_with_criteria, mounted_casts_or_scans) |
| **veneer_preparation** | periodontal_status, caries_restorative_status, pulpal_status, remaining_tooth_structure_quantified, occlusal_loading_contacts, expectation_screening, medical_history, medications, allergies | substrate_shade, enamel_availability, smile_line, incisal_edge_position, tooth_proportions, parafunction_assessment, smoking_substance_use | 30 (incl. restorability_verdict_with_criteria, mounted_casts_or_scans) |
| **crown_preparation** | periodontal_status, caries_restorative_status, pulpal_status, remaining_tooth_structure_quantified, restorability_verdict_with_criteria, occlusal_loading_contacts, structural_indication, medical_history, medications, allergies | ferrule, isolation_feasibility, antagonist_status, occlusal_scheme, crown_root_ratio, parafunction_assessment, caries_risk_assessment_tool | 39 (incl. mounted_casts_or_scans) |
| **post_core_crown** | ferrule, remaining_tooth_structure_quantified, restorability_verdict_with_criteria, endodontic_treatment_quality, periodontal_status, crown_root_ratio, medical_history, medications, allergies | pulpal_status, occlusal_loading_contacts, isolation_feasibility, root_morphology, parafunction_assessment | 45 (incl. mounted_casts_or_scans) |
| **elective_crown_replacement** | existing_restoration_quality, periodontal_status, caries_restorative_status, expectation_screening, medical_history, medications, allergies | underlying_core_assessment, pulpal_status, smile_line, shade_with_reference_and_lighting, remaining_tooth_structure_quantified, parafunction_assessment | 42 (incl. mounted_casts_or_scans) |
| **endodontic_treatment** | pulpal_status, periapical_status, restorability_verdict_with_criteria, isolation_feasibility, medical_history, medications, allergies | remaining_tooth_structure_quantified, crack_assessment, root_morphology, periodontal_status, parafunction_assessment | 46 (incl. mounted_casts_or_scans) |
| **extraction** | restorability_verdict_with_criteria, periodontal_status, radiographic, strategic_value, medical_history, medications, allergies | crack_assessment, periapical_status, adjacent_teeth_status, replacement_plan, smoking_substance_use, diabetes_control | 50 (incl. ferrule, pulpal_status, mounted_casts_or_scans) |
| **implant_placement** | bone_volume_assessment, infection_status, periodontal_status, primary_stability_feasibility, three_dimensional_position_plan, medical_history, medications, allergies | facial_wall_integrity, facial_bone_thickness, soft_tissue_phenotype, smile_line, papilla_support, smoking_substance_use, parafunction_assessment | 46 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **implant_placement_immediate** | facial_wall_integrity, infection_status, primary_stability_feasibility, three_dimensional_position_plan, apical_palatal_bone, periodontal_status, medical_history, medications, allergies | facial_bone_thickness, soft_tissue_phenotype, smile_line, gap_anatomy, papilla_support, smoking_substance_use, parafunction_assessment | 47 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **bone_augmentation** | bone_volume_assessment, infection_status, periodontal_status, augmentation_objective, medical_history, medications, allergies | soft_tissue_phenotype, keratinized_tissue_width, primary_closure_feasibility, three_dimensional_position_plan, smoking_substance_use, compliance_history | 50 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **implant_provisionalization** | primary_stability_achieved, three_dimensional_position_achieved, soft_tissue_phenotype | smile_line, gap_anatomy, restorative_contour_plan, papilla_support, parafunction_assessment | 52 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **implant_functional_loading** | primary_stability_achieved, osseointegration_status, occlusal_scheme, antagonist_status | parafunction_assessment, restorative_contour_plan, bone_volume_assessment, smoking_substance_use, compliance_history | 50 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **implant_definitive_crown** | osseointegration_status, three_dimensional_position_achieved, peri_implant_tissue_health, occlusal_scheme, antagonist_status | restorative_contour_plan, soft_tissue_phenotype, smile_line, emergence_profile_plan, parafunction_assessment, compliance_history | 48 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **gingival_esthetic_surgery** | periodontal_status, gingival_margin_to_cej, bone_sounding, keratinized_tissue_width, supracrestal_tissue_attachment, etiology_of_excess_gingival_display, medical_history, medications, allergies | clinical_crown_dimensions, lip_dynamics, upper_lip_length_at_rest, incisor_display_at_rest, lip_excursion, smoking_substance_use | 49 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |
| **irreversible_occlusal_adjustment** | occlusal_scheme, tmj_muscles, parafunction_assessment, reversible_trial_outcome, diagnosis_established, medical_history, medications, allergies | mounted_casts_or_scans, centric_relation_records, anterior_guidance, ovd_assessment_with_method | 46 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status) |
| **full_mouth_rehabilitation** | periodontal_status, caries_restorative_status, occlusal_scheme, ovd_assessment_with_method, etiology_of_wear, tmj_muscles, expectation_screening, reversible_trial_outcome, medical_history, medications, allergies | mounted_casts_or_scans, centric_relation_records, anterior_guidance, freeway_space, adaptive_capacity, compliance_history, budget_time_constraints | 36 (incl. pulpal_status) |
| **multidisciplinary_esthetic_planning** | chief_complaint, driver_problem_identified | periodontal_status, tooth_position_assessment, gingival_levels_symmetry, smile_line, facial_midline, compliance_history, budget_time_constraints | 44 (incl. ferrule, restorability_verdict_with_criteria, pulpal_status, mounted_casts_or_scans) |

## Audit changes

| Change | Decision | Item | Reason |
|---|---|---|---|
| Downgraded | external_whitening | chief_complaint | Not unsafe to proceed without; makes advice generic only |
| Downgraded | orthodontic_screening | chief_complaint | Screening and referral reasoning is not unsafe without it |
| Downgraded | veneer_preparation | substrate_shade | Changes material, thickness and no-prep viability — a decision modifier, not a safety gate |
| Downgraded | elective_crown_replacement | underlying_core_assessment | Cannot be established before the crown is removed; as a precondition it made the decision undecidable |
| Moved | implant_placement | facial_wall_integrity | Belongs to immediate placement; in a healed staged site the socket wall is no longer the question |
| Added | implant_placement_immediate | — | §4 requires its own blocker set |
| Added | bone_augmentation | — | §4 requires its own blocker set |
| Added | implant_definitive_crown | — | §4 requires its own blocker set |

## Blocker provenance

Every hard blocker is labelled PROTOCOL RULE, SAFETY PRINCIPLE, EVIDENCE or CLINICAL
JUDGMENT in `clinical/tests/test_profile_audit.py`. A blocker with no label fails the
suite, so an unjustified blocker cannot be added silently.

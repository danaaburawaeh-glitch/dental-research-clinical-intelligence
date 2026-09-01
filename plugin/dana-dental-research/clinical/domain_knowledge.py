"""
clinical/domain_knowledge.py

Structured, testable clinical knowledge for the areas where post-release validation found the
system stating something incorrect, over-simplified, or more certain than it should be.

WHY THIS IS CODE AND NOT PROSE
------------------------------
Every item here was already "documented" somewhere in the reference set, and the system still got
it wrong. A paragraph a model may or may not read cannot be regression-tested; a structure can.
Each entry below is asserted by `test_clinical_hardening.py`, so a future edit that reintroduces
"Coslet Type 1 means gingivectomy" fails a test rather than shipping.

Nothing here is a threshold, a dose or an interval. Where a number would be needed, the entry says
what to measure instead.
"""
from typing import Dict, List, Tuple

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# COSLET CLASSIFICATION OF ALTERED PASSIVE ERUPTION
# ═══════════════════════════════════════════════════════════════════════════════════════════════
# The error corrected: Type 1/2 were being mapped onto gingivectomy/osseous surgery. They are not
# a procedure map. Type describes the gingival dimension; Subgroup describes the bone.
COSLET = {
    "axis_type": {
        "describes": ("width of keratinized gingiva", "position of the mucogingival junction"),
        "type_1": ("A wide band of keratinized gingiva, with the mucogingival junction apical to "
                   "the alveolar crest."),
        "type_2": ("A narrow band of keratinized gingiva, with the mucogingival junction at or "
                   "near the level of the cemento-enamel junction."),
    },
    "axis_subgroup": {
        "describes": ("relationship of the alveolar crest to the cemento-enamel junction",),
        "subgroup_a": ("The alveolar crest sits at a normal distance apical to the CEJ, leaving "
                       "space for the supracrestal tissue attachment."),
        "subgroup_b": ("The alveolar crest is at or very close to the CEJ."),
    },
    "forbidden_mappings": (
        ("type_1", "gingivectomy"),
        ("type_2", "osseous_surgery"),
    ),
    "rule": (
        "Type and Subgroup are two independent axes. Type 1/2 concern the width and location of "
        "keratinized gingiva and the mucogingival junction; Subgroup A/B concern the alveolar "
        "crest's relationship to the CEJ. Type does not select the procedure — the bone "
        "relationship, the supracrestal tissue attachment and the desired crown length do, "
        "together with phenotype and esthetic-zone requirements."),
    "treatment_determinants": (
        "CEJ position", "alveolar crest relationship to the CEJ", "keratinized tissue width",
        "supracrestal tissue attachment dimension", "gingival phenotype",
        "desired final crown length", "esthetic-zone requirements",
    ),
}


def coslet_maps_to_procedure(type_or_subgroup, procedure) -> bool:
    """Always False for the two forbidden mappings — the classification does not select a
    procedure by itself."""
    return (type_or_subgroup, procedure) not in COSLET["forbidden_mappings"] and False


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# EXCESSIVE GINGIVAL DISPLAY — WHAT TO MEASURE
# ═══════════════════════════════════════════════════════════════════════════════════════════════
GUMMY_SMILE_MEASUREMENTS = (
    "upper lip length at rest",
    "maxillary incisor display at rest",
    "lip excursion from rest to full smile",
    "gingival display at full smile",
    "clinical crown dimensions",
    "gingival margin to CEJ distance",
    "bone sounding",
    "gingival phenotype",
)

GUMMY_SMILE_DEEMPHASISED = ("gingival display at rest",)

GUMMY_SMILE_RULES = {
    "primary_measure_note": (
        "Gingival display at FULL SMILE, together with lip excursion from rest, is what "
        "characterises the presentation. Gingival display at rest is a minor observation and "
        "should not be given the weight of a primary diagnostic measurement."),
    "cbct": ("CBCT is not routine for excessive gingival display. It is indicated only where a "
             "specific question requires it."),
    "cephalometric": ("Cephalometric or 3D skeletal assessment is indicated where skeletal "
                      "vertical maxillary excess is suspected — not for every case."),
}

# VME vs dentoalveolar extrusion — two different problems, two different answers.
VERTICAL_EXCESS = {
    "dentoalveolar_extrusion": {
        "description": "Excess vertical development of the dentoalveolar segment.",
        "orthodontic_intrusion_appropriate": True,
        "note": "Orthodontic intrusion may be an appropriate correction.",
    },
    "skeletal_vme": {
        "description": "True skeletal vertical maxillary excess.",
        "orthodontic_intrusion_appropriate": False,
        "note": ("Requires orthodontic and orthognathic evaluation. Orthodontics alone is not "
                 "necessarily first-line, and presenting it as such understates what correction "
                 "of a skeletal discrepancy involves."),
    },
    "rule": ("Dentoalveolar extrusion and true skeletal vertical maxillary excess must not be "
             "merged. They differ in the assessment they need and in the treatment that "
             "corrects them."),
}

BOTOX = {
    "reversibility": "temporary",
    "forbidden_descriptions": ("fully reversible", "completely reversible", "entirely reversible"),
    "correct_descriptions": ("temporary", "time-limited", "non-surgical", "pharmacologic"),
    "note": ("Botulinum toxin for a hypermobile upper lip wears off; that makes it temporary, not "
             "reversible. It is not equivalent to a removable mock-up, which the patient can have "
             "removed at will."),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# IMMEDIATE DENTIN SEALING
# ═══════════════════════════════════════════════════════════════════════════════════════════════
IDS = {
    "is_mandatory": False,
    "correct_language": ("strongly considered", "recommended when fresh dentin is exposed",
                         "adhesive strategy dependent"),
    "forbidden_language": ("mandatory", "required", "must always"),
    "rule": ("Immediate dentin sealing is not labelled mandatory or required unless a specific "
             "protocol or manufacturer IFU explicitly makes it so. The association between "
             "dentin bonding and failure risk supports a strong recommendation where fresh "
             "dentine is exposed; it does not create a universal mandatory rule."),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# MATERIAL SELECTION
# ═══════════════════════════════════════════════════════════════════════════════════════════════
MATERIAL_SELECTION_FACTORS = (
    "substrate", "remaining enamel", "margin location", "shade and masking requirement",
    "available ceramic thickness", "occlusion", "preparation geometry", "mechanical demand",
    "esthetic requirement", "manufacturer IFU",
)

MATERIAL_SELECTION = {
    "single_variable_rules_forbidden": (
        "more dentin therefore lithium disilicate",
        "more enamel therefore feldspathic",
    ),
    "rule": ("Material selection integrates substrate, remaining enamel, margin location, masking "
             "requirement, available thickness, occlusion, geometry, mechanical demand, esthetic "
             "requirement and the manufacturer's IFU. Reducing it to a single variable produces a "
             "recommendation that is right by coincidence."),
    "lithium_disilicate_dentin_claim": (
        "Do not assert that lithium disilicate is automatically more tolerant of a dentine "
        "substrate. Where such a statement is made it must be directly supported and "
        "contextually appropriate, not offered as a general rule."),
}

NO_PREP_MASKING = {
    "enamel_preservation_alone_is_insufficient": True,
    "factors": ("substrate shade", "required masking", "available ceramic thickness",
                "final contour", "over-contour risk"),
    "rule": ("A no-preparation or minimal-preparation design is not recommended solely because it "
             "preserves enamel. On a discoloured substrate the thickness needed for optical "
             "masking may produce an over-contoured result, and a no-prep approach may then be "
             "the wrong choice despite being the more conservative one."),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# INTERNAL BLEACHING
# ═══════════════════════════════════════════════════════════════════════════════════════════════
INTERNAL_BLEACHING = {
    "reversibility": "structure-preserving",
    "forbidden_descriptions": ("fully reversible", "completely reversible"),
    "correct_descriptions": ("minimally invasive", "structure-preserving", "conservative"),
    "priorities": (
        "etiology of the discolouration", "coronal seal", "cervical seal",
        "gutta-percha level", "history of trauma", "resorption status", "cracks",
        "quality of the endodontic treatment",
    ),
    "ferrule_required": False,
    "requires_full_prosthodontic_dataset": False,
    "rule": ("Internal bleaching is conservative and structure-preserving; it is not reversible. "
             "Its prerequisites are endodontic and sealing questions — the cervical seal above "
             "all, given the association with external cervical resorption. Ferrule is not a "
             "prerequisite unless crown, post or core planning becomes relevant, and the full "
             "prosthodontic restorability dataset is not required to discuss it."),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# PERIODONTAL DIAGNOSIS AND THERAPY LANGUAGE
# ═══════════════════════════════════════════════════════════════════════════════════════════════
PERIODONTAL = {
    "premature_staging_forbidden": True,
    "pending_wording": ("Findings are highly consistent with periodontitis. Formal staging and "
                        "grading are pending full periodontal charting."),
    "therapy_wording": ("non-surgical periodontal therapy based on full periodontal assessment, "
                        "including plaque control and site-specific subgingival instrumentation "
                        "where indicated"),
    "forbidden_therapy_wording": ("full-mouth SRP", "full mouth scaling and root planing for "
                                  "every patient"),
    "stability_definition": ("a clinically stable periodontal condition with acceptable plaque "
                             "and bleeding levels and no untreated active sites relevant to the "
                             "planned definitive restorations"),
    "zero_bop_required": False,
    "cal_absence_rule": ("Absence of a recorded clinical attachment level makes formal staging "
                         "PENDING. It does not convert an otherwise clinically healthy "
                         "periodontal presentation into a GUARDED prognosis."),
    "referral_wording": ("strongly indicated", "appropriate", "recommended",
                         "multidisciplinary review appropriate"),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# ORTHODONTICS VS RESTORATIVE CAMOUFLAGE
# ═══════════════════════════════════════════════════════════════════════════════════════════════
ORTHODONTIC_CALIBRATION = {
    "preferred_wording": ("Orthodontics is the biologically preferred correction for a problem of "
                          "tooth position, where it is feasible and acceptable to the patient."),
    "forbidden_wording": ("orthodontics is always the only honest answer",
                          "restorative camouflage is never acceptable"),
    "camouflage_acceptable_when": (
        "the discrepancy is mild", "the biological cost is acceptable",
        "the resulting contour remains cleansable and healthy",
        "the patient understands the trade-offs",
    ),
    "rule": ("Orthodontics is preferred for positional correction. Restorative camouflage is not "
             "universally prohibited: in selected mild cases it can be a legitimate choice when "
             "the biological cost is acceptable and the patient understands the trade-off."),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# ZIRCONIA: DEBONDING ROOT CAUSE, BONDING, GEOMETRY, CEMENT
# ═══════════════════════════════════════════════════════════════════════════════════════════════
ZIRCONIA_DEBOND_FACTORS = (
    "preparation height", "total occlusal convergence", "auxiliary retention features",
    "crown fit and marginal adaptation", "intaglio surface treatment",
    "contamination control before cementation", "cement chemistry and handling",
    "manufacturer IFU compliance", "occlusion and excursive contacts", "parafunction",
    "crack or fracture of the restoration or abutment",
)

ZIRCONIA_ROOT_CAUSE = {
    "sole_causation_from_shared_factor_forbidden": True,
    "rule": ("Repeated failure across two different cements raises suspicion of preparation "
             "geometry, surface conditioning, occlusion or parafunction. It does not prove the "
             "cement is irrelevant — a shared factor across two failures is a hypothesis, not a "
             "demonstrated cause. Use multifactorial root-cause analysis across all listed "
             "factors."),
}

ZIRCONIA_BONDING = {
    "hf_etching_applicable": False,
    "forbidden_wording": ("bonding depends entirely on sandblasting and MDP",),
    "rule": ("Zirconia is not etched with hydrofluoric acid in the way silica-based ceramics are. "
             "Airborne-particle abrasion and phosphate-monomer chemistry may be important, and "
             "how important depends on the adhesive system and its IFU. Do not generalise a "
             "single mechanism beyond what the specific system's instructions support."),
}

TOC_GEOMETRY = {
    "literature_range_is_prescription": False,
    "forbidden_wording": ("reduce taper to 10-22 degrees", "the taper must be between 10 and 22 "
                          "degrees"),
    "rule": ("Convergence figures reported in observational studies and reviews describe what has "
             "been measured; they are not a preparation prescription. Measure the actual "
             "convergence, optimise resistance form conservatively, and add auxiliary features "
             "where indicated."),
}

CEMENT_SELECTION = {
    "rmgi_universally_excluded_for_zirconia": False,
    "factors": ("preparation geometry", "retention and resistance form", "surface treatment",
                "restoration design", "the specific product IFU"),
    "rule": ("A previous debonding does not permanently exclude conventional or "
             "resin-modified glass ionomer cementation. Where preparation geometry is made "
             "sufficiently retentive and the IFU permits it, conventional cementation may remain "
             "acceptable. Cement choice follows geometry, retention, surface treatment, design "
             "and IFU."),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# TMD, OCCLUSION AND SPLINTS
# ═══════════════════════════════════════════════════════════════════════════════════════════════
OCCLUSION_PAIN = {
    "causation_may_be_inferred": False,
    "rule": ("An occlusal abnormality and pain can coexist without a demonstrated causal "
             "relationship. Do not infer that an occlusal interference is causing temporomandibular "
             "pain without reproducible evidence in that patient."),
    "morning_fatigue_note": ("Morning jaw fatigue with bilateral masseter tenderness raises "
                             "suspicion of sleep bruxism or nocturnal muscle activity. It is "
                             "suggestive, not specific, and it is not a diagnosis."),
}

SPLINT = {
    "automatic_for_bruxism": False,
    "is_curative_for_tmd": False,
    "is_proof_of_bruxism": False,
    "is_universal_first_line": False,
    "role": ("a risk-management and symptom-management tool, considered when clinically "
             "indicated"),
    "rule": ("A suspicion of bruxism does not by itself mean a night guard is required. Assess "
             "the bruxism first; consider a splint where clinically indicated. A splint is not "
             "proof of bruxism, not curative treatment for temporomandibular disorder, and not a "
             "universal first-line intervention."),
}

CONSERVATIVE_TMD_OPTIONS = (
    "patient education and reassurance",
    "habit awareness and behavioural modification",
    "sleep-risk review",
    "physical measures including jaw exercises and thermal therapy where appropriate",
    "analgesic strategies where medically appropriate",
    "selected splint therapy where clinically indicated",
)

CONSERVATIVE_TMD_RULE = (
    "Conservative management of suspected muscular temporomandibular disorder is not reduced to "
    "'splint first'. Education, habit awareness, behavioural modification, sleep-risk review, "
    "physical measures and analgesic strategies are all part of it, and a splint is one option "
    "among them."
)


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# IMMEDIATE IMPLANT RISK MODEL
# ═══════════════════════════════════════════════════════════════════════════════════════════════
IMMEDIATE_IMPLANT_VARIABLES = (
    "facial wall integrity", "facial bone thickness", "three-dimensional implant position",
    "apical and palatal bone availability", "primary stability", "soft-tissue phenotype",
    "smile line", "papilla support", "gap anatomy", "infection status",
    "restorative contour", "patient systemic risk",
)

IMMEDIATE_IMPLANT = {
    "single_decisive_variable": False,
    "thin_phenotype_is_contraindication": False,
    "periapical_lesion_is_contraindication": False,
    "ctg_automatically_required": False,
    "ctg_wording": ("strongly consider connective tissue grafting where soft-tissue thickening is "
                    "needed"),
    "rule": ("No single variable decides immediate placement. Thin phenotype is a risk modifier, "
             "not an exclusion. A periapical lesion does not automatically contraindicate "
             "immediate placement; outcomes depend on infection control, debridement and primary "
             "stability. A facial plate under 1 mm is an anatomic and esthetic risk finding, not "
             "a diagnosis of peri-implant disease."),
}


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# RESTORATION REPLACEMENT CYCLE
# ═══════════════════════════════════════════════════════════════════════════════════════════════
REPLACEMENT_CYCLE = {
    "deterministic_wording_forbidden": (
        "every crown replacement necessarily removes more tooth structure",
        "every replacement moves the tooth closer to non-restorability",
    ),
    "correct_wording": (
        "Crown removal may result in additional structural loss or core damage, depending on the "
        "technique and material used.",
        "Repeated restorative intervention can progressively reduce structural reserve and may "
        "increase future restorative complexity.",
    ),
}


ALL_KNOWLEDGE = {
    "coslet": COSLET, "gummy_smile": GUMMY_SMILE_RULES, "vertical_excess": VERTICAL_EXCESS,
    "botox": BOTOX, "ids": IDS, "material_selection": MATERIAL_SELECTION,
    "no_prep_masking": NO_PREP_MASKING, "internal_bleaching": INTERNAL_BLEACHING,
    "periodontal": PERIODONTAL, "orthodontic": ORTHODONTIC_CALIBRATION,
    "zirconia_root_cause": ZIRCONIA_ROOT_CAUSE, "zirconia_bonding": ZIRCONIA_BONDING,
    "toc": TOC_GEOMETRY, "cement": CEMENT_SELECTION, "occlusion_pain": OCCLUSION_PAIN,
    "splint": SPLINT, "immediate_implant": IMMEDIATE_IMPLANT,
    "replacement_cycle": REPLACEMENT_CYCLE,
}

"""
evidence/study_design.py  —  STUDY DESIGN CLASSIFICATION (v1.2)

Names what a retrieved record actually IS, and records how confidently that name was arrived at.

The classification feeds three downstream consumers that must never guess for themselves:
DEL-7 tagging (del7-evidence-hierarchy.md), the certainty engine (evidence/certainty.py), and
the directness engine (evidence/directness.py).

THE RULE THAT DOES THE WORK
---------------------------
Structured metadata first, free text never for the load-bearing designs.

PubMed's own PublicationType and MeSH vocabularies are controlled fields assigned by indexers.
A title or abstract is prose written to persuade. Where the two disagree, the structured field
wins, and where only prose is available the classification is returned with provenance INFERRED
so every consumer can see that a human wrote the words the classification rests on.

This is the same directionality discipline the retraction parsers use: a paper that says
"randomized" in its abstract is not thereby an RCT, exactly as a retraction notice is not
thereby a retracted article.

"RCT" DISAMBIGUATION
--------------------
In dental literature "RCT" means randomized controlled trial OR root canal treatment. This
module derives the study-design sense only from PubMed's structured PublicationType field and
never from the letters appearing in text — the rule already stated in
`connectors/pubmed/models.py`, enforced here at the classification layer.

ONE DOCUMENTED ADDITION TO THE BRIEF'S VOCABULARY
-------------------------------------------------
The brief's design list separates "Prospective cohort" from "Retrospective cohort". PubMed's
structured fields frequently establish that a study is a cohort study without establishing its
direction. Choosing a direction in that situation would be an invention, and collapsing it to
"Other" would lose the (L3) mapping that a cohort study legitimately earns. So one extra value
exists — COHORT_DIRECTION_UNREPORTED — and it is used whenever, and only whenever, the direction
was genuinely not reported.
"""
import _paths  # noqa: F401

# ── Design vocabulary (the brief's list, verbatim, plus the one documented addition) ─────────
GUIDELINE = "Guideline"
SYSTEMATIC_REVIEW = "Systematic review"
META_ANALYSIS = "Meta-analysis"
RCT = "Randomized controlled trial"
PROSPECTIVE_COHORT = "Prospective cohort"
RETROSPECTIVE_COHORT = "Retrospective cohort"
COHORT_DIRECTION_UNREPORTED = "Cohort study (direction not reported)"
CASE_CONTROL = "Case-control"
CROSS_SECTIONAL = "Cross-sectional"
DIAGNOSTIC_ACCURACY = "Diagnostic accuracy study"
IN_VITRO = "In-vitro"
FINITE_ELEMENT = "Finite element"
CASE_SERIES = "Case series"
CASE_REPORT = "Case report"
NARRATIVE_REVIEW = "Narrative review"
EXPERT_OPINION = "Expert opinion"
REGISTRY_RECORD = "Clinical trial registry record"
OTHER = "Other"

DESIGNS = (
    GUIDELINE, SYSTEMATIC_REVIEW, META_ANALYSIS, RCT,
    PROSPECTIVE_COHORT, RETROSPECTIVE_COHORT, COHORT_DIRECTION_UNREPORTED,
    CASE_CONTROL, CROSS_SECTIONAL, DIAGNOSTIC_ACCURACY,
    IN_VITRO, FINITE_ELEMENT, CASE_SERIES, CASE_REPORT,
    NARRATIVE_REVIEW, EXPERT_OPINION, REGISTRY_RECORD, OTHER,
)

# ── Provenance of the classification itself ─────────────────────────────────────────────────
REPORTED = "REPORTED"    # from a controlled structured field (PublicationType / MeSH / registry)
INFERRED = "INFERRED"    # from free text, with the matched phrase recorded as its basis
UNKNOWN = "UNKNOWN"      # nothing available to classify on

# ── Hard labels that travel with the classification ─────────────────────────────────────────
REGISTRY_LABEL = "REGISTRY ONLY — NOT EVIDENCE OF EFFICACY"
LAB_FIREWALL_LABEL = (
    "LABORATORY EVIDENCE — describes a mechanism or a plausibility. It may never be used to "
    "claim clinical superiority, longer survival or better patient outcomes."
)

# Designs that can never, by themselves, support a claim about patient outcomes.
NON_CLINICAL_DESIGNS = (IN_VITRO, FINITE_ELEMENT, REGISTRY_RECORD)

# ── Structured vocabulary ───────────────────────────────────────────────────────────────────
PUBTYPE_TO_DESIGN = {
    "practice guideline": GUIDELINE,
    "guideline": GUIDELINE,
    "meta-analysis": META_ANALYSIS,
    "systematic review": SYSTEMATIC_REVIEW,
    "randomized controlled trial": RCT,
    "case reports": CASE_REPORT,
    "editorial": EXPERT_OPINION,
    "comment": EXPERT_OPINION,
    "letter": EXPERT_OPINION,
    "consensus development conference": EXPERT_OPINION,
    "review": NARRATIVE_REVIEW,   # only when no SR/MA tag is also present — see _from_pubtypes
}

MESH_TO_DESIGN = {
    "case-control studies": CASE_CONTROL,
    "cross-sectional studies": CROSS_SECTIONAL,
    "finite element analysis": FINITE_ELEMENT,
    "in vitro techniques": IN_VITRO,
    "sensitivity and specificity": DIAGNOSTIC_ACCURACY,
}

# Free-text markers. Used ONLY to produce an INFERRED classification, never a REPORTED one,
# and only for designs that PubMed's controlled vocabulary does not tag.
TEXT_MARKERS = (
    (FINITE_ELEMENT, ("finite element", "fea model", "finite-element")),
    (IN_VITRO, ("in vitro", "in-vitro", "bond strength", "microtensile", "shear bond",
                "thermocycling", "load to fracture", "microleakage", "dye penetration",
                "artificial saliva", "zone of inhibition")),
    (CASE_SERIES, ("case series", "consecutive cases", "a series of")),
    (DIAGNOSTIC_ACCURACY, ("diagnostic accuracy", "sensitivity and specificity")),
    (CROSS_SECTIONAL, ("cross-sectional", "cross sectional")),
)

# Precedence when several structured signals fire at once. Highest wins.
PRECEDENCE = (
    REGISTRY_RECORD, GUIDELINE, META_ANALYSIS, SYSTEMATIC_REVIEW, RCT,
    PROSPECTIVE_COHORT, RETROSPECTIVE_COHORT, COHORT_DIRECTION_UNREPORTED,
    CASE_CONTROL, DIAGNOSTIC_ACCURACY, CROSS_SECTIONAL,
    FINITE_ELEMENT, IN_VITRO, CASE_SERIES, CASE_REPORT,
    NARRATIVE_REVIEW, EXPERT_OPINION, OTHER,
)


class DesignClassification:
    """The named design, plus everything a consumer needs to know about how it was named."""

    def __init__(self, design, provenance, basis, design_detail=None, lab_firewall=False,
                 registry_only=False, disambiguation_note=None):
        if design not in DESIGNS:
            raise ValueError(f"{design!r} is not a recognised design value")
        if provenance not in (REPORTED, INFERRED, UNKNOWN):
            raise ValueError(f"{provenance!r} is not a recognised provenance value")
        if provenance == INFERRED and not basis:
            # Same discipline as clinical/case_state.py: an inference without a stated basis is
            # indistinguishable from an invention, so it is refused at construction time.
            raise ValueError("An INFERRED classification requires an explicit basis")
        self.design = design
        self.provenance = provenance
        self.basis = basis
        self.design_detail = design_detail
        self.lab_firewall = lab_firewall
        self.registry_only = registry_only
        self.disambiguation_note = disambiguation_note

    @property
    def supports_clinical_outcome_claims(self):
        """False for laboratory, computational and registry records — the firewall, in code."""
        return not (self.lab_firewall or self.registry_only or
                    self.design in NON_CLINICAL_DESIGNS)

    def to_dict(self):
        d = {
            "design": self.design,
            "provenance": self.provenance,
            "basis": self.basis,
            "design_detail": self.design_detail,
            "lab_firewall": self.lab_firewall,
            "registry_only": self.registry_only,
            "supports_clinical_outcome_claims": self.supports_clinical_outcome_claims,
            "disambiguation_note": self.disambiguation_note,
        }
        if self.registry_only:
            d["hard_label"] = REGISTRY_LABEL
        elif self.lab_firewall:
            d["hard_label"] = LAB_FIREWALL_LABEL
        return d

    def __repr__(self):
        return f"<DesignClassification {self.design!r} ({self.provenance})>"


def _norm_list(values):
    return [str(v).strip().lower() for v in (values or []) if v]


def _from_pubtypes(pubtypes):
    """Returns list of (design, matched_term). 'Review' only counts as a narrative review when
    no systematic-review or meta-analysis tag is present alongside it."""
    found = []
    has_sr_or_ma = any(p in ("systematic review", "meta-analysis") for p in pubtypes)
    for p in pubtypes:
        design = PUBTYPE_TO_DESIGN.get(p)
        if design is None:
            continue
        if design == NARRATIVE_REVIEW and has_sr_or_ma:
            continue
        found.append((design, p))
    return found


def _from_mesh(mesh_terms):
    found = []
    mesh = set(mesh_terms)
    for term, design in MESH_TO_DESIGN.items():
        if term in mesh:
            found.append((design, term))

    # Cohort direction is derived from the pair of MeSH terms, never assumed.
    if "cohort studies" in mesh or "longitudinal studies" in mesh or "follow-up studies" in mesh:
        if "prospective studies" in mesh and "retrospective studies" not in mesh:
            found.append((PROSPECTIVE_COHORT, "prospective studies + cohort studies"))
        elif "retrospective studies" in mesh and "prospective studies" not in mesh:
            found.append((RETROSPECTIVE_COHORT, "retrospective studies + cohort studies"))
        else:
            found.append((COHORT_DIRECTION_UNREPORTED, "cohort studies"))
    elif "prospective studies" in mesh:
        found.append((PROSPECTIVE_COHORT, "prospective studies"))
    elif "retrospective studies" in mesh:
        found.append((RETROSPECTIVE_COHORT, "retrospective studies"))
    return found


def _from_text(record):
    text = " ".join(str(x) for x in (record.get("title") or "", record.get("abstract") or "")).lower()
    if not text.strip():
        return []
    found = []
    for design, markers in TEXT_MARKERS:
        for marker in markers:
            if marker in text:
                found.append((design, marker))
                break
    return found


def _best(candidates):
    """Pick by documented precedence, not by order of discovery."""
    by_design = {}
    for design, term in candidates:
        by_design.setdefault(design, term)
    for design in PRECEDENCE:
        if design in by_design:
            return design, by_design[design]
    return None, None


def classify(record, is_registry_record=False):
    """
    record: an EvidenceRecord-shaped dict, or a ClinicalTrials.gov record when
            is_registry_record is True.
    Returns a DesignClassification.

    A registry record short-circuits everything: it is not a study report, it is a registration,
    and it carries REGISTRY ONLY — NOT EVIDENCE OF EFFICACY for the rest of its life in the
    pipeline no matter what its registered design field says.
    """
    if is_registry_record or record.get("nct_id"):
        registered_design = record.get("study_type") or record.get("design")
        return DesignClassification(
            REGISTRY_RECORD, REPORTED,
            basis=f"Trial registry record ({record.get('nct_id') or 'NCT id not present'}).",
            design_detail=(f"Registered study type: {registered_design}" if registered_design
                           else "Registered study type not stated in the record."),
            registry_only=True,
        )

    pubtypes = _norm_list(record.get("publication_types"))
    mesh = _norm_list(record.get("mesh_terms"))

    structured = _from_pubtypes(pubtypes) + _from_mesh(mesh)
    design, term = _best(structured)

    if design is not None:
        detail = None
        # An RCT tag plus a systematic-review tag means a review OF trials, not a trial.
        if design in (SYSTEMATIC_REVIEW, META_ANALYSIS) and RCT in [d for d, _ in structured]:
            detail = "Synthesises randomized controlled trials."
        if design == COHORT_DIRECTION_UNREPORTED:
            detail = ("Indexed as a cohort study without a prospective/retrospective term. The "
                      "direction is not reported and has not been assumed.")
        return DesignClassification(
            design, REPORTED,
            basis=f"PubMed structured metadata: {term!r}.",
            design_detail=detail,
            lab_firewall=design in (IN_VITRO, FINITE_ELEMENT),
            disambiguation_note=(_RCT_NOTE if design == RCT else None),
        )

    inferred = _from_text(record)
    design, term = _best(inferred)
    if design is not None:
        return DesignClassification(
            design, INFERRED,
            basis=(f"No controlled PublicationType/MeSH signal was present. Classified from the "
                   f"phrase {term!r} in the title/abstract — free text, not an indexed field."),
            lab_firewall=design in (IN_VITRO, FINITE_ELEMENT),
        )

    return DesignClassification(
        OTHER, UNKNOWN,
        basis=("No PublicationType, MeSH term, or recognisable design phrasing was available. "
               "The design is unknown and has not been guessed."),
    )


_RCT_NOTE = (
    "RCT here means RANDOMIZED CONTROLLED TRIAL (a study design), sourced from PubMed's "
    "structured PublicationType field. It does not mean root canal treatment. Spell the "
    "intended sense out on first use in any dental output."
)


# ── DEL-7 mapping ───────────────────────────────────────────────────────────────────────────
DESIGN_TO_DEL7 = {
    GUIDELINE: "L1",
    SYSTEMATIC_REVIEW: "L2",
    META_ANALYSIS: "L2",
    RCT: "L3",
    PROSPECTIVE_COHORT: "L3",
    RETROSPECTIVE_COHORT: "L3",
    COHORT_DIRECTION_UNREPORTED: "L3",
    CASE_CONTROL: "L3",
    CROSS_SECTIONAL: "L4",
    DIAGNOSTIC_ACCURACY: "L3",
    CASE_SERIES: "L4",
    CASE_REPORT: "L4",
    NARRATIVE_REVIEW: "L4",
    EXPERT_OPINION: "L4",
    IN_VITRO: "LAB",
    FINITE_ELEMENT: "LAB",
    REGISTRY_RECORD: "REG",
    OTHER: "UNVER",
}


def del7_tag(classification):
    """
    Map a named design onto its DEL-7 tag. Preserves the v1.1 hierarchy exactly — this function
    reads it, it does not redefine it (del7-evidence-hierarchy.md remains canonical).

    A classification whose provenance is UNKNOWN never receives a supporting-evidence tag: an
    unnamed design cannot earn a tier.
    """
    if classification.provenance == UNKNOWN:
        return "UNVER"
    return DESIGN_TO_DEL7[classification.design]

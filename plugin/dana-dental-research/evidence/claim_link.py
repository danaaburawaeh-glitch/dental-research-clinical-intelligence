"""
evidence/claim_link.py  —  CLAIM-EVIDENCE LINKING (v1.2)

Binds every consequential clinical claim to the five things that make it checkable:

    citation · verification state · study type · certainty · directness

WHY ALL FIVE, AND WHY AT THE CLAIM
----------------------------------
Each one alone is routinely mistaken for the others. A citation says the paper exists. A
verification state says the citation is accurate. A study type says what kind of investigation it
was. Certainty says how much confidence the evidence justifies. Directness says whether it
answers this question at all. A claim carrying only the first is the most common form of
evidence theatre in clinical writing — the reference is real, and it establishes nothing about
what is being asserted.

They attach at the claim, not in a bibliography. A reader deciding whether to act on one sentence
should not have to reconstruct which of eleven references supports it.

RELATIONSHIP TO THE CLINICAL LAYER
----------------------------------
`clinical/evidence_binding.py` already binds a claim to a decision in a specific case, with its
DEL-7 tag, directness, retrieval provenance and Saudi regulatory state. That is the case-facing
binding and it is unchanged. This module is the evidence-facing one, carrying the richer v1.2
axes; `to_bound_claim()` converts across so a linked claim can enter case reasoning without being
re-derived.
"""
import _paths  # noqa: F401

import citation_verification as cv
import certainty as ce
import directness as dr
import study_design as sd

# The five required links.
REQUIRED_LINKS = ("citation", "verification_state", "study_type", "certainty", "directness")

PASS = "PASS"
FAIL = "FAIL"


class UnsupportedClaimError(ValueError):
    """Raised when a consequential claim is asserted without the links that make it checkable."""


class EvidenceLinkedClaim:
    """One clinical claim and the evidence actually standing behind it."""

    def __init__(self, claim, citation=None, verification_state=None, design_classification=None,
                 certainty_assessment=None, directness_assessment=None, limitations=None,
                 consequential=True, del7_tag=None, search_strategy=None):
        self.claim = claim
        self.citation = citation
        self.verification_state = verification_state
        self.design_classification = design_classification
        self.certainty_assessment = certainty_assessment
        self.directness_assessment = directness_assessment
        self.limitations = list(limitations or [])
        self.consequential = consequential
        self.search_strategy = search_strategy
        self._del7_tag = del7_tag

    @property
    def del7_tag(self):
        if self._del7_tag:
            return self._del7_tag
        if self.design_classification is not None:
            return sd.del7_tag(self.design_classification)
        return "UNVER"

    @property
    def study_type(self):
        return getattr(self.design_classification, "design", None)

    @property
    def certainty(self):
        return getattr(self.certainty_assessment, "rating", None)

    @property
    def directness(self):
        return getattr(self.directness_assessment, "verdict", None)

    def missing_links(self):
        missing = []
        if not self.citation:
            missing.append("citation")
        if self.verification_state not in cv.STATES:
            missing.append("verification_state")
        if not self.study_type:
            missing.append("study_type")
        if self.certainty not in ce.RATINGS:
            missing.append("certainty")
        if self.directness not in dr.VERDICTS:
            missing.append("directness")
        return missing

    def problems(self):
        """Every reason this claim may not be released as written."""
        problems = []

        missing = self.missing_links()
        if self.consequential and missing:
            problems.append({
                "severity": "CRITICAL",
                "reason": (f"A consequential claim is missing: {', '.join(missing)}. Every "
                           f"consequential clinical claim links to all five of "
                           f"{', '.join(REQUIRED_LINKS)}."),
            })

        if self.verification_state == cv.RETRACTED:
            problems.append({
                "severity": "CRITICAL",
                "reason": ("The supporting source is RETRACTED. Retracted evidence may never "
                           "support a clinical recommendation. It may be named only as a "
                           "historical note — 'RETRACTED — EXCLUDED FROM SYNTHESIS'."),
            })

        if self.verification_state == cv.NOT_VERIFIED and self.consequential:
            problems.append({
                "severity": "CRITICAL",
                "reason": ("The supporting citation is NOT_VERIFIED. An unverified reference is "
                           "never presented as a confirmed citation; mark the item (UNVER) and "
                           "supply a runnable search strategy instead."),
            })

        if self.verification_state == cv.NOT_VERIFIED and not self.search_strategy:
            problems.append({
                "severity": "MAJOR",
                "reason": ("An unverified claim must carry a runnable search strategy in place of "
                           "the citation it does not have."),
            })

        if self.design_classification is not None:
            if not self.design_classification.supports_clinical_outcome_claims:
                problems.append({
                    "severity": "CRITICAL",
                    "reason": (f"The supporting source is a {self.study_type}. "
                               + (sd.REGISTRY_LABEL if self.design_classification.registry_only
                                  else sd.LAB_FIREWALL_LABEL)
                               + " It cannot support a claim about what happens to patients."),
                })

        if self.certainty == ce.NOT_ASSESSABLE and self.consequential:
            problems.append({
                "severity": "MAJOR",
                "reason": ("Certainty is NOT ASSESSABLE. The claim may be stated only with that "
                           "explicitly attached — never with the confidence of an assessed body "
                           "of evidence."),
            })

        if self.directness == dr.INDIRECT and self.consequential:
            problems.append({
                "severity": "MAJOR",
                "reason": ("The evidence is INDIRECT for this question. It may be reported as "
                           "indirect supporting evidence; it may not be presented as directly "
                           "answering the claim."),
            })

        # The single rule the whole v1.2 engine exists to enforce.
        if self.verification_state in (cv.VERIFIED, cv.VERIFIED_WITH_METADATA_DISCREPANCY) and \
                self.certainty in (ce.NOT_ASSESSABLE, ce.VERY_LOW, ce.LOW) and \
                not self.limitations:
            problems.append({
                "severity": "MAJOR",
                "reason": (f"The citation is {self.verification_state} but the certainty is "
                           f"{self.certainty}. A verified citation is not strong evidence. State "
                           f"the limitation explicitly so the verification state cannot be read "
                           f"as strength."),
            })

        return problems

    def audit(self):
        problems = self.problems()
        return {
            "result": FAIL if any(p["severity"] == "CRITICAL" for p in problems) else PASS,
            "claim": self.claim,
            "problems": problems,
            "links": {
                "citation": self.citation,
                "verification_state": self.verification_state,
                "study_type": self.study_type,
                "certainty": self.certainty,
                "directness": self.directness,
                "del7_tag": self.del7_tag,
            },
            "limitations": list(self.limitations),
        }

    def to_markdown(self):
        lines = [
            f"**Claim:** {self.claim}", "",
            f"**Evidence:** {self.study_type or 'not established'}  ",
            f"**Citation:** {self.citation or '(UNVER) — no retrieved source'}  ",
            f"**Citation status:** {self.verification_state or 'not established'}  ",
            f"**DEL-7:** {self.del7_tag}  ",
            f"**Certainty:** {self.certainty or ce.NOT_ASSESSABLE}"
            + (f" ({ce.ASSESSMENT_LABEL})" if self.certainty else "") + "  ",
            f"**Directness:** {self.directness or dr.UNKNOWN}  ",
        ]
        if self.limitations:
            lines.append("**Limitations:** " + "; ".join(self.limitations))
        if self.verification_state == cv.NOT_VERIFIED and self.search_strategy:
            lines.append(f"**Search strategy (in place of a citation):** `{self.search_strategy}`")
        return "\n".join(lines)

    def to_bound_claim(self, decision):
        """Convert to the clinical layer's BoundClaim so a linked claim can enter case reasoning
        without being re-derived. Imported lazily: the clinical layer is independent of this one
        and must stay loadable without it."""
        import os
        import sys
        clinical_dir = os.path.join(_paths.PLUGIN_ROOT, "clinical")
        if clinical_dir not in sys.path:
            sys.path.insert(0, clinical_dir)
        import evidence_binding as eb

        directness_map = {dr.DIRECT: eb.DIRECT, dr.PARTIALLY_DIRECT: eb.INDIRECT,
                          dr.INDIRECT: eb.INDIRECT, dr.UNKNOWN: eb.UNKNOWN_DIRECTNESS}
        return eb.bind(
            self.claim, decision, self.del7_tag,
            directness_map.get(self.directness, eb.UNKNOWN_DIRECTNESS),
            sources=[{"connector": "pubmed", "citation": self.citation,
                      "verification_state": self.verification_state,
                      "is_retracted": self.verification_state == cv.RETRACTED}],
            confidence=self.certainty,
            search_strategy=self.search_strategy)


def audit_claims(claims):
    """Audit a set of claims together. Any CRITICAL problem fails the whole set — a single
    unsupported consequential claim is not offset by well-supported neighbours."""
    audits = [c.audit() for c in claims]
    critical = [a for a in audits if a["result"] == FAIL]
    return {
        "result": FAIL if critical else PASS,
        "claims": audits,
        "critical_count": len(critical),
        "unsupported_claims": [a["claim"] for a in critical],
    }

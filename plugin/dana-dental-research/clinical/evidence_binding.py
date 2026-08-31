"""
clinical/evidence_binding.py

Evidence↔case binding — the component that turns "DANA can search PubMed" into "DANA can support
THIS decision for THIS patient, and show its work".

A bound claim carries four things at the point of use, not in a footer:
  1. the DEL-7 evidence tag,
  2. the retrieval provenance chain from the connector that produced it,
  3. the Saudi regulatory state, where the claim touches a product or a permission,
  4. its directness to this case.

An unverifiable claim becomes (UNVER) with a runnable PICO search string. It never becomes a
fabricated citation — the rule the connectors already enforce, carried up into clinical reasoning.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

# DEL-7 tags, as already used by the evidence layer.
DEL7_TAGS = ("L1", "L2", "L3", "L4", "IFU", "JUDG", "OPS", "LAB", "REG", "KOL", "UNVER")

# Directness of the evidence to THIS case.
DIRECT = "DIRECT"
INDIRECT = "INDIRECT"
EXTRAPOLATION = "EXTRAPOLATION"
UNKNOWN_DIRECTNESS = "UNKNOWN"
DIRECTNESS = (DIRECT, INDIRECT, EXTRAPOLATION, UNKNOWN_DIRECTNESS)

REGULATORY_VERIFIED = "VERIFIED"
REGULATORY_REQUIRES_VERIFICATION = "REQUIRES VERIFICATION"

UNVER_RULE = (
    "A claim that cannot be traced to a real retrieved source is tagged (UNVER) and accompanied "
    "by a runnable search strategy. It is never given a plausible-looking citation."
)

SEPARATION_RULE = (
    "Evidence and authorisation are answered separately. Evidence says whether something works; "
    "the Saudi regulatory state says whether it may lawfully be used here. Neither substitutes "
    "for the other."
)


@dataclass
class BoundClaim:
    """One clinical claim, bound to a specific decision in a specific case."""
    claim: str
    decision: str                       # which decision in this case the claim supports
    del7_tag: str = "UNVER"
    directness: str = UNKNOWN_DIRECTNESS
    confidence: Optional[str] = None    # stated at the claim, not in a footer (M1 universal rule)
    # Provenance chain — whatever the connectors actually returned.
    sources: List[Dict[str, Any]] = field(default_factory=list)
    # Regulatory state, when the claim touches a product/device/drug or a permission.
    regulatory_state: Optional[str] = None
    regulatory_note: Optional[str] = None
    search_strategy: Optional[str] = None   # required when UNVER

    def __post_init__(self):
        if self.del7_tag not in DEL7_TAGS:
            raise ValueError(f"Unknown DEL-7 tag {self.del7_tag!r}. Must be one of {DEL7_TAGS}.")
        if self.directness not in DIRECTNESS:
            raise ValueError(f"Unknown directness {self.directness!r}.")
        if self.del7_tag == "UNVER" and not self.search_strategy:
            raise ValueError(
                f"Claim {self.claim[:60]!r} is tagged UNVER but carries no search strategy. "
                + UNVER_RULE)
        if self.del7_tag != "UNVER" and not self.sources:
            raise ValueError(
                f"Claim {self.claim[:60]!r} is tagged {self.del7_tag} but has no source. A tag "
                "above UNVER asserts that something was actually retrieved.")

    def to_dict(self):
        return asdict(self)


def source_from_pubmed(record: Dict[str, Any]):
    """Build a provenance entry from a PubMed connector record. Copies, never invents."""
    return {
        "connector": "pubmed", "database": "pubmed",
        "pmid": record.get("pmid"), "doi": record.get("doi"),
        "title": record.get("title"), "journal": record.get("journal"),
        "year": record.get("publication_year"),
        "publication_types": record.get("publication_types"),
        "is_retracted": record.get("is_retracted"),
        "retrieved_at": record.get("retrieved_at"),
    }


def source_from_crossref(record: Dict[str, Any], verification_status: Optional[str] = None):
    return {
        "connector": "crossref", "database": "crossref-works",
        "doi": record.get("doi"), "title": record.get("title"),
        "journal": record.get("journal"), "year": record.get("publication_year"),
        "citation_verification_status": verification_status,
        "retrieved_at": record.get("retrieved_at"),
    }


def source_from_trial(record: Dict[str, Any]):
    """
    From a ClinicalTrials.gov record. Carries the evidence_class forward, because a registry
    record is not published evidence and the distinction must survive into the claim.
    """
    return {
        "connector": "clinical_trials", "database": "ClinicalTrials.gov",
        "nct_id": record.get("nct_id"), "overall_status": record.get("overall_status"),
        "has_results": record.get("has_results"),
        "evidence_class": record.get("evidence_class"),
        "status_safety_note": record.get("status_safety_note"),
        "retrieved_at": record.get("retrieved_at"),
    }


def source_from_sfda(result: Dict[str, Any]):
    return {
        "connector": "sfda", "database": "SFDA",
        "regulatory_state": result.get("regulatory_state"),
        "status": result.get("status"),
        "records": result.get("records"),
        "retrieved_at": (result.get("provenance") or {}).get("retrieval_timestamp"),
    }


def bind(claim, decision, del7_tag="UNVER", directness=UNKNOWN_DIRECTNESS, sources=None,
         regulatory_state=None, regulatory_note=None, search_strategy=None, confidence=None):
    """Construct a BoundClaim, validating the binding contract."""
    return BoundClaim(claim=claim, decision=decision, del7_tag=del7_tag, directness=directness,
                      sources=list(sources or []), regulatory_state=regulatory_state,
                      regulatory_note=regulatory_note, search_strategy=search_strategy,
                      confidence=confidence)


def unver(claim, decision, search_strategy, confidence="Cannot assess"):
    """Shorthand for the honest-gap case."""
    return bind(claim, decision, del7_tag="UNVER", search_strategy=search_strategy,
                confidence=confidence)


def audit_claims(claims: List[BoundClaim]):
    """
    Check a set of bound claims before release.

    Returns {ok, issues, unver_count, retracted_sources, regulatory_unverified}. A retracted
    source supporting a live claim is the most serious finding here — the retraction gate exists
    at retrieval time, and this is the second place it must not slip through.
    """
    issues = []
    retracted = []
    regulatory_unverified = []
    unver_count = 0

    for c in claims:
        if c.del7_tag == "UNVER":
            unver_count += 1
        for s in c.sources:
            if s.get("is_retracted") is True:
                retracted.append({"claim": c.claim, "source": s})
                issues.append(
                    f"Claim {c.claim[:60]!r} is supported by a RETRACTED source "
                    f"(PMID {s.get('pmid')}). It must be removed, not annotated.")
            if s.get("evidence_class") == "REGISTERED_NO_RESULTS":
                issues.append(
                    f"Claim {c.claim[:60]!r} cites a registered trial with no posted results. "
                    "Registration is not evidence that an intervention works.")
        if c.regulatory_state and c.regulatory_state != REGULATORY_VERIFIED:
            regulatory_unverified.append(c.claim)
        if c.directness == EXTRAPOLATION and c.confidence in (None, "High"):
            issues.append(
                f"Claim {c.claim[:60]!r} is an EXTRAPOLATION but carries confidence "
                f"{c.confidence!r}. Extrapolated evidence does not support high confidence.")

    return {
        "ok": not issues,
        "issues": issues,
        "unver_count": unver_count,
        "retracted_sources": retracted,
        "regulatory_unverified": regulatory_unverified,
        "separation_rule": SEPARATION_RULE,
    }

"""
clinical/identity_policy.py

Author Identity & Citation Policy — executable.

The rule: the assistant's creator is never a clinical, scientific, regulatory or protocol
authority. Her name belongs in creator attribution and ownership metadata, nowhere else.

This is code rather than prose because §7 of the policy asks for a scan before final output, and a
scan that depends on remembering to run it is not a scan. `scan()` returns violations; the safety
veto blocks on them.

The distinction that matters is CONTEXT, not presence:
  - "Designed by Dr. Dana Abu Rawaeh" in an About section — allowed.
  - "Dr Dana recommends full-coverage crowns" in a clinical answer — forbidden, and forbidden
    precisely because it dresses a personal preference as a source.
"""
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# The protected identity
# ---------------------------------------------------------------------------
NAME_PATTERNS = (
    r"Dr\.?\s+Dana\s+Abu\s*Rawaeh",
    r"Dana\s+Abu\s*Rawaeh",
    r"Dr\.?\s+Dana\b",
    r"\bDana\b",
    r"د\.?\s*دانا\s*أبو\s*روائح",
    r"دانا\s*أبو\s*روائح",
    r"د\.?\s*دانا\b",
    r"\bدانا\b",
)
NAME_RE = re.compile("|".join(NAME_PATTERNS), re.IGNORECASE)

# "DANA" as the product name is not the person. Matched case-sensitively and by construction:
# the assistant is DANA, the clinician is Dana.
# ---------------------------------------------------------------------------
# The product's user-facing display name (v1.0.0).
#
# The name contains the creator's name by design — it is the product's identity, not a citation.
# It is therefore stripped in EVERY context, unlike the creator-attribution string, which §4
# restricts to About/credits. An assistant may identify itself in a clinical output; it may not
# cite its designer as a source there.
#
# ONLY the exact full phrase is exempt. "Dr. Dana" standing alone remains blocked everywhere, and
# because the authority patterns require the name adjacent to the authority verb, stripping the
# full product name cannot mask "Dr. Dana recommends…".
# ---------------------------------------------------------------------------
PRODUCT_DISPLAY_NAME = "Dental Research & Clinical Intelligence by Dr. Dana"
PRODUCT_DISPLAY_NAME_VARIANTS = (
    PRODUCT_DISPLAY_NAME,
    "Dental Research & Clinical Intelligence by Dr Dana",
    "Dental Research and Clinical Intelligence by Dr. Dana",
    "Dental Research and Clinical Intelligence by Dr Dana",
)
INTERNAL_PLUGIN_ID = "dana-dental-research"

# All-caps DANA is the assistant; mixed-case Dana is the clinician. That casing distinction is the
# reliable separator, so standalone DANA is treated as the product — EXCEPT where it is preceded by
# an honorific, which would make it the person written in caps.
PRODUCT_NAME_RE = re.compile(
    r"(?<!DR\s)(?<!DR\.\s)(?<!Dr\s)(?<!Dr\.\s)\bDANA\b"
    r"|dana-[\w]+(?:-[\w]+)*"          # hyphenated package/repo names: dana-dental-research,
                                        # dana-clinical-core, and any future sibling
    r"|DANA_[\w]+"
)

# ---------------------------------------------------------------------------
# The only permitted strings, and where
# ---------------------------------------------------------------------------
ALLOWED_CREATOR_STRING_EN = "Designed by Dr. Dana Abu Rawaeh"
ALLOWED_CREATOR_STRING_AR = "تم تصميم هذا المساعد بواسطة د. دانا أبوروائح"
ALLOWED_CREATOR_STRINGS = (ALLOWED_CREATOR_STRING_EN, ALLOWED_CREATOR_STRING_AR)

CONTEXT_CREATOR_METADATA = "creator_metadata"   # plugin.json, README, About, credits
CONTEXT_OWNERSHIP_RECORD = "ownership_record"   # approval records, amendment authority, signatures
CONTEXT_CLINICAL = "clinical"                   # any clinical answer or reasoning
CONTEXT_EVIDENCE = "evidence"                   # evidence synthesis, citations
CONTEXT_REGULATORY = "regulatory"               # Saudi regulatory answers
CONTEXT_TREATMENT = "treatment"                 # treatment recommendations / plans
CONTEXT_PROTOCOL_TITLE = "protocol_title"
CONTEXT_PATIENT_FACING = "patient_facing"

ALLOWED_CONTEXTS = (CONTEXT_CREATOR_METADATA, CONTEXT_OWNERSHIP_RECORD)
FORBIDDEN_CONTEXTS = (CONTEXT_CLINICAL, CONTEXT_EVIDENCE, CONTEXT_REGULATORY,
                      CONTEXT_TREATMENT, CONTEXT_PROTOCOL_TITLE, CONTEXT_PATIENT_FACING)

# ---------------------------------------------------------------------------
# Authority phrasing — forbidden in every context, including an About section.
# "According to Dr Dana, crowns are indicated" does not become acceptable by being
# printed under a credits heading.
# ---------------------------------------------------------------------------
# NOTE: this MUST stay wrapped in a non-capturing group. Unwrapped, `A|B\s+verb` parses as
# `A` OR `B\s+verb`, so every bare name matched the authority patterns — a false positive
# that would have flagged the creator metadata in plugin.json.
_N = r"(?:(?:Dr\.?\s+)?Dana(?:\s+Abu\s*Rawaeh)?|(?:د\.?\s*)?دانا(?:\s*أبو\s*روائح)?)"
AUTHORITY_PATTERNS = {
    "attributed_recommendation": rf"(?:according to|per|as (?:stated|recommended) by)\s+{_N}",
    "verb_authority": rf"{_N}\s+(?:recommends?|requires?|states?|advises?|mandates?|prescribes?|says?)",
    "possessive_protocol": rf"{_N}(?:'s|’s)?\s+(?:protocol|guideline|rule|standard|criteria|method|technique|evidence|recommendation)",
    "named_protocol": rf"\b{_N}\s+(?:Clinical\s+)?(?:Protocol|Guideline|Standard|Method|Criteria)\b",
    "evidence_source": rf"{_N}\s+(?:evidence|study|data|research|findings)",
}
AUTHORITY_RES = {k: re.compile(v, re.IGNORECASE) for k, v in AUTHORITY_PATTERNS.items()}

# Protocol naming — the neutral names that are correct.
NEUTRAL_PROTOCOL_NAMES = (
    "Clinical Protocol", "Clinical Governance Protocol", "Prosthodontic Decision Protocol",
    "Evidence Protocol", "Saudi Regulatory Protocol", "Treatment Planning Protocol",
    "the approved Clinical Protocol", "the internal Clinical Protocol",
)

# Source classes to use instead of a person's name.
SOURCE_CLASS_ALTERNATIVES = {
    "clinic_policy": "(OPS) Clinic operational policy",
    "clinical_judgement": "(JUDG) Clinical judgement — not externally validated",
    "user_supplied": "(USER-SUPPLIED)",
    "internal_protocol": "(INTERNAL PROTOCOL) the approved Clinical Protocol",
}

REWRITE_GUIDE = {
    "attributed_recommendation": "Name the actual source (guideline, review, study, IFU, authority), or use (OPS)/(JUDG).",
    "verb_authority": "Replace with '(OPS) Clinic policy requires…' or '(JUDG) Clinical judgement…'.",
    "possessive_protocol": "Use 'the approved Clinical Protocol' — never a person's name.",
    "named_protocol": "Rename to a neutral title, e.g. 'Clinical Protocol'.",
    "evidence_source": "Cite the real evidence source. A person's name is never a DEL-7 source.",
}


@dataclass
class IdentityViolation:
    kind: str
    matched_text: str
    position: int
    context: str
    reason: str
    remedy: str

    def to_dict(self):
        return asdict(self)


def _strip_allowed(text: str):
    """Blank out the permitted creator strings so they cannot register as violations."""
    out = text
    for s in ALLOWED_CREATOR_STRINGS:
        out = out.replace(s, " " * len(s))
    return out


def _strip_product_name(text: str):
    """
    Blank out the product's own identifiers so they are never mistaken for the person:
    the display name, the internal plugin id, and DANA-the-assistant.

    Longest first, so the display name is removed before the bare-name pattern can see it.
    """
    out = text
    for variant in sorted(PRODUCT_DISPLAY_NAME_VARIANTS, key=len, reverse=True):
        out = out.replace(variant, " " * len(variant))
    return PRODUCT_NAME_RE.sub(lambda m: " " * len(m.group(0)), out)


def scan(text: str, context: str = CONTEXT_CLINICAL):
    """
    Scan one piece of output. Returns {ok, violations, context, scanned}.

    Two independent checks:
      1. Authority phrasing — forbidden in EVERY context, allowed contexts included.
      2. Bare name occurrence — forbidden in clinical/evidence/regulatory/treatment/protocol-title
         and patient-facing contexts; permitted in creator metadata and ownership records.
    """
    if context not in ALLOWED_CONTEXTS + FORBIDDEN_CONTEXTS:
        raise ValueError(f"Unknown context {context!r}. "
                         f"Use one of {ALLOWED_CONTEXTS + FORBIDDEN_CONTEXTS}.")

    violations: List[IdentityViolation] = []
    # The permitted creator string is exempt ONLY where the policy permits it. Pasting
    # "Designed by Dr. Dana Abu Rawaeh" into a treatment plan is still a violation (§4).
    working = text if context in FORBIDDEN_CONTEXTS else _strip_allowed(text)
    working = _strip_product_name(working)

    # 1. Authority phrasing — context-independent.
    for kind, rx in AUTHORITY_RES.items():
        for m in rx.finditer(working):
            violations.append(IdentityViolation(
                kind=kind, matched_text=m.group(0).strip(), position=m.start(), context=context,
                reason=("The assistant's creator is being presented as a clinical, scientific or "
                        "protocol authority. She is never a source."),
                remedy=REWRITE_GUIDE[kind]))

    # 2. Bare name in a forbidden context.
    if context in FORBIDDEN_CONTEXTS:
        already = {(v.position, v.matched_text) for v in violations}
        for m in NAME_RE.finditer(working):
            if any(abs(m.start() - p) < 60 for p, _ in already):
                continue  # already reported as authority phrasing
            violations.append(IdentityViolation(
                kind="name_in_forbidden_context", matched_text=m.group(0).strip(),
                position=m.start(), context=context,
                reason=(f"The creator's name appears in a {context} output. Permitted only in "
                        "creator metadata or an ownership record."),
                remedy=(f"Remove it, or state the real source. Allowed creator string, in an "
                        f"About/credits context only: '{ALLOWED_CREATOR_STRING_EN}'.")))

    return {
        "ok": not violations,
        "context": context,
        "violations": [v.to_dict() for v in violations],
        "violation_count": len(violations),
        "allowed_creator_strings": list(ALLOWED_CREATOR_STRINGS),
    }


def assert_clean(text: str, context: str = CONTEXT_CLINICAL):
    """Raise on violation. For call sites that must not proceed."""
    result = scan(text, context)
    if not result["ok"]:
        first = result["violations"][0]
        raise IdentityPolicyError(
            f"Identity policy violation ({first['kind']}): {first['matched_text']!r}. "
            f"{first['remedy']}")
    return True


class IdentityPolicyError(RuntimeError):
    """Raised when output would present the creator as a source."""


def suggest_source_class(origin: str):
    """Map a rule's origin to the label that should carry it instead of a person's name."""
    return SOURCE_CLASS_ALTERNATIVES.get(origin, SOURCE_CLASS_ALTERNATIVES["internal_protocol"])

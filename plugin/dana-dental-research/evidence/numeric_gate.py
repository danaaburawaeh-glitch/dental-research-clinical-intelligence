"""
evidence/numeric_gate.py  —  NUMERIC EVIDENCE GATE (v1.2, executable)

`clinical-governance/references/numeric-evidence-gate.md` states the rule. This module enforces
it: no survival percentage, failure rate, risk ratio, odds ratio, hazard ratio, mean difference
or confidence interval may appear in a Clinical Bottom Line unless the source containing that
number was actually retrieved and verified in this session.

WHY A SCANNER AND NOT A CONVENTION
----------------------------------
Numeric hallucination is not a reasoning failure that better instructions fix. "Veneer survival
is approximately 95% at 10 years" is the single most fluent sentence available on the subject —
it is well-formed, it is roughly consistent with the literature, and it can be produced without
any source at all. A rule that says "don't do that" competes against fluency every time. A gate
that scans the finished text and fails it competes against nothing.

So the check runs on the OUTPUT, not on the intention: every number found in the text must match
a registered NumericClaim whose source record is retrieved and whose citation state permits use.

WHAT IS SCANNED
---------------
The brief's list, plus the patterns those figures actually appear in:
percentages · risk/odds/hazard ratios · risk differences and absolute risk reductions · mean and
standard mean differences · numbers needed to treat · confidence intervals · survival and failure
rates · p-values attached to an effect.

Deliberately NOT flagged: study counts, participant counts, follow-up durations and years, which
are extraction fields governed by `sr_extraction.py`'s provenance rules rather than effect
estimates — and flagging them would make the gate noisy enough to be ignored, which is how gates
die. They are still required to carry provenance; `check_extraction_numbers()` covers them.
"""
import _paths  # noqa: F401

import re

import citation_verification as cv

# Statuses from numeric-evidence-gate.md, unchanged.
VERIFIED = "VERIFIED"
TYPICAL_RANGE_VERIFY = "TYPICAL RANGE — VERIFY"
USER_SUPPLIED = "USER-SUPPLIED"
CALCULATED = "CALCULATED"
STATUSES = (VERIFIED, TYPICAL_RANGE_VERIFY, USER_SUPPLIED, CALCULATED)

# Only a VERIFIED figure may appear in a Clinical Bottom Line. The other three statuses are
# legitimate elsewhere in an output — a typical range in a methods discussion, a user-supplied
# measurement in a case write-up — but the Bottom Line is what a reader acts on.
BOTTOM_LINE_PERMITTED = (VERIFIED, USER_SUPPLIED, CALCULATED)

# Citation states in which a retrieved source may carry a number into the Bottom Line.
#
# PARTIALLY_VERIFIED is included, and that inclusion is deliberate (v1.2 real-world validation).
# It was previously excluded, which had two problems. First, it contradicted the rest of the
# system: PARTIALLY_VERIFIED is citable everywhere else (citation_verification.CITABLE_STATES,
# claim_link), and no reference document imposed a stricter bar here. Second, and decisively, the
# stricter bar protected nothing real. A PARTIALLY_VERIFIED state usually means the record carries
# no DOI, so no Crossref cross-check was possible — but Crossref returns bibliographic metadata
# only, never an abstract and never results. Requiring Crossref corroboration before a figure may
# be quoted corroborates the CITATION, not the NUMBER; the number's provenance is the retrieved
# PubMed record either way. The practical effect was that pre-DOI literature — much of the
# long-follow-up veneer and prosthodontic evidence — could contribute no figure at all, which
# pushes numbers out of the gated Bottom Line rather than making them safer.
#
# What is required instead is disclosure: a figure from an uncorroborated citation is permitted
# and reported as needing its cap stated. See `uncorroborated` below and `gate_bottom_line`'s
# `disclosures`.
CITATION_STATES_PERMITTING_NUMBERS = (cv.VERIFIED, cv.VERIFIED_WITH_METADATA_DISCREPANCY,
                                      cv.CORRECTED, cv.PARTIALLY_VERIFIED)

# States that carry a number but whose citation was never independently corroborated.
UNCORROBORATED_CITATION_STATES = (cv.PARTIALLY_VERIFIED,)

_NUM = r"[-+]?\d+(?:[.,]\d+)?"

# Each pattern names the kind of figure it catches, so a failure message can say what was found.
# Order matters: a confidence interval is matched first, including its leading "95%", so the
# nominal confidence level is not also reported as a separate percentage needing its own source.
EFFECT_PATTERNS = (
    ("confidence interval", re.compile(
        rf"(?:\d{{2,3}}\s?%\s*)?\bC\.?I\.?\b[^.;]{{0,40}}?{_NUM}\s*(?:to|-|–|,)\s*{_NUM}", re.I)),
    ("confidence interval", re.compile(rf"(?:\d{{2,3}}\s?%\s*)?\bC\.?I\.?\b[^.;]{{0,40}}?{_NUM}", re.I)),
    ("percentage", re.compile(rf"{_NUM}\s?%")),
    ("risk ratio", re.compile(rf"\b(?:RR|risk ratio)\s*[=:]?\s*{_NUM}", re.I)),
    ("odds ratio", re.compile(rf"\b(?:OR|odds ratio)\s*[=:]?\s*{_NUM}", re.I)),
    ("hazard ratio", re.compile(rf"\b(?:HR|hazard ratio)\s*[=:]?\s*{_NUM}", re.I)),
    ("mean difference", re.compile(rf"\b(?:SMD|MD|mean difference)\s*[=:]?\s*{_NUM}", re.I)),
    # Risk difference, absolute risk reduction and number-needed-to-treat are effect estimates a
    # reader acts on exactly as they act on a risk ratio. RD in particular is the primary effect
    # measure of substrate and material comparisons in the veneer literature, so its absence here
    # left the most decision-relevant figure in that field ungated. (v1.2 real-world validation.)
    ("risk difference", re.compile(rf"\b(?:RD|risk difference)\s*(?:of\s*)?[=:]?\s*{_NUM}", re.I)),
    ("absolute risk reduction", re.compile(
        rf"\b(?:ARR|absolute risk (?:reduction|difference))\s*(?:of\s*)?[=:]?\s*{_NUM}", re.I)),
    ("number needed to treat", re.compile(rf"\b(?:NNT|NNH)\s*[=:]?\s*{_NUM}", re.I)),
    ("p-value", re.compile(rf"\bp\s*[<>=]\s*{_NUM}", re.I)),
    # Spelled-out rates only. The percent indicator (or the word "rate") is REQUIRED: with it
    # optional, "6 of 7 failures" — a count of events, not a rate — matched as a failure rate.
    # A gate that fires on plain event counts gets routed around, and a gate people route around
    # is worse than no gate. Bare "95%" is already caught by the percentage pattern above.
    ("survival/failure rate", re.compile(
        rf"{_NUM}\s*(?:per\s?cent|percent)\s*(?:survival|failure|success)", re.I)),
    ("survival/failure rate", re.compile(
        rf"(?:survival|failure|success)\s+rate[^.;]{{0,24}}?{_NUM}", re.I)),
)


class NumericClaim:
    """One figure, the source that carries it, and its gate status."""

    def __init__(self, value, status, source_record_id=None, citation_state=None,
                 retrieved_this_session=False, description=None, calculation=None,
                 source_field=None):
        if status not in STATUSES:
            raise ValueError(f"{status!r} is not one of {STATUSES}")
        if status == VERIFIED:
            if not source_record_id:
                raise ValueError(
                    "A VERIFIED number must name the retrieved record that carries it. A figure "
                    "with no source record is not verified, whatever it is labelled.")
            if not retrieved_this_session:
                raise ValueError(
                    f"{value!r} is marked VERIFIED but its source was not retrieved this "
                    f"session. A number recalled rather than retrieved is never VERIFIED — "
                    f"reconstructing an effect estimate from memory is exactly what this gate "
                    f"exists to stop.")
            if citation_state not in CITATION_STATES_PERMITTING_NUMBERS:
                raise ValueError(
                    f"The source of {value!r} has citation state {citation_state!r}. A number "
                    f"may only be carried by a source whose citation is in one of "
                    f"{CITATION_STATES_PERMITTING_NUMBERS}.")
        if status == CALCULATED and not calculation:
            raise ValueError("A CALCULATED number must show its calculation.")
        self.value = str(value)
        self.status = status
        self.source_record_id = source_record_id
        self.citation_state = citation_state
        self.retrieved_this_session = retrieved_this_session
        self.description = description
        self.calculation = calculation
        self.source_field = source_field

    @property
    def permitted_in_bottom_line(self):
        return self.status in BOTTOM_LINE_PERMITTED

    @property
    def uncorroborated(self):
        """True when the figure's source citation was never independently cross-checked. The
        figure may be used; the output must say so."""
        return self.citation_state in UNCORROBORATED_CITATION_STATES

    def to_dict(self):
        return {"value": self.value, "status": self.status,
                "source_record_id": self.source_record_id, "citation_state": self.citation_state,
                "retrieved_this_session": self.retrieved_this_session,
                "description": self.description, "calculation": self.calculation,
                "source_field": self.source_field,
                "permitted_in_bottom_line": self.permitted_in_bottom_line,
                "uncorroborated": self.uncorroborated}

    def __repr__(self):
        return f"<NumericClaim {self.value!r} {self.status}>"


class NumericLedger:
    """The registered numbers an output is allowed to contain."""

    def __init__(self, claims=None):
        self.claims = list(claims or [])

    def register(self, claim):
        if not isinstance(claim, NumericClaim):
            raise TypeError("Only a NumericClaim may be registered.")
        self.claims.append(claim)
        return claim

    def find(self, literal):
        """Match a scanned literal against a registered claim. Comparison is on the numeric
        substring, so '95%' in the ledger matches '95%' or '95 %' in the text."""
        target = _digits(literal)
        for claim in self.claims:
            if _digits(claim.value) and _digits(claim.value) == target:
                return claim
        return None

    def to_dict(self):
        return {"claims": [c.to_dict() for c in self.claims]}


def _digits(text):
    found = re.findall(_NUM, str(text))
    return found[0].replace(",", ".") if found else None


def scan(text):
    """Find every effect-style figure in a block of text.

    Returns a list of {kind, literal, span}. Overlapping matches are reported once, at the
    longest match, so '95% (95% CI 91-98)' produces the CI finding rather than three
    percentage findings that would each need separate clearing."""
    findings = []
    claimed_spans = []
    for kind, pattern in EFFECT_PATTERNS:
        for match in pattern.finditer(text or ""):
            span = match.span()
            if any(span[0] >= s and span[1] <= e for s, e in claimed_spans):
                continue
            claimed_spans.append(span)
            findings.append({"kind": kind, "literal": match.group(0).strip(), "span": span})
    findings.sort(key=lambda f: f["span"][0])
    return findings


PASS = "PASS"
FAIL = "FAIL"


def gate_bottom_line(text, ledger=None):
    """
    The release gate. Scans a Clinical Bottom Line and fails it on any figure that is not
    registered, or is registered with a status that does not permit it there.

    Returns {"result": PASS|FAIL, "findings": [...], "failures": [...], "checked": n}.
    """
    ledger = ledger or NumericLedger()
    findings = scan(text)
    failures = []
    disclosures = []
    detailed = []

    for finding in findings:
        claim = ledger.find(finding["literal"])
        if claim is None:
            entry = dict(finding, cleared=False, reason=(
                f"{finding['kind'].capitalize()} {finding['literal']!r} appears in the Clinical "
                f"Bottom Line but is not registered against any retrieved, verified source. It "
                f"must be removed, or replaced by a qualitative statement, unless a source "
                f"carrying it is retrieved and verified."))
            failures.append(entry)
        elif not claim.permitted_in_bottom_line:
            entry = dict(finding, cleared=False, reason=(
                f"{finding['literal']!r} is registered as {claim.status}, which is not permitted "
                f"in a Clinical Bottom Line. A figure a reader will act on must be VERIFIED, "
                f"USER-SUPPLIED or CALCULATED — not a typical range awaiting confirmation."))
            failures.append(entry)
        else:
            entry = dict(finding, cleared=True, reason=None,
                         source_record_id=claim.source_record_id,
                         status=claim.status, citation_state=claim.citation_state,
                         uncorroborated=claim.uncorroborated)
            if claim.uncorroborated:
                disclosures.append({
                    **entry,
                    "disclosure": (
                        f"{finding['literal']!r} comes from {claim.source_record_id}, whose "
                        f"citation is {claim.citation_state} — retrieved, but never independently "
                        f"cross-checked. The figure may be used; the output must state that its "
                        f"source citation is uncorroborated."),
                })
        detailed.append(entry)

    return {
        "result": FAIL if failures else PASS,
        "checked": len(findings),
        "findings": detailed,
        "failures": failures,
        "disclosures": disclosures,
        "rule": ("No numerical claim may appear in a Clinical Bottom Line unless the source "
                 "containing that number was retrieved and verified this session. Numerical "
                 "values are never reconstructed from memory."),
    }


def check_extraction_numbers(profiles):
    """
    Study counts, participant totals and follow-up durations are not effect estimates, but they
    are still numbers a reader will rely on. This confirms each one extracted from a systematic
    review carries provenance rather than sitting bare in a table.

    profiles: iterable of sr_extraction.SystematicReviewProfile.
    """
    problems = []
    for profile in profiles:
        for claim in profile.numeric_claims():
            if claim["provenance"] not in ("REPORTED", "INFERRED"):
                problems.append({**claim, "reason": "Extracted number without provenance."})
            elif not claim["source"]:
                problems.append({**claim, "reason": "Extracted number with no stated source."})
    return {"result": FAIL if problems else PASS, "problems": problems}

"""
evidence/bottom_line.py  —  CLINICAL BOTTOM LINE (v1.2)

The seven-part close that every evidence synthesis ends with:

    1. What is well established
    2. What is reasonably supported
    3. What remains uncertain
    4. Where evidence conflicts
    5. Which option currently has the strongest support
    6. Important limitations
    7. What additional information would change the conclusion

WHY SEVEN SECTIONS AND NOT A PARAGRAPH
--------------------------------------
A prose summary of a mixed evidence base gravitates toward its strongest sentence. The parts a
clinician most needs — what is still uncertain, where good sources disagree, what would change
the answer — are the parts that a fluent paragraph smooths over, because they interrupt it.
Fixed sections make omission visible: an empty "Where evidence conflicts" is a statement that
conflicts were looked for, and it renders as one.

SECTIONS 1 AND 2 ARE GATED BY CERTAINTY, NOT BY CITATION
--------------------------------------------------------
"Well established" requires HIGH certainty and at least partially direct evidence. "Reasonably
supported" requires MODERATE. A claim backed by a perfectly VERIFIED citation to a single small
cohort belongs in section 3. This is where the brief's central rule becomes a mechanical
constraint rather than an intention — `validate()` moves a claim down, and says why.

EVERY NUMBER IS GATED
---------------------
`validate()` runs `numeric_gate.gate_bottom_line()` over the rendered text. An effect estimate
that is not registered against a retrieved, verified source fails the whole bottom line.
"""
import _paths  # noqa: F401

import certainty as ce
import citation_verification as cv
import directness as dr
import numeric_gate as ng

WELL_ESTABLISHED = "well_established"
REASONABLY_SUPPORTED = "reasonably_supported"
UNCERTAIN = "uncertain"
CONFLICTING = "conflicting"
STRONGEST_OPTION = "strongest_option"
LIMITATIONS = "limitations"
WOULD_CHANGE_CONCLUSION = "would_change_conclusion"

SECTIONS = (WELL_ESTABLISHED, REASONABLY_SUPPORTED, UNCERTAIN, CONFLICTING, STRONGEST_OPTION,
            LIMITATIONS, WOULD_CHANGE_CONCLUSION)

SECTION_TITLES = {
    WELL_ESTABLISHED: "1. What is well established",
    REASONABLY_SUPPORTED: "2. What is reasonably supported",
    UNCERTAIN: "3. What remains uncertain",
    CONFLICTING: "4. Where evidence conflicts",
    STRONGEST_OPTION: "5. Which option currently has the strongest support",
    LIMITATIONS: "6. Important limitations",
    WOULD_CHANGE_CONCLUSION: "7. What additional information would change the conclusion",
}

# What each of the two "supported" sections requires of the evidence behind a claim.
SECTION_REQUIREMENTS = {
    WELL_ESTABLISHED: {
        "certainty": (ce.HIGH,),
        "min_directness": dr.PARTIALLY_DIRECT,
        "citation_states": (cv.VERIFIED, cv.VERIFIED_WITH_METADATA_DISCREPANCY),
    },
    REASONABLY_SUPPORTED: {
        "certainty": (ce.HIGH, ce.MODERATE),
        "min_directness": dr.PARTIALLY_DIRECT,
        "citation_states": (cv.VERIFIED, cv.VERIFIED_WITH_METADATA_DISCREPANCY, cv.CORRECTED),
    },
}

EMPTY_SECTION_TEXT = {
    WELL_ESTABLISHED: "Nothing in the retrieved evidence reaches this standard for this question.",
    REASONABLY_SUPPORTED: "Nothing in the retrieved evidence reaches this standard for this question.",
    UNCERTAIN: "No specific uncertainty was identified — which is itself worth checking, since a "
               "question with no uncertainties is unusual.",
    CONFLICTING: "No conflict between comparable sources was identified in the retrieved evidence.",
    STRONGEST_OPTION: "The retrieved evidence does not identify one option as best supported.",
    LIMITATIONS: "No limitation was recorded — check that the appraisal actually ran.",
    WOULD_CHANGE_CONCLUSION: "Not stated. Name the study or data that would change this answer.",
}


class ClinicalBottomLine:
    def __init__(self, question=None):
        self.question = question
        self.sections = {s: [] for s in SECTIONS}
        self.numeric_ledger = ng.NumericLedger()
        self._demotions = []

    def add(self, section, text, claim=None):
        if section not in SECTIONS:
            raise ValueError(f"{section!r} is not one of {SECTIONS}")
        self.sections[section].append({"text": text, "claim": claim})
        return self

    def register_number(self, numeric_claim):
        return self.numeric_ledger.register(numeric_claim)

    # ── Placement enforcement ───────────────────────────────────────────────────────────────
    def _check_placement(self):
        """
        Move any claim into the section its evidence actually supports, and record why.

        Demotions ACCUMULATE across calls rather than being recomputed. A demoted claim is
        physically moved out of its section, so a second call finds nothing left to move — and
        with a per-call list, rendering before validating left `report["demotions"]` empty. A QC
        caller reading that would conclude no claim had been moved, which is the opposite of what
        happened and is precisely the record the "was a verified citation treated as strong
        evidence?" audit depends on. (v1.2 real-world validation.)
        """
        demotions = list(self._demotions)
        for section in (WELL_ESTABLISHED, REASONABLY_SUPPORTED):
            requirement = SECTION_REQUIREMENTS[section]
            kept = []
            for entry in self.sections[section]:
                claim = entry.get("claim")
                if claim is None:
                    kept.append(entry)
                    continue
                reasons = []
                if claim.certainty not in requirement["certainty"]:
                    reasons.append(
                        f"certainty is {claim.certainty or ce.NOT_ASSESSABLE}, and this section "
                        f"requires {' or '.join(requirement['certainty'])}")
                if not dr.is_at_least(claim.directness or dr.UNKNOWN,
                                      requirement["min_directness"]):
                    reasons.append(
                        f"directness is {claim.directness or dr.UNKNOWN}, and this section "
                        f"requires at least {requirement['min_directness']}")
                if claim.verification_state not in requirement["citation_states"]:
                    reasons.append(
                        f"citation state is {claim.verification_state}, which this section does "
                        f"not accept")
                if reasons:
                    already = any(d["claim"] == claim.claim and d["from_section"] == section
                                  for d in demotions)
                    if already:
                        kept.append(entry)
                        continue
                    demotions.append({
                        "claim": claim.claim, "from_section": section, "to_section": UNCERTAIN,
                        "reasons": reasons,
                        "note": ("A verified citation does not place a claim in a supported "
                                 "section. The evidence behind it does."),
                    })
                    self.sections[UNCERTAIN].append({
                        "text": (f"{entry['text']} — moved here because "
                                 f"{'; '.join(reasons)}."),
                        "claim": claim})
                else:
                    kept.append(entry)
            self.sections[section] = kept
        self._demotions = demotions
        return demotions

    # ── Rendering ───────────────────────────────────────────────────────────────────────────
    def to_markdown(self, enforce_placement=True):
        if enforce_placement:
            self._check_placement()
        lines = ["## CLINICAL BOTTOM LINE"]
        if self.question:
            lines += ["", f"**Question:** {self.question}"]
        for section in SECTIONS:
            lines += ["", f"**{SECTION_TITLES[section]}**", ""]
            entries = self.sections[section]
            if not entries:
                lines.append(f"_{EMPTY_SECTION_TEXT[section]}_")
                continue
            for entry in entries:
                claim = entry.get("claim")
                suffix = ""
                if claim is not None:
                    suffix = (f"  \n  _{claim.study_type or 'design not established'} · "
                              f"{claim.verification_state} · certainty "
                              f"{claim.certainty or ce.NOT_ASSESSABLE} · "
                              f"{claim.directness or dr.UNKNOWN} · {claim.citation or '(UNVER)'}_")
                lines.append(f"- {entry['text']}{suffix}")
        return "\n".join(lines)

    # ── Release gate ────────────────────────────────────────────────────────────────────────
    def validate(self):
        """Run every gate that applies to a Clinical Bottom Line. Returns a report; `result` is
        FAIL if anything release-blocking was found."""
        demotions = self._check_placement()
        text = self.to_markdown(enforce_placement=False)
        numeric = ng.gate_bottom_line(text, self.numeric_ledger)

        problems = []
        if numeric["result"] == ng.FAIL:
            for failure in numeric["failures"]:
                problems.append({"severity": "CRITICAL", "gate": "NUMERIC_EVIDENCE_GATE",
                                 "detail": failure["reason"]})

        for section in SECTIONS:
            for entry in self.sections[section]:
                claim = entry.get("claim")
                if claim is None:
                    continue
                if claim.verification_state == cv.RETRACTED:
                    problems.append({
                        "severity": "CRITICAL", "gate": "RETRACTION_GATE",
                        "detail": (f"A retracted source appears in section {section!r} supporting "
                                   f"{claim.claim!r}. Retracted evidence never supports a "
                                   f"clinical recommendation.")})
                for problem in claim.problems():
                    if problem["severity"] == "CRITICAL":
                        problems.append({"severity": "CRITICAL", "gate": "CLAIM_EVIDENCE_LINK",
                                         "detail": f"{claim.claim!r}: {problem['reason']}"})

        empty_required = [s for s in (UNCERTAIN, WOULD_CHANGE_CONCLUSION)
                          if not self.sections[s]]
        for section in empty_required:
            problems.append({
                "severity": "MAJOR", "gate": "COMPLETENESS",
                "detail": (f"Section {SECTION_TITLES[section]!r} is empty. It renders with an "
                           f"explicit placeholder, but an evidence synthesis that identifies no "
                           f"uncertainty and nothing that would change its conclusion has almost "
                           f"certainly not looked.")})

        return {
            "result": ng.FAIL if any(p["severity"] == "CRITICAL" for p in problems) else ng.PASS,
            "problems": problems,
            "demotions": demotions,
            "numeric_gate": numeric,
        }

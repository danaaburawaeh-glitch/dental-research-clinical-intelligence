"""
evidence/output_modes.py  —  USER OUTPUT MODES (v1.2)

Five modes, each with a section contract that `validate()` checks against a produced output.

    QUICK EVIDENCE ANSWER       one question, a short answer, and the caveats that would change
                                what the reader does. Stays short.
    FULL EVIDENCE REVIEW        search methods, evidence table, appraisal, certainty, conflicts,
                                synthesis, limitations. Exposes its own working.
    SYSTEMATIC REVIEW SUMMARY   one review, read structurally — what it pooled, how, and what it
                                found, with everything it does not report marked as such.
    TREATMENT OPTION COMPARISON several options side by side, each with its own evidence, and no
                                option left without one.
    LECTURE / RESEARCH MODE     teaching or manuscript use: the evidence base, its gaps, and what
                                is worth investigating.

WHAT A MODE DOES AND DOES NOT CHANGE
------------------------------------
A mode changes how much is shown. It never changes what is true. QUICK is shorter than FULL
because it omits the working, not because it lowers a gate — the same certainty, directness,
citation and numeric rules apply to every mode, and `REQUIRED_GATES` is identical across all five.

That matters because "quick" is exactly where a system is tempted to relax: the caveat costs a
line, the reader wants an answer, and one unqualified sentence is faster. QUICK's contract
therefore keeps certainty and directness mandatory and only makes the evidence table optional.
"""
import _paths  # noqa: F401

QUICK = "QUICK EVIDENCE ANSWER"
FULL = "FULL EVIDENCE REVIEW"
SR_SUMMARY = "SYSTEMATIC REVIEW SUMMARY"
OPTION_COMPARISON = "TREATMENT OPTION COMPARISON"
LECTURE = "LECTURE / RESEARCH MODE"

MODES = (QUICK, FULL, SR_SUMMARY, OPTION_COMPARISON, LECTURE)

# Section identifiers used by the contracts below.
ANSWER = "answer"
CERTAINTY = "certainty"
DIRECTNESS = "directness"
CITATION_STATUS = "citation_status"
MATERIAL_CAVEAT = "material_caveat"
SEARCH_STRATEGY = "search_strategy"
SEARCH_LOG = "search_log"
EVIDENCE_TABLE = "evidence_table"
APPRAISAL = "appraisal"
SR_PROFILE = "sr_profile"
CONFLICTS = "conflicts"
SYNTHESIS_BUCKETS = "synthesis_buckets"
BOTTOM_LINE = "bottom_line"
LIMITATIONS = "limitations"
OPTIONS = "options"
EVIDENCE_GAPS = "evidence_gaps"
RESEARCH_DIRECTIONS = "research_directions"
APPLICABILITY = "applicability"

# Gates that run regardless of mode. Identical for all five, deliberately.
REQUIRED_GATES = ("retraction_gate", "citation_verification", "numeric_evidence_gate",
                  "claim_evidence_link", "laboratory_firewall", "registry_evidence_gate")

MODE_CONTRACTS = {
    QUICK: {
        "required": (ANSWER, CERTAINTY, DIRECTNESS, CITATION_STATUS),
        "optional": (MATERIAL_CAVEAT, SEARCH_STRATEGY),
        "forbidden": (),
        "max_words": 200,
        "note": ("Concise by contract. Certainty, directness and citation status stay mandatory: "
                 "brevity is achieved by omitting the working, never by dropping the "
                 "qualifications that tell the reader how far to trust the answer."),
    },
    FULL: {
        "required": (ANSWER, SEARCH_LOG, EVIDENCE_TABLE, APPRAISAL, CERTAINTY, DIRECTNESS,
                     SYNTHESIS_BUCKETS, CONFLICTS, BOTTOM_LINE, LIMITATIONS, APPLICABILITY),
        "optional": (SR_PROFILE, EVIDENCE_GAPS),
        "forbidden": (),
        "max_words": None,
        "note": ("Exposes methodology and limitations in full — the search actually run, the "
                 "appraisal actually performed, and what could not be established."),
    },
    SR_SUMMARY: {
        "required": (ANSWER, SR_PROFILE, CERTAINTY, DIRECTNESS, CITATION_STATUS, LIMITATIONS),
        "optional": (EVIDENCE_TABLE, CONFLICTS, BOTTOM_LINE),
        "forbidden": (),
        "max_words": None,
        "note": ("Every field the review does not report is shown as NOT REPORTED or NOT "
                 "AVAILABLE. A tidy summary with no gaps means the gaps were filled in."),
    },
    OPTION_COMPARISON: {
        "required": (OPTIONS, EVIDENCE_TABLE, CERTAINTY, DIRECTNESS, CONFLICTS, BOTTOM_LINE,
                     LIMITATIONS, APPLICABILITY),
        "optional": (SEARCH_LOG, APPRAISAL),
        "forbidden": (),
        "max_words": None,
        "note": ("Each option carries its own evidence and its own certainty. An option with no "
                 "retrieved evidence is shown as having none — never given the neighbouring "
                 "option's support by proximity."),
    },
    LECTURE: {
        "required": (ANSWER, SEARCH_LOG, EVIDENCE_TABLE, SYNTHESIS_BUCKETS, EVIDENCE_GAPS,
                     LIMITATIONS),
        "optional": (RESEARCH_DIRECTIONS, CONFLICTS, BOTTOM_LINE, APPRAISAL),
        "forbidden": (),
        "max_words": None,
        "note": ("Teaching and manuscript use. Gaps are a required section, not an afterthought "
                 "— what the field does not know is the part a lecture most often omits."),
    },
}

PASS = "PASS"
FAIL = "FAIL"


def contract(mode):
    if mode not in MODE_CONTRACTS:
        raise ValueError(f"{mode!r} is not one of {MODES}")
    return MODE_CONTRACTS[mode]


def select(task, question_scope="single", full_text_available=False, options=None,
           audience="clinician"):
    """
    Route to the smallest sufficient mode.

    task: "answer" | "review" | "summarise_review" | "compare" | "teach"
    Returns a mode. The routing is deliberately boring — the interesting judgement is whether the
    question is really as small as it looks, and that belongs to the person asking, not here.
    """
    if task == "compare" or (options and len(options) > 1):
        return OPTION_COMPARISON
    if task == "summarise_review":
        return SR_SUMMARY
    if task == "teach" or audience in ("student", "researcher", "audience"):
        return LECTURE
    if task == "review" or question_scope == "broad":
        return FULL
    return QUICK


def validate(mode, sections_present, word_count=None, gates_run=None):
    """
    sections_present: iterable of section identifiers actually produced.
    gates_run: iterable of gate names actually executed.

    Returns {"result", "missing_sections", "missing_gates", "problems"}.
    """
    spec = contract(mode)
    present = set(sections_present or ())
    missing = [s for s in spec["required"] if s not in present]
    forbidden_present = [s for s in spec["forbidden"] if s in present]

    gates = set(gates_run or ())
    missing_gates = [g for g in REQUIRED_GATES if g not in gates]

    problems = []
    for section in missing:
        problems.append({"severity": "MAJOR", "issue": "MISSING_SECTION", "section": section,
                         "detail": f"{mode} requires a {section!r} section."})
    for section in forbidden_present:
        problems.append({"severity": "MAJOR", "issue": "FORBIDDEN_SECTION", "section": section,
                         "detail": f"{mode} must not include {section!r}."})
    for gate in missing_gates:
        problems.append({"severity": "CRITICAL", "issue": "GATE_NOT_RUN", "gate": gate,
                         "detail": (f"{gate} did not run. Every gate applies to every mode — a "
                                    f"shorter output is not a less-checked one.")})
    if spec["max_words"] and word_count and word_count > spec["max_words"]:
        problems.append({"severity": "WARNING", "issue": "OVER_LENGTH",
                         "detail": (f"{mode} ran to {word_count} words against a {spec['max_words']}-word "
                                    f"contract. If the answer genuinely needs more, the question "
                                    f"needed a fuller mode.")})

    return {
        "result": FAIL if any(p["severity"] == "CRITICAL" for p in problems) else (
            FAIL if missing else PASS),
        "mode": mode,
        "missing_sections": missing,
        "missing_gates": missing_gates,
        "problems": problems,
    }

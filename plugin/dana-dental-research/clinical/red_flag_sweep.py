"""
clinical/red_flag_sweep.py

M2 V0.4 §7 — the red-flag sweep, as an executable checklist rather than a paragraph.

All 14 flags are migrated verbatim in meaning. The module carries no threshold, dose or interval:
M2 §7 states none, and inventing one here would be exactly the failure the whole system is built
to avoid. Each flag is a QUESTION the clinician answers, not a value this code evaluates.

The design rule that makes it worth being code: **silence is not clearance.** A flag that was
never considered is not a flag that was cleared, and the sweep refuses to report "all clear"
unless every flag was explicitly answered.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

PRESENT = "PRESENT"
ABSENT = "ABSENT"
NOT_ASSESSED = "NOT_ASSESSED"

RESPONSES = (PRESENT, ABSENT, NOT_ASSESSED)


@dataclass(frozen=True)
class RedFlag:
    key: str
    description: str
    why: str


# M2 §7, in order.
RED_FLAGS = (
    RedFlag("spreading_swelling",
            "Spreading swelling — facial, submandibular, floor of mouth, periorbital",
            "Airway and deep-space infection risk"),
    RedFlag("trismus_dysphagia",
            "Trismus with dysphagia, drooling, voice change, or fever",
            "Deep-space infection with airway involvement"),
    RedFlag("airway_concern", "Airway concern", "Immediately life-threatening"),
    RedFlag("uncontrolled_bleeding",
            "Uncontrolled bleeding, or any bleeding risk on anticoagulant/antiplatelet therapy",
            "Haemorrhage risk; M2 §3.1"),
    RedFlag("anaphylaxis_or_la_toxicity",
            "Suspected anaphylaxis or local-anaesthetic toxicity",
            "Immediately life-threatening; M2 §3.9 / §4.3"),
    RedFlag("persistent_oral_lesion",
            "Oral lesion persisting without explanation beyond ~2-3 weeks, or any suspicious lesion",
            "Malignancy — referral is time-critical"),
    RedFlag("unexplained_paraesthesia",
            "Unexplained paraesthesia or anaesthesia, including numb-chin sign",
            "May indicate malignancy or nerve involvement"),
    RedFlag("exposed_bone_mronj_ornj",
            "Exposed bone, non-healing socket, or bone pain in an antiresorptive/antiangiogenic "
            "or irradiated patient",
            "MRONJ / osteoradionecrosis; M2 §3.2 / §3.6"),
    RedFlag("time_critical_trauma",
            "Avulsed permanent tooth or other time-critical trauma",
            "Outcome depends on time elapsed"),
    RedFlag("possible_cardiac_pain",
            "Jaw/dental pain with features suggesting cardiac origin",
            "Referred cardiac pain; M2 §3.4"),
    RedFlag("acute_medical_event",
            "Hypoglycaemia, syncope, seizure, altered consciousness",
            "Acute medical emergency; M2 §3.3 / §3.10"),
    RedFlag("serious_drug_interaction",
            "Serious drug interaction identified",
            "M2 §4.5 interaction screen"),
    RedFlag("rapidly_progressive",
            "Rapidly progressive symptoms of any kind",
            "Trajectory matters more than the current severity"),
    RedFlag("safeguarding",
            "Safeguarding concern (paediatric or vulnerable adult) — including injury "
            "inconsistent with the history",
            "Duty of protection overrides the dental question"),
)

RED_FLAG_KEYS = tuple(f.key for f in RED_FLAGS)
_BY_KEY = {f.key: f for f in RED_FLAGS}

CLEAR_WORDING = ("Red-flag sweep: no flags identified from the information provided.")

BLOCK_HEADER = "⚠ CLINICAL RED FLAG"


def sweep(responses: Optional[Dict[str, str]] = None, notes: Optional[Dict[str, str]] = None):
    """
    Run the sweep.

    `responses` maps flag key -> PRESENT / ABSENT / NOT_ASSESSED. Any flag omitted is treated as
    NOT_ASSESSED — never as ABSENT. That asymmetry is the point: not having looked is not the same
    as having looked and found nothing.

    Returns a dict with:
      status        — "RED_FLAG" | "CLEAR" | "INCOMPLETE_SWEEP"
      present       — flags raised
      not_assessed  — flags never answered
      block         — the ⚠ block to place at the TOP of the response (M2 §7 / CORE §15), or None
      statement     — the exact clear wording when genuinely clear
      what_would_change_it — required by M2 §7 whenever reporting clear
    """
    responses = dict(responses or {})
    notes = dict(notes or {})

    unknown_keys = [k for k in responses if k not in _BY_KEY]
    if unknown_keys:
        raise ValueError(f"Unknown red-flag key(s): {unknown_keys}. The M2 §7 list is fixed.")
    bad = {k: v for k, v in responses.items() if v not in RESPONSES}
    if bad:
        raise ValueError(f"Invalid response(s) {bad}. Must be one of {RESPONSES}.")

    present, not_assessed = [], []
    for f in RED_FLAGS:
        r = responses.get(f.key, NOT_ASSESSED)
        if r == PRESENT:
            present.append({"key": f.key, "description": f.description, "why": f.why,
                            "note": notes.get(f.key)})
        elif r == NOT_ASSESSED:
            not_assessed.append({"key": f.key, "description": f.description})

    if present:
        lines = [BLOCK_HEADER] + [f"- {p['description']}" + (f" — {p['note']}" if p["note"] else "")
                                   for p in present]
        if not_assessed:
            lines.append(f"({len(not_assessed)} further flag(s) not assessed.)")
        return {
            "status": "RED_FLAG",
            "present": present,
            "not_assessed": not_assessed,
            "block": "\n".join(lines),
            "statement": None,
            "what_would_change_it": None,
            "placement": "TOP of the response, before anything else (CORE §15).",
        }

    if not_assessed:
        return {
            "status": "INCOMPLETE_SWEEP",
            "present": [],
            "not_assessed": not_assessed,
            "block": None,
            "statement": None,
            "what_would_change_it": [f["description"] for f in not_assessed],
            "note": ("The sweep is incomplete, so it cannot be reported as clear. Silence is not "
                     "clearance — each flag must be explicitly answered."),
        }

    return {
        "status": "CLEAR",
        "present": [],
        "not_assessed": [],
        "block": None,
        "statement": CLEAR_WORDING,
        "what_would_change_it": [
            "Any new or worsening swelling, trismus, dysphagia, voice change or fever.",
            "Any bleeding that does not settle with local measures, or a newly disclosed "
            "anticoagulant/antiplatelet.",
            "Any newly disclosed antiresorptive, antiangiogenic or radiotherapy history.",
            "Any lesion still present at review, or any new paraesthesia.",
            "Any rapid change in trajectory since this information was gathered.",
        ],
    }


def sweep_from_case(case, responses=None, notes=None):
    """
    Convenience wrapper. Deliberately does NOT infer flag answers from the case record — inferring
    ABSENT from an incomplete history is precisely the failure mode this module exists to prevent.
    The case is used only to carry the reference into the result.
    """
    result = sweep(responses, notes)
    result["case_ref"] = getattr(case, "case_ref", None)
    return result

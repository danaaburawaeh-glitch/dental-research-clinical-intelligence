"""
clinical/safety_veto.py

The veto in the output path. Every clinical output passes through `review()` before it reaches
the user.

Architecture reused (concept, not code) from dana-clinical-core:
  - SAFETY_BLOCK is non-overridable. No component, and no later assembly step, may turn it into
    anything else. The only exit is a full stop and human referral.
  - safety status and execution status may not contradict each other.
  - Rule of Conservative Conflict: where two readings are defensible, the more conservative wins.

Why this is one veto and not six assistants: v1.0 is a single plugin. The value of the
architecture is the non-overridable block, not the message bus around it.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from case_state import CaseState, INSUFFICIENT, OUT_OF_SCOPE, UNKNOWN
import red_flag_sweep as rfs
import identity_policy as idp

# Statuses. Deliberately the same vocabulary as the connector layer where they overlap.
OK = "OK"
SAFETY_BLOCK = "SAFETY_BLOCK"
BLOCKED = "BLOCKED"
NEEDS_INPUT = "NEEDS_INPUT"

# Flags recorded alongside a block, so the reason is machine-readable, not only prose.
FLAG_RED_FLAG = "RED_FLAG"
FLAG_INCOMPLETE_SWEEP = "INCOMPLETE_SWEEP"
FLAG_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
FLAG_PROGNOSIS_BLOCKED = "PROGNOSIS_UNDETERMINED"
FLAG_OUT_OF_SCOPE = "OUT_OF_SCOPE"
FLAG_UNVERIFIED_REGULATORY = "UNVERIFIED_REGULATORY_CLAIM"
FLAG_UNVERIFIED_CLAIM = "UNVERIFIED_CLAIM"
FLAG_PATIENT_IDENTIFIERS = "PATIENT_IDENTIFIERS"
FLAG_PROGNOSIS_UNDETERMINED = "PROGNOSIS_UNDETERMINED_BLOCKS_PLANNING"
FLAG_IDENTITY_POLICY = "IDENTITY_POLICY_VIOLATION"

NON_OVERRIDABLE_NOTE = (
    "SAFETY_BLOCK is not overridable. No downstream step, and no repetition or reassurance from "
    "the requester, converts it to another status. The only path past it is to resolve the stated "
    "cause, or to stop and refer to a human clinician."
)

CONSERVATIVE_CONFLICT_RULE = (
    "Where two readings of the same situation are both defensible, the more conservative one is "
    "taken. A tie is resolved toward not acting, not toward acting."
)

# Acts that require the data to actually support them. Ordered by how much they demand.
ACT_INFORMATION = "information"          # explanation, education
ACT_PLAN_PROVISIONAL = "provisional_plan"
ACT_PLAN_DEFINITIVE = "definitive_plan"
ACT_IRREVERSIBLE = "irreversible_treatment"
ACT_PRESCRIBING = "prescribing_support"


@dataclass
class VetoResult:
    status: str
    flags: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    required_before_proceeding: List[str] = field(default_factory=list)
    block_text: Optional[str] = None
    overridable: bool = False
    note: str = ""

    def to_dict(self):
        d = asdict(self)
        d["non_overridable_note"] = NON_OVERRIDABLE_NOTE
        return d


def review(case: CaseState,
           requested_act: str = ACT_PLAN_DEFINITIVE,
           sweep_result: Optional[Dict[str, Any]] = None,
           plan_result: Optional[Dict[str, Any]] = None,
           prognosis_result: Optional[Dict[str, Any]] = None,
           regulatory_states: Optional[List[str]] = None,
           unverified_claims: Optional[List[str]] = None,
           contains_identifiers: bool = False,
           draft_output: Optional[str] = None,
           output_context: str = idp.CONTEXT_CLINICAL):
    """
    The single gate. Returns a VetoResult.

    A SAFETY_BLOCK from any one check cannot be traded off against a clean result elsewhere —
    the checks are not scored, they are all binding.
    """
    flags: List[str] = []
    reasons: List[str] = []
    required: List[str] = []
    hard_block = False

    # --- 1. Scope -------------------------------------------------------
    if not case.in_scope():
        flags.append(FLAG_OUT_OF_SCOPE)
        reasons.append(
            f"Discipline {case.discipline!r} is outside v1.0 scope (Fixed Prosthodontics and "
            "Esthetic Restorative Dentistry).")
        required.append("Refer to a clinician or system covering this discipline.")
        # Out of scope is BLOCKED, not SAFETY_BLOCK — it is a competence boundary, not a hazard.
        return VetoResult(status=BLOCKED, flags=flags, reasons=reasons,
                          required_before_proceeding=required,
                          note="Out of scope. Answering less well is not the safer option.")

    # --- 2. Red flags ---------------------------------------------------
    if sweep_result is None:
        sweep_result = rfs.sweep()          # nothing answered -> INCOMPLETE_SWEEP
    if sweep_result.get("status") == "RED_FLAG":
        hard_block = True
        flags.append(FLAG_RED_FLAG)
        reasons.append("Red flag(s) present — clinical escalation takes precedence over the "
                       "requested output (CORE §15, M2 §7).")
        required.append("Address or escalate the red flag(s) before any planning output.")
    elif sweep_result.get("status") == "INCOMPLETE_SWEEP":
        # Not a hazard in itself, but it cannot be reported as clear, and an unswept case may not
        # proceed to anything irreversible.
        flags.append(FLAG_INCOMPLETE_SWEEP)
        reasons.append(f"Red-flag sweep incomplete — {len(sweep_result.get('not_assessed', []))} "
                       "flag(s) never assessed. Silence is not clearance.")
        required.append("Complete the M2 §7 sweep explicitly.")
        if requested_act in (ACT_PLAN_DEFINITIVE, ACT_IRREVERSIBLE, ACT_PRESCRIBING):
            hard_block = True

    # --- 3. Data sufficiency vs the act being requested ------------------
    suff = case.sufficiency()
    if suff["verdict"] == INSUFFICIENT:
        flags.append(FLAG_INSUFFICIENT_DATA)
        reasons.append(f"Data sufficiency is INSUFFICIENT — {suff['reason']}")
        required.extend([f"Obtain: {m['item']}" for m in suff["missing"][:8]])
        if requested_act in (ACT_PLAN_DEFINITIVE, ACT_IRREVERSIBLE, ACT_PRESCRIBING):
            hard_block = True

    # --- 4. Prescribing pre-check (M1 RX §1 / M2 §4.1) -------------------
    if requested_act == ACT_PRESCRIBING:
        precheck = ("allergies", "medications", "medical_history", "pregnancy_lactation_status")
        unknown = [k for k in precheck if not case.known(k)]
        if unknown:
            hard_block = True
            flags.append(FLAG_INSUFFICIENT_DATA)
            reasons.append(
                "Prescribing pre-check ledger has [Unknown] items "
                f"({', '.join(unknown)}). Any [Unknown] makes the case INSUFFICIENT for "
                "prescribing support (M1 RX §1, M2 §4.1).")
            required.append("Complete the pre-check ledger before any prescribing support.")

    # --- 5. Prognosis before prosthesis ---------------------------------
    if plan_result and plan_result.get("blocking"):
        prognosis_hits = [b for b in plan_result["blocking"]
                          if b.get("rule") == "prognosis_before_prosthesis"]
        if prognosis_hits:
            hard_block = True
            flags.append(FLAG_PROGNOSIS_BLOCKED)
            for b in prognosis_hits:
                reasons.append(b["detail"])
            required.append("Determine prognosis before planning restorative treatment.")
        other = [b for b in plan_result["blocking"] if b not in prognosis_hits]
        for b in other:
            reasons.append(b["detail"])
            if b.get("rule") in ("sequencing", "failure_planning", "reversible_test_phase"):
                hard_block = True

    # --- 5b. Prognosis gate (v0.8.0) ------------------------------------
    # An UNDETERMINED prognosis blocks definitive irreversible planning. This is the executable
    # form of CORE §2 "prognosis before prosthesis": without the block, the principle is advice.
    if prognosis_result and prognosis_result.get("blocks_irreversible_planning"):
        if requested_act in (ACT_PLAN_DEFINITIVE, ACT_IRREVERSIBLE):
            hard_block = True
            flags.append(FLAG_PROGNOSIS_UNDETERMINED)
            reasons.append(prognosis_result.get("block_reason")
                           or "Prognosis is UNDETERMINED; definitive irreversible planning is blocked.")
            for m in (prognosis_result.get("missing_determinants") or [])[:8]:
                required.append(f"Establish determinant: {m}")

    # --- 6. Saudi regulatory claims (v0.6.0 layer) ----------------------
    for state in (regulatory_states or []):
        if state and state.strip().upper() != "VERIFIED":
            flags.append(FLAG_UNVERIFIED_REGULATORY)
            reasons.append(
                f"A Saudi regulatory claim is in state '{state}'. It may be reported with that "
                "state attached, but must not be presented as established Saudi status.")
            required.append("Attach the regulatory state to the claim, or remove the claim.")
            break

    # --- 7. Unverified clinical claims ----------------------------------
    if unverified_claims:
        flags.append(FLAG_UNVERIFIED_CLAIM)
        reasons.append(f"{len(unverified_claims)} claim(s) are unverified and must carry (UNVER) "
                       "with a runnable search strategy, never a fabricated citation.")

    # --- 8. Patient identifiers (v0.6.0 PDPL layer) ---------------------
    if contains_identifiers:
        hard_block = True
        flags.append(FLAG_PATIENT_IDENTIFIERS)
        reasons.append("Output carries patient identifiers. Minimise and de-identify before "
                       "anything leaves the clinical setting (PDPL layer).")
        required.append("Remove identifiers; use a de-identified case reference.")

    # --- 9. Identity & citation policy (v0.9.1) -------------------------
    # §7 global output check. Presenting the assistant's creator as a clinical, scientific or
    # regulatory source is a source-fabrication defect, not a style issue: it dresses a personal
    # preference as evidence. Blocking, not advisory.
    if draft_output:
        ident = idp.scan(draft_output, output_context)
        if not ident["ok"]:
            hard_block = True
            flags.append(FLAG_IDENTITY_POLICY)
            for v in ident["violations"][:4]:
                reasons.append(f"Identity policy: {v['matched_text']!r} — {v['reason']}")
                required.append(v["remedy"])

    # --- Verdict --------------------------------------------------------
    if hard_block:
        block_text = "\n".join([f"{rfs.BLOCK_HEADER} — OUTPUT BLOCKED"] +
                                [f"- {r}" for r in reasons] +
                                ["", "Required before proceeding:"] +
                                [f"- {r}" for r in dict.fromkeys(required)])
        return VetoResult(status=SAFETY_BLOCK, flags=list(dict.fromkeys(flags)), reasons=reasons,
                          required_before_proceeding=list(dict.fromkeys(required)),
                          block_text=block_text, overridable=False,
                          note=NON_OVERRIDABLE_NOTE)

    if flags:
        return VetoResult(status=NEEDS_INPUT if required else OK,
                          flags=list(dict.fromkeys(flags)), reasons=reasons,
                          required_before_proceeding=list(dict.fromkeys(required)),
                          overridable=False,
                          note=CONSERVATIVE_CONFLICT_RULE)

    return VetoResult(status=OK, note=CONSERVATIVE_CONFLICT_RULE)


def assert_consistent(safety_status: str, execution_status: str):
    """
    Reused from dana-clinical-core's handoff validation: safety.status == SAFETY_BLOCK requires
    execution.status == SAFETY_BLOCK. A contradiction between the two is how a block gets lost.
    """
    if safety_status == SAFETY_BLOCK and execution_status != SAFETY_BLOCK:
        raise ValueError(
            f"Inconsistent statuses: safety={safety_status} but execution={execution_status}. "
            "A SAFETY_BLOCK may not be reported as anything else.")
    return True

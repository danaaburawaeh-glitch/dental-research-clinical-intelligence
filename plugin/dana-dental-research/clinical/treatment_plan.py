"""
clinical/treatment_plan.py

M1 V0.4 §12 — the phased treatment plan, as a generated structure rather than a remembered format.

Phases 0-4 with the re-evaluation gate between Phase 1 and Phase 2. The module supplies the
SHAPE and enforces the SEQUENCING RULES; the clinical content of each phase is supplied by the
clinician or by a reasoning step above it. No procedure, interval, threshold or material is
invented here.

The three rules it enforces, all from M1/M2/CORE rather than invented:
  1. Prognosis before prosthesis — a tooth with PROGNOSIS UNDETERMINED cannot carry restorative
     planning (M2 §5, CORE §2).
  2. Nothing irreversible before its prerequisite is resolved (M1 AUDIT §5).
  3. Alternatives always include "no treatment" and "monitor/defer" (M1 §13, CORE §8).
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

from case_state import (
    CaseState, SUFFICIENT, PARTIALLY_SUFFICIENT, INSUFFICIENT, OUT_OF_SCOPE,
)

# Irreversibility tiers — the plugin already ships irreversibility-tiers.md; these are the tier
# labels only, used for gating. T3/T4 require the full failure-planning set (M2 §6).
# CORRECTED in v0.8.0. Phase D omitted T0 and labelled T1 "fully reversible", which contradicted
# CORE §7 and the plugin's own irreversibility-tiers.md. The tiers below now match both exactly.
TIER_T0 = "T0"  # fully reversible — observation, hygiene, fluoride, whitening, removable appliance
TIER_T1 = "T1"  # additive / minimally invasive, no irreversible reduction — sealant, resin
                # infiltration, bonded composite, genuine no-prep ceramic
TIER_T2 = "T2"  # limited irreversible reduction — partial coverage, minimal-prep veneer, onlay
TIER_T3 = "T3"  # substantial reduction — full crown, endodontic, extraction, implant, perio surgery
TIER_T4 = "T4"  # arch-level irreversible reconstruction, OVD alteration, elective devitalisation
ALL_TIERS = (TIER_T0, TIER_T1, TIER_T2, TIER_T3, TIER_T4)
IRREVERSIBLE_TIERS = (TIER_T3, TIER_T4)
# T2 is irreversible too — limited, but tooth structure does not grow back. It does not carry the
# full T3/T4 failure-planning requirement, but it is never described as reversible.
REDUCTIVE_TIERS = (TIER_T2, TIER_T3, TIER_T4)

PHASE_0 = "Phase 0 — Emergency"
PHASE_1 = "Phase 1 — Stabilisation & control"
REEVAL = "Re-evaluation"
PHASE_2 = "Phase 2 — Reversible test phase"
PHASE_3 = "Phase 3 — Definitive"
PHASE_4 = "Phase 4 — Maintenance"

PHASE_ORDER = (PHASE_0, PHASE_1, REEVAL, PHASE_2, PHASE_3, PHASE_4)

PHASE_PURPOSE = {
    PHASE_0: "Relieve pain/infection",
    PHASE_1: ("Disease control, caries risk, perio therapy, provisional restoration, "
              "habit control"),
    REEVAL: "Defined interval; defined re-entry criteria",
    PHASE_2: ("Wax-up, mock-up, provisionals, appliance, OVD trial, phonetic and functional "
              "verification"),
    PHASE_3: "Irreversible treatment, tiered per CORE §7",
    PHASE_4: "Recall interval, home care, monitoring parameters",
}

# The esthetic sub-protocol (M1 ESTHETIC §4) makes Phase 2 mandatory before any T2+ esthetic work.
REVERSIBLE_TEST_MANDATORY_NOTE = (
    "A reversible test phase (diagnostic wax-up and intraoral mock-up, patient approval "
    "documented) is mandatory before any preparation for an elective esthetic result — M1 "
    "ESTHETIC §4. It is not an optional refinement."
)


@dataclass
class PlannedItem:
    """One proposed intervention."""
    description: str
    phase: str
    tier: str = TIER_T0
    teeth: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)   # phases that must complete first
    # M2 §6 — required for T3/T4
    expected_service_life: Optional[str] = None
    failure_mode: Optional[str] = None
    early_warning_signs: Optional[str] = None
    retreatability: Optional[str] = None
    maintenance_obligation: Optional[str] = None
    cost_of_being_wrong: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def failure_planning_gaps(self):
        if self.tier not in IRREVERSIBLE_TIERS:
            return []
        required = ("expected_service_life", "failure_mode", "early_warning_signs",
                    "retreatability", "maintenance_obligation", "cost_of_being_wrong")
        return [f for f in required if not getattr(self, f)]


@dataclass
class Alternative:
    option: str
    rationale: str
    tier: str = TIER_T0


NO_TREATMENT = "No treatment"
MONITOR_DEFER = "Monitor / defer"


def build_plan(case: CaseState, items: List[PlannedItem],
               alternatives: Optional[List[Alternative]] = None,
               objectives: Optional[List[str]] = None,
               esthetic_elective: bool = False):
    """
    Assemble the phased plan and run the sequencing gates.

    Returns a dict with the phase table, the blocking issues, and a `blocked` flag. It does NOT
    silently drop an offending item — it reports it, so the clinician sees what was wrong rather
    than a quietly shortened plan.
    """
    alternatives = list(alternatives or [])
    blocking: List[Dict[str, Any]] = []
    warnings: List[str] = []

    # ---- Gate 0: scope and sufficiency -----------------------------------
    suff = case.sufficiency()
    if suff["verdict"] == OUT_OF_SCOPE:
        return {"blocked": True, "phases": {}, "blocking": [
            {"rule": "scope", "detail": suff["reason"]}], "sufficiency": suff}
    if suff["verdict"] == INSUFFICIENT:
        blocking.append({
            "rule": "data_sufficiency",
            "detail": (f"Data is INSUFFICIENT — {suff['reason']} A definitive plan cannot be "
                       "issued on this dataset."),
            "missing": suff["missing"][:10],
        })
    elif suff["verdict"] == PARTIALLY_SUFFICIENT:
        warnings.append(f"Data is PARTIALLY SUFFICIENT — {suff['reason']} "
                        "Definitive (Phase 3) items are provisional until the gaps are closed.")

    # ---- Gate 1: prognosis before prosthesis ------------------------------
    undetermined = set(case.prognosis_undetermined_teeth())
    for item in items:
        if item.phase == PHASE_3 and item.tier in IRREVERSIBLE_TIERS:
            hit = sorted(set(item.teeth) & undetermined)
            if hit:
                blocking.append({
                    "rule": "prognosis_before_prosthesis",
                    "detail": (f"'{item.description}' plans irreversible restorative treatment on "
                               f"tooth/teeth {', '.join(hit)} marked PROGNOSIS UNDETERMINED. "
                               "Restorative planning on an undetermined prognosis is blocked "
                               "(M2 §5, CORE §2)."),
                    "teeth": hit,
                })

    # ---- Gate 2: irreversible before prerequisite -------------------------
    for item in items:
        if item.tier not in IRREVERSIBLE_TIERS:
            continue
        for prereq in item.prerequisites:
            if PHASE_ORDER.index(prereq) >= PHASE_ORDER.index(item.phase):
                blocking.append({
                    "rule": "sequencing",
                    "detail": (f"'{item.description}' is irreversible ({item.tier}) and scheduled "
                               f"in {item.phase}, at or before its prerequisite {prereq}."),
                })

    # ---- Gate 3: reversible test phase for elective esthetic --------------
    if esthetic_elective:
        has_phase2 = any(i.phase == PHASE_2 for i in items)
        irreversible_esthetic = [i for i in items
                                 if i.tier in IRREVERSIBLE_TIERS and i.phase == PHASE_3]
        if irreversible_esthetic and not has_phase2:
            blocking.append({
                "rule": "reversible_test_phase",
                "detail": REVERSIBLE_TEST_MANDATORY_NOTE,
            })

    # ---- Gate 4: failure planning for T3/T4 (M2 §6) -----------------------
    for item in items:
        gaps = item.failure_planning_gaps()
        if gaps:
            blocking.append({
                "rule": "failure_planning",
                "detail": (f"'{item.description}' is {item.tier} but has no {', '.join(gaps)}. "
                           "A plan without an exit strategy is incomplete (M2 §6)."),
            })

    # ---- Gate 5: alternatives must include no-treatment and monitor -------
    labels = {a.option.strip().lower() for a in alternatives}
    for required in (NO_TREATMENT, MONITOR_DEFER):
        if required.lower() not in labels:
            blocking.append({
                "rule": "alternatives",
                "detail": (f"Alternatives must include '{required}' (M1 §13, CORE §8). "
                           "Omitting it presents treatment as the only option."),
            })

    # ---- Assemble the phase table ----------------------------------------
    phases = {}
    for phase in PHASE_ORDER:
        in_phase = [i for i in items if i.phase == phase]
        phases[phase] = {
            "purpose": PHASE_PURPOSE[phase],
            "content": [i.to_dict() for i in in_phase],
            "exit_criteria": None,   # supplied by the clinician; never invented here
        }

    return {
        "blocked": bool(blocking),
        "case_ref": case.case_ref,
        "discipline": case.discipline,
        "sufficiency": suff,
        "objectives": list(objectives or []),
        "objectives_note": ("Objectives must be measurable endpoints, not aspirations (M1 §11). "
                            "'Improve esthetics' is not an objective."),
        "phases": phases,
        "alternatives": [asdict(a) for a in alternatives],
        "blocking": blocking,
        "warnings": warnings,
        "next_single_step": None,   # M1: every template ends with one; the caller supplies it
        "next_step_required": True,
    }

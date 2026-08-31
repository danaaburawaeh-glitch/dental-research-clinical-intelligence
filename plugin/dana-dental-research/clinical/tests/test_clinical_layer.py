"""
clinical/tests/test_clinical_layer.py

Executable tests for the Phase D clinical layer. No network.
Run: python3 clinical/tests/test_clinical_layer.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLINICAL = os.path.dirname(HERE)
sys.path.insert(0, CLINICAL)

from case_state import (
    CaseState, DataPoint, ProvenanceError, REPORTED, OBSERVED, INFERRED, UNKNOWN,
    PROVENANCE_TAGS, DATASET_BY_SCOPE, SUFFICIENT, PARTIALLY_SUFFICIENT, INSUFFICIENT,
    OUT_OF_SCOPE, header_line, INTRINSICALLY_BLOCKING,
)
import red_flag_sweep as rfs
import safety_veto as veto
import treatment_plan as tp
import evidence_binding as eb

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def full_case(discipline="fixed_prosthodontics", ref="CASE-T"):
    c = CaseState(ref, discipline, notation="FDI")
    for k in DATASET_BY_SCOPE[discipline]:
        c.record(k, "recorded", OBSERVED)
    return c


def clear_sweep():
    return rfs.sweep({k: rfs.ABSENT for k in rfs.RED_FLAG_KEYS})


# ── 1. Provenance ───────────────────────────────────────────────────────────
check("01 exactly four provenance tags", PROVENANCE_TAGS == (REPORTED, OBSERVED, INFERRED, UNKNOWN))
try:
    DataPoint("ferrule", "adequate", INFERRED)
    ok = False
except ProvenanceError:
    ok = True
check("02 [Inferred] without a basis is rejected", ok)
check("03 [Inferred] with a basis is accepted",
      DataPoint("ferrule", "adequate", INFERRED, basis="2mm sound dentin").provenance == INFERRED)
try:
    DataPoint("allergies", "probably none", UNKNOWN)
    ok = False
except ProvenanceError:
    ok = True
check("04 [Unknown] cannot smuggle a finding", ok)
try:
    DataPoint("x", "y", "[Assumed]")
    ok = False
except ProvenanceError:
    ok = True
check("05 invented provenance tag rejected", ok)
c = full_case()
c.record("ferrule", "adequate", INFERRED, basis="periapical")
check("06 tag is never promoted by re-recording",
      c.get("ferrule").provenance == INFERRED and c.get("ferrule").basis)

# ── 2. Sufficiency ──────────────────────────────────────────────────────────
check("07 complete dataset -> SUFFICIENT", full_case().sufficiency()["verdict"] == SUFFICIENT)
c = full_case(); c.data.pop("ferrule")
check("08 missing intrinsically-blocking item -> INSUFFICIENT",
      c.sufficiency()["verdict"] == INSUFFICIENT)
check("09 caller cannot downgrade a blocking item",
      c.sufficiency({"ferrule": "refines_plan"})["verdict"] == INSUFFICIENT)
c2 = full_case(); c2.data.pop("anxiety_level")
check("10 missing non-blocking item -> PARTIALLY SUFFICIENT",
      c2.sufficiency()["verdict"] == PARTIALLY_SUFFICIENT)
c3 = CaseState("CASE-X", "fixed_prosthodontics")
check("11 near-empty case -> INSUFFICIENT, not PARTIAL",
      c3.sufficiency()["verdict"] == INSUFFICIENT)
check("12 SUFFICIENT is never reported with outstanding gaps",
      all(not (s["verdict"] == SUFFICIENT and s["missing"])
          for s in (full_case().sufficiency(), c.sufficiency(), c2.sufficiency())))
check("13 missing data is ranked by decision value",
      [m["rank"] for m in c3.sufficiency()["missing"]]
      == sorted([m["rank"] for m in c3.sufficiency()["missing"]], reverse=True))
check("14 header line carries mode, ref, notation and sufficiency",
      header_line(full_case(), "CASE").startswith("CASE · CASE-T · Notation: FDI · Data sufficiency:"))

# ── 3. Scope ────────────────────────────────────────────────────────────────
check("15 out-of-scope discipline refused",
      CaseState("C", "orthodontics").sufficiency()["verdict"] == OUT_OF_SCOPE)
check("16 both v1.0 disciplines in scope",
      full_case("fixed_prosthodontics").in_scope() and full_case("esthetic_restorative").in_scope())
check("17 out-of-scope is BLOCKED, not answered",
      veto.review(CaseState("C", "endodontics")).status == veto.BLOCKED)

# ── 4. Red-flag sweep ───────────────────────────────────────────────────────
check("18 all 14 M2 §7 flags present", len(rfs.RED_FLAGS) == 14)
check("19 nothing answered -> INCOMPLETE_SWEEP, not CLEAR",
      rfs.sweep()["status"] == "INCOMPLETE_SWEEP")
check("20 partial sweep is not clearance",
      rfs.sweep({"airway_concern": rfs.ABSENT})["status"] == "INCOMPLETE_SWEEP")
s = clear_sweep()
check("21 fully answered absent -> CLEAR with the exact M2 wording",
      s["status"] == "CLEAR" and s["statement"] == rfs.CLEAR_WORDING)
check("22 CLEAR always names what would change it", bool(s["what_would_change_it"]))
f = rfs.sweep({**{k: rfs.ABSENT for k in rfs.RED_FLAG_KEYS}, "spreading_swelling": rfs.PRESENT})
check("23 a flag produces the ⚠ block", f["status"] == "RED_FLAG" and rfs.BLOCK_HEADER in f["block"])
check("24 block is placed at the top", "TOP of the response" in f["placement"])
try:
    rfs.sweep({"invented_flag": rfs.ABSENT}); ok = False
except ValueError:
    ok = True
check("25 the flag list is fixed; unknown keys rejected", ok)
check("26 sweep never infers answers from the case record",
      rfs.sweep_from_case(full_case())["status"] == "INCOMPLETE_SWEEP")

# ── 5. Safety veto ──────────────────────────────────────────────────────────
check("27 clean case, complete sweep -> OK",
      veto.review(full_case(), sweep_result=clear_sweep()).status == veto.OK)
check("28 red flag -> SAFETY_BLOCK",
      veto.review(full_case(), sweep_result=f).status == veto.SAFETY_BLOCK)
check("29 SAFETY_BLOCK is marked non-overridable",
      veto.review(full_case(), sweep_result=f).overridable is False)
check("30 incomplete sweep blocks a definitive plan",
      veto.review(full_case(), veto.ACT_PLAN_DEFINITIVE).status == veto.SAFETY_BLOCK)
check("31 insufficient data blocks irreversible treatment",
      veto.review(c3, veto.ACT_IRREVERSIBLE, sweep_result=clear_sweep()).status == veto.SAFETY_BLOCK)
pc = full_case(); pc.record("allergies", None, UNKNOWN)
check("32 [Unknown] in the RX pre-check blocks prescribing support",
      veto.review(pc, veto.ACT_PRESCRIBING, sweep_result=clear_sweep()).status == veto.SAFETY_BLOCK)
check("33 identifiers in output -> SAFETY_BLOCK",
      veto.review(full_case(), sweep_result=clear_sweep(),
                  contains_identifiers=True).status == veto.SAFETY_BLOCK)
check("34 unverified Saudi regulatory claim is flagged",
      veto.FLAG_UNVERIFIED_REGULATORY in veto.review(
          full_case(), sweep_result=clear_sweep(),
          regulatory_states=["REQUIRES VERIFICATION"]).flags)
try:
    veto.assert_consistent(veto.SAFETY_BLOCK, "COMPLETE"); ok = False
except ValueError:
    ok = True
check("35 a SAFETY_BLOCK cannot be reported as another status", ok)
check("36 one clean check never cancels a block",
      veto.review(c3, veto.ACT_IRREVERSIBLE, sweep_result=clear_sweep()).status == veto.SAFETY_BLOCK)
check("37 block text states what is required before proceeding",
      "Required before proceeding" in veto.review(full_case(), sweep_result=f).block_text)

# ── 6. Treatment plan ───────────────────────────────────────────────────────
def crown(teeth, tier=tp.TIER_T3, phase=tp.PHASE_3, **kw):
    return tp.PlannedItem("Full-coverage crown", phase, tier, teeth=list(teeth), **kw)


FULL_FAILURE_PLAN = dict(expected_service_life="10-15 y (L2)", failure_mode="cement failure",
                         early_warning_signs="marginal staining", retreatability="re-prep possible",
                         maintenance_obligation="6-monthly recall",
                         cost_of_being_wrong="tooth structure unrecoverable")
ALTS = [tp.Alternative(tp.NO_TREATMENT, "accept current state"),
        tp.Alternative(tp.MONITOR_DEFER, "review in 6 months")]

good = full_case(); good.prognosis = {"16": "favourable"}
p = tp.build_plan(good, [crown(["16"], **FULL_FAILURE_PLAN)], ALTS)
check("38 a complete, well-sequenced plan is not blocked", p["blocked"] is False, str(p["blocking"])[:120])
check("39 all six phases present in order", tuple(p["phases"].keys()) == tp.PHASE_ORDER)

bad = full_case(); bad.prognosis = {"26": ""}
p2 = tp.build_plan(bad, [crown(["26"], **FULL_FAILURE_PLAN)], ALTS)
check("40 restorative on PROGNOSIS UNDETERMINED is blocked",
      any(b["rule"] == "prognosis_before_prosthesis" for b in p2["blocking"]))
check("41 a tooth absent from prognosis counts as undetermined",
      "26" in bad.prognosis_undetermined_teeth())

p3 = tp.build_plan(good, [crown(["16"], **FULL_FAILURE_PLAN)], [ALTS[0]])
check("42 alternatives must include monitor/defer",
      any(b["rule"] == "alternatives" for b in p3["blocking"]))
p4 = tp.build_plan(good, [crown(["16"])], ALTS)
check("43 T3 without failure planning is blocked",
      any(b["rule"] == "failure_planning" for b in p4["blocking"]))
p5 = tp.build_plan(good, [crown(["16"], prerequisites=[tp.PHASE_4], **FULL_FAILURE_PLAN)], ALTS)
check("44 irreversible item before its prerequisite is blocked",
      any(b["rule"] == "sequencing" for b in p5["blocking"]))
est = full_case("esthetic_restorative"); est.prognosis = {"11": "favourable"}
p6 = tp.build_plan(est, [crown(["11"], **FULL_FAILURE_PLAN)], ALTS, esthetic_elective=True)
check("45 elective esthetic without a reversible test phase is blocked",
      any(b["rule"] == "reversible_test_phase" for b in p6["blocking"]))
p7 = tp.build_plan(est, [tp.PlannedItem("Mock-up", tp.PHASE_2, tp.TIER_T1),
                          crown(["11"], **FULL_FAILURE_PLAN)], ALTS, esthetic_elective=True)
check("46 adding the mock-up clears that gate",
      not any(b["rule"] == "reversible_test_phase" for b in p7["blocking"]))
check("47 blocked items are reported, not silently dropped",
      len(p2["phases"][tp.PHASE_3]["content"]) == 1)
check("48 exit criteria are never invented",
      all(v["exit_criteria"] is None for v in p["phases"].values()))
check("49 plan demands a next single step", p["next_step_required"] is True)
check("50 out-of-scope case cannot produce a plan",
      tp.build_plan(CaseState("C", "orthodontics"), [], ALTS)["blocked"] is True)

# ── 7. Evidence binding ─────────────────────────────────────────────────────
try:
    eb.bind("x", "d", del7_tag="L1"); ok = False
except ValueError:
    ok = True
check("51 a tag above UNVER requires a real source", ok)
try:
    eb.bind("x", "d"); ok = False
except ValueError:
    ok = True
check("52 UNVER requires a runnable search strategy", ok)
try:
    eb.bind("x", "d", del7_tag="L9", search_strategy="s"); ok = False
except ValueError:
    ok = True
check("53 invented DEL-7 tag rejected", ok)
u = eb.unver("claim", "decision", "PICO: ...")
check("54 UNVER shorthand produces an honest gap",
      u.del7_tag == "UNVER" and u.search_strategy and u.confidence == "Cannot assess")
src = eb.source_from_pubmed({"pmid": "1", "doi": "10.1/x", "title": "t", "is_retracted": False})
bound = eb.bind("claim", "decision", "L2", eb.DIRECT, [src], confidence="Moderate")
check("55 a bound claim carries decision, tag, directness and provenance",
      bound.decision == "decision" and bound.sources[0]["pmid"] == "1")
ret = eb.bind("c", "d", "L2", eb.DIRECT, [{"connector": "pubmed", "pmid": "9", "is_retracted": True}])
a = eb.audit_claims([ret])
check("56 a retracted source is caught at claim level too",
      not a["ok"] and a["retracted_sources"])
reg = eb.bind("c", "d", "L2", eb.DIRECT, [src], regulatory_state="REQUIRES VERIFICATION")
check("57 unverified regulatory state surfaces in the audit",
      eb.audit_claims([reg])["regulatory_unverified"])
trial = eb.source_from_trial({"nct_id": "NCT1", "evidence_class": "REGISTERED_NO_RESULTS"})
tclaim = eb.bind("works", "d", "L2", eb.DIRECT, [trial])
check("58 a registered trial with no results cannot support efficacy",
      not eb.audit_claims([tclaim])["ok"])
ext = eb.bind("c", "d", "L2", eb.EXTRAPOLATION, [src], confidence="High")
check("59 extrapolation cannot carry high confidence",
      not eb.audit_claims([ext])["ok"])
check("60 evidence and authorisation are kept separate",
      "Neither substitutes for the other" in eb.SEPARATION_RULE)

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

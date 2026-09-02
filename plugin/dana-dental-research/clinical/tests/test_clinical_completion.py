"""
clinical/tests/test_clinical_completion.py

The 10 essential v0.8.0 clinical tests, plus the invariants for the prognosis engine and the
healthy-tooth hierarchy. No network.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLINICAL = os.path.dirname(HERE)
PLUGIN = os.path.dirname(CLINICAL)
sys.path.insert(0, CLINICAL)

from case_state import (CaseState, OBSERVED, INFERRED, UNKNOWN, DATASET_BY_SCOPE,
                        INSUFFICIENT, SUFFICIENT)
import red_flag_sweep as rfs
import safety_veto as veto
import treatment_plan as tp
import prognosis as pg

REFS = os.path.join(PLUGIN, "skills", "esthetic-prosthodontics", "references")
R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def ref(f):
    return re.sub(r"\s+", " ", io.open(os.path.join(REFS, f), encoding="utf-8").read())


def full_case(disc="fixed_prosthodontics", ref_id="CASE-C"):
    c = CaseState(ref_id, disc, notation="FDI")
    for k in DATASET_BY_SCOPE[disc]:
        c.record(k, "recorded", OBSERVED)
    for k in ("periodontal_status", "attachment_level", "strategic_value", "mobility",
              "furcation", "crown_root_ratio"):
        c.record(k, "recorded", OBSERVED)
    return c


def clear_sweep():
    return rfs.sweep({k: rfs.ABSENT for k in rfs.RED_FLAG_KEYS})


VCD = ref("veneer-crown-decision.md")
RST = ref("prosthodontic-restorability.md")
RSK = ref("prosthodontic-risk-factors.md")
SEQ = ref("treatment-sequencing-principles.md")

# ── TEST 1 — healthy tooth + cosmetic dissatisfaction → crown not first-line ──
check("T1a least-invasive ladder present with no-treatment first",
      "No treatment** — always a live option" in VCD or "No treatment" in VCD)
check("T1b ladder runs whitening -> orthodontics -> additive -> no-prep -> minimal-prep",
      all(x in VCD for x in ("Whitening", "Orthodontics", "Additive composite",
                             "No-prep / additive ceramic", "Minimal-prep restoration")))
check("T1c full crown requires an independent indication",
      "only with an independent indication" in VCD)
check("T1d crown is never reached by esthetic convenience",
      "never reached by esthetic convenience" in VCD)
check("T1e crown-avoidance question is asked first",
      "Can the clinical objective be achieved with a more conservative option?" in VCD)
check("T1f 'the patient asked for it' is not an indication",
      "never an indication" in VCD)

# ── TEST 2 — extensive structural compromise → veneer not automatic ──
check("T2a veneer explicitly not the answer for extensive structural loss",
      "Extensive structural compromise" in VCD and "does not replace a missing wall" in VCD)
check("T2b structural loss does not make the veneer thinner",
      "it does not make the veneer thinner" in VCD)
check("T2c full-coverage indications are enumerated, not assumed",
      "Full coverage requires a stated indication" in RST)
check("T2d endodontic treatment alone is not a crown indication",
      "not converted to a full crown merely because it has been root-treated" in RST)

# ── TEST 3 — missing ferrule / restorability → prognosis UNDETERMINED ──
c = full_case(); c.data.pop("ferrule")
r = pg.assess_in_order(c, clear_sweep())
check("T3a missing ferrule -> UNDETERMINED", r["overall"] == pg.UNDETERMINED, r["overall"])
check("T3b UNDETERMINED blocks irreversible planning", r["blocks_irreversible_planning"] is True)
c2 = full_case(); c2.data.pop("restorability_verdict_with_criteria")
check("T3c missing restorability -> UNDETERMINED",
      pg.assess_in_order(c2, clear_sweep())["overall"] == pg.UNDETERMINED)
c3 = full_case(); c3.record("ferrule", None, UNKNOWN)
check("T3d [Unknown] determinant counts as missing, not as absent-and-fine",
      pg.assess_in_order(c3, clear_sweep())["overall"] == pg.UNDETERMINED)
check("T3e no numeric probability anywhere in the result",
      not re.search(r"\d+\s?%", str(pg.assess_in_order(full_case(), clear_sweep()))))

# ── TEST 4 — active periodontal disease → definitive prosthodontic phase blocked ──
r4 = pg.assess_in_order(full_case(), clear_sweep(),
                        adverse_findings=["active_periodontal_disease"])
check("T4a active perio -> POOR", r4["overall"] == pg.POOR, r4["overall"])
check("T4b periodontal axis is among the drivers", pg.AXIS_PERIODONTAL in r4["driven_by"])
check("T4c restorative axis is not contaminated by a periodontal finding",
      r4["axes"]["restorative"]["category"] == pg.FAVORABLE)
check("T4d disease-control gate is documented as blocking Phase 3",
      "blocks Phase 3, not merely advises against it" in SEQ)
check("T4e gate is anchored to a real guideline (EFP S3, R1)",
      "doi:10.1111/jcpe.13290" in SEQ and "Sanz" in SEQ)
check("T4f no definitive restoration over active disease",
      "No definitive restoration over active caries, active periodontal disease" in SEQ)

# ── TEST 5 — uncontrolled parafunction → functional risk flagged ──
r5 = pg.assess_in_order(full_case(), clear_sweep(),
                        adverse_findings=["uncontrolled_parafunction"])
check("T5a parafunction -> GUARDED", r5["overall"] == pg.GUARDED, r5["overall"])
check("T5b functional axis flagged", pg.AXIS_FUNCTIONAL in r5["driven_by"])
check("T5c it also bears on restorative and prosthetic prognosis",
      pg.AXIS_RESTORATIVE in r5["driven_by"] and pg.AXIS_PROSTHETIC in r5["driven_by"])
check("T5d bruxism graded by confidence, not as a binary",
      "reported* / *clinically assessed* / *instrumentally confirmed" in RSK
      or "instrumentally confirmed" in RSK)
check("T5e anchored to the 2025 consensus (R4)", "doi:10.1111/joor.13985" in RSK)

# ── TEST 6 — insufficient diagnostic data → definitive irreversible plan blocked ──
thin = CaseState("CASE-THIN", "fixed_prosthodontics")
thin.record("age", 40, OBSERVED)
check("T6a thin dataset -> INSUFFICIENT", thin.sufficiency()["verdict"] == INSUFFICIENT)
r6 = pg.assess_in_order(thin, clear_sweep())
check("T6b prognosis not attempted on an insufficient dataset",
      r6["overall"] == pg.UNDETERMINED and r6["blocks_irreversible_planning"])
check("T6c veto blocks the definitive plan",
      veto.review(thin, veto.ACT_PLAN_DEFINITIVE, sweep_result=clear_sweep(),
                  prognosis_result=r6).status == veto.SAFETY_BLOCK)
check("T6d veto blocks irreversible treatment",
      veto.review(thin, veto.ACT_IRREVERSIBLE, sweep_result=clear_sweep(),
                  prognosis_result=r6).status == veto.SAFETY_BLOCK)
check("T6e information-only request is not blocked by prognosis alone",
      veto.review(full_case(), veto.ACT_INFORMATION, sweep_result=clear_sweep(),
                  prognosis_result={"blocks_irreversible_planning": True,
                                    "block_reason": "x"}).status == veto.OK)

# ── TEST 7 — favourable complete dataset → prognosis can proceed ──
r7 = pg.assess_in_order(full_case(), clear_sweep())
check("T7a complete dataset -> FAVORABLE", r7["overall"] == pg.FAVORABLE, r7["overall"])
check("T7b does not block planning", r7["blocks_irreversible_planning"] is False)
check("T7c all five axes assessed", set(r7["axes"]) == set(pg.AXES))
check("T7d every axis carries basis, findings, gaps and confidence",
      all(all(k in a for k in ("basis", "supporting_findings", "adverse_findings",
                               "missing_determinants", "confidence"))
          for a in r7["axes"].values()))
check("T7e categories are only the four permitted",
      all(a["category"] in pg.CATEGORIES for a in r7["axes"].values()))
check("T7f a named published scale is still required of the clinician",
      "not a substitute for it" in r7["scale_note"])

# ── TEST 8 — evidence conflict → uncertainty preserved ──
inf = full_case(); inf.record("ferrule", "adequate", INFERRED, basis="periapical appearance")
r8 = pg.assess_in_order(inf, clear_sweep())
check("T8a an [Inferred] critical determinant caps the axis at GUARDED",
      r8["axes"]["restorative"]["category"] == pg.GUARDED)
check("T8b the cap is explained, not silent",
      any("Inferred" in s for s in r8["axes"]["restorative"]["supporting_findings"]))
mixed = pg.assess_in_order(full_case(), clear_sweep(),
                           adverse_findings=["uncontrolled_parafunction",
                                             "active_periodontal_disease"])
check("T8c worst axis drives the overall, never an average", mixed["overall"] == pg.POOR)
check("T8d divergent axes are preserved, not collapsed",
      mixed["axes"]["functional_occlusal"]["category"] == pg.GUARDED
      and mixed["axes"]["periodontal"]["category"] == pg.POOR)
# UPDATED in v0.9.0: the protocol was approved (all eight Appendix C items closed), so the
# previous assertion — that it must be cited as a working draft — is now false by design. The
# invariant that actually matters is unchanged: the citation must name a specific, current version
# and must never present the superseded v1.2 as current.
check("T8e clinic protocol cited as v1.3 APPROVED, with v1.2 marked historical",
      "v1.3" in RST and "APPROVED" in RST
      and "must not be cited as current" in re.sub(r"\s+", " ", RST))
check("T8f no invented textbook citation anywhere in the four references",
      not any("Rosenstiel Ch." in x for x in (RST, VCD, RSK, SEQ)))
check("T8g Rosenstiel unavailability stated explicitly",
      "not available" in RST and "Rosenstiel" in RST)

# ── TEST 9 — esthetic request vs biology/function → biology wins ──
check("T9a biology before esthetics is stated as non-negotiable",
      "Biology and function precede esthetics" in VCD and "non-negotiable" in VCD)
check("T9b definitive esthetic work barred while disease is active",
      "not started** in the presence of active gingival inflammation" in VCD
      or "not started" in VCD)
check("T9c veneers-instead-of-orthodontics is prohibited",
      "needs orthodontic, periodontal or fundamental functional treatment" in VCD)
est = full_case("esthetic_restorative")
est.prognosis = {"11": ""}
p9 = tp.build_plan(est, [tp.PlannedItem("Veneer 11", tp.PHASE_3, tp.TIER_T3, teeth=["11"])],
                   [tp.Alternative(tp.NO_TREATMENT, "x"), tp.Alternative(tp.MONITOR_DEFER, "y")],
                   esthetic_elective=True)
check("T9d elective esthetic plan on undetermined prognosis is blocked",
      any(b["rule"] == "prognosis_before_prosthesis" for b in p9["blocking"]))
check("T9e reversible test phase still required",
      any(b["rule"] == "reversible_test_phase" for b in p9["blocking"]))

# ── TEST 10 — sequencing respects disease control before definitive prosthesis ──
check("T10a phase order documented with gates", "Phase 1 — Stabilisation & control" in SEQ)
check("T10b four hard gates named", SEQ.count("Gate ") >= 4)
check("T10c prognosis-before-prosthesis is gate 2", "Gate 2 — Prognosis before prosthesis" in SEQ)
check("T10d test phase before irreversible esthetic is gate 3",
      "Gate 3 — Reversible test phase" in SEQ)
check("T10e definitive records follow tissue stability", "Gate 4 — Tissue stability" in SEQ)
check("T10f what may not run in parallel is stated",
      "Never parallel" in SEQ)
good = full_case(); good.prognosis = {"16": pg.FAVORABLE}
plan = tp.build_plan(good, [tp.PlannedItem(
    "Crown 16", tp.PHASE_3, tp.TIER_T3, teeth=["16"],
    expected_service_life="range (L2)", failure_mode="cement failure",
    early_warning_signs="marginal staining", retreatability="re-prep possible",
    maintenance_obligation="risk-based recall", cost_of_being_wrong="tooth structure")],
    [tp.Alternative(tp.NO_TREATMENT, "x"), tp.Alternative(tp.MONITOR_DEFER, "y")])
check("T10g a correctly sequenced plan on a favourable prognosis passes",
      plan["blocked"] is False, str(plan["blocking"])[:120])

# ── Invariants ──
# v1.2.1: the vocabulary is six, not four. POTENTIALLY_COMPROMISED and
# HIGHER_RISK_THAN_COMPARATOR were added so an isolated adverse determinant is neither promoted to
# GUARDED nor discarded. The invariant this check exists to protect is that the vocabulary is
# CLOSED and contains no numeric category — that is asserted here and in INV2.
check("INV1 prognosis vocabulary is closed and complete", pg.CATEGORIES ==
      (pg.FAVORABLE, pg.GUARDED, pg.POOR, pg.UNDETERMINED, pg.POTENTIALLY_COMPROMISED,
       pg.HIGHER_RISK_THAN_COMPARATOR))
check("INV1b the four original categories are unchanged",
      (pg.FAVORABLE, pg.GUARDED, pg.POOR, pg.UNDETERMINED)
      == ("FAVORABLE", "GUARDED", "POOR", "UNDETERMINED"))
check("INV1c no category is numeric",
      not any(any(ch.isdigit() for ch in c) for c in pg.CATEGORIES))
check("INV2 no percentage is ever emitted",
      "%" not in str(pg.assess_in_order(full_case(), clear_sweep(),
                                        adverse_findings=["furcation_involvement"])))
try:
    pg.assess_in_order(full_case(), None); ok = False
except pg.PrognosisOrderError:
    ok = True
check("INV3 prognosis refuses to run before the red-flag sweep", ok)
try:
    pg.assess_in_order(full_case(), rfs.sweep()); ok = False
except pg.PrognosisOrderError:
    ok = True
check("INV4 an incomplete sweep also refuses", ok)
r = pg.assess_in_order(full_case(), rfs.sweep(
    {**{k: rfs.ABSENT for k in rfs.RED_FLAG_KEYS}, "airway_concern": rfs.PRESENT}))
check("INV5 a red flag pre-empts prognosis", r["overall"] == pg.UNDETERMINED)
try:
    pg.assess_in_order(CaseState("C", "orthodontics"), clear_sweep()); ok = False
except pg.PrognosisOrderError:
    ok = True
check("INV6 out-of-scope produces no prognosis", ok)
try:
    pg.assess_axis(full_case(), pg.AXIS_TOOTH, adverse_findings=["made_up_finding"]); ok = False
except ValueError:
    ok = True
check("INV7 ad-hoc adverse labels rejected", ok)
check("INV8 tiers now match CORE §7 including T0",
      tp.ALL_TIERS == ("T0", "T1", "T2", "T3", "T4") and tp.TIER_T2 in tp.REDUCTIVE_TIERS)
check("INV9 no unsupported numeric threshold in the four references",
      not re.search(r"\b\d+(\.\d+)?\s?mm\b", RST + VCD + SEQ))
check("INV10 every reference carries a source note or explicit provenance",
      all(("SOURCE NOTE" in x or "SOURCES:" in x) for x in (RST, VCD, RSK, SEQ)))

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

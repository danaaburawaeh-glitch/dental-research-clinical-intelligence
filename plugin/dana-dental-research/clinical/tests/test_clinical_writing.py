# -*- coding: utf-8 -*-
"""
clinical/tests/test_clinical_writing.py

v1.2.1 writing-layer regression suite (§74) and the manual twelve-case CLINICAL MODE
validation (§75).

The point of every check here: internal rigour is unchanged, and none of it reaches the page.

No network. Run: python3 clinical/tests/test_clinical_writing.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLINICAL = os.path.dirname(HERE)
sys.path.insert(0, CLINICAL)
sys.path.insert(0, os.path.join(CLINICAL, "benchmark"))

import clinical_writing as cw          # noqa: E402
import decision_context as dc          # noqa: E402
import prognosis as pg                 # noqa: E402
import language_governor as lg         # noqa: E402
from clinical_mode_renders import RENDERS  # noqa: E402

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


# ── Modes ───────────────────────────────────────────────────────────────────────────────────
print("── Modes ──")
check("W01 five modes are defined", len(cw.MODES) == 5)
check("W02 CLINICAL is the default", cw.DEFAULT_MODE == cw.CLINICAL)
check("W03 no mode requested resolves to CLINICAL", cw.resolve_mode(None) == cw.CLINICAL)
check("W04 an unrecognised mode falls back to CLINICAL, not to the most verbose",
      cw.resolve_mode("something") == cw.CLINICAL)
check("W05 debug/developer/governance aliases resolve explicitly",
      cw.resolve_mode("debug") == cw.TECHNICAL and cw.resolve_mode("governance") == cw.AUDIT)
check("W06 only AUDIT and TECHNICAL expose internals",
      cw.MODES_EXPOSING_INTERNALS == (cw.AUDIT, cw.TECHNICAL))

# ── Translation ─────────────────────────────────────────────────────────────────────────────
print("\n── Internal label translation ──")
for label in ("HARD_BLOCKER", "DECISION_MODIFIER", "RISK_MODIFIER", "PLANNING_REFINER",
              "UNDETERMINED", "POTENTIALLY_COMPROMISED", "ELECTIVE_BUT_ACCEPTABLE",
              "DO_NOT_PROCEED", "INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT"):
    check(f"W.tr {label} is translated in CLINICAL mode",
          cw.translate(label) != label and cw.translate(label) in cw.TRANSLATIONS.values())
check("W07 the brief's worked translation is exact",
      cw.translate("INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT").startswith(
          "المعطيات الحالية كافية لتحديد الاتجاه العلاجي المحافظ"))
check("W08 labels are returned unchanged in AUDIT mode",
      cw.translate("HARD_BLOCKER", cw.AUDIT) == "HARD_BLOCKER")
check("W09 every sufficiency verdict has a translation",
      all(v in cw.TRANSLATIONS for v in dc.SUFFICIENCY_VERDICTS))
check("W10 every prognosis category has a translation",
      all(c in cw.TRANSLATIONS for c in pg.CATEGORIES))
check("W11 every priority level has a translation",
      all(p in cw.TRANSLATIONS for p in dc.PRIORITY_ORDER))
check("W12 every appropriateness class has a translation",
      all(a in cw.TRANSLATIONS for a in lg.APPROPRIATENESS))

# ── Jargon guard ────────────────────────────────────────────────────────────────────────────
print("\n── Jargon guard ──")
BAD = "Case state: INSUFFICIENT.\n29/40 fields missing. HARD_BLOCKER present. driver_problem_identified: UNKNOWN."
check("W13 a status-report answer fails the clinical check",
      cw.check_clinical_prose(BAD)["result"] == "FAIL")
check("W14 the status-report opener is identified",
      any(f["kind"] == "STATUS_REPORT_OPENER" for f in cw.check_clinical_prose(BAD)["findings"]))
check("W15 engine vocabulary is identified",
      any(f["kind"] == "INTERNAL_JARGON" for f in cw.check_clinical_prose(BAD)["findings"]))
check("W16 the same text passes in AUDIT mode",
      cw.check_clinical_prose(BAD, cw.AUDIT)["result"] == "PASS")
check("W17 irreversibility tier codes are caught",
      any(f["kind"] == "INTERNAL_TIER_CODE"
          for f in cw.check_clinical_prose("هذا الإجراء من فئة T3.")["findings"]))
check("W18 a clean clinical paragraph passes",
      cw.check_clinical_prose("لا يوجد حاليًا ما يبرر البدء بعشرة قشور خزفية.")["result"] == "PASS")
check("W19 module filenames are forbidden in clinical output",
      "case_state.py" in cw.FORBIDDEN_IN_CLINICAL and "prognosis.py" in cw.FORBIDDEN_IN_CLINICAL)

# ── Claim calibration and patient preference ────────────────────────────────────────────────
print("\n── Claim calibration and patient preference ──")
check("W20 absolute Arabic verbs are flagged",
      cw.check_claim_calibration("هذا يثبت أن الإطباق هو السبب المباشر.")["result"] == "FAIL")
check("W21 calibrated verbs are offered", "تشير المعطيات إلى" in cw.CALIBRATED_VERBS)
check("W22 adversarial phrasing toward the patient is flagged",
      any(f["kind"] == "ADVERSARIAL_TOWARD_PATIENT"
          for f in cw.check_claim_calibration("طلب المريض غير مقبول.")["findings"]))
check("W23 respectful alternatives are provided",
      any("تفضيل المريض مفهوم" in p for p in cw.RESPECTFUL_PREFERENCE))
check("W24 calibrated clinical prose passes",
      cw.check_claim_calibration("تشير المعطيات إلى أن العامل الليلي قد يكون مساهمًا.")["result"]
      == "PASS")

# ── Structure ───────────────────────────────────────────────────────────────────────────────
print("\n── Structure ──")
check("W25 eleven sections are defined", len(cw.SECTIONS) == 11)
check("W26 only the problem and the decision are always required",
      cw.ALWAYS_REQUIRED == ("المشكلة الرئيسية", "القرار السريري الحالي"))
check("W27 sections are not emitted mechanically",
      "Mechanically emitting eleven headings" in cw.STRUCTURE_RULE)
check("W28 an answer without a current decision fails validation",
      cw.ClinicalConsultation(main_problem="x").validate()["result"] == "FAIL")
check("W29 the compact evidence line is available and single-line",
      "\n" not in cw.evidence_line("Systematic review", "Citation verified", "Moderate",
                                   "Partially direct"))

# ── AUDIT mode still shows everything ───────────────────────────────────────────────────────
print("\n── Governance preserved ──")
audit = RENDERS["CASE-01"].render(cw.AUDIT)
check("W30 AUDIT mode exposes the decision profile", "veneer_preparation" in audit)
check("W31 AUDIT mode exposes the internal sufficiency state",
      "INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT" in audit)
check("W32 AUDIT mode exposes suppressed fields", "ferrule" in audit)
check("W33 CLINICAL mode exposes none of them",
      all(t not in RENDERS["CASE-01"].render()
          for t in ("veneer_preparation", "INSUFFICIENT_FOR_IRREVERSIBLE_TREATMENT", "ferrule")))
check("W34 TECHNICAL mode returns the raw structure",
      isinstance(RENDERS["CASE-01"].render(cw.TECHNICAL), dict))
check("W35 the internal state is retained, not discarded",
      RENDERS["CASE-01"].internal.get("decision") == "veneer_preparation")

# ── §75: manual twelve-case CLINICAL MODE validation ────────────────────────────────────────
print("\n── §75: twelve cases in CLINICAL MODE ──")

for cid in [f"CASE-{i:02d}" for i in range(1, 13)]:
    c = RENDERS[cid]
    prose = c.render(cw.CLINICAL)
    v = c.validate(cw.CLINICAL)
    reads_like_software = cw.check_clinical_prose(prose)["result"] == "FAIL"
    decision_clear = bool(c.body.get("القرار السريري الحالي"))
    rationale_clear = bool(c.body.get("تفسير المعطيات الحالية")
                           or c.body.get("المشكلة الرئيسية")
                           or c.body.get("التشخيص التفريقي"))
    next_step_clear = bool(c.body.get("خطة العلاج وتسلسلها")
                           or c.body.get("ما الذي قد يغيّر القرار")
                           or c.body.get("البدائل"))
    calibrated = cw.check_claim_calibration(prose)["result"] == "PASS"
    jargon_hidden = not cw.check_clinical_prose(prose)["findings"]
    ok = (v["result"] == "PASS" and not reads_like_software and decision_clear
          and rationale_clear and next_step_clear and calibrated and jargon_hidden
          and v["decision_appears_early"])
    check(f"{cid} clinical consultation (decision/rationale/next-step/calibration/no-jargon)",
          ok, f"validate={v['result']} software={reads_like_software} "
              f"decision={decision_clear} rationale={rationale_clear} next={next_step_clear} "
              f"calibrated={calibrated} jargon_hidden={jargon_hidden}")

check("W36 all twelve renders exist", len(RENDERS) == 12)
check("W37 no render opens with a status line",
      all(not cw.FORBIDDEN_OPENERS.search(RENDERS[c].render().split("\n")[0])
          for c in RENDERS))
check("W38 every render uses fewer than all eleven sections where appropriate",
      any(len(RENDERS[c].validate()["sections_used"]) < 11 for c in RENDERS))

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

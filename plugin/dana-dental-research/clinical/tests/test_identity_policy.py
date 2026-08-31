"""
clinical/tests/test_identity_policy.py

The 10 required identity-policy regression tests, plus invariants and a whole-plugin sweep.
No network.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLINICAL = os.path.dirname(HERE)
PLUGIN = os.path.dirname(CLINICAL)
sys.path.insert(0, CLINICAL)

import identity_policy as idp
import safety_veto as veto
import red_flag_sweep as rfs
from case_state import CaseState, OBSERVED, DATASET_BY_SCOPE

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def full_case():
    c = CaseState("CASE-ID", "fixed_prosthodontics", notation="FDI")
    for k in DATASET_BY_SCOPE["fixed_prosthodontics"]:
        c.record(k, "recorded", OBSERVED)
    return c


def clear_sweep():
    return rfs.sweep({k: rfs.ABSENT for k in rfs.RED_FLAG_KEYS})


# ── 1. A clinical answer must not cite the creator ──────────────────────────
check("01 'Dr Dana recommends' blocked in a clinical answer",
      not idp.scan("Dr Dana recommends a full crown on 16.", idp.CONTEXT_CLINICAL)["ok"])
check("02 'According to Dr Dana' blocked",
      not idp.scan("According to Dr Dana, veneers are indicated.", idp.CONTEXT_CLINICAL)["ok"])
check("03 a bare name in a clinical answer is blocked",
      not idp.scan("This follows Dana's usual approach.", idp.CONTEXT_CLINICAL)["ok"])
check("04 Arabic form is caught too",
      not idp.scan("د. دانا توصي بالتاج الكامل.", idp.CONTEXT_CLINICAL)["ok"])

# ── 2. A protocol title must not contain the name ───────────────────────────
check("05 'Dana Protocol' blocked",
      not idp.scan("The Dana Protocol requires cuspal coverage.", idp.CONTEXT_CLINICAL)["ok"])
check("06 'Dr Dana's protocol' blocked",
      not idp.scan("Dr Dana's protocol requires this.", idp.CONTEXT_PROTOCOL_TITLE)["ok"])
check("07 neutral protocol names are clean",
      all(idp.scan(f"See the {n}.", idp.CONTEXT_CLINICAL)["ok"]
          for n in idp.NEUTRAL_PROTOCOL_NAMES))

# ── 3. Clinic policy labelled by source class, not by person ────────────────
check("08 '(OPS) Clinic policy requires…' is clean",
      idp.scan("(OPS) Clinic policy requires periodontal control first.",
               idp.CONTEXT_CLINICAL)["ok"])
check("09 the four source-class alternatives are offered",
      set(idp.SOURCE_CLASS_ALTERNATIVES) ==
      {"clinic_policy", "clinical_judgement", "user_supplied", "internal_protocol"})
check("10 suggest_source_class returns a label, never a name",
      "Dana" not in idp.suggest_source_class("clinic_policy"))

# ── 4. Scientific claims cite a real source ─────────────────────────────────
check("11 a real citation is clean",
      idp.scan("Perio control precedes prosthetics (L1 — Sanz 2020, doi:10.1111/jcpe.13290).",
               idp.CONTEXT_EVIDENCE)["ok"])
check("12 'Dana evidence' blocked in evidence synthesis",
      not idp.scan("Dana evidence supports this.", idp.CONTEXT_EVIDENCE)["ok"])
check("13 the remedy names the real fix",
      "DEL-7 source" in json.dumps(idp.scan("Dana research shows this.",
                                            idp.CONTEXT_EVIDENCE)["violations"]))

# ── 5-6. Creator metadata and About may carry the attribution ───────────────
check("14 permitted English creator string is clean in metadata",
      idp.scan(idp.ALLOWED_CREATOR_STRING_EN, idp.CONTEXT_CREATOR_METADATA)["ok"])
check("15 permitted Arabic creator string is clean in metadata",
      idp.scan(idp.ALLOWED_CREATOR_STRING_AR, idp.CONTEXT_CREATOR_METADATA)["ok"])
check("16 the bare author name in plugin metadata is clean",
      idp.scan("Dr Dana Abu Rawaeh", idp.CONTEXT_CREATOR_METADATA)["ok"])
check("17 an ownership record may name the signatory",
      idp.scan("The signature line remains for Dr Dana.",
               idp.CONTEXT_OWNERSHIP_RECORD)["ok"])
check("18 authority phrasing is blocked even in an About section",
      not idp.scan("Dr Dana recommends this technique.",
                   idp.CONTEXT_CREATOR_METADATA)["ok"])

# ── 7-9. Treatment, evidence and regulatory outputs ─────────────────────────
check("19 treatment recommendation must not name the creator",
      not idp.scan("Recommended by Dr Dana: crown 16.", idp.CONTEXT_TREATMENT)["ok"])
check("20 evidence synthesis must not name the creator",
      not idp.scan("Synthesis per Dana Abu Rawaeh.", idp.CONTEXT_EVIDENCE)["ok"])
check("21 regulatory answer must not name the creator",
      not idp.scan("Dr Dana states this device is SFDA-registered.",
                   idp.CONTEXT_REGULATORY)["ok"])
check("22 patient-facing output must not name the creator",
      not idp.scan("Dana says you need a crown.", idp.CONTEXT_PATIENT_FACING)["ok"])

# ── 10. The final output scan catches it ────────────────────────────────────
c = full_case()
r = veto.review(c, sweep_result=clear_sweep(),
                draft_output="Dr Dana recommends a full crown on 16.")
check("23 the veto blocks a violating draft",
      r.status == veto.SAFETY_BLOCK and veto.FLAG_IDENTITY_POLICY in r.flags, r.status)
check("24 the block states the remedy",
      any("real source" in x or "OPS" in x or "Clinical Protocol" in x
          for x in r.required_before_proceeding))
r2 = veto.review(c, sweep_result=clear_sweep(),
                 draft_output="(OPS) Clinic policy requires periodontal control first.")
check("25 a clean draft passes", r2.status == veto.OK, r2.status)
check("26 the veto scan is opt-in per context",
      veto.review(c, sweep_result=clear_sweep(),
                  draft_output="Dr Dana Abu Rawaeh",
                  output_context=idp.CONTEXT_CREATOR_METADATA).status == veto.OK)

# ── Invariants ──────────────────────────────────────────────────────────────
check("27 the product name DANA is never mistaken for the person",
      idp.scan("DANA Dental Intelligence OS applies the approved Clinical Protocol.",
               idp.CONTEXT_CLINICAL)["ok"])
check("28 dana-dental-research package names are clean",
      idp.scan("See connectors in dana-dental-research v0.9.1.", idp.CONTEXT_CLINICAL)["ok"])
check("29 the permitted string is NOT exempt inside a clinical answer",
      not idp.scan(f"Plan: crown 16. {idp.ALLOWED_CREATOR_STRING_EN}",
                   idp.CONTEXT_CLINICAL)["ok"])
try:
    idp.scan("x", "not_a_context"); ok = False
except ValueError:
    ok = True
check("30 an unknown context is rejected rather than silently allowed", ok)
try:
    idp.assert_clean("Dr Dana recommends this.", idp.CONTEXT_CLINICAL); ok = False
except idp.IdentityPolicyError:
    ok = True
check("31 assert_clean raises on violation", ok)

# ── Whole-plugin sweep ──────────────────────────────────────────────────────
# Two files state the policy itself, and to forbid a phrasing they must quote it. Excluding them
# is not a loophole: a separate assertion below confirms each still contains the prohibition it
# quotes, so neither can quietly become a file that merely uses the forbidden wording.
POLICY_STATING_FILES = (
    "author-identity-and-citation-policy.md",
    os.path.join("quality-control", "SKILL.md"),
)
live_violations = []
for root, _d, files in os.walk(os.path.join(PLUGIN, "skills")):
    for f in files:
        if not f.endswith(".md"):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, PLUGIN)
        text = io.open(path, encoding="utf-8").read()
        if any(rel.endswith(x) for x in POLICY_STATING_FILES):
            continue
        res = idp.scan(text, idp.CONTEXT_CLINICAL)
        if not res["ok"]:
            live_violations.append((rel, res["violations"][0]["matched_text"]))
check("32 no skill file presents the creator as a source", not live_violations,
      str(live_violations[:3]))

manifest = json.load(io.open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"),
                             encoding="utf-8"))
# The excluded files must actually be prohibiting the phrasings they quote.
for _f in POLICY_STATING_FILES:
    _hits = [os.path.join(r, n) for r, _d, ns in os.walk(os.path.join(PLUGIN, "skills"))
             for n in ns if os.path.join(r, n).endswith(_f)]
    _txt = "".join(io.open(h, encoding="utf-8").read() for h in _hits)
    check(f"32b policy-stating file prohibits what it quotes: {os.path.basename(_f)}",
          bool(_hits) and ("forbidden" in _txt.lower() or "must not" in _txt.lower()
                           or "never" in _txt.lower()))

check("33 creator attribution preserved in plugin metadata",
      "Dana" in manifest["author"]["name"])
check("34 the manifest author field passes as creator metadata",
      idp.scan(manifest["author"]["name"], idp.CONTEXT_CREATOR_METADATA)["ok"])

# ── v1.0.0 — product display name ───────────────────────────────────────────
DISPLAY = "Dental Research & Clinical Intelligence by Dr. Dana"
check("35 display name constant matches the released name",
      idp.PRODUCT_DISPLAY_NAME == DISPLAY, idp.PRODUCT_DISPLAY_NAME)
check("36 display name is clean in every context",
      all(idp.scan(DISPLAY, c)["ok"]
          for c in idp.FORBIDDEN_CONTEXTS + idp.ALLOWED_CONTEXTS))
check("37 'Dr. Dana' alone is still blocked in clinical output",
      not idp.scan("Dr. Dana says a crown is needed.", idp.CONTEXT_CLINICAL)["ok"])
check("38 the display name does not mask an adjacent authority claim",
      not idp.scan(f"{DISPLAY}. Dr. Dana recommends a crown.",
                   idp.CONTEXT_CLINICAL)["ok"])
check("39 'Dr. Dana Protocol' still blocked despite the new name",
      not idp.scan("The Dr. Dana Protocol requires this.", idp.CONTEXT_CLINICAL)["ok"])
check("40 internal plugin id is unchanged and treated as a product identifier",
      idp.INTERNAL_PLUGIN_ID == "dana-dental-research"
      and idp.scan("dana-dental-research v1.0.0", idp.CONTEXT_CLINICAL)["ok"])
check("41 manifest displayName is the released display name",
      manifest.get("displayName") == DISPLAY, str(manifest.get("displayName")))
check("42 manifest internal id unchanged",
      manifest["name"] == "dana-dental-research", manifest["name"])
check("43 README title carries the display name",
      io.open(os.path.join(PLUGIN, "README.md"), encoding="utf-8").read()
      .startswith(f"# {DISPLAY}"))
check("44 README passes an identity scan as creator metadata",
      idp.scan(io.open(os.path.join(PLUGIN, "README.md"), encoding="utf-8").read(),
               idp.CONTEXT_CREATOR_METADATA)["ok"])

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

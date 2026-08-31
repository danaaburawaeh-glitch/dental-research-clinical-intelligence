"""
clinical/tests/test_protocol_approval.py

v0.9.0 — the eight checks required for the Clinical Protocol approval gate.
No network.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(os.path.dirname(HERE))
REFS = os.path.join(PLUGIN, "skills", "esthetic-prosthodontics", "references")
GOV = os.path.join(PLUGIN, "skills", "clinical-governance", "references")
DOCS = os.path.join(PLUGIN, "docs")
SKILLS = os.path.join(PLUGIN, "skills")

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def read(*parts):
    return io.open(os.path.join(*parts), encoding="utf-8").read()


REF_FILES = ["prosthodontic-restorability.md", "veneer-crown-decision.md",
             "prosthodontic-risk-factors.md", "treatment-sequencing-principles.md"]
REFS_TEXT = {f: read(REFS, f) for f in REF_FILES}
RECORD = read(DOCS, "CLINICAL_PROTOCOL_APPROVAL_RECORD.md")

# ── 1. No unresolved Appendix C item remains ────────────────────────────────
check("01 approval record states zero open items",
      "Open items remaining: 0" in RECORD)
check("02 all eight items are recorded as CLOSED", RECORD.count("**CLOSED**") == 8,
      f"count={RECORD.count('**CLOSED**')}")
check("03 each item names its basis and whether external or clinic policy",
      RECORD.count("Clinic policy") + RECORD.count("External verification") >= 8)
# The phrase survives only inside the sentence stating it no longer exists; what matters is that
# no reference still USES the tag to mark an unresolved item.
open_uses = [f for f, t in REFS_TEXT.items()
             if re.search(r"\(OPEN\)(?!\s+tag no longer exists)", t)]
check("04 no reference still uses the (OPEN) tag to mark an unresolved item",
      not open_uses, str(open_uses))

# ── 2. No unsupported numeric value was added ───────────────────────────────
NUM = re.compile(r"\b\d+(\.\d+)?\s?mm\b")
offenders = [f for f, t in REFS_TEXT.items() if NUM.search(t)]
check("05 no mm threshold anywhere in the four references", not offenders, str(offenders))
check("06 references state the protocol carries no numeric thickness",
      "states **no numeric minimum at all**" in REFS_TEXT["prosthodontic-restorability.md"]
      or "no numeric thickness" in REFS_TEXT["prosthodontic-restorability.md"])
check("07 approval record confirms numbers were removed, not sourced",
      "Zero numeric thresholds were added — six were removed" in RECORD)

# ── 3. IFU-governed values are traceable ────────────────────────────────────
flat = re.sub(r"\s+", " ", REFS_TEXT["prosthodontic-restorability.md"])
check("08 IFU is named as the binding authority for thickness",
      "binding minimum is the IFU of the product in use" in flat
      and "no numeric minimum" in flat)
check("09 product use is gated on an Appendix B IFU record",
      "recorded in\n  Appendix B with the IFU attached" in REFS_TEXT["prosthodontic-restorability.md"]
      or "Appendix B with the IFU attached" in REFS_TEXT["prosthodontic-restorability.md"])
check("10 failed IFU retrieval is recorded, not silently dropped",
      "IFU retrieval failed" in RECORD or "cannot be\nretrieved" in RECORD
      or "REQUIRES\nVERIFICATION" in RECORD or "REQUIRES VERIFICATION" in RECORD)

# ── 4. Clinic-policy decisions are labelled OPS/JUDG appropriately ──────────
check("11 clinic-policy closures are labelled as such in the record",
      RECORD.count("Clinic policy") >= 6)
check("12 the one externally-verified item is distinguished",
      RECORD.count("**External verification**") == 1)
check("13 item 8 cites the real guideline DOI", "doi:10.1111/jcpe.13290" in RECORD)

# ── 5. v1.2 preserved historically ──────────────────────────────────────────
check("14 record states v1.2 was not modified or overwritten",
      "v1.2 was not modified and not overwritten" in RECORD)
check("15 references warn v1.2 must not be cited as current",
      "must not be cited as current" in REFS_TEXT["prosthodontic-restorability.md"].replace("\n", " ")
      or "never cite it as\ncurrent" in read(SKILLS, "esthetic-prosthodontics", "SKILL.md"))

# ── 6. v1.3 is the approved source ──────────────────────────────────────────
check("16 all four references cite v1.3 APPROVED",
      all("v1.3 (APPROVED)" in t or "v1.3 is\nAPPROVED" in t or "v1.3 is **APPROVED**" in t
          or "**v1.3 APPROVED**" in t for t in REFS_TEXT.values()))
check("17 no reference still cites v1.2 as its source",
      not any("Clinic Protocol v1.2 (WORKING DRAFT)" in t for t in REFS_TEXT.values()))
check("18 the Drive document id is recorded for traceability",
      "1XAU6VWqKnK7JAl6zhGt4SzqlAQx8OOkJaD2AQMqmAzs" in RECORD)

# ── 7. DANA no longer calls the protocol a draft ────────────────────────────
stale = []
for root, _dirs, files in os.walk(SKILLS):
    for f in files:
        if not f.endswith(".md"):
            continue
        path = os.path.join(root, f)
        t = io.open(path, encoding="utf-8").read()
        if "مسودة عمل" in t or "working draft" in t.lower():
            # acceptable only if the same file records the resolution
            if not any(m in t for m in ("no longer applies", "caveat that applied to v1.2 is withdrawn",
                                        "STATUS UPDATE", "general rule")):
                stale.append(os.path.relpath(path, PLUGIN))
check("19 no skill file calls the protocol a current draft", not stale, str(stale))
check("20 the withdrawal of the draft caveat is explicit",
      "caveat that applied to v1.2 is withdrawn" in REFS_TEXT["prosthodontic-restorability.md"])
check("21 quality-control checks for v1.3 citation, not draft citation",
      "Clinic Protocol cited as v1.3 APPROVED" in read(SKILLS, "quality-control", "SKILL.md"))

# ── 8. Approval scope is honest ─────────────────────────────────────────────
check("22 surviving use-gates are stated, not hidden",
      "use gates" in RECORD and "Appendix B is currently empty" in RECORD)
check("23 the signature is reserved to the clinician",
      "signature line remains for Dr Dana" in RECORD)
check("24 no new reference was invented to close the protocol",
      "Zero new references were added" in RECORD)

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

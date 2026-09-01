"""
evidence/tests/test_safety_nonnegotiable.py

The nine things the v1.2 Evidence Intelligence Engine must never do (brief §20), as executable
tests. Each is stated as a prohibition and tested as one: the test passes when the engine
REFUSES, not when it merely happens to behave.

No network. Run: python3 evidence/tests/test_safety_nonnegotiable.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
sys.path.insert(0, EVIDENCE)

import _paths  # noqa: F401,E402

import appraisal as ap          # noqa: E402
import bottom_line as bl        # noqa: E402
import certainty as ce          # noqa: E402
import citation_verification as cv  # noqa: E402
import claim_link as cl         # noqa: E402
import conflict as cf           # noqa: E402
import directness as dr         # noqa: E402
import numeric_gate as ng       # noqa: E402
import pipeline as pl           # noqa: E402
import rank as rk               # noqa: E402
import sr_extraction as sre     # noqa: E402
import study_design as sd       # noqa: E402

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def refuses(fn, exc=Exception):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


SR = sd.classify({"publication_types": ["Systematic Review"]})
RCT = sd.classify({"publication_types": ["Randomized Controlled Trial"]})
LAB = sd.classify({"title": "In vitro microtensile bond strength of universal adhesives"})
REG = sd.classify({"nct_id": "FIXTURE-NCT", "study_type": "INTERVENTIONAL"})
CASE = sd.classify({"publication_types": ["Case Reports"]})
FULL_DOMAINS = {"risk_of_bias": ce.NOT_SERIOUS, "inconsistency": ce.NOT_SERIOUS,
                "imprecision": ce.NOT_SERIOUS, "publication_bias": ce.NOT_SERIOUS}
DIRECT_ALL = dr.assess({d: dr.HIGH for d in dr.DIMENSIONS})


def claim(design, certainty_rating, directness_verdict, state=cv.VERIFIED, limitations=None):
    return cl.EvidenceLinkedClaim(
        "Intervention A improves outcome X.", "FIXTURE-CITATION", state, design,
        type("C", (), {"rating": certainty_rating})(),
        type("D", (), {"verdict": directness_verdict})(),
        limitations=limitations)


# ══ 1. Never equate a VERIFIED citation with strong evidence ════════════════════════════════
print("\n── 1. A VERIFIED citation is never strong evidence ──")

result = cv.verify_citation(
    {"source": "pubmed", "doi": "10.1/x", "title": "T", "authors": ["Smith J"], "journal": "J Dent",
     "publication_year": 2019, "is_retracted": False, "publication_status": "active"},
    {"source": "crossref", "doi": "10.1/x", "title": "T", "authors": ["Smith J"],
     "journal": "Journal of Dentistry", "publication_year": 2019})
check("01 verification returns no evidential-strength value",
      result["state"] == cv.VERIFIED and result["evidential_strength"] is None)
check("02 verification result says in words that it is not a strength claim",
      "nothing whatever about how strong" in result["evidential_strength_note"])

weak = claim(CASE, ce.VERY_LOW, dr.PARTIALLY_DIRECT, cv.VERIFIED)
check("03 a VERIFIED citation with VERY LOW certainty and no stated limitation is flagged",
      any("verified citation is not strong evidence" in p["reason"] for p in weak.problems()))

line = bl.ClinicalBottomLine("q")
line.add(bl.WELL_ESTABLISHED, "Intervention A improves outcome X.",
         claim(CASE, ce.VERY_LOW, dr.PARTIALLY_DIRECT, cv.VERIFIED, ["single case series"]))
report = line.validate()
check("04 a VERIFIED but low-certainty claim is moved out of 'well established'",
      report["demotions"] and report["demotions"][0]["to_section"] == bl.UNCERTAIN)

# ══ 2 & 3. Never fabricate a PMID or a DOI ══════════════════════════════════════════════════
print("\n── 2/3. Identifiers are never invented ──")

empty = cv.verify_citation(None, None)
check("05 nothing retrieved yields NOT_VERIFIED, not a constructed citation",
      empty["state"] == cv.NOT_VERIFIED and empty["sources_consulted"] == [])
check("06 an unverified claim may not back a consequential statement",
      empty["may_support_clinical_claim"] is False)

no_ids = cv.verify_citation({"source": "pubmed", "title": "T"}, None)
check("07 a record with no DOI is PARTIALLY_VERIFIED, and no DOI is supplied for it",
      no_ids["state"] == cv.PARTIALLY_VERIFIED
      and no_ids["components"][cv.DOI_MATCH]["value_a"] in (None, ""))

unver = cl.EvidenceLinkedClaim("A works.", None, cv.NOT_VERIFIED, SR,
                               type("C", (), {"rating": ce.LOW})(),
                               type("D", (), {"verdict": dr.DIRECT})())
check("08 an unverified consequential claim fails, and is told to carry a search strategy",
      unver.audit()["result"] == cl.FAIL
      and any("search strategy" in p["reason"] for p in unver.problems()))

benchmark = open(os.path.join(EVIDENCE, "benchmark", "benchmark_questions.json")).read()
import re  # noqa: E402
check("09 the benchmark file contains no PMID-shaped identifier",
      not re.search(r'"pmid"\s*:\s*"?\d{7,8}', benchmark))
check("10 the benchmark file contains no DOI",
      "10." not in benchmark or not re.search(r"\b10\.\d{4,9}/", benchmark))
check("11 the benchmark file contains no real-shaped NCT id",
      not re.search(r"NCT\d{8}", benchmark))

# ══ 4. Never invent a GRADE rating ══════════════════════════════════════════════════════════
print("\n── 4. GRADE is never asserted on the authors' behalf ──")

own = ce.assess(RCT, None, DIRECT_ALL, FULL_DOMAINS)
check("12 the engine's own rating is not labelled GRADE",
      own.label == ce.ASSESSMENT_LABEL and own.to_dict()["is_grade"] is False)
check("13 the engine's own rating states in words that it is not GRADE",
      "NOT a GRADE rating" in own.to_dict()["not_grade_note"])
check("14 an author-reported GRADE without attribution is refused",
      refuses(lambda: ce.AuthorReportedGrade(ce.HIGH, "survival", None), ValueError))
check("15 an author-reported GRADE without a named outcome is refused",
      refuses(lambda: ce.AuthorReportedGrade(ce.HIGH, None, "Author et al."), ValueError))

attributed = ce.AuthorReportedGrade(ce.MODERATE, "5-year survival", "the review authors")
check("16 an attributed GRADE is marked as not produced by this system",
      attributed.to_dict()["produced_by_this_system"] is False)

carried = ce.assess(RCT, None, DIRECT_ALL, FULL_DOMAINS, author_grade=attributed)
check("17 an author GRADE is carried through unchanged alongside the system's own rating",
      carried.to_dict()["author_reported_grade"]["rating"] == ce.MODERATE
      and carried.rating == ce.HIGH)
check("18 the engine never upgrades certainty",
      carried.to_dict()["upgrades_applied"] is None
      and "never upgrades" in carried.to_dict()["upgrade_policy"])

# ══ 5. Never invent a sample size ═══════════════════════════════════════════════════════════
print("\n── 5. Appraisal values are never invented ──")

bare = ap.appraise({"pmid": "FIXTURE-1"}, RCT)
check("19 every appraisal field defaults to UNKNOWN, not to a plausible value",
      all(getattr(bare, f).value is None for f in ap.APPRAISAL_FIELDS if f != "study_design"))
check("20 an INFERRED value without a stated basis is refused",
      refuses(lambda: ap.inferred(120, None), ap.ProvenanceError))
check("21 a REPORTED field with no value is refused",
      refuses(lambda: ap.AppraisalField(None, ap.REPORTED), ap.ProvenanceError))
check("22 a value carrying UNKNOWN provenance is refused",
      refuses(lambda: ap.AppraisalField(120, ap.UNKNOWN), ap.ProvenanceError))
check("23 a bare value cannot be passed as an appraisal field",
      refuses(lambda: ap.Appraisal(sample_size=120), ap.ProvenanceError))
check("24 a formal tool is refused where its required domains are missing",
      refuses(lambda: ap.risk_of_bias(RCT, ap.ROB2, {"randomisation_process": "low"}), ValueError))
check("25 a formal tool is refused where it does not apply to the design",
      refuses(lambda: ap.risk_of_bias(RCT, ap.AMSTAR2,
                                      {d: "yes" for d in ap.TOOL_REQUIRED_DOMAINS[ap.AMSTAR2]}),
              ValueError))

profile = sre.from_abstract({"pmid": "FIXTURE-2"}, SR)
check("26 unretrieved review fields are NOT AVAILABLE, not blank and not filled",
      profile.absent_fields()["total_participants"] == sre.NOT_AVAILABLE)
check("27 a full-text-sourced field is refused when no full text was retrieved",
      refuses(lambda: sre.SystematicReviewProfile(
          design_classification=SR, full_text_retrieved=False,
          grade_method=ap.reported("GRADE applied", ap.FROM_FULL_TEXT)), ap.ProvenanceError))

# ══ 6. Never invent an effect estimate ══════════════════════════════════════════════════════
print("\n── 6. Effect estimates are never reconstructed ──")

text = "Survival was 95% at 10 years (RR 0.62, 95% CI 0.41-0.93)."
check("28 an unregistered effect estimate fails the numeric gate",
      ng.gate_bottom_line(text)["result"] == ng.FAIL)
check("29 the gate names every unregistered figure it found",
      len(ng.gate_bottom_line(text)["failures"]) >= 3)
check("30 a number whose source was not retrieved this session cannot be VERIFIED",
      refuses(lambda: ng.NumericClaim("95%", ng.VERIFIED, "FIXTURE-1", cv.VERIFIED,
                                      retrieved_this_session=False), ValueError))
check("31 a number with no source record cannot be VERIFIED",
      refuses(lambda: ng.NumericClaim("95%", ng.VERIFIED, None, cv.VERIFIED, True), ValueError))
check("32 a number carried by a retracted source is refused",
      refuses(lambda: ng.NumericClaim("95%", ng.VERIFIED, "FIXTURE-1", cv.RETRACTED, True),
              ValueError))
check("33 a CALCULATED number must show its calculation",
      refuses(lambda: ng.NumericClaim("50%", ng.CALCULATED, None), ValueError))

ledger = ng.NumericLedger()
ledger.register(ng.NumericClaim("95%", ng.TYPICAL_RANGE_VERIFY, description="typical range"))
check("34 a TYPICAL RANGE figure is not permitted in a Clinical Bottom Line",
      ng.gate_bottom_line("Survival is about 95%.", ledger)["result"] == ng.FAIL)

# ══ 7. Never hide conflicting evidence ══════════════════════════════════════════════════════
print("\n── 7. Conflicts are surfaced, never averaged ──")

a = cf.EvidenceSource("FIXTURE-A", "Favours the intervention.", cf.FAVOURS_INTERVENTION,
                      SR, ce.MODERATE, dr.DIRECT, population="adults", follow_up="6 months")
b = cf.EvidenceSource("FIXTURE-B", "Finds no difference.", cf.NO_DIFFERENCE,
                      SR, ce.MODERATE, dr.DIRECT, population="adults", follow_up="12 months")
detected = cf.detect([a, b])
check("35 two comparable sources pointing different ways produce an EVIDENCE CONFLICT",
      len(detected["conflicts"]) == 1)

conflict = detected["conflicts"][0].to_dict()
check("36 a conflict emits no pooled estimate", conflict["pooled_estimate"] is None)
check("37 the no-averaging rule travels with the conflict",
      "never averaged" in conflict["no_averaging_rule"])
check("38 both sources are reported in full",
      conflict["source_a"]["record_id"] == "FIXTURE-A"
      and conflict["source_b"]["record_id"] == "FIXTURE-B")
check("39 every comparison dimension is answered, including the unestablished ones",
      set(conflict["differences"]) == set(cf.COMPARISON_DIMENSIONS)
      and "methods" in conflict["unexplained_dimensions"])
check("40 the module offers no averaging function at all",
      not any("average" in n or "pool" in n for n in dir(cf) if not n.startswith("_")))

weakling = cf.EvidenceSource("FIXTURE-C", "Favours the comparator.", cf.FAVOURS_COMPARATOR,
                             CASE, ce.VERY_LOW, dr.INDIRECT)
mixed = cf.detect([a, weakling])
check("41 a weak dissenting source is a quality note, not an equal counterweight",
      not mixed["conflicts"] and mixed["quality_notes"]
      and mixed["quality_notes"][0]["type"] == cf.SUPERSEDED_BY_QUALITY)

# ══ 8. Never treat a registry entry as proof of efficacy ════════════════════════════════════
print("\n── 8. A registration is not a result ──")

check("42 a registry record carries its hard label",
      REG.to_dict()["hard_label"] == sd.REGISTRY_LABEL)
check("43 a registry record cannot support a clinical outcome claim",
      REG.supports_clinical_outcome_claims is False)
check("44 a registry record is NOT ASSESSABLE on the certainty scale",
      ce.assess(REG, None, DIRECT_ALL, FULL_DOMAINS).rating == ce.NOT_ASSESSABLE)
check("45 a registry record is capped at INDIRECT however its dimensions rate",
      dr.assess({d: dr.HIGH for d in dr.DIMENSIONS}, REG).verdict == dr.INDIRECT)

registry_claim = claim(REG, ce.NOT_ASSESSABLE, dr.INDIRECT, cv.VERIFIED)
check("46 a claim resting on a registry record fails at CRITICAL",
      registry_claim.audit()["result"] == cl.FAIL
      and any(sd.REGISTRY_LABEL in p["reason"] for p in registry_claim.problems()))

# ══ 9. Never treat in-vitro evidence as equivalent to patient evidence ══════════════════════
print("\n── 9. The laboratory firewall holds ──")

check("47 a laboratory record carries the firewall label",
      LAB.lab_firewall is True and LAB.to_dict()["hard_label"] == sd.LAB_FIREWALL_LABEL)
check("48 a laboratory record cannot support a clinical outcome claim",
      LAB.supports_clinical_outcome_claims is False)
check("49 a laboratory record is capped at INDIRECT with the cap made visible",
      dr.assess({d: dr.HIGH for d in dr.DIMENSIONS}, LAB).capped_from == dr.DIRECT)
check("50 a laboratory record is NOT ASSESSABLE on the clinical certainty scale",
      ce.assess(LAB, None, DIRECT_ALL, FULL_DOMAINS).rating == ce.NOT_ASSESSABLE)
check("51 a laboratory record is tagged (LAB), never an L-tier",
      sd.del7_tag(LAB) == "LAB")
check("52 (LAB) sits off the clinical ladder in ranking, not at the bottom of it",
      rk.RankedItem("FIXTURE-LAB", "LAB", ce.NOT_ASSESSABLE, dr.INDIRECT).on_clinical_ladder is False)

lab_claim = claim(LAB, ce.NOT_ASSESSABLE, dr.INDIRECT, cv.VERIFIED)
check("53 a clinical claim resting on a laboratory record fails at CRITICAL",
      lab_claim.audit()["result"] == cl.FAIL)

# ══ Retraction — the most severe individual failure mode ════════════════════════════════════
print("\n── Retraction: excluded before classification, never in synthesis ──")

records = [
    {"pmid": "FIXTURE-CLEAN", "title": "A clean trial", "publication_types": ["Randomized Controlled Trial"],
     "is_retracted": False, "publication_status": "active"},
    {"pmid": "FIXTURE-RETRACTED", "title": "A retracted trial",
     "publication_types": ["Randomized Controlled Trial"], "is_retracted": True,
     "publication_status": "retracted", "retraction_source": "pubmed"},
]
p = pl.EvidencePipeline("q").retrieve(records, "SUCCESS").verify()
retracted = [r for r in p.records if r.record_id == "FIXTURE-RETRACTED"][0]
check("54 a retracted record is excluded at the verification stage",
      retracted.is_excluded and retracted.excluded_at == pl.VERIFICATION)
check("55 a retracted record is never classified as usable evidence",
      retracted.design_classification is None)

p.appraise().assess_certainty()
check("56 a retracted record still has no design classification after appraisal ran",
      retracted.design_classification is None)
synth = p.synthesise()
check("57 a retracted record appears in no synthesis bucket",
      all("FIXTURE-RETRACTED" not in [r.record_id for r in v] for v in synth["buckets"].values()))
check("58 a retracted record is reported as excluded provenance",
      [r.record_id for r in synth["excluded"]] == ["FIXTURE-RETRACTED"])

retracted_verification = cv.verify_citation(records[1], None)
check("59 a retracted record's headline citation state is RETRACTED",
      retracted_verification["state"] == cv.RETRACTED)
check("60 a retracted record may not support a clinical claim",
      retracted_verification["may_support_clinical_claim"] is False)
check("61 the bibliographic reading survives alongside the retraction",
      retracted_verification["bibliographic_state"] == cv.PARTIALLY_VERIFIED)

# ══ Stage separation ════════════════════════════════════════════════════════════════════════
print("\n── The six stages cannot collapse into one another ──")

check("62 appraisal cannot run before verification",
      refuses(lambda: pl.EvidencePipeline().appraise(), pl.StageError))
check("63 synthesis cannot run before certainty",
      refuses(lambda: pl.EvidencePipeline().retrieve([]).verify().synthesise(), pl.StageError))
check("64 applicability is the last stage, separate from certainty",
      pl.STAGES[-1] == pl.APPLICABILITY and pl.STAGES.index(pl.CERTAINTY) < len(pl.STAGES) - 1)
check("65 ranking by publication date is not available",
      refuses(lambda: rk.sort_by_recency([]), NotImplementedError))

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

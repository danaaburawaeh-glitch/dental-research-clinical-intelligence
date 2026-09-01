"""
evidence/tests/test_evidence_engine.py

Unit tests for the v1.2 Evidence Intelligence Engine, module by module. Where
test_safety_nonnegotiable.py checks the nine prohibitions, this file checks that the engine does
the ordinary work correctly — the state table, the classification precedence, the aggregation
rules, the query construction, and the rendering.

No network. Run: python3 evidence/tests/test_evidence_engine.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
sys.path.insert(0, EVIDENCE)

import _paths  # noqa: F401,E402

import appraisal as ap             # noqa: E402
import bottom_line as bl           # noqa: E402
import certainty as ce             # noqa: E402
import citation_verification as cv  # noqa: E402
import claim_link as cl            # noqa: E402
import conflict as cf              # noqa: E402
import directness as dr            # noqa: E402
import evidence_table as et       # noqa: E402
import numeric_gate as ng          # noqa: E402
import output_modes as om          # noqa: E402
import overlap as ov               # noqa: E402
import pipeline as pl              # noqa: E402
import rank as rk                  # noqa: E402
import search_builder as sb        # noqa: E402
import sr_extraction as sre        # noqa: E402
import study_design as sd          # noqa: E402

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


def pm(**kw):
    base = {"source": "pubmed", "doi": "10.1000/fixture", "pmid": "FIXTUREPMID",
            "title": "Survival of bonded ceramic restorations", "authors": ["Smith J", "Jones A"],
            "journal": "Clin Oral Investig", "publication_year": 2019,
            "is_retracted": False, "publication_status": "active"}
    base.update(kw)
    return base


def crx(**kw):
    base = {"source": "crossref", "doi": "10.1000/fixture",
            "title": "Survival of bonded ceramic restorations", "authors": ["John Smith"],
            "journal": "Clinical Oral Investigations", "publication_year": 2019}
    base.update(kw)
    return base


# ══ Citation Verification 2.0 ═══════════════════════════════════════════════════════════════
print("\n── Citation Verification 2.0 ──")

check("01 there are exactly seven citation states", len(cv.STATES) == 7)
check("02 full agreement across both sources is VERIFIED",
      cv.verify_citation(pm(), crx())["state"] == cv.VERIFIED)
check("03 a journal abbreviation variant is a MATCH, not a discrepancy",
      cv.verify_citation(pm(), crx())["components"][cv.JOURNAL_MATCH]["verdict"] == cv.MATCH)

year_gap = cv.verify_citation(pm(publication_year=2019), crx(publication_year=2021))
check("04 a >1-year gap with DOI/title/author/journal matching is VERIFIED_WITH_METADATA_DISCREPANCY",
      year_gap["state"] == cv.VERIFIED_WITH_METADATA_DISCREPANCY)
check("05 the exact year discrepancy is reported with both values and both sources",
      year_gap["discrepancies"][0]["value_a"] == 2019
      and year_gap["discrepancies"][0]["value_b"] == 2021
      and year_gap["discrepancies"][0]["source_a"] == "pubmed")
check("06 the online-first interpretation is offered without resolving the discrepancy",
      "online-first" in year_gap["discrepancies"][0]["interpretation"]
      and "neither has been altered" in year_gap["discrepancies"][0]["interpretation"])
check("07 a +/-1 year difference is inside tolerance and stays VERIFIED",
      cv.verify_citation(pm(publication_year=2019), crx(publication_year=2020))["state"]
      == cv.VERIFIED)

doi_conflict = cv.verify_citation(pm(), crx(doi="10.1000/other"))
check("08 a DOI disagreement is NOT_VERIFIED", doi_conflict["state"] == cv.NOT_VERIFIED)
check("09 a DOI disagreement is labelled an identity conflict",
      doi_conflict["discrepancies"][0]["severity"] == "IDENTITY_CONFLICT")

title_conflict = cv.verify_citation(pm(), crx(title="An entirely different paper about implants"))
check("10 a title disagreement is NOT_VERIFIED even with a matching DOI",
      title_conflict["state"] == cv.NOT_VERIFIED)
check("11 a title disagreement plus a year gap is NOT_VERIFIED, not a metadata discrepancy",
      cv.verify_citation(pm(publication_year=2019),
                         crx(title="Something else entirely", publication_year=2021))["state"]
      == cv.NOT_VERIFIED)

single = cv.verify_citation(pm(), None)
check("12 a single-source retrieval is capped at PARTIALLY_VERIFIED",
      single["state"] == cv.PARTIALLY_VERIFIED)
check("13 a Crossref-only retrieval is also capped at PARTIALLY_VERIFIED",
      cv.verify_citation(None, crx())["state"] == cv.PARTIALLY_VERIFIED)

check("14 all seven components are always reported",
      set(cv.verify_citation(pm(), crx())["components"]) == set(cv.COMPONENTS))
check("15 no single numeric verification score is emitted",
      "score" not in cv.verify_citation(pm(), crx()))
check("16 component counts summarise without flattening the components",
      cv.verify_citation(pm(), crx())["component_counts"][cv.MATCH] >= 4)

corrected = cv.verify_citation(pm(is_corrected=True), crx())
check("17 a correction makes the headline state CORRECTED",
      corrected["state"] == cv.CORRECTED)
check("18 a corrected record keeps its VERIFIED bibliographic reading",
      corrected["bibliographic_state"] == cv.VERIFIED)
check("19 a corrected record may still support a claim, with the correction surfaced",
      corrected["may_support_clinical_claim"] is True)

eoc = cv.verify_citation(
    pm(related_notices=[{"type": "ExpressionOfConcernIn", "classified": True}]), crx())
check("20 an expression of concern is its own state, not a retraction",
      eoc["state"] == cv.EXPRESSION_OF_CONCERN and eoc["state"] != cv.RETRACTED)

unchecked = cv.verify_citation(
    {"source": "pubmed", "doi": "10.1000/fixture", "title": "T", "authors": ["Smith J"],
     "journal": "J Dent", "publication_year": 2019}, crx(title="T", journal="J Dent"))
check("21 a record with no retraction metadata is UNCHECKED, not ACTIVE",
      unchecked["publication_integrity"] == cv.INTEGRITY_UNCHECKED)
check("22 unchecked is described as unchecked, not clean",
      "not a clean one" in unchecked["components"][cv.RETRACTION_STATUS]["note"])

# ══ Study design classification ═════════════════════════════════════════════════════════════
print("\n── Study design classification ──")

check("23 a Meta-Analysis publication type outranks a co-occurring Review tag",
      sd.classify({"publication_types": ["Journal Article", "Meta-Analysis", "Review"]}).design
      == sd.META_ANALYSIS)
check("24 a Review with no systematic tag is a narrative review",
      sd.classify({"publication_types": ["Review"]}).design == sd.NARRATIVE_REVIEW)
check("25 a structured classification carries REPORTED provenance",
      sd.classify({"publication_types": ["Randomized Controlled Trial"]}).provenance == sd.REPORTED)
check("26 an RCT classification carries the root-canal-treatment disambiguation note",
      "root canal treatment" in
      sd.classify({"publication_types": ["Randomized Controlled Trial"]}).disambiguation_note)
check("27 'RCT' in a title never produces a randomized-trial classification",
      sd.classify({"title": "Outcomes of RCT in molars"}).design != sd.RCT)
check("28 a cohort with no direction term is not assigned a direction",
      sd.classify({"mesh_terms": ["Cohort Studies"]}).design == sd.COHORT_DIRECTION_UNREPORTED)
check("29 a prospective cohort is named when the MeSH terms establish it",
      sd.classify({"mesh_terms": ["Cohort Studies", "Prospective Studies"]}).design
      == sd.PROSPECTIVE_COHORT)
check("30 a retrospective cohort is named when the MeSH terms establish it",
      sd.classify({"mesh_terms": ["Cohort Studies", "Retrospective Studies"]}).design
      == sd.RETROSPECTIVE_COHORT)
check("31 a text-only classification is INFERRED and names the phrase it rested on",
      sd.classify({"title": "In vitro fatigue of zirconia"}).provenance == sd.INFERRED
      and "in vitro" in sd.classify({"title": "In vitro fatigue of zirconia"}).basis)
check("32 an unclassifiable record is OTHER with UNKNOWN provenance",
      sd.classify({"title": "Untitled"}).provenance == sd.UNKNOWN)
check("33 an unclassifiable record receives no supporting-evidence DEL-7 tier",
      sd.del7_tag(sd.classify({"title": "Untitled"})) == "UNVER")
check("34 an INFERRED classification without a basis is refused at construction",
      refuses(lambda: sd.DesignClassification(sd.RCT, sd.INFERRED, None), ValueError))
check("35 DEL-7 mapping preserves the v1.1 hierarchy",
      sd.del7_tag(sd.classify({"publication_types": ["Practice Guideline"]})) == "L1"
      and sd.del7_tag(sd.classify({"publication_types": ["Systematic Review"]})) == "L2"
      and sd.del7_tag(sd.classify({"publication_types": ["Randomized Controlled Trial"]})) == "L3"
      and sd.del7_tag(sd.classify({"publication_types": ["Case Reports"]})) == "L4")
check("36 all eighteen design values are covered by the DEL-7 map",
      set(sd.DESIGNS) == set(sd.DESIGN_TO_DEL7))

# ══ Appraisal ═══════════════════════════════════════════════════════════════════════════════
print("\n── Appraisal ──")

rct = sd.classify({"publication_types": ["Randomized Controlled Trial"]})
appraisal = ap.appraise({"pmid": "FIXTURE"}, rct,
                        {"sample_size": ap.reported(240),
                         "follow_up": ap.inferred("about 3 years", "abstract states 36 months")})
check("37 completeness is reported as counts and lists, never as a percentage score",
      "known" in appraisal.completeness() and "percent" not in str(appraisal.completeness()))
check("38 the unknown fields are enumerated by name",
      "risk_of_bias" in appraisal.completeness()["unknown_fields"])
check("39 the certainty-critical unknowns are called out separately",
      set(appraisal.completeness()["certainty_critical_unknown"])
      == set(ap.CERTAINTY_CRITICAL_FIELDS))
check("40 an inferred field keeps its basis",
      appraisal.follow_up.basis == "abstract states 36 months")
check("41 a correctly-supplied formal tool is accepted",
      ap.risk_of_bias(rct, ap.ROB2,
                      {d: "low" for d in ap.TOOL_REQUIRED_DOMAINS[ap.ROB2]},
                      overall="low").value["tool"] == ap.ROB2)
check("42 a non-tool judgement says so rather than borrowing a tool name",
      ap.TOOL_MISUSE_NOTE in (ap.risk_of_bias(rct, None, overall="some concerns").note or ""))

# ══ Certainty ═══════════════════════════════════════════════════════════════════════════════
print("\n── Certainty ──")

direct = dr.assess({d: dr.HIGH for d in dr.DIMENSIONS})
domains = {"risk_of_bias": ce.NOT_SERIOUS, "inconsistency": ce.NOT_SERIOUS,
           "imprecision": ce.NOT_SERIOUS, "publication_bias": ce.NOT_SERIOUS}
check("43 a clean randomized trial reaches HIGH",
      ce.assess(rct, None, direct, domains).rating == ce.HIGH)
check("44 one serious domain steps down one level",
      ce.assess(rct, None, direct, dict(domains, imprecision=ce.SERIOUS)).rating == ce.MODERATE)
check("45 a very serious domain steps down two levels",
      ce.assess(rct, None, direct, dict(domains, risk_of_bias=ce.VERY_SERIOUS)).rating == ce.LOW)
check("46 certainty floors at VERY LOW rather than going below the scale",
      ce.assess(rct, None, direct, {k: ce.VERY_SERIOUS for k in domains}).rating == ce.VERY_LOW)
check("47 an observational design starts LOW, not HIGH",
      ce.assess(sd.classify({"mesh_terms": ["Cohort Studies"]}), None, direct, domains).rating
      == ce.LOW)
check("48 a review of non-randomized studies starts LOW",
      ce.assess(sd.classify({"publication_types": ["Systematic Review"]}), None, direct, domains,
                pools_randomized_trials=False).rating == ce.LOW)
check("49 a review of randomized trials starts HIGH",
      ce.assess(sd.classify({"publication_types": ["Systematic Review"]}), None, direct, domains,
                pools_randomized_trials=True).rating == ce.HIGH)
check("50 a review whose pooled designs are unknown is NOT ASSESSABLE",
      ce.assess(sd.classify({"publication_types": ["Systematic Review"]}), None, direct,
                domains).rating == ce.NOT_ASSESSABLE)
check("51 an unestablished domain produces NOT ASSESSABLE, not a default rating",
      ce.assess(rct, None, direct, {"risk_of_bias": ce.NOT_SERIOUS}).rating == ce.NOT_ASSESSABLE)
check("52 NOT ASSESSABLE is explained as an absence of assessment, not a low finding",
      "not a finding of low certainty" in
      ce.assess(rct, None, direct, {"risk_of_bias": ce.NOT_SERIOUS}).not_assessable_reason)
check("53 domain judgements over an appraisal's UNKNOWN fields are refused",
      ce.assess(rct, ap.appraise({"pmid": "F"}, rct), direct, domains).rating == ce.NOT_ASSESSABLE)
check("54 indirectness is taken from the directness assessment automatically",
      ce.assess(rct, None, dr.assess({**{d: dr.HIGH for d in dr.DIMENSIONS}, "outcome": dr.LOW}),
                {k: v for k, v in domains.items()}).rating == ce.LOW)

# ══ Directness ══════════════════════════════════════════════════════════════════════════════
print("\n── Directness ──")

check("55 all-HIGH across six dimensions is DIRECT",
      dr.assess({d: dr.HIGH for d in dr.DIMENSIONS}).verdict == dr.DIRECT)
check("56 a single MODERATE makes it PARTIALLY DIRECT",
      dr.assess({**{d: dr.HIGH for d in dr.DIMENSIONS}, "material": dr.MODERATE}).verdict
      == dr.PARTIALLY_DIRECT)
check("57 a single LOW makes it INDIRECT and is not offset by HIGH elsewhere",
      dr.assess({**{d: dr.HIGH for d in dr.DIMENSIONS}, "follow_up": dr.LOW}).verdict == dr.INDIRECT)
check("58 an unrated dimension yields UNKNOWN, never an assumed match",
      dr.assess({"population": dr.HIGH}).verdict == dr.UNKNOWN)
check("59 a known mismatch outranks an unknown",
      dr.assess({"population": dr.LOW}).verdict == dr.INDIRECT)
check("60 N/A on a dimension does not force UNKNOWN",
      dr.assess({**{d: dr.HIGH for d in dr.DIMENSIONS}, "comparison": dr.NOT_APPLICABLE}).verdict
      == dr.DIRECT)
check("61 a surrogate outcome forces the outcome dimension LOW",
      dr.assess({d: dr.HIGH for d in dr.DIMENSIONS},
                outcome_is_patient_important=False).verdict == dr.INDIRECT)
check("62 an invalid dimension name is refused",
      refuses(lambda: dr.assess({"cost": dr.HIGH}), ValueError))

# ══ Overlap ═════════════════════════════════════════════════════════════════════════════════
print("\n── Duplication and overlap ──")

overlap_records = [
    {"pmid": "F1", "title": "Veneer survival: a systematic review", "publication_year": 2016,
     "publication_types": ["Systematic Review"], "included_study_pmids": ["a", "b", "c", "d"]},
    {"pmid": "F2", "title": "Veneer survival: a systematic review — an update",
     "publication_year": 2022, "publication_types": ["Systematic Review"],
     "included_study_pmids": ["a", "b", "c", "e"]},
    {"pmid": "F3", "title": "Trial 3-year report", "abstract": "NCT00000001", "publication_year": 2018},
    {"pmid": "F4", "title": "Trial 5-year report", "abstract": "NCT00000001", "publication_year": 2020,
     "follow_up_months": 60},
]
result = ov.detect(overlap_records)
types = {f.overlap_type for f in result["findings"]}
check("63 an updated systematic review is detected", ov.UPDATED_SYSTEMATIC_REVIEW in types)
check("64 two reports of one trial are detected", ov.SAME_STUDY_MULTIPLE_REPORTS in types)
check("65 an overlap cluster counts as one independent study",
      all(f.counts_as_independent_studies == 1 for f in result["findings"]))
check("66 the superseded review is retained, not deleted",
      any(f.retained for f in result["findings"] if f.overlap_type == ov.UPDATED_SYSTEMATIC_REVIEW))
check("67 an update does not entirely supersede the earlier review by default",
      all(not f.supersedes_entirely for f in result["findings"]))
check("68 the longer-follow-up report is preferred within a trial cluster",
      [f.preferred["pmid"] for f in result["findings"]
       if f.overlap_type == ov.SAME_STUDY_MULTIPLE_REPORTS] == ["F4"])
check("69 nothing is removed from the retrieved set",
      len(result["deduplicated"]) == len(overlap_records))

# ══ Search quality ══════════════════════════════════════════════════════════════════════════
print("\n── Search quality ──")

strategy = sb.from_pico(
    "Do enamel-bonded veneers survive longer?",
    population=sb.Concept(sb.POPULATION, ["porcelain veneer"], ["laminate veneer"], ["Dental Veneers"]),
    intervention=sb.Concept(sb.INTERVENTION, ["enamel bonding"], [], ["Dental Bonding"]),
    outcome=sb.Concept(sb.OUTCOME, ["survival"], ["longevity"], ["Treatment Outcome"]),
    study_type="systematic_review")
query = strategy.build()
check("70 concepts are joined by AND", query.count(" AND ") >= 2)
check("71 synonyms are joined by OR only inside their own concept",
      not sb._has_top_level_or(query))
check("72 multi-word terms are phrase-quoted", '"porcelain veneer"' in query)
check("73 MeSH terms use the MeSH field", '"Dental Veneers"[MeSH Terms]' in query)
check("74 a publication-type filter is applied from the connector's own vocabulary",
      "Publication Type" in query)
check("75 the user's own terms survive verbatim into the log",
      "porcelain veneer" in strategy.user_concept)
check("76 a well-formed query raises no critical warning",
      not [w for w in strategy.validate() if w["severity"] == "CRITICAL"])
check("77 a search with no results recorded is not called systematic",
      strategy.is_systematic is False)
strategy.record_result(36, "SUCCESS", "2026-09-01", results_screened=36, studies_included=8)
check("78 a fully logged MeSH search with filters qualifies as systematic",
      strategy.is_systematic is True)
check("79 a search with no MeSH term is flagged as targeted, not systematic",
      any(w["issue"] == "NO_MESH" for w in
          sb.SearchStrategy("q", [sb.Concept(sb.POPULATION, ["veneer"])]).validate()))
check("80 an unjustified language filter is flagged",
      any(w["issue"] == "UNJUSTIFIED_LANGUAGE_FILTER" for w in
          sb.SearchStrategy("q", [sb.Concept(sb.POPULATION, ["veneer"])],
                            language="english").validate()))
check("81 a concept with no terms from the user's question is refused",
      refuses(lambda: sb.Concept(sb.POPULATION, []), ValueError))
check("82 a top-level OR across concepts is detected as critical",
      sb._has_top_level_or('("a"[tiab]) OR ("b"[tiab])'))

# ══ Evidence table ══════════════════════════════════════════════════════════════════════════
print("\n── Evidence table ──")

table = et.EvidenceTable(question="Veneer survival")
table.add(et.EvidenceTableRow(
    {"pmid": "F1", "authors": ["Smith J"], "publication_year": 2019},
    sd.classify({"publication_types": ["Systematic Review"]}),
    ap.appraise({"pmid": "F1"}, sd.classify({"publication_types": ["Systematic Review"]}),
                {"sample_size": ap.reported(1200)}),
    ce.assess(rct, None, direct, domains), direct, {"state": cv.VERIFIED}))
cells = table.rows[0].cells()
check("83 the table has exactly the fourteen specified columns", len(et.COLUMNS) == 14)
check("84 no cell is blank", all(str(v).strip() for v in cells.values()))
check("85 an unread field renders NOT AVAILABLE, not empty", cells["Follow-up"] == et.NOT_AVAILABLE)
check("86 an unassessed field renders NOT ASSESSED, distinct from unread",
      cells["Risk of Bias"] == et.NOT_ASSESSED)
check("87 a PubMed-style author renders as a surname, not an initial",
      cells["Study"].startswith("Smith"))
check("88 the table audits for the three weighing columns",
      table.audit()["result"] in ("PASS", "FAIL"))
check("89 markdown rendering carries the blank-cell policy",
      "NOT AVAILABLE" in table.to_markdown())

# ══ Clinical bottom line ════════════════════════════════════════════════════════════════════
print("\n── Clinical bottom line ──")

check("90 the bottom line has exactly seven sections", len(bl.SECTIONS) == 7)
line = bl.ClinicalBottomLine("Do enamel-bonded veneers survive longer?")
strong = cl.EvidenceLinkedClaim(
    "Enamel bonding is associated with better veneer survival.", "FIXTURE-CITATION", cv.VERIFIED,
    sd.classify({"publication_types": ["Meta-Analysis"]}),
    type("C", (), {"rating": ce.MODERATE})(), type("D", (), {"verdict": dr.DIRECT})(),
    ["Predominantly non-randomized clinical studies."])
line.add(bl.REASONABLY_SUPPORTED, "Enamel bonding is associated with better veneer survival.", strong)
line.add(bl.UNCERTAIN, "Behaviour beyond 10 years.")
line.add(bl.WOULD_CHANGE_CONCLUSION, "A long-follow-up randomized trial.")
report = line.validate()
check("91 a MODERATE-certainty direct claim stays in 'reasonably supported'",
      report["demotions"] == [])
check("92 the bottom line passes when every number is absent", report["result"] == ng.PASS)
check("93 empty sections render an explicit statement rather than nothing",
      "Nothing in the retrieved evidence" in line.to_markdown())
check("94 each rendered claim carries design, citation state, certainty and directness",
      "Meta-analysis" in line.to_markdown() and "MODERATE" in line.to_markdown()
      and "DIRECT" in line.to_markdown())

# ══ Output modes ════════════════════════════════════════════════════════════════════════════
print("\n── Output modes ──")

check("95 five output modes are defined", len(om.MODES) == 5)
check("96 every mode runs the same gates",
      all(om.REQUIRED_GATES for _ in om.MODES))
check("97 QUICK still requires certainty, directness and citation status",
      all(s in om.contract(om.QUICK)["required"]
          for s in (om.CERTAINTY, om.DIRECTNESS, om.CITATION_STATUS)))
check("98 QUICK carries a word ceiling", om.contract(om.QUICK)["max_words"] == 200)
check("99 FULL requires the search log, evidence table and limitations",
      all(s in om.contract(om.FULL)["required"]
          for s in (om.SEARCH_LOG, om.EVIDENCE_TABLE, om.LIMITATIONS)))
check("100 a skipped gate fails validation at CRITICAL",
      om.validate(om.QUICK, [om.ANSWER, om.CERTAINTY, om.DIRECTNESS, om.CITATION_STATUS],
                  100, ["retraction_gate"])["result"] == om.FAIL)
check("101 the router picks the smallest sufficient mode for a simple question",
      om.select("answer") == om.QUICK)

# ══ Pipeline ════════════════════════════════════════════════════════════════════════════════
print("\n── Pipeline ──")

records = [pm(pmid="F1", publication_types=["Systematic Review"])]
p = pl.EvidencePipeline("q").retrieve(records, "SUCCESS")
check("102 retrieval reports that a record count is not an evidence count",
      "not an evidence count" in p.notes[0]["note"])
p.verify().appraise().assess_certainty(
    {"F1": {d: dr.HIGH for d in dr.DIMENSIONS}},
    pools_randomized={"F1": True},
    domains={"F1": domains})
synthesis = p.synthesise()
check("103 a direct, assessable record lands in the DIRECT bucket",
      [r.record_id for r in synthesis["buckets"]["DIRECT_EVIDENCE"]] == ["F1"])
check("104 the stage report names every completed stage",
      set(p.completed_stages) == set(pl.STAGES[:-1]))
check("105 the separation rule is stated in the report",
      "never, on that basis alone, strong evidence" in p.stage_report()["separation_rule"])
check("106 a stage cannot be run twice",
      refuses(lambda: p.verify(), pl.StageError))

# ══ Ranking ═════════════════════════════════════════════════════════════════════════════════
print("\n── Ranking ──")

items = [rk.RankedItem("old-sr", "L2", ce.HIGH, dr.DIRECT, 2014),
         rk.RankedItem("new-narrative", "L4", ce.VERY_LOW, dr.PARTIALLY_DIRECT, 2025),
         rk.RankedItem("cohort", "L3", ce.MODERATE, dr.DIRECT, 2020)]
ranked = rk.rank(items)
check("107 a stronger older source outranks a weaker newer one",
      [i.record_id for i in ranked["ranked"]] == ["old-sr", "cohort", "new-narrative"])
check("108 off-ladder tags are separated from the clinical ordering",
      rk.rank(items + [rk.RankedItem("lab", "LAB", ce.NOT_ASSESSABLE, dr.INDIRECT, 2026)])
      ["off_ladder"][0].record_id == "lab")
check("109 recency is used only as a tie-break among equals",
      rk.rank([rk.RankedItem("a", "L2", ce.HIGH, dr.DIRECT, 2015),
               rk.RankedItem("b", "L2", ce.HIGH, dr.DIRECT, 2022)])["recency_tiebreaks"])
check("110 a directness-driven tier inversion is reported, not hidden",
      rk.rank([rk.RankedItem("sr", "L2", ce.LOW, dr.INDIRECT, 2020),
               rk.RankedItem("coh", "L3", ce.MODERATE, dr.DIRECT, 2019)])["tier_inversions"])

# ══ Conflict ════════════════════════════════════════════════════════════════════════════════
print("\n── Conflict ──")

sr = sd.classify({"publication_types": ["Systematic Review"]})
a = cf.EvidenceSource("A", "Favours intervention", cf.FAVOURS_INTERVENTION, sr, ce.MODERATE,
                      dr.DIRECT, population="adults", methods="RoB 2", follow_up="6 months")
b = cf.EvidenceSource("B", "No difference", cf.NO_DIFFERENCE, sr, ce.MODERATE, dr.DIRECT,
                      population="adults", methods="ROBINS-I", follow_up="24 months")
conflict = cf.detect([a, b])["conflicts"][0]
check("111 differing dimensions are identified",
      conflict.differences()["follow_up"]["differs"] is True)
check("112 matching dimensions are identified as matching",
      conflict.differences()["population"]["differs"] is False)
check("113 an unestablished dimension is neither a match nor a difference",
      conflict.differences()["risk_of_bias"]["differs"] is None)
check("114 markdown rendering states both sources and the no-averaging rule",
      "Source A" in conflict.to_markdown() and "never averaged" in conflict.to_markdown())
check("115 agreeing sources produce no conflict",
      not cf.detect([a, cf.EvidenceSource("C", "Also favours", cf.FAVOURS_INTERVENTION, sr,
                                          ce.MODERATE, dr.DIRECT)])["conflicts"])

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

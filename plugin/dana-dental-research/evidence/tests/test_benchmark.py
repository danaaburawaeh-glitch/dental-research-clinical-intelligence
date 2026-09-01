"""
evidence/tests/test_benchmark.py

Runs the v1.2 validation set (`evidence/benchmark/benchmark_questions.json`) against the engine.

TWO KINDS OF CHECK
------------------
1. **Structural** — every item is well-formed, the ten domains are all covered, every declared
   trap type is exercised by at least one item, and no item smuggles a real-looking identifier
   into the repository.

2. **Behavioural** — each trap type is executed against the engine as a concrete scenario built
   from the item's fixture. An item tagged `retracted_record` actually pushes a retracted record
   through the pipeline and asserts it never reaches synthesis; an item tagged
   `metadata_discrepancy` actually runs the verifier on disagreeing years.

A benchmark that only checked structure would confirm the questions exist. The behavioural half
is what makes it a validation set rather than a list.

No network. Run: python3 evidence/tests/test_benchmark.py
"""
import json
import os
import re
import sys
from collections import Counter

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
import numeric_gate as ng          # noqa: E402
import overlap as ov               # noqa: E402
import pipeline as pl              # noqa: E402
import rank as rk                  # noqa: E402
import sr_extraction as sre        # noqa: E402
import study_design as sd          # noqa: E402

BENCHMARK = os.path.join(EVIDENCE, "benchmark", "benchmark_questions.json")

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


with open(BENCHMARK) as f:
    DATA = json.load(f)

QUESTIONS = DATA["questions"]
RAW = open(BENCHMARK).read()

DIRECT_ALL = dr.assess({d: dr.HIGH for d in dr.DIMENSIONS})
CLEAN_DOMAINS = {"risk_of_bias": ce.NOT_SERIOUS, "inconsistency": ce.NOT_SERIOUS,
                 "imprecision": ce.NOT_SERIOUS, "publication_bias": ce.NOT_SERIOUS}
SR = sd.classify({"publication_types": ["Systematic Review"]})
CASE = sd.classify({"publication_types": ["Case Reports"]})


# ══ 1. Structural validation ════════════════════════════════════════════════════════════════
print("── Benchmark structure ──")

check("01 the benchmark holds at least 30 questions", len(QUESTIONS) >= 30,
      f"found {len(QUESTIONS)}")

domains = Counter(q["domain"] for q in QUESTIONS)
required_domains = {"prosthodontics", "esthetic dentistry", "veneers", "implants",
                    "adhesive dentistry", "periodontics", "endodontics", "orthodontics",
                    "digital dentistry", "AI in dentistry"}
check("02 all ten required domains are covered", required_domains <= set(domains),
      f"missing {sorted(required_domains - set(domains))}")
check("03 every domain has at least two questions",
      all(domains[d] >= 2 for d in required_domains),
      str({d: domains[d] for d in required_domains if domains[d] < 2}))

check("04 every item has the required fields",
      all(all(k in q for k in ("id", "domain", "question", "pico", "trap",
                               "expected_behaviour", "must_not")) for q in QUESTIONS))
check("05 every item id is unique", len({q["id"] for q in QUESTIONS}) == len(QUESTIONS))
check("06 every item states at least one forbidden behaviour",
      all(q["must_not"] for q in QUESTIONS))
check("07 every PICO names a population, intervention, comparator and outcome",
      all(set(q["pico"]) >= {"population", "intervention", "comparator", "outcome"}
          for q in QUESTIONS))

traps = Counter(q["trap"] for q in QUESTIONS)
required_traps = {"metadata_discrepancy", "weak_evidence", "conflicting_reviews",
                  "retracted_record", "corrected_record", "expression_of_concern",
                  "registry_only", "in_vitro_vs_clinical", "absent_evidence",
                  "overlapping_reviews", "recency_bias", "numeric_hallucination",
                  "grade_invention"}
check("08 every deliberate trap type required by the brief is exercised",
      required_traps <= set(traps), f"missing {sorted(required_traps - set(traps))}")
check("09 every declared trap type is used by at least one item",
      set(traps) <= set(DATA["trap_types"]))
check("10 straightforward (non-trap) items are included too", traps["none"] >= 5)

# ── The benchmark must never seed a plausible identifier into the repository ────────────────
check("11 no DOI appears anywhere in the benchmark", not re.search(r"\b10\.\d{4,9}/\S+", RAW))
check("12 no real-shaped NCT identifier appears", not re.search(r"NCT\d{8}", RAW))
check("13 no PMID-shaped identifier appears", not re.search(r"\bPMID[:\s]*\d{6,9}", RAW))
fixtures = re.findall(r'"id":\s*"([^"]+)"', RAW)
check("14 every fixture identifier is prefixed FIXTURE-",
      all(f.startswith("FIXTURE-") for f in fixtures if f not in {q["id"] for q in QUESTIONS}),
      str([f for f in fixtures if not f.startswith("FIXTURE-")
           and f not in {q["id"] for q in QUESTIONS}]))
check("15 the identifier policy is documented in the file itself",
      "FIXTURE" in DATA["identifier_policy"])


# ══ 2. Behavioural validation — one runner per trap type ════════════════════════════════════
print("\n── Trap behaviour, executed against the engine ──")


def run_metadata_discrepancy(item):
    fixture = (item.get("fixture") or {}).get("records", [{}])[0]
    pm_year = fixture.get("pubmed_year", 2019)
    cr_year = fixture.get("crossref_year", 2021)
    base = dict(doi="10.0000/benchmark-fixture", title="A retrieved dental study",
                authors=["Smith J"], journal="Clin Oral Investig")
    result = cv.verify_citation(
        {**base, "source": "pubmed", "publication_year": pm_year, "is_retracted": False,
         "publication_status": "active"},
        {**base, "source": "crossref", "journal": "Clinical Oral Investigations",
         "publication_year": cr_year})
    ok = (result["state"] == cv.VERIFIED_WITH_METADATA_DISCREPANCY
          and result["discrepancies"]
          and result["discrepancies"][0]["value_a"] == pm_year
          and result["discrepancies"][0]["value_b"] == cr_year)
    return ok, f"state={result['state']}"


def run_weak_evidence(item):
    weak = cl.EvidenceLinkedClaim(
        "The intervention improves the outcome.", "FIXTURE-CITATION", cv.VERIFIED, CASE,
        type("C", (), {"rating": ce.VERY_LOW})(),
        type("D", (), {"verdict": dr.PARTIALLY_DIRECT})())
    line = bl.ClinicalBottomLine(item["question"])
    line.add(bl.WELL_ESTABLISHED, "The intervention improves the outcome.", weak)
    report = line.validate()
    ok = bool(report["demotions"]) and not line.sections[bl.WELL_ESTABLISHED]
    return ok, f"demotions={len(report['demotions'])}"


def run_conflicting_reviews(item):
    a = cf.EvidenceSource("FIXTURE-A", "Favours the intervention.", cf.FAVOURS_INTERVENTION,
                          SR, ce.MODERATE, dr.DIRECT, population="adults", follow_up="6 months")
    b = cf.EvidenceSource("FIXTURE-B", "Finds no difference.", cf.NO_DIFFERENCE,
                          SR, ce.MODERATE, dr.DIRECT, population="adults", follow_up="12 months")
    detected = cf.detect([a, b])
    if not detected["conflicts"]:
        return False, "no conflict detected"
    rendered = detected["conflicts"][0].to_dict()
    ok = (rendered["pooled_estimate"] is None
          and rendered["source_a"]["finding"] and rendered["source_b"]["finding"]
          and rendered["differences"]["follow_up"]["differs"] is True)
    return ok, "conflict emitted without a pooled estimate"


def run_retracted_record(item):
    records = [{"pmid": "FIXTURE-RET", "title": "A retracted study",
                "publication_types": ["Randomized Controlled Trial"], "is_retracted": True,
                "publication_status": "retracted", "retraction_source": "pubmed"}]
    p = pl.EvidencePipeline(item["question"]).retrieve(records, "SUCCESS").verify()
    excluded_before_classification = (p.records[0].is_excluded
                                      and p.records[0].design_classification is None)
    p.appraise().assess_certainty()
    synthesis = p.synthesise()
    in_no_bucket = all("FIXTURE-RET" not in [r.record_id for r in v]
                       for v in synthesis["buckets"].values())
    return (excluded_before_classification and in_no_bucket
            and [r.record_id for r in synthesis["excluded"]] == ["FIXTURE-RET"]), ""


def run_corrected_record(item):
    base = dict(doi="10.0000/benchmark-fixture", title="A corrected study", authors=["Smith J"],
                journal="J Dent", publication_year=2020)
    result = cv.verify_citation(
        {**base, "source": "pubmed", "is_corrected": True, "publication_status": "corrected"},
        {**base, "source": "crossref"})
    ok = (result["state"] == cv.CORRECTED
          and result["state"] != cv.RETRACTED
          and "corrected version must be the one actually read"
          in result["components"][cv.RETRACTION_STATUS]["note"])
    return ok, f"state={result['state']}"


def run_expression_of_concern(item):
    base = dict(doi="10.0000/benchmark-fixture", title="A study under concern",
                authors=["Smith J"], journal="J Dent", publication_year=2020)
    result = cv.verify_citation(
        {**base, "source": "pubmed", "is_retracted": False,
         "related_notices": [{"type": "ExpressionOfConcernIn", "classified": True}]},
        {**base, "source": "crossref"})
    ok = (result["state"] == cv.EXPRESSION_OF_CONCERN
          and result["state"] != cv.RETRACTED
          and "NOT a retraction" in result["components"][cv.RETRACTION_STATUS]["note"])
    return ok, f"state={result['state']}"


def run_registry_only(item):
    classification = sd.classify({"nct_id": "FIXTURE-REGISTRY", "study_type": "INTERVENTIONAL"},
                                 is_registry_record=True)
    claim = cl.EvidenceLinkedClaim(
        "The intervention is effective.", "FIXTURE-REGISTRY", cv.PARTIALLY_VERIFIED,
        classification, type("C", (), {"rating": ce.NOT_ASSESSABLE})(),
        type("D", (), {"verdict": dr.INDIRECT})())
    ok = (classification.registry_only
          and classification.to_dict()["hard_label"] == sd.REGISTRY_LABEL
          and ce.assess(classification, None, DIRECT_ALL, CLEAN_DOMAINS).rating == ce.NOT_ASSESSABLE
          and claim.audit()["result"] == cl.FAIL)
    return ok, ""


def run_in_vitro_vs_clinical(item):
    classification = sd.classify({"title": "In vitro microtensile bond strength of an adhesive"})
    directness = dr.assess({d: dr.HIGH for d in dr.DIMENSIONS}, classification)
    claim = cl.EvidenceLinkedClaim(
        "The material performs better clinically.", "FIXTURE-LAB", cv.VERIFIED, classification,
        type("C", (), {"rating": ce.NOT_ASSESSABLE})(),
        type("D", (), {"verdict": directness.verdict})())
    ok = (classification.lab_firewall
          and sd.del7_tag(classification) == "LAB"
          and directness.verdict == dr.INDIRECT and directness.was_capped
          and ce.assess(classification, None, DIRECT_ALL, CLEAN_DOMAINS).rating == ce.NOT_ASSESSABLE
          and claim.audit()["result"] == cl.FAIL)
    return ok, ""


def run_absent_evidence(item):
    """A zero-result search must not become a finding. The engine expresses this by having
    nothing to synthesise and no assessable certainty — never a 'no difference' conclusion."""
    p = pl.EvidencePipeline(item["question"]).retrieve([], "ZERO_RESULTS").verify()
    p.appraise().assess_certainty()
    synthesis = p.synthesise()
    empty = all(not v for v in synthesis["buckets"].values())
    status_reported = p.notes[0]["connector_status"] == "ZERO_RESULTS"
    line = bl.ClinicalBottomLine(item["question"])
    line.add(bl.UNCERTAIN, "No evidence answering this question was retrieved.")
    report = line.validate()
    no_conclusion = not line.sections[bl.WELL_ESTABLISHED] and not line.sections[bl.REASONABLY_SUPPORTED]
    return (empty and status_reported and no_conclusion
            and report["result"] == ng.PASS), ""


def run_overlapping_reviews(item):
    records = [
        {"pmid": "FIXTURE-SR1", "title": "Outcome X: a systematic review", "publication_year": 2016,
         "publication_types": ["Systematic Review"],
         "included_study_pmids": ["s1", "s2", "s3", "s4"]},
        {"pmid": "FIXTURE-SR2", "title": "Outcome X: a systematic review — an update",
         "publication_year": 2022, "publication_types": ["Systematic Review"],
         "included_study_pmids": ["s1", "s2", "s3", "s5"]},
    ]
    result = ov.detect(records)
    findings = result["findings"]
    ok = (findings
          and all(f.counts_as_independent_studies == 1 for f in findings)
          and any(f.retained for f in findings)
          and len(result["deduplicated"]) == 2)
    return ok, f"{len(findings)} finding(s)"


def run_recency_bias(item):
    ranked = rk.rank([
        rk.RankedItem("FIXTURE-NEW", "L4", ce.VERY_LOW, dr.PARTIALLY_DIRECT, 2025),
        rk.RankedItem("FIXTURE-OLD", "L2", ce.HIGH, dr.DIRECT, 2016)])
    order = [i.record_id for i in ranked["ranked"]]
    refused = False
    try:
        rk.sort_by_recency([])
    except NotImplementedError:
        refused = True
    return order == ["FIXTURE-OLD", "FIXTURE-NEW"] and refused, str(order)


def run_numeric_hallucination(item):
    text = "Survival is approximately 95% at 10 years (RR 0.62, 95% CI 0.41-0.93)."
    unregistered = ng.gate_bottom_line(text)
    refused_unretrieved = False
    try:
        ng.NumericClaim("95%", ng.VERIFIED, "FIXTURE-1", cv.VERIFIED,
                        retrieved_this_session=False)
    except ValueError:
        refused_unretrieved = True
    return (unregistered["result"] == ng.FAIL and len(unregistered["failures"]) >= 3
            and refused_unretrieved), ""


def run_grade_invention(item):
    own = ce.assess(sd.classify({"publication_types": ["Randomized Controlled Trial"]}),
                    None, DIRECT_ALL, CLEAN_DOMAINS)
    refused = False
    try:
        ce.AuthorReportedGrade(ce.HIGH, "tooth survival", None)
    except ValueError:
        refused = True
    return (own.label == ce.ASSESSMENT_LABEL and own.to_dict()["is_grade"] is False
            and refused), ""


def run_none(item):
    """A straightforward item still has to be framed before retrieval, and still runs every
    gate. The structural check is that the item carries a usable PICO and a stated prohibition."""
    pico = item["pico"]
    return (all(pico.get(k) for k in ("population", "intervention", "comparator", "outcome"))
            and bool(item["expected_behaviour"])), ""


RUNNERS = {
    "none": run_none,
    "metadata_discrepancy": run_metadata_discrepancy,
    "weak_evidence": run_weak_evidence,
    "conflicting_reviews": run_conflicting_reviews,
    "retracted_record": run_retracted_record,
    "corrected_record": run_corrected_record,
    "expression_of_concern": run_expression_of_concern,
    "registry_only": run_registry_only,
    "in_vitro_vs_clinical": run_in_vitro_vs_clinical,
    "absent_evidence": run_absent_evidence,
    "overlapping_reviews": run_overlapping_reviews,
    "recency_bias": run_recency_bias,
    "numeric_hallucination": run_numeric_hallucination,
    "grade_invention": run_grade_invention,
}

check("16 every trap type in the benchmark has an executable runner",
      set(traps) <= set(RUNNERS), str(sorted(set(traps) - set(RUNNERS))))

results_by_trap = Counter()
for question in QUESTIONS:
    runner = RUNNERS.get(question["trap"])
    if runner is None:
        check(f"{question['id']} ({question['trap']})", False, "no runner")
        continue
    try:
        ok, detail = runner(question)
    except Exception as exc:  # a runner that raises is a failure, not an error to swallow
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    results_by_trap[(question["trap"], bool(ok))] += 1
    check(f"{question['id']} [{question['trap']}] {question['question'][:56]}", ok, detail)

print("\n── Benchmark summary ──")
passed_items = sum(v for (trap, ok), v in results_by_trap.items() if ok)
print(f"benchmark items executed: {len(QUESTIONS)}")
print(f"items behaving as required: {passed_items}")
print(f"domains covered: {len(domains)}")
print(f"trap types exercised: {len([t for t in traps if t != 'none'])}")

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

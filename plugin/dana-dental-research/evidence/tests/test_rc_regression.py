"""
evidence/tests/test_rc_regression.py

v1.2 Release Candidate regression suite — the two blockers the real-world validation left open.

Cases A-F are the ones named in the RC brief:

    A. PubMed/Crossref year-only mismatch        (T1/T2 must agree)
    B. exact metadata match
    C. genuine mismatched citation
    D. shared authors but distinct cohorts       (must NOT flag)
    E. likely overlapping cohorts                (must flag, must not delete)
    F. confirmed duplicate / publication overlap

Identifiers are synthetic FIXTURE- values except where a real public record is needed to prove
behaviour against real data shapes; those are marked REAL and are records already retrieved and
verified in this session.

No network. Run: python3 evidence/tests/test_rc_regression.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
sys.path.insert(0, EVIDENCE)

import _paths  # noqa: F401,E402

import citation_verification as cv       # noqa: E402
import overlap as ov                     # noqa: E402
import transport_reconcile as tr         # noqa: E402

R = []


def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def rec(source, year, **kw):
    base = {"source": source, "doi": "10.0000/fixture-rc",
            "title": "Survival of bonded ceramic laminate veneers",
            "authors": ["Smith J", "Jones A"] if source == "pubmed" else ["John Smith", "Alice Jones"],
            "journal": "Clin Oral Investig" if source == "pubmed" else "Clinical Oral Investigations",
            "publication_year": year}
    if source == "pubmed":
        base.update({"is_retracted": False, "publication_status": "active"})
    base.update(kw)
    return base


# ══ A. PubMed/Crossref year-only mismatch ═══════════════════════════════════════════════════
print("\n── A. Year-only mismatch ──")

a = cv.verify_citation(rec("pubmed", 2025), rec("crossref", 2026))
check("A1 a one-year gap is VERIFIED_WITH_METADATA_DISCREPANCY",
      a["state"] == cv.VERIFIED_WITH_METADATA_DISCREPANCY)
check("A2 it is not silently upgraded to VERIFIED", a["state"] != cv.VERIFIED)
check("A3 it is not reported as a failed verification", a["state"] != cv.NOT_VERIFIED)
check("A4 both years are returned explicitly",
      a["pubmed_year"] == 2025 and a["crossref_year"] == 2026)
check("A5 the discrepancy type is named",
      a["discrepancy_type"] == cv.DISCREPANCY_ONLINE_FIRST)
check("A6 the source of each year is named",
      a["year_source_names"]["pubmed_year_from"] == "pubmed"
      and a["year_source_names"]["crossref_year_from"] == "crossref")
check("A7 neither year is replaced by the other",
      a["components"][cv.YEAR_MATCH]["value_a"] == 2025
      and a["components"][cv.YEAR_MATCH]["value_b"] == 2026)
check("A8 the citation may still support a clinical claim",
      a["may_support_clinical_claim"] is True)
check("A9 the direction of the gap does not change the verdict",
      cv.verify_citation(rec("pubmed", 2026), rec("crossref", 2025))["state"]
      == cv.VERIFIED_WITH_METADATA_DISCREPANCY)
check("A10 a gap beyond tolerance falls back to NOT_VERIFIED",
      cv.verify_citation(rec("pubmed", 2019), rec("crossref", 2021))["state"] == cv.NOT_VERIFIED)
check("A11 the beyond-tolerance case is not given the online-first explanation",
      "does not account for it" in cv.verify_citation(
          rec("pubmed", 2019), rec("crossref", 2021))["discrepancies"][0]["interpretation"])

# ── T1/T2 parity, including against a legacy server ─────────────────────────────────────────
legacy_payload = {"verification_status": "NOT_VERIFIED",
                  "metadata_match": {"title": True, "year": False, "doi": True}}
recon = tr.reconcile(legacy_payload, rec("pubmed", 2025), rec("crossref", 2026))
check("A12 a legacy server's year-only NOT_VERIFIED is recognised as the known pattern",
      recon["divergence"]["pattern"] == tr.LEGACY_YEAR_ONLY_PATTERN)
check("A13 the reconciled state matches the local v1.2 state",
      recon["state"] == cv.VERIFIED_WITH_METADATA_DISCREPANCY)
check("A14 the divergence is reported, not hidden",
      recon["divergence"]["remote_state"] == cv.NOT_VERIFIED
      and recon["divergence"]["local_state"] == cv.VERIFIED_WITH_METADATA_DISCREPANCY)
check("A15 the local layer is the authority", recon["authority"] == "local")

current_payload = {"verification_status": "VERIFIED_WITH_METADATA_DISCREPANCY",
                   "metadata_match": {"title": True, "authors": True, "journal": True,
                                      "year": False, "doi": True},
                   "year_comparison": "WITHIN_TOLERANCE", "pubmed_year": 2025,
                   "crossref_year": 2026, "discrepancy_type": "ONLINE_FIRST_VS_ISSUE_YEAR"}
recon2 = tr.reconcile(current_payload, rec("pubmed", 2025), rec("crossref", 2026))
check("A16 an upgraded server produces no divergence at all", recon2["divergence"] is None)
check("A17 the upgraded server's schema is detected",
      recon2["remote_schema"] == tr.SCHEMA_CURRENT)
check("A18 a legacy schema is detected as legacy",
      tr.detect_schema(legacy_payload) == tr.SCHEMA_LEGACY)

# ══ B. Exact metadata match ═════════════════════════════════════════════════════════════════
print("\n── B. Exact match ──")

b = cv.verify_citation(rec("pubmed", 2025), rec("crossref", 2025))
check("B1 identical years give plain VERIFIED", b["state"] == cv.VERIFIED)
check("B2 no discrepancy is manufactured", b["discrepancies"] == [])
check("B3 no discrepancy type is set", b["discrepancy_type"] is None)
check("B4 the year component is a plain MATCH",
      b["components"][cv.YEAR_MATCH]["verdict"] == cv.MATCH)
check("B5 an abbreviated journal name still matches",
      b["components"][cv.JOURNAL_MATCH]["verdict"] == cv.MATCH)
check("B6 differently-rendered author names still match",
      b["components"][cv.AUTHOR_MATCH]["verdict"] == cv.MATCH)
check("B7 a matching exact-match payload reconciles with no divergence",
      tr.reconcile({"verification_status": "VERIFIED", "metadata_match": {"title": True, "year": True, "doi": True}},
                   rec("pubmed", 2025), rec("crossref", 2025))["divergence"] is None)

# ══ C. Genuine mismatched citation ══════════════════════════════════════════════════════════
print("\n── C. Genuine mismatch ──")

c_doi = cv.verify_citation(rec("pubmed", 2025), rec("crossref", 2025, doi="10.0000/other"))
check("C1 a DOI conflict is NOT_VERIFIED", c_doi["state"] == cv.NOT_VERIFIED)
check("C2 a DOI conflict is labelled an identity conflict",
      c_doi["discrepancies"][0]["severity"] == "IDENTITY_CONFLICT")

c_title = cv.verify_citation(rec("pubmed", 2025),
                             rec("crossref", 2025, title="Peri-implantitis surgical management"))
check("C3 a title conflict is NOT_VERIFIED even with a matching DOI",
      c_title["state"] == cv.NOT_VERIFIED)
check("C4 a title conflict with a within-tolerance year gap is still NOT_VERIFIED",
      cv.verify_citation(rec("pubmed", 2025),
                         rec("crossref", 2026, title="A completely different paper"))["state"]
      == cv.NOT_VERIFIED)
check("C5 a journal conflict is NOT_VERIFIED",
      cv.verify_citation(rec("pubmed", 2025),
                         rec("crossref", 2025, journal="Journal of Endodontics"))["state"]
      == cv.NOT_VERIFIED)
check("C6 a mismatched citation may not support a clinical claim",
      c_title["may_support_clinical_claim"] is False)
check("C7 both conflicting values are named, neither dropped",
      c_doi["discrepancies"][0]["value_a"] and c_doi["discrepancies"][0]["value_b"])

# ══ D. Shared authors, distinct cohorts — MUST NOT FLAG ═════════════════════════════════════
print("\n── D. Shared authors, distinct cohorts (false-positive test) ──")

d_a = {"pmid": "FIXTURE-D1", "authors": ["Herbert Dumfahrt", "A Colleague"],
       "institutions": ["Medical University Innsbruck"], "study_period": [1990, 1998],
       "sample_size_n": 191, "intervention": "porcelain laminate veneers", "country": "Austria"}
d_b = {"pmid": "FIXTURE-D2", "authors": ["Herbert Dumfahrt", "Another Colleague"],
       "institutions": ["University of Bern"], "study_period": [2012, 2019],
       "sample_size_n": 240, "intervention": "zirconia implant crowns", "country": "Switzerland"}
d = ov.assess_cohort_overlap(d_a, d_b)
check("D1 shared authors with different everything is NO_OVERLAP_SIGNAL",
      d.level == ov.NO_OVERLAP_SIGNAL)
check("D2 the pair still counts as two independent studies",
      d.counts_as_independent_studies == 2)
check("D3 pooled confidence is not reduced", d.reduces_pooled_confidence is False)
check("D4 shared authorship is reported even though it did not count",
      d.features["shared_authors"] is True)
check("D5 the authors-alone rule is stated in the output",
      "never counts toward an overlap level" in d.to_dict()["authors_alone_rule"])

d_same_topic = ov.assess_cohort_overlap(
    d_a, {**d_b, "intervention": "porcelain laminate veneers", "country": "Austria"})
check("D6 shared authors plus topic, but different unit and period, still does not reach PROBABLE",
      d_same_topic.level != ov.PROBABLE_OVERLAP)

# ══ E. Likely overlapping cohorts ═══════════════════════════════════════════════════════════
print("\n── E. Likely overlapping cohorts (REAL records: PMID 22259802 / PMID 11203615) ──")

e_a = {"pmid": "22259802", "authors": ["Ulrike Stephanie Beier", "Ines Kapferer",
                                       "Doris Burtscher", "Herbert Dumfahrt"],
       "institutions": ["Medical University Innsbruck"], "study_period": [1987, 2009],
       "sample_size_n": 318, "intervention": "porcelain laminate veneers", "country": "Austria"}
e_b = {"pmid": "11203615", "authors": ["H Dumfahrt", "H Schaeffer"],
       "institutions": ["Medical University Innsbruck"], "study_period": [1989, 1999],
       "sample_size_n": 191, "intervention": "porcelain laminate veneers", "country": "Austria"}
e = ov.assess_cohort_overlap(e_a, e_b)
check("E1 same unit, overlapping period and matching intervention reaches PROBABLE_OVERLAP",
      e.level == ov.PROBABLE_OVERLAP, e.level)
check("E2 it is NOT reported as confirmed without an identifier",
      e.level != ov.CONFIRMED_OVERLAP)
check("E3 the triggering features are named",
      "shared_institution" in e.triggered and "study_period_overlap" in e.triggered)
check("E4 pooled confidence is reduced", e.reduces_pooled_confidence is True)
check("E5 the pair contributes one independent study, not two",
      e.counts_as_independent_studies == 1)
check("E6 neither study is deleted", e.deletes_a_study is False)
check("E7 both citations are preserved",
      set(e.to_dict()["citations_preserved"]) == {"22259802", "11203615"})
check("E8 the caution states the overlap is probable, not established",
      "pending verification" in e.to_dict()["pooled_interpretation_caution"])

e_possible = ov.assess_cohort_overlap(
    e_a, {**e_b, "study_period": [2015, 2019]})
check("E9 same unit but a non-overlapping period drops below PROBABLE",
      e_possible.level in (ov.POSSIBLE_OVERLAP, ov.NO_OVERLAP_SIGNAL), e_possible.level)
check("E10 a POSSIBLE overlap leaves the independent-study count unresolved rather than guessed",
      ov.CohortOverlapAssessment(ov.POSSIBLE_OVERLAP, e_a, e_b, {}, [], "x"
                                 ).counts_as_independent_studies is None)

# ══ F. Confirmed duplicate / publication overlap ════════════════════════════════════════════
print("\n── F. Confirmed overlap ──")

f_a = {"pmid": "FIXTURE-F1", "title": "Trial 3-year report", "nct_id": "NCT00000001",
       "authors": ["A Author"], "publication_year": 2018}
f_b = {"pmid": "FIXTURE-F2", "title": "Trial 5-year report", "nct_id": "NCT00000001",
       "authors": ["B Author"], "publication_year": 2020, "follow_up_months": 60}
f = ov.assess_cohort_overlap(f_a, f_b)
check("F1 a shared registration identifier is CONFIRMED_OVERLAP",
      f.level == ov.CONFIRMED_OVERLAP)
check("F2 the identifier is named as the trigger",
      any("NCT00000001" in t for t in f.triggered))
check("F3 a confirmed overlap counts once", f.counts_as_independent_studies == 1)
check("F4 a confirmed overlap deletes neither study", f.deletes_a_study is False)
check("F5 both citations are preserved",
      len(f.to_dict()["citations_preserved"]) == 2)

f_declared = ov.assess_cohort_overlap(
    {"pmid": "FIXTURE-F3", "authors": ["X"], "same_cohort_as": "FIXTURE-F4"},
    {"pmid": "FIXTURE-F4", "authors": ["Y"]})
check("F6 an explicitly declared linkage is CONFIRMED_OVERLAP",
      f_declared.level == ov.CONFIRMED_OVERLAP)
check("F7 confirmation is never reached by circumstantial features alone",
      "never reached by accumulating" in f.to_dict()["confirmed_requirement"])

circumstantial = ov.assess_cohort_overlap(
    {**e_a, "nct_id": None}, {**e_b, "nct_id": None})
check("F8 the strongest circumstantial case still stops at PROBABLE",
      circumstantial.level == ov.PROBABLE_OVERLAP)

check("F9 the registration-based clusterer and the cohort assessor agree on a shared NCT",
      ov.detect([f_a, f_b])["findings"][0].overlap_type == ov.SAME_STUDY_MULTIPLE_REPORTS)
check("F10 assess_all_cohort_overlaps returns only pairs at or above the threshold",
      len(ov.assess_all_cohort_overlaps([d_a, d_b])) == 0
      and len(ov.assess_all_cohort_overlaps([e_a, e_b])) == 1)
check("F11 no record is removed from the input set",
      len(ov.detect([f_a, f_b])["deduplicated"]) == 2)

total = len(R)
failed = [n for n, ok, _ in R if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

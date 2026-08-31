"""
connectors/clinical_trials/tests/test_clinical_trials.py

Executable regression tests for the ClinicalTrials.gov connector — all 20 scenarios required by
the Phase B brief, plus the safety invariants.

Run:  python3 connectors/clinical_trials/tests/test_clinical_trials.py
Exit code 0 = all passed.

Design notes:
- Network is MOCKED for every scenario that must be deterministic (retry, 429, 5xx, timeout,
  malformed response). Mocking is what makes a failure test reproducible; the live tests live
  separately in LIVE_CLINICALTRIALS_VALIDATION.md and are run against the real API.
- Fixtures are shaped from REAL responses captured during API verification, not invented.
"""
import json
import os
import sys
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CT = os.path.dirname(HERE)
CONNECTORS = os.path.dirname(CT)

# NOTE: connectors/shared/ also contains a models.py, so it must NOT be placed on sys.path here —
# doing so shadows clinical_trials/models.py and breaks the connector's own imports. The shared
# module is loaded by explicit file path instead. This mirrors how client.py resolves modules at
# runtime (its own directory first, connectors/ only for the `shared.` package prefix).
sys.path.insert(0, CONNECTORS)
sys.path.insert(0, CT)

import client
import models
import parser as ct_parser
import errors

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "trial_publication_linkage",
    os.path.join(CONNECTORS, "shared", "trial_publication_linkage.py"))
linkage = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(linkage)

RESULTS = []


def check(name, condition, detail=""):
    RESULTS.append((name, bool(condition), detail))
    print(("PASS  " if condition else "FAIL  ") + name + (f"  [{detail}]" if detail and not condition else ""))


def _study(nct="NCT12345678", status="COMPLETED", study_type="INTERVENTIONAL", phases=None,
           enrollment=None, has_results=False, refs=None, why_stopped=None, results_section=None):
    """Build a study payload shaped like a real API v2 response."""
    protocol = {
        "identificationModule": {"nctId": nct, "briefTitle": "Test trial",
                                  "officialTitle": "An Official Test Trial"},
        "statusModule": {"overallStatus": status,
                          "studyFirstPostDateStruct": {"date": "2020-01-01", "type": "ACTUAL"}},
        "designModule": {"studyType": study_type},
        "conditionsModule": {"conditions": ["Dental Caries"]},
        "armsInterventionsModule": {"interventions": [{"type": "DEVICE", "name": "Implant"}]},
        "eligibilityModule": {"sex": "ALL", "minimumAge": "18 Years", "healthyVolunteers": True,
                               "eligibilityCriteria": "Inclusion: adults."},
        "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Test Uni", "class": "OTHER"}},
    }
    if phases is not None:
        protocol["designModule"]["phases"] = phases
    if enrollment is not None:
        protocol["designModule"]["enrollmentInfo"] = enrollment
    if why_stopped:
        protocol["statusModule"]["whyStopped"] = why_stopped
    if refs is not None:
        protocol["referencesModule"] = {"references": refs}
    study = {"protocolSection": protocol, "hasResults": has_results}
    if results_section:
        study["resultsSection"] = results_section
    return study


def _mock_http(responses):
    """Replace client._single_attempt with a scripted sequence. Returns the call counter."""
    seq = list(responses)
    calls = {"n": 0}

    def fake(url, rate_limiter, timeout):
        calls["n"] += 1
        item = seq[min(calls["n"] - 1, len(seq) - 1)]
        if isinstance(item, Exception):
            raise item
        code, body = item
        return client._Response(code, body)

    client._single_attempt = fake
    return calls


_ORIGINAL_SINGLE_ATTEMPT = client._single_attempt


def _restore():
    client._single_attempt = _ORIGINAL_SINGLE_ATTEMPT


class _NoSleepLimiter:
    def acquire(self):
        pass


# ---------------------------------------------------------------------------
# 1. valid NCT ID
# ---------------------------------------------------------------------------
check("01 valid NCT ID accepted and canonicalised",
      models.validate_nct_id(" nct00782171 ") == "NCT00782171")

# ---------------------------------------------------------------------------
# 2. invalid NCT ID — rejected, never repaired, never sent
# ---------------------------------------------------------------------------
bad = ["NCT123", "NCT123456789", "NOTANID", "", None, "12345678", "NCT1234567a"]
check("02a invalid NCT IDs all rejected",
      all(models.validate_nct_id(b) is None for b in bad))
calls = _mock_http([(200, "{}")])
r = client.clinical_trials_fetch("NCT123", rate_limiter=_NoSleepLimiter())
_restore()
check("02b invalid NCT ID returns IDENTIFIER_INVALID",
      r["status"] == errors.STATUS_IDENTIFIER_INVALID, r["status"])
check("02c invalid NCT ID issues NO network request", calls["n"] == 0, f"calls={calls['n']}")
check("02d short ID is NOT zero-padded into a valid-looking ID",
      "NCT00000123" not in json.dumps(r))

# ---------------------------------------------------------------------------
# 3. zero-results query
# ---------------------------------------------------------------------------
_mock_http([(200, json.dumps({"totalCount": 0, "studies": []}))])
r = client.clinical_trials_search(condition="zzz", rate_limiter=_NoSleepLimiter())
_restore()
check("03a zero results -> ZERO_RESULTS", r["status"] == errors.STATUS_ZERO_RESULTS)
check("03b ZERO_RESULTS carries the 'not proof of absence' meaning",
      "NOT a statement that no such trials exist" in r.get("zero_results_meaning", ""))

# ---------------------------------------------------------------------------
# 4-7. recruiting / completed / terminated / withdrawn
# ---------------------------------------------------------------------------
rec = ct_parser.parse_study(_study(status="RECRUITING"))
check("04 recruiting parsed, no outcome implied",
      rec["overall_status"] == "RECRUITING" and "No outcome information" in rec["status_safety_note"])

comp = ct_parser.parse_study(_study(status="COMPLETED"))
check("05 completed parsed", comp["overall_status"] == "COMPLETED")

term = ct_parser.parse_study(_study(status="TERMINATED", why_stopped="funding withdrawn"))
check("06a terminated parsed with reason",
      term["overall_status"] == "TERMINATED" and term["why_stopped"] == "funding withdrawn")
check("06b termination is not framed as intervention failure",
      "not by itself evidence the intervention failed" in term["status_safety_note"])

wd = ct_parser.parse_study(_study(status="WITHDRAWN", enrollment={"count": 0, "type": "ACTUAL"}))
check("07a withdrawn parsed", wd["overall_status"] == "WITHDRAWN" and wd["enrollment"] == 0)
check("07b withdrawn flagged as never-started and not a negative result",
      "NEVER STARTED" in wd["status_safety_note"] and "NOT a negative result" in wd["status_safety_note"])

# ---------------------------------------------------------------------------
# 8-9. with / without results
# ---------------------------------------------------------------------------
res_section = {
    "participantFlowModule": {"groups": [{"id": "FG000"}], "periods": []},
    "baselineCharacteristicsModule": {"groups": [], "denoms": [], "measures": []},
    "outcomeMeasuresModule": {"outcomeMeasures": [{"title": "ISQ change", "type": "PRIMARY"}]},
    "adverseEventsModule": {"eventGroups": [{"id": "EG000"}]},
}
with_res = ct_parser.parse_study(_study(has_results=True, results_section=res_section))
check("08a has_results true -> registry_results captured",
      with_res["has_results"] is True and with_res["registry_results"] is not None)
check("08b registry results labelled non-peer-reviewed",
      "NOT peer-reviewed" in with_res["registry_results"]["label"])
check("08c registry results classified B, not as publication",
      with_res["evidence_class"] == models.EVIDENCE_CLASS_REGISTRY_RESULTS)
check("08d outcome measures captured without derivation",
      with_res["registry_results"]["outcome_measure_count"] == 1)

no_res = ct_parser.parse_study(_study(has_results=False))
check("09a no results -> registry_results is None", no_res["registry_results"] is None)
check("09b classified A (registered, no results)",
      no_res["evidence_class"] == models.EVIDENCE_CLASS_NO_RESULTS)

# ---------------------------------------------------------------------------
# 10-11. missing enrollment / missing phase stay missing
# ---------------------------------------------------------------------------
missing = ct_parser.parse_study(_study(enrollment=None, phases=None))
check("10 missing enrollment stays None, not 0",
      missing["enrollment"] is None and missing["enrollment_type"] is None)
check("11 missing phase stays None, not 'NA'", missing["phases"] is None)

# ---------------------------------------------------------------------------
# 12. malformed API response
# ---------------------------------------------------------------------------
_mock_http([(200, "this is not json")])
r = client.clinical_trials_search(condition="x", rate_limiter=_NoSleepLimiter())
_restore()
check("12a non-JSON body -> PARSE_ERROR", r["status"] == errors.STATUS_PARSE_ERROR, r["status"])

_mock_http([(200, json.dumps({"unexpected": True}))])
r = client.clinical_trials_search(condition="x", rate_limiter=_NoSleepLimiter())
_restore()
check("12b JSON without 'studies' -> PARSE_ERROR", r["status"] == errors.STATUS_PARSE_ERROR)

try:
    ct_parser.parse_study({"protocolSection": {"identificationModule": {"nctId": "GARBAGE"}}})
    ok = False
except errors.ClinicalTrialsConnectorError as e:
    ok = e.status == errors.STATUS_PARSE_ERROR
check("12c study with invalid nctId raises PARSE_ERROR, never emits a null-identity record", ok)

# ---------------------------------------------------------------------------
# 13. timeout
# ---------------------------------------------------------------------------
_mock_http([urllib.error.URLError("timed out")] * 6)
r = client.clinical_trials_search(condition="x", rate_limiter=_NoSleepLimiter())
_restore()
check("13 network failure -> TIMEOUT, no raw exception escapes",
      r["status"] == errors.STATUS_TIMEOUT, r["status"])

# ---------------------------------------------------------------------------
# 14. HTTP 429
# ---------------------------------------------------------------------------
calls = _mock_http([(429, "slow down")] * 6)
r = client.clinical_trials_search(condition="x", rate_limiter=_NoSleepLimiter())
_restore()
check("14a persistent 429 -> RATE_LIMITED", r["status"] == errors.STATUS_RATE_LIMITED, r["status"])
check("14b 429 was retried, not accepted on first response", calls["n"] > 1, f"calls={calls['n']}")

# ---------------------------------------------------------------------------
# 15. 5xx retry then success
# ---------------------------------------------------------------------------
good = json.dumps({"totalCount": 1, "studies": [_study(nct="NCT00000001")]})
calls = _mock_http([(503, "unavailable"), (503, "unavailable"), (200, good)])
r = client.clinical_trials_search(condition="x", rate_limiter=_NoSleepLimiter())
_restore()
check("15a 5xx retried then succeeded", r["status"] == errors.STATUS_SUCCESS, r["status"])
check("15b exactly 3 attempts made", calls["n"] == 3, f"calls={calls['n']}")

# ---------------------------------------------------------------------------
# 16. duplicate registry/publication -> counted ONCE
# ---------------------------------------------------------------------------
trial = ct_parser.parse_study(_study(nct="NCT00782171",
                                      refs=[{"pmid": "18416725", "type": "RESULT"}]))
pub = {"pmid": "18416725", "title": "A paper", "doi": "10.1/x"}
d = linkage.deduplicate_trials_and_publications([trial], [pub])
check("16a two records collapse to one underlying study",
      d["total_input_records"] == 2 and d["independent_study_count"] == 1)
check("16b the merged study still carries both records",
      d["studies"][0]["record_count"] == 2 and d["studies"][0]["counts_as_studies"] == 1)

# ---------------------------------------------------------------------------
# 17. NCT-PubMed linkage match
# ---------------------------------------------------------------------------
link = linkage.link_trial_to_publication(trial, pub)
check("17a registry RESULT reference verifies the link",
      link["status"] == linkage.LINK_VERIFIED and link["basis"] == linkage.BASIS_REGISTRY_REFERENCE)
link2 = linkage.link_trial_to_publication(
    ct_parser.parse_study(_study(nct="NCT00782171")),
    {"pmid": "999", "abstract": "This trial was registered as NCT00782171."})
check("17b NCT ID inside publication metadata also verifies the link",
      link2["status"] == linkage.LINK_VERIFIED and link2["basis"] == linkage.BASIS_PUBLICATION_NCT)

# ---------------------------------------------------------------------------
# 18. mismatched NCT linkage
# ---------------------------------------------------------------------------
link3 = linkage.link_trial_to_publication(
    ct_parser.parse_study(_study(nct="NCT00782171")),
    {"pmid": "555", "abstract": "Registered as NCT99999999."})
check("18a publication naming a different trial -> MISMATCH",
      link3["status"] == linkage.LINK_MISMATCH)
bg_trial = ct_parser.parse_study(_study(nct="NCT00782171",
                                         refs=[{"pmid": "777", "type": "BACKGROUND"}]))
link4 = linkage.link_trial_to_publication(bg_trial, {"pmid": "777"})
check("18b BACKGROUND reference does NOT verify a link",
      link4["status"] == linkage.LINK_UNVERIFIED)
link5 = linkage.link_trial_to_publication(
    ct_parser.parse_study(_study(nct="NCT00782171")),
    {"pmid": "888", "title": "Same topic, same year, same authors"})
check("18c topical similarity alone never verifies a link",
      link5["status"] == linkage.LINK_UNVERIFIED and link5["basis"] is None)

# ---------------------------------------------------------------------------
# 19. completed does not imply successful
# ---------------------------------------------------------------------------
note = models.status_safety_note("COMPLETED")
check("19a COMPLETED carries an explicit not-successful warning",
      "NOT THAT IT SUCCEEDED" in note)
check("19b no status maps to an efficacy claim",
      all(not any(w in models.status_safety_note(s).lower()
                  for w in ("effective", "works", "successful treatment"))
          for s in models.OVERALL_STATUSES))

# ---------------------------------------------------------------------------
# 20. a registry record is not automatically published evidence
# ---------------------------------------------------------------------------
plain = ct_parser.parse_study(_study(status="COMPLETED", has_results=False))
check("20a completed-without-results is class A, not evidence",
      plain["evidence_class"] == models.EVIDENCE_CLASS_NO_RESULTS)
check("20b class A note states registration is not a finding",
      "not a finding" in plain["evidence_class_note"])
check("20c registry-results class is explicitly not peer-reviewed",
      "NOT peer-reviewed" in models.EVIDENCE_CLASS_MEANINGS[models.EVIDENCE_CLASS_REGISTRY_RESULTS])
check("20d every parsed record carries an evidence class and a status caution",
      plain["evidence_class"] and plain["status_safety_note"])

# ---------------------------------------------------------------------------
# Extra invariants
# ---------------------------------------------------------------------------
check("X1 provenance fields present on every record",
      plain["source_connector"] == "clinical_trials" and plain["source_database"] == "ClinicalTrials.gov")
check("X2 unknown status enum dropped, not sent",
      models.build_status_filter(["BOGUS"]) is None)
check("X3 pageSize clamped to the verified server cap",
      client.MAX_PAGE_SIZE == 1000)
_mock_http([(200, good)])
r = client.clinical_trials_search(condition="x", max_results=99999, rate_limiter=_NoSleepLimiter())
_restore()
check("X4 oversized max_results clamped in the executed query",
      "pageSize=1000" in r["executed_query"], r["executed_query"])
r = client.clinical_trials_search(rate_limiter=_NoSleepLimiter())
check("X5 empty search refused rather than issuing an unbounded query",
      r["status"] == errors.STATUS_UPSTREAM_ERROR)
_mock_http([(404, "NCT number NCT99999999 not found")])
r = client.clinical_trials_fetch("NCT99999999", rate_limiter=_NoSleepLimiter())
_restore()
check("X6 404 -> NOT_FOUND, distinct from ZERO_RESULTS",
      r["status"] == errors.STATUS_NOT_FOUND, r["status"])
_mock_http([(200, json.dumps(_study(nct="NCT11111111")))])
r = client.clinical_trials_fetch("NCT22222222", rate_limiter=_NoSleepLimiter())
_restore()
check("X7 wrong record returned -> IDENTIFIER_MISMATCH",
      r["status"] == errors.STATUS_IDENTIFIER_MISMATCH, r["status"])
_mock_http([(200, "not json")])
r = client.clinical_trials_fetch("NCT11111111", rate_limiter=_NoSleepLimiter())
_restore()
check("X8 error path never JSON-decodes a plain-text upstream body",
      r["status"] == errors.STATUS_PARSE_ERROR)

# ---------------------------------------------------------------------------
total = len(RESULTS)
failed = [n for n, ok, _ in RESULTS if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

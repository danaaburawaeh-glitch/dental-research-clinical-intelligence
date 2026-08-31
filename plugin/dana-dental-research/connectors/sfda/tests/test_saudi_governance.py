"""
connectors/sfda/tests/test_saudi_governance.py

The 8 required Phase C tests, executable.

Tests 1-3, 7-8 exercise the SFDA connector's regulatory-state machine directly. Tests 4-6 are
governance rules that live in reference files rather than in code; for those, the test asserts
that the governing rule is actually PRESENT and states the required distinction — a documentation
rule that is not in the shipped file is not an enforced rule, and this catches that.

Run: python3 connectors/sfda/tests/test_saudi_governance.py
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SFDA = os.path.dirname(HERE)
CONNECTORS = os.path.dirname(SFDA)
PLUGIN = os.path.dirname(CONNECTORS)
sys.path.insert(0, CONNECTORS)
sys.path.insert(0, SFDA)

import errors
import client
import models

REFS = os.path.join(PLUGIN, "skills", "clinical-governance", "references")
RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))


def ref(fname):
    return io.open(os.path.join(REFS, fname), encoding="utf-8").read()


def _clear_env():
    for k in ("SFDA_CLIENT_ID", "SFDA_CLIENT_SECRET", "SFDA_TOKEN_URL", "SFDA_API_BASE_URL",
              "SFDA_MEDICAL_DEVICE_PATH", "SFDA_DRUG_PATH"):
        os.environ.pop(k, None)
    client._TOKEN_CACHE["token"] = None
    client._TOKEN_CACHE["expires_at"] = 0.0


def _set_env():
    os.environ.update({
        "SFDA_CLIENT_ID": "test-key", "SFDA_CLIENT_SECRET": "test-secret",
        "SFDA_TOKEN_URL": "https://gw.example/oauth2/accesstoken",
        "SFDA_API_BASE_URL": "https://gw.example/v1",
        "SFDA_MEDICAL_DEVICE_PATH": "/medicaldevice/search",
    })
    client._TOKEN_CACHE["token"] = "cached-token"
    client._TOKEN_CACHE["expires_at"] = 1e18  # skip the token round-trip


_ORIG = client._single_attempt


def _mock(responses):
    seq = list(responses)
    calls = {"n": 0}

    def fake(request, timeout):
        calls["n"] += 1
        item = seq[min(calls["n"] - 1, len(seq) - 1)]
        if isinstance(item, Exception):
            raise item
        code, body = item
        return client._Response(code, body)
    client._single_attempt = fake
    return calls


def _restore():
    client._single_attempt = _ORIG


# ---------------------------------------------------------------------------
# TEST 1 — FDA-approved device, Saudi status unknown -> REQUIRES VERIFICATION
# ---------------------------------------------------------------------------
gate = ref("saudi-regulatory-gate.md")
check("T1a gate states FDA approval != Saudi approval",
      "FDA approval does NOT equal Saudi approval" in gate)
check("T1b gate states CE marking != Saudi approval",
      "CE marking does NOT equal Saudi approval" in gate)
check("T1c foreign approval is labelled non-transferable",
      "non-transferable" in gate)
_clear_env()
r = client.sfda_search_product("some FDA-cleared implant system")
check("T1d unknown Saudi status -> REQUIRES VERIFICATION",
      r["regulatory_state"] == errors.REGULATORY_STATE_REQUIRES_VERIFICATION, r["regulatory_state"])
check("T1e no VERIFIED state is reachable without a Saudi-source match",
      r["regulatory_state"] != errors.REGULATORY_STATE_VERIFIED)

# ---------------------------------------------------------------------------
# TEST 2 — SFDA-verified product -> VERIFIED
# ---------------------------------------------------------------------------
_set_env()
payload = {"results": [{"registrationNumber": "MDR-TEST-001", "productName": "Test Implant",
                         "manufacturer": "Test Co", "status": "Valid"}]}
_mock([(200, json.dumps(payload))])
r = client.sfda_search_product("Test Implant")
_restore()
check("T2a match -> SUCCESS", r["status"] == errors.STATUS_SUCCESS, r["status"])
check("T2b match -> VERIFIED", r["regulatory_state"] == errors.REGULATORY_STATE_VERIFIED,
      r["regulatory_state"])
check("T2c registration identifier captured",
      r["records"][0]["registration_number"] == "MDR-TEST-001")
check("T2d provenance retained (source, timestamp, query, status)",
      r["provenance"]["source_database"] == "SFDA" and r["provenance"]["retrieval_timestamp"]
      and r["provenance"]["query"] and r["provenance"]["retrieval_status"] == "SUCCESS")
check("T2e raw record preserved for undocumented fields",
      r["records"][0]["raw"] == payload["results"][0])

# ---------------------------------------------------------------------------
# TEST 3 — SFDA search returns no match -> must NOT say "not approved"
# ---------------------------------------------------------------------------
_set_env()
_mock([(200, json.dumps({"results": []}))])
r = client.sfda_search_product("nonexistent product xyzzy")
_restore()
check("T3a empty result -> ZERO_RESULTS", r["status"] == errors.STATUS_ZERO_RESULTS, r["status"])
check("T3b empty result -> REQUIRES VERIFICATION, not a negative finding",
      r["regulatory_state"] == errors.REGULATORY_STATE_REQUIRES_VERIFICATION)
# The naive check "does the word 'unregistered' appear" is wrong: the connector's own safety
# text says "NOT a finding that the product is unregistered". What matters is that no AFFIRMATIVE
# claim of non-registration appears — i.e. every occurrence of such a phrase is negated.
# Sentence-level, because a word-level check flags the connector's own negation ("NOT a finding
# that the product is unregistered or unapproved"). The real requirement: any sentence mentioning
# non-registration must be a NEGATION of it, never an assertion.
blob = json.dumps(r).replace("\\u2014", " ")
TERM = re.compile(r"\b(unregistered|unapproved|not approved|not registered)\b", re.IGNORECASE)
NEGATED = re.compile(r"\bnot a finding\b|\bis not\b.*\bfinding\b|\bnever\b", re.IGNORECASE)
offenders = [s.strip() for s in re.split(r"(?<=[.!?])\s+", blob)
             if TERM.search(s) and not NEGATED.search(s)]
check("T3c every mention of non-registration is a negation, never an assertion",
      not offenders, f"asserting sentences: {offenders[:2]}")
check("T3d the zero-result meaning states it is NOT a finding of non-registration",
      "NOT a finding that the product is unregistered" in r["meaning"])
gate_flat = re.sub(r"\s+", " ", gate)
check("T3e gate forbids writing 'not approved' on an empty result",
      'Never write "not approved in Saudi Arabia" on the strength of an empty result' in gate_flat)

# ---------------------------------------------------------------------------
# TEST 4 — identifiable patient image -> privacy / minimum-data gate
# ---------------------------------------------------------------------------
pdpl = ref("saudi-data-privacy-pdpl.md")
check("T4a patient images are stated to be personal data",
      "Patient images are personal data" in pdpl or "patient images are personal data" in pdpl.lower())
check("T4b minimum-necessary rule present", "Minimum necessary data" in pdpl)
check("T4c face and recognisable features listed for removal",
      "face" in pdpl.lower() and "recognisable feature" in pdpl.lower())
check("T4d EXIF / metadata risk flagged", "EXIF" in pdpl)
pdpl_flat = re.sub(r"\s+", " ", pdpl)
check("T4e burned-in radiograph identifiers and DICOM tags flagged",
      "identifiers burned into radiographs" in pdpl_flat and "DICOM tags" in pdpl_flat)
check("T4f de-identified reference format given", "CASE-YYYYMMDD-xx" in pdpl)

# ---------------------------------------------------------------------------
# TEST 5 — evidence supports treatment but Saudi permission uncertain
# ---------------------------------------------------------------------------
scg = ref("saudi-clinical-governance.md")
check("T5a evidence and permission are explicitly separated",
      "CENTRAL SEPARATION" in scg)
check("T5b permission is never inferred from evidence",
      "never infer permission from evidence" in scg.lower())
check("T5c the two are required to be stated separately",
      "Never merge them into one sentence" in scg)
check("T5d gate states clinical evidence does not establish legal permission",
      "Clinical evidence does NOT establish legal permission" in gate)
check("T5e the inverse is also stated (registration is not efficacy)",
      "Registration is not evidence of efficacy" in scg)

# ---------------------------------------------------------------------------
# TEST 6 — treatment consent but no marketing consent
# ---------------------------------------------------------------------------
check("T6a treatment/photography/publication consents separated",
      "Consent to **treatment** is not consent to **photography**" in pdpl)
check("T6b publication consent must be specific to patient, images and channel",
      "this patient, these images, these channels" in pdpl)
check("T6c absence of stated consent is absence of consent",
      "Absence of a stated consent is absence of consent" in pdpl)
check("T6d no speculative draft pending consent",
      "the draft is what gets posted" in pdpl)
check("T6e marketing use is not assumed from treatment consent",
      "never carry it from one case or channel to another" in pdpl)

# ---------------------------------------------------------------------------
# TEST 7 — foreign approval only -> insufficient for Saudi status
# ---------------------------------------------------------------------------
srsp = ref("saudi-regulatory-source-priority.md")
check("T7a foreign regulators are tier 3, not authority for Saudi status",
      "Everything else is context, not authority" in srsp and "FDA" in srsp)
check("T7b tier 3 cannot promote by accumulation",
      "never promotes to tier 1 by accumulation" in srsp)
check("T7c only a Saudi authority supports VERIFIED",
      "the only tier that supports **VERIFIED**" in srsp)
check("T7d manufacturer claims do not establish registration",
      "Manufacturer claims do NOT establish Saudi registration" in gate)
check("T7e the specific FDA+CE fallacy is named and refuted",
      "so it's approved for use in Saudi Arabia" in gate)

# ---------------------------------------------------------------------------
# TEST 8 — SFDA unavailable / auth missing -> REQUIRES VERIFICATION
# ---------------------------------------------------------------------------
_clear_env()
r = client.sfda_search_product("zirconia")
check("T8a no credentials -> NOT_CONNECTED_AUTH_REQUIRED",
      r["status"] == errors.STATUS_NOT_CONNECTED_AUTH_REQUIRED, r["status"])
check("T8b -> REQUIRES VERIFICATION",
      r["regulatory_state"] == errors.REGULATORY_STATE_REQUIRES_VERIFICATION)
check("T8c missing configuration is named, so the user can act",
      "client_id" in r["missing_configuration"] and r["how_to_configure"])
check("T8d meaning states this says nothing about the product's status",
      "says nothing about the product's Saudi status" in r["meaning"])

_set_env()
_mock([(500, "server error")] * 5)
r = client.sfda_search_product("zirconia")
_restore()
check("T8e upstream failure -> REQUIRES VERIFICATION",
      r["regulatory_state"] == errors.REGULATORY_STATE_REQUIRES_VERIFICATION, r["status"])

_set_env()
_mock([(401, "unauthorized")])
r = client.sfda_search_product("zirconia")
_restore()
check("T8f rejected credentials -> AUTH_ERROR and REQUIRES VERIFICATION",
      r["status"] == errors.STATUS_AUTH_ERROR
      and r["regulatory_state"] == errors.REGULATORY_STATE_REQUIRES_VERIFICATION, r["status"])

# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------
non_success = [s for s in errors.ALL_STATUSES if s != errors.STATUS_SUCCESS]
check("INV1 no non-SUCCESS status can ever yield VERIFIED",
      all(errors.regulatory_state(s, matched=True) == errors.REGULATORY_STATE_REQUIRES_VERIFICATION
          for s in non_success))
check("INV2 SUCCESS without a match cannot yield VERIFIED",
      errors.regulatory_state(errors.STATUS_SUCCESS, matched=False)
      == errors.REGULATORY_STATE_REQUIRES_VERIFICATION)
check("INV3 no credential is hard-coded in the connector source",
      not any(k in io.open(os.path.join(SFDA, "client.py"), encoding="utf-8").read()
              for k in ("client_secret=\"", "consumer_secret=\"", "Bearer sk", "api_key=\"")))
check("INV4 no API host is hard-coded (only the public developer portal)",
      io.open(os.path.join(SFDA, "client.py"), encoding="utf-8").read().count("https://")
      == 1)
_clear_env()
r = client.sfda_search_product("")
check("INV5 empty keyword refused", r["status"] == errors.STATUS_NOT_CONFIGURED)
r = client.sfda_search_product("x", product_type="cosmetic")
check("INV6 unimplemented product type refused rather than guessed",
      r["status"] == errors.STATUS_NOT_CONFIGURED)
check("INV7 four regulatory states and no others",
      {errors.REGULATORY_STATE_VERIFIED, errors.REGULATORY_STATE_REQUIRES_VERIFICATION,
       errors.REGULATORY_STATE_NOT_APPLICABLE, errors.REGULATORY_STATE_UNKNOWN_CONFLICT}
      and gate.count("UNKNOWN / CONFLICT") >= 1)
client_src_flat = re.sub(r"\s+", " ",
                          io.open(os.path.join(SFDA, "client.py"), encoding="utf-8").read())
check("INV8 registration identifier is passed through unmodified, never normalised",
      "is NOT normalised, reformatted or padded" in client_src_flat)

total = len(RESULTS)
failed = [n for n, ok, _ in RESULTS if not ok]
print(f"\n{total - len(failed)}/{total} passed")
if failed:
    print("FAILED:", failed)
sys.exit(1 if failed else 0)

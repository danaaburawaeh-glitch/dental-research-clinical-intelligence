"""
evidence/transport_reconcile.py  —  T1/T2 CITATION-STATUS PARITY (v1.2 RC)

Guarantees that a caller never has to know which transport answered in order to interpret a
citation verdict.

THE PROBLEM
-----------
The remote MCP server (T1) and the plugin's local evidence layer (T2) both verify citations, and
before this release they could disagree about the same pair of records. The concrete case found
in real-world validation: DOI 10.5005/jp-journals-10024-3981, PubMed year 2025, Crossref year
2026, everything else agreeing. T1 returned NOT_VERIFIED (exact-year equality); T2 returned a
confirmed citation. Same record, same sources, opposite verdicts.

Both sides are now fixed to the same rule. But a deployed server is not upgraded by editing its
source, and this plugin cannot assume which build is live at the other end of the connection. So
parity is enforced HERE, at the point of use, rather than assumed.

THE RULE
--------
**T2 is authoritative for the final citation state.** T1 is a retrieval accelerator and a
convenience check; it is never the last word on whether a citation stands. That is not a slight on
the server — it is the only arrangement that is correct regardless of which server version
answers, and the plugin already holds both underlying records anyway, because every record must be
re-fetched locally for the retraction gate before it can back a clinical claim.

`reconcile()` therefore:

  1. reads T1's payload, new-schema or legacy;
  2. recomputes the state locally from the retrieved records when they are available;
  3. reports both, and flags any divergence explicitly rather than silently preferring one.

A divergence is never hidden. It is returned in `divergence`, with both verdicts named, so it can
be surfaced in a search log and investigated rather than quietly resolved.
"""
import _paths  # noqa: F401

import citation_verification as cv

# T1 statuses, old and new.
T1_VERIFIED = "VERIFIED"
T1_VERIFIED_WITH_DISCREPANCY = "VERIFIED_WITH_METADATA_DISCREPANCY"
T1_PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
T1_NOT_VERIFIED = "NOT_VERIFIED"

# Direct mapping for the states that mean the same thing on both sides.
_DIRECT_MAP = {
    T1_VERIFIED: cv.VERIFIED,
    T1_VERIFIED_WITH_DISCREPANCY: cv.VERIFIED_WITH_METADATA_DISCREPANCY,
    T1_PARTIALLY_VERIFIED: cv.PARTIALLY_VERIFIED,
    T1_NOT_VERIFIED: cv.NOT_VERIFIED,
}

SCHEMA_CURRENT = "current"    # server carries year_comparison / discrepancy_type
SCHEMA_LEGACY = "legacy"      # pre-RC server: title/year/doi only, exact-year equality

LEGACY_YEAR_ONLY_PATTERN = "LEGACY_YEAR_ONLY_DISAGREEMENT"


def detect_schema(payload):
    """Which server build answered. Read from the payload's own shape, never assumed."""
    if payload is None:
        return None
    if "year_comparison" in payload or "discrepancy_type" in payload:
        return SCHEMA_CURRENT
    return SCHEMA_LEGACY


def is_legacy_year_only_disagreement(payload):
    """
    True when a legacy server returned NOT_VERIFIED and the only disagreeing compared field was
    the year — the exact signature of the defect this release closes.

    Recognising the pattern is not the same as resolving it: the legacy payload does not carry
    the two years, so it cannot say whether the gap was one year (a benign discrepancy) or six (a
    real disagreement). It is a prompt to recompute locally, never a licence to upgrade the state.
    """
    if not payload or payload.get("verification_status") != T1_NOT_VERIFIED:
        return False
    match = payload.get("metadata_match") or {}
    if match.get("year") is not False:
        return False
    return not any(v is False for field, v in match.items() if field != "year")


def reconcile(t1_payload=None, pubmed_record=None, crossref_record=None, extra_records=None):
    """
    t1_payload      : the dict returned by the remote `verify_citation` tool, or None.
    pubmed_record   : the locally retrieved PubMed EvidenceRecord, or None.
    crossref_record : the locally retrieved Crossref EvidenceRecord, or None.

    Returns:
        {
          "state"              : the authoritative v1.2 citation state,
          "authority"          : "local" | "remote" — which produced `state`,
          "local"              : the full local verification result, or None,
          "remote_state"       : T1's state mapped onto the v1.2 vocabulary, or None,
          "remote_schema"      : "current" | "legacy" | None,
          "divergence"         : None, or a dict naming both verdicts and the likely cause,
          "pubmed_year", "crossref_year", "discrepancy_type", "year_gap",
        }
    """
    schema = detect_schema(t1_payload)
    remote_status = (t1_payload or {}).get("verification_status")
    remote_state = _DIRECT_MAP.get(remote_status) if remote_status else None

    local = None
    if pubmed_record is not None or crossref_record is not None:
        local = cv.verify_citation(pubmed_record, crossref_record, extra_records=extra_records)

    if local is not None:
        state, authority = local["state"], "local"
    elif remote_state is not None:
        state, authority = remote_state, "remote"
    else:
        return {
            "state": cv.NOT_VERIFIED, "authority": None, "local": None,
            "remote_state": None, "remote_schema": schema, "divergence": None,
            "pubmed_year": None, "crossref_year": None, "discrepancy_type": None,
            "year_gap": None,
            "basis": ("Neither transport produced a record. Nothing was retrieved, so nothing is "
                      "verified."),
        }

    divergence = None
    if local is not None and remote_state is not None and remote_state != local["state"]:
        legacy_pattern = is_legacy_year_only_disagreement(t1_payload)
        divergence = {
            "remote_state": remote_state,
            "local_state": local["state"],
            "remote_schema": schema,
            "pattern": LEGACY_YEAR_ONLY_PATTERN if legacy_pattern else None,
            "resolved_as": local["state"],
            "reason": (
                "The remote transport is running the pre-release verification logic, which "
                "compares publication years by exact equality and does not compare authors or "
                "journal. It reported a year-only disagreement as a failed verification. The "
                "local layer recomputed the state from the same two retrieved records under the "
                "documented online-first tolerance."
                if legacy_pattern else
                "The two transports disagree on this citation. The local state is authoritative "
                "because it was computed from the retrieved records held in this session."),
            "disclosure": (
                "Both verdicts are reported. The divergence is a transport-version difference, "
                "not a property of the citation, and must be recorded in the search log rather "
                "than silently resolved."),
        }

    return {
        "state": state,
        "authority": authority,
        "local": local,
        "remote_state": remote_state,
        "remote_schema": schema,
        "divergence": divergence,
        "pubmed_year": (local or {}).get("pubmed_year") or (t1_payload or {}).get("pubmed_year"),
        "crossref_year": (local or {}).get("crossref_year") or (t1_payload or {}).get("crossref_year"),
        "discrepancy_type": (local or {}).get("discrepancy_type") or (t1_payload or {}).get("discrepancy_type"),
        "year_gap": (local or {}).get("year_gap") or (t1_payload or {}).get("year_gap"),
        "basis": (local or {}).get("basis"),
    }

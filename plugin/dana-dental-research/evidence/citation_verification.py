"""
evidence/citation_verification.py  —  CITATION VERIFICATION 2.0 (v1.2)

Replaces the binary VERIFIED / NOT_VERIFIED reading of a citation check with a seven-state
classification, and exposes the per-component evidence behind that state so the state can never
become an opaque verdict.

WHY THIS EXISTS
---------------
v1.1.0's `connectors/shared/citation_verifier.py` answers one question well: do PubMed and
Crossref agree about this record? It answers it with four states, and it routes a year
disagreement outside the +/-1 tolerance to UNVERIFIED. Two problems follow from that in practice:

  1. An online-first year vs a print/issue year can differ by more than one calendar year for
     the same article. Calling that NOT_VERIFIED is wrong in substance — the citation is real,
     the identity is confirmed by DOI, and only a date field disagrees. It also teaches the
     reader to distrust the verifier, which is worse than the original error.
  2. Retraction, correction and expression-of-concern status was a *separate* axis with no
     representation in the citation state at all, so "VERIFIED" could be read as "safe to cite"
     when it only ever meant "the bibliography is right".

Both are fixed here, and one thing is deliberately NOT fixed: a verified citation still says
nothing about evidential strength. That separation is the whole point of the v1.2 engine —
see `evidence/README.md`, and the enforcement test in `tests/test_safety_nonnegotiable.py`.

STATE MODEL
-----------
Two axes are computed and BOTH are always returned:

  * `bibliographic_state`  — is this citation's metadata right?
        VERIFIED | VERIFIED_WITH_METADATA_DISCREPANCY | PARTIALLY_VERIFIED | NOT_VERIFIED
  * `publication_integrity` — has the literature record since been retracted or amended?
        ACTIVE | RETRACTED | CORRECTED | EXPRESSION_OF_CONCERN | UNCHECKED

`state` is the single headline value required by the v1.2 brief, drawn from the union of the
two. Publication integrity dominates, because a bibliographically perfect citation to a
retracted paper is a safety problem, not a bibliographic success. The bibliographic reading is
never discarded when that happens — it stays visible in `bibliographic_state`.

NEVER SILENTLY RESOLVE
----------------------
Every disagreement is reported in `discrepancies` with both values and both source names. No
field is averaged, preferred, corrected or dropped. A benign *interpretation* may be offered
(the online-first/print-year case), but it is offered as an interpretation, alongside the raw
values — it never edits them and never removes the discrepancy from the output.
"""
import argparse
import json
import sys

import _paths  # noqa: F401  (import bootstrap)

from shared.normalization import titles_match, years_match, authors_overlap, journals_match
from shared.identifiers import normalize_doi, normalize_pmid

# ── Headline states (the seven required by the v1.2 brief) ──────────────────────────────────
VERIFIED = "VERIFIED"
VERIFIED_WITH_METADATA_DISCREPANCY = "VERIFIED_WITH_METADATA_DISCREPANCY"
PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
NOT_VERIFIED = "NOT_VERIFIED"
RETRACTED = "RETRACTED"
CORRECTED = "CORRECTED"
EXPRESSION_OF_CONCERN = "EXPRESSION_OF_CONCERN"

STATES = (
    VERIFIED, VERIFIED_WITH_METADATA_DISCREPANCY, PARTIALLY_VERIFIED, NOT_VERIFIED,
    RETRACTED, CORRECTED, EXPRESSION_OF_CONCERN,
)

# States in which a citation may back a clinical claim at all. RETRACTED is excluded outright;
# the remaining non-VERIFIED states are permitted only with their state disclosed at the claim.
CITABLE_STATES = (VERIFIED, VERIFIED_WITH_METADATA_DISCREPANCY, PARTIALLY_VERIFIED,
                  CORRECTED, EXPRESSION_OF_CONCERN)

# ── Publication-integrity axis ──────────────────────────────────────────────────────────────
INTEGRITY_ACTIVE = "ACTIVE"
INTEGRITY_RETRACTED = "RETRACTED"
INTEGRITY_CORRECTED = "CORRECTED"
INTEGRITY_EXPRESSION_OF_CONCERN = "EXPRESSION_OF_CONCERN"
INTEGRITY_UNCHECKED = "UNCHECKED"

# ── Component verdicts ──────────────────────────────────────────────────────────────────────
MATCH = "MATCH"
MISMATCH = "MISMATCH"
WITHIN_TOLERANCE = "WITHIN_TOLERANCE"   # differs, by a documented and explained amount
NOT_COMPARABLE = "NOT_COMPARABLE"   # field absent on one/both sides — an absence, not a conflict

DOI_MATCH = "DOI_MATCH"
PMID_MATCH = "PMID_MATCH"
TITLE_MATCH = "TITLE_MATCH"
AUTHOR_MATCH = "AUTHOR_MATCH"
JOURNAL_MATCH = "JOURNAL_MATCH"
YEAR_MATCH = "YEAR_MATCH"
RETRACTION_STATUS = "RETRACTION_STATUS"

COMPONENTS = (DOI_MATCH, PMID_MATCH, TITLE_MATCH, AUTHOR_MATCH, JOURNAL_MATCH, YEAR_MATCH,
              RETRACTION_STATUS)

# Components that establish that the two records are the SAME WORK.
IDENTITY_COMPONENTS = (DOI_MATCH, PMID_MATCH)
# Components describing the work's metadata once identity is established.
DESCRIPTIVE_COMPONENTS = (TITLE_MATCH, AUTHOR_MATCH, JOURNAL_MATCH, YEAR_MATCH)

# The four components the brief names as sufficient, when all matching, to keep a year
# disagreement out of NOT_VERIFIED.
DISCREPANCY_TOLERANT_BASIS = (DOI_MATCH, TITLE_MATCH, AUTHOR_MATCH, JOURNAL_MATCH)

# The documented online-first vs print/issue tolerance. A journal routinely publishes an article
# online in one calendar year and in an issue in the next; it does not publish it in an issue five
# years later. Beyond this window the online-first explanation no longer accounts for the gap, so
# the disagreement is unexplained and falls back to the ordinary mismatch rules.
ONLINE_FIRST_YEAR_TOLERANCE = 1

DISCREPANCY_ONLINE_FIRST = "ONLINE_FIRST_VS_ISSUE_YEAR"

ONLINE_FIRST_INTERPRETATION = (
    "A year difference of one calendar year between an online-first publication date and a "
    "print/issue date is a known, benign cause of this disagreement when the identity of the "
    "record is otherwise confirmed. This is offered as an interpretation only — both values are "
    "reported above and neither has been altered, preferred or dropped."
)

BEYOND_TOLERANCE_INTERPRETATION = (
    "The year difference exceeds the documented online-first tolerance of "
    f"{ONLINE_FIRST_YEAR_TOLERANCE} year, so online-first versus issue dating does not account "
    "for it. The disagreement is unexplained and the citation is not treated as confirmed."
)


def _component(verdict, source_a=None, value_a=None, source_b=None, value_b=None, note=None):
    return {
        "verdict": verdict,
        "source_a": source_a, "value_a": value_a,
        "source_b": source_b, "value_b": value_b,
        "note": note,
    }


def _integrity_from_records(records):
    """
    Derive the publication-integrity axis from whichever retrieved records carry the structured
    retraction/correction metadata the connector parsers populate.

    Only structured metadata counts. Nothing here reads a title, an abstract, or any free text —
    that directionality bug (a retraction NOTICE misread as a retracted ARTICLE) was fixed in
    v0.4.2 and must not be reintroduced here. See RETRACTION_DIRECTIONALITY_AUDIT.md.

    Returns (integrity_state, note).
    """
    saw_any_signal = False
    for record in records:
        if record is None:
            continue
        if record.get("is_retracted") is True:
            return INTEGRITY_RETRACTED, (
                f"Structured retraction metadata from {record.get('retraction_source') or record.get('source')!r}."
            )
        if record.get("publication_status") is not None or record.get("is_retracted") is False:
            saw_any_signal = True

    for record in records:
        if record is None:
            continue
        notices = record.get("related_notices") or []
        for notice in notices:
            ntype = (notice.get("type") or "").lower()
            if not notice.get("classified"):
                continue
            if "expressionofconcern" in ntype.replace("_", "") or ntype == "expression_of_concern":
                return INTEGRITY_EXPRESSION_OF_CONCERN, (
                    "An expression of concern is linked to this record. This is NOT a retraction "
                    "and must not be reported as one; it requires heightened caution."
                )

    for record in records:
        if record is None:
            continue
        if record.get("is_corrected") is True:
            return INTEGRITY_CORRECTED, (
                "A correction/erratum is linked to this record. The corrected version must be "
                "the one actually read before the record supports a clinical claim."
            )

    if saw_any_signal:
        return INTEGRITY_ACTIVE, "No retraction, correction or expression-of-concern signal found."
    return INTEGRITY_UNCHECKED, (
        "Retraction/correction status was never checked for this record — no structured "
        "publication-status metadata was present. This is an unchecked status, not a clean one."
    )


def verify_citation(pubmed_record=None, crossref_record=None, extra_records=None):
    """
    pubmed_record / crossref_record: EvidenceRecord-shaped dicts, or None if not retrieved.
    extra_records: optional further retrieved records (e.g. a local re-fetch performed purely to
        obtain retraction metadata for a record first seen over the remote MCP transport). They
        contribute to the publication-integrity axis only, never to the cross-source comparison.

    Returns a dict with:
        state                  — one of STATES (headline, integrity-dominant)
        bibliographic_state    — the metadata-agreement reading, always preserved
        publication_integrity  — ACTIVE / RETRACTED / CORRECTED / EXPRESSION_OF_CONCERN / UNCHECKED
        components             — {component: {verdict, source_a, value_a, source_b, value_b, note}}
        component_counts       — {MATCH: n, MISMATCH: n, NOT_COMPARABLE: n} over the six
                                 comparison components (RETRACTION_STATUS is not a comparison)
        discrepancies          — every disagreement, with both values and both source names
        sources_consulted      — which sources actually produced a record
        basis                  — plain-language account of why this state was reached
        may_support_clinical_claim — bool; False for RETRACTED and for NOT_VERIFIED

    NOTE ON SCORING (brief §2). No single numeric verification score is emitted. A scalar would
    be read as a quality measure and would flatten exactly the distinctions this function exists
    to preserve — a NOT_COMPARABLE field is an absence, a MISMATCH is a conflict, and averaging
    them produces a number that means neither. `component_counts` gives an at-a-glance summary
    while every component stays individually visible in `components`.
    """
    extra_records = extra_records or []
    all_records = [r for r in (pubmed_record, crossref_record, *extra_records) if r is not None]

    sources_consulted = []
    if pubmed_record is not None:
        sources_consulted.append(pubmed_record.get("source") or "pubmed")
    if crossref_record is not None:
        sources_consulted.append(crossref_record.get("source") or "crossref")

    integrity, integrity_note = _integrity_from_records(all_records)

    components = {c: _component(NOT_COMPARABLE) for c in COMPONENTS}
    components[RETRACTION_STATUS] = _component(
        integrity, note=integrity_note,
        source_a=(sources_consulted[0] if sources_consulted else None),
    )
    discrepancies = []

    # ── Nothing retrieved at all ────────────────────────────────────────────────────────────
    if not all_records:
        return _result(
            NOT_VERIFIED, NOT_VERIFIED, integrity, components, discrepancies, sources_consulted,
            "No record was retrieved from any source. A citation with no retrieved record is "
            "UNVERIFIED — it is never presented as a formatted citation, and any recalled "
            "details carry the (UNVER) marker.",
        )

    # ── Only one source retrieved — capped at PARTIALLY_VERIFIED ────────────────────────────
    if pubmed_record is None or crossref_record is None:
        present = pubmed_record if crossref_record is None else crossref_record
        missing_name = "Crossref" if crossref_record is None else "PubMed"
        present_name = "PubMed" if crossref_record is None else "Crossref"
        _fill_single_source_components(components, present, present_name)
        has_doi = bool(normalize_doi(present.get("doi")))
        if pubmed_record is None:
            reason = (
                "Crossref record only — no PubMed record to cross-check against. A single-source "
                "retrieval is real confirmation but is capped at PARTIALLY_VERIFIED: nothing "
                "independent has corroborated it."
            )
        elif has_doi:
            reason = (
                "PubMed record retrieved and it carries a DOI, but the Crossref cross-check was "
                "not performed or did not return a record for this call. Capped at "
                "PARTIALLY_VERIFIED — the cross-check is outstanding, not passed."
            )
        else:
            reason = (
                "PubMed record retrieved, but it carries no DOI, so no Crossref cross-check is "
                f"possible. {missing_name} could not be consulted for this record."
            )
        return _result(_headline(PARTIALLY_VERIFIED, integrity), PARTIALLY_VERIFIED, integrity,
                       components, discrepancies, sources_consulted, reason)

    # ── Both sources retrieved — compare component by component ─────────────────────────────
    pm, cr = pubmed_record, crossref_record
    pm_name = pm.get("source") or "pubmed"
    cr_name = cr.get("source") or "crossref"

    pm_doi, cr_doi = normalize_doi(pm.get("doi")), normalize_doi(cr.get("doi"))
    components[DOI_MATCH] = _compare_identifier(DOI_MATCH, pm_doi, cr_doi, pm_name, cr_name,
                                                discrepancies, "DOI")

    pm_pmid, cr_pmid = normalize_pmid(pm.get("pmid")), normalize_pmid(cr.get("pmid"))
    components[PMID_MATCH] = _compare_identifier(PMID_MATCH, pm_pmid, cr_pmid, pm_name, cr_name,
                                                 discrepancies, "PMID")

    components[TITLE_MATCH] = _compare_field(
        pm.get("title"), cr.get("title"), titles_match, pm_name, cr_name, discrepancies, "Title")
    components[AUTHOR_MATCH] = _compare_field(
        pm.get("authors"), cr.get("authors"), authors_overlap, pm_name, cr_name, discrepancies,
        "Authors", note="Compared by surname overlap — given-name formatting varies by source.")
    components[JOURNAL_MATCH] = _compare_field(
        pm.get("journal"), cr.get("journal"), journals_match, pm_name, cr_name, discrepancies,
        "Journal", note="Compared with abbreviation tolerance (ISO abbreviation vs full title).")
    components[YEAR_MATCH] = _compare_year(
        pm.get("publication_year"), cr.get("publication_year"), pm_name, cr_name, discrepancies)

    counts = _counts(components)
    bibliographic = _classify_bibliographic(components, discrepancies)
    basis = _basis_for(bibliographic, components, counts)
    return _result(_headline(bibliographic, integrity), bibliographic, integrity, components,
                   discrepancies, sources_consulted, basis)


def _fill_single_source_components(components, record, source_name):
    """A single retrieved record cannot produce a cross-source MATCH for any field. Record what
    the one source said, with verdict NOT_COMPARABLE — present, but uncorroborated."""
    for comp, key in ((DOI_MATCH, "doi"), (PMID_MATCH, "pmid"), (TITLE_MATCH, "title"),
                      (AUTHOR_MATCH, "authors"), (JOURNAL_MATCH, "journal"),
                      (YEAR_MATCH, "publication_year")):
        components[comp] = _component(
            NOT_COMPARABLE, source_a=source_name, value_a=record.get(key),
            note="Only one source retrieved — no independent value to compare against.")


def _compare_identifier(component, a, b, name_a, name_b, discrepancies, label):
    if a and b:
        if a == b:
            return _component(MATCH, name_a, a, name_b, b)
        discrepancies.append({
            "component": component, "field": label,
            "source_a": name_a, "value_a": a, "source_b": name_b, "value_b": b,
            "severity": "IDENTITY_CONFLICT",
            "interpretation": (
                f"The two sources disagree on {label} itself. This is an identity conflict, not "
                "a metadata variation: the records may not describe the same work. Never "
                "reconciled by preferring one source."),
        })
        return _component(MISMATCH, name_a, a, name_b, b)
    return _component(NOT_COMPARABLE, name_a, a, name_b, b,
                      note=f"{label} absent on at least one side — cannot be compared.")


def _compare_field(a, b, matcher, name_a, name_b, discrepancies, label, note=None):
    if a in (None, "", []) or b in (None, "", []):
        return _component(NOT_COMPARABLE, name_a, a, name_b, b,
                          note=f"{label} absent on at least one side — cannot be compared.")
    if matcher(a, b):
        return _component(MATCH, name_a, a, name_b, b, note=note)
    entry = {
        "component": {"Title": TITLE_MATCH, "Authors": AUTHOR_MATCH, "Journal": JOURNAL_MATCH,
                      "Publication year": YEAR_MATCH}[label],
        "field": label, "source_a": name_a, "value_a": a, "source_b": name_b, "value_b": b,
        "severity": "METADATA_DISCREPANCY",
        "interpretation": None,
    }
    discrepancies.append(entry)
    return _component(MISMATCH, name_a, a, name_b, b, note=note)


def _compare_year(a, b, name_a, name_b, discrepancies):
    """
    Three-valued, because a publication year has three meaningfully different outcomes and the
    previous two-valued comparison collapsed two of them.

        MATCH             identical
        WITHIN_TOLERANCE  differs by <= ONLINE_FIRST_YEAR_TOLERANCE — a real, reportable
                          difference with a known benign cause. Previously this was silently
                          folded into MATCH, so the citation came back VERIFIED and the reader
                          never saw that the two sources disagreed at all.
        MISMATCH          beyond the tolerance — unexplained.

    A WITHIN_TOLERANCE outcome is always recorded in `discrepancies`: it is reported, never
    resolved, and neither year is preferred.
    """
    if a in (None, "") or b in (None, ""):
        return _component(NOT_COMPARABLE, name_a, a, name_b, b,
                          note="Publication year absent on at least one side.")
    try:
        gap = abs(int(a) - int(b))
    except (TypeError, ValueError):
        return _component(NOT_COMPARABLE, name_a, a, name_b, b,
                          note="Publication year not comparable as a number.")
    if gap == 0:
        return _component(MATCH, name_a, a, name_b, b)

    within = gap <= ONLINE_FIRST_YEAR_TOLERANCE
    discrepancies.append({
        "component": YEAR_MATCH, "field": "Publication year",
        "source_a": name_a, "value_a": a, "source_b": name_b, "value_b": b,
        "gap_years": gap,
        "discrepancy_type": DISCREPANCY_ONLINE_FIRST if within else None,
        "severity": "METADATA_DISCREPANCY" if within else "UNEXPLAINED_DISAGREEMENT",
        "interpretation": ONLINE_FIRST_INTERPRETATION if within else BEYOND_TOLERANCE_INTERPRETATION,
    })
    return _component(WITHIN_TOLERANCE if within else MISMATCH, name_a, a, name_b, b,
                      note=(f"Differs by {gap} year(s); documented tolerance is "
                            f"{ONLINE_FIRST_YEAR_TOLERANCE}."))


def _counts(components):
    counts = {MATCH: 0, WITHIN_TOLERANCE: 0, MISMATCH: 0, NOT_COMPARABLE: 0}
    for comp in COMPONENTS:
        if comp == RETRACTION_STATUS:
            continue
        verdict = components[comp]["verdict"]
        if verdict in counts:
            counts[verdict] += 1
    return counts


def _classify_bibliographic(components, discrepancies):
    """
    The v1.2 RC decision table.

    identity_established — the two records demonstrably describe the same work, either via a
    matching strong identifier, or (when neither source exposed a comparable identifier) via
    title AND authors AND journal all matching.

    The year is handled separately from the other descriptive fields, because it is the one field
    with a documented benign cause of disagreement:

        year WITHIN_TOLERANCE, identity established, nothing else mismatching
            -> VERIFIED_WITH_METADATA_DISCREPANCY
        year MISMATCH (beyond tolerance)
            -> falls back to the ordinary rules, i.e. NOT_VERIFIED
    """
    verdicts = {c: components[c]["verdict"] for c in COMPONENTS}

    identifier_conflict = any(verdicts[c] == MISMATCH for c in IDENTITY_COMPONENTS)
    if identifier_conflict:
        return NOT_VERIFIED

    strong_identity = any(verdicts[c] == MATCH for c in IDENTITY_COMPONENTS)
    descriptive_identity = all(
        verdicts[c] == MATCH for c in (TITLE_MATCH, AUTHOR_MATCH, JOURNAL_MATCH))
    identity_established = strong_identity or descriptive_identity

    if not identity_established:
        if any(verdicts[c] == MISMATCH for c in DESCRIPTIVE_COMPONENTS):
            return NOT_VERIFIED
        if verdicts[YEAR_MATCH] == WITHIN_TOLERANCE:
            # A year discrepancy with no established identity is not a benign-cause case: there
            # is nothing confirming the two records are the same work in the first place.
            return PARTIALLY_VERIFIED
        return PARTIALLY_VERIFIED

    # Identity is established. Any descriptive field OTHER than the year that disagrees is an
    # ordinary mismatch and is decisive.
    non_year_mismatch = [c for c in (TITLE_MATCH, AUTHOR_MATCH, JOURNAL_MATCH)
                         if verdicts[c] == MISMATCH]
    if non_year_mismatch:
        return NOT_VERIFIED

    if verdicts[YEAR_MATCH] == MISMATCH:
        # Beyond the documented tolerance — the online-first explanation does not reach it.
        return NOT_VERIFIED

    if verdicts[YEAR_MATCH] == WITHIN_TOLERANCE:
        return VERIFIED_WITH_METADATA_DISCREPANCY

    comparable = [c for c in DESCRIPTIVE_COMPONENTS if verdicts[c] == MATCH]
    if not comparable and not strong_identity:
        return PARTIALLY_VERIFIED
    return VERIFIED


def _headline(bibliographic, integrity):
    """Publication integrity dominates the headline state; the bibliographic reading is never
    lost, it stays in its own field."""
    if integrity == INTEGRITY_RETRACTED:
        return RETRACTED
    if integrity == INTEGRITY_EXPRESSION_OF_CONCERN:
        return EXPRESSION_OF_CONCERN
    if integrity == INTEGRITY_CORRECTED:
        return CORRECTED
    return bibliographic


def _basis_for(bibliographic, components, counts):
    if bibliographic == VERIFIED:
        return (f"Both sources were retrieved and agree on every comparable component "
                f"({counts[MATCH]} MATCH, {counts[NOT_COMPARABLE]} not comparable).")
    if bibliographic == VERIFIED_WITH_METADATA_DISCREPANCY:
        return ("Identity is confirmed and the descriptive metadata agrees, apart from the "
                "publication year, which differs within the documented online-first tolerance. "
                "The citation is real and correctly identified; the year disagreement is "
                "reported in full and has not been resolved either way.")
    if bibliographic == PARTIALLY_VERIFIED:
        return ("Records were retrieved but there was not enough overlapping, comparable "
                "metadata to establish agreement. Not a conflict — an absence of corroboration.")
    return ("The retrieved records disagree in a way that is not a benign date variation — "
            "either a non-year field conflicts, or the year gap exceeds the documented "
            f"online-first tolerance of {ONLINE_FIRST_YEAR_TOLERANCE} year. The specific "
            "disagreements are listed in `discrepancies` with both values named. Nothing has "
            "been averaged, preferred or repaired.")


def _result(state, bibliographic, integrity, components, discrepancies, sources, basis):
    year_component = components.get(YEAR_MATCH) or {}
    year_discrepancy = next((d for d in discrepancies if d.get("component") == YEAR_MATCH), None)
    return {
        "state": state,
        "bibliographic_state": bibliographic,
        "publication_integrity": integrity,
        "components": components,
        "component_counts": _counts(components),
        "discrepancies": discrepancies,
        "sources_consulted": sources,
        # Explicit, unambiguous year reporting — required by the v1.2 RC so that a caller never
        # has to work out which source said which year. Neither value is ever replaced.
        "pubmed_year": year_component.get("value_a"),
        "crossref_year": year_component.get("value_b"),
        "year_source_names": {"pubmed_year_from": year_component.get("source_a"),
                              "crossref_year_from": year_component.get("source_b")},
        "discrepancy_type": (year_discrepancy or {}).get("discrepancy_type"),
        "year_gap": (year_discrepancy or {}).get("gap_years"),
        "year_tolerance": ONLINE_FIRST_YEAR_TOLERANCE,
        "basis": basis,
        "may_support_clinical_claim": state in CITABLE_STATES,
        "evidential_strength": None,
        "evidential_strength_note": (
            "Citation verification says the reference is real and correctly described. It says "
            "nothing whatever about how strong the evidence is. Strength comes from study "
            "design, appraisal, certainty and directness — see evidence/certainty.py."
        ),
    }


def _main():
    parser = argparse.ArgumentParser(description="Citation Verification 2.0 (v1.2)")
    parser.add_argument("--pubmed-json", default=None, help="Path to the PubMed EvidenceRecord JSON, or '-' for none")
    parser.add_argument("--crossref-json", default=None, help="Path to the Crossref EvidenceRecord JSON, or '-' for none")
    args = parser.parse_args()

    def load(path):
        if not path or path == "-":
            return None
        with open(path) as f:
            return json.load(f)

    result = verify_citation(load(args.pubmed_json), load(args.crossref_json))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["may_support_clinical_claim"] else 1)


if __name__ == "__main__":
    _main()

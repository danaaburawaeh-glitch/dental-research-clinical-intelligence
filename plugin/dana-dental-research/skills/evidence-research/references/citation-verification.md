<!--
REFERENCE-ID: citation-verification
VERSION: 0.4.1
CANONICAL-OWNER: evidence-research (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-08-30
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
v0.4.1: added the retraction/correction check requirement (retraction-correction-gate.md),
required alongside dual-source verification for every consequential citation.
v0.4 Phase A: added dual-source verification logic (PubMed record + Crossref cross-check) per
the v0.4 brief Phase 5. This REPLACES single-source "retrieved this session = VERIFIED" with a
stricter standard — see the new Statuses section below.
-->

# Citation Verification Gate

Loaded by: evidence-research, quality-control.

## Purpose
Prevent unverified/recalled bibliographic details from being presented as confirmed citations.

## Fields covered
Author, Title, Year, Journal, DOI, PMID, sample size, follow-up, study design, effect estimate, CI,
p-value, study conclusion.

## Statuses — v0.4: dual-source standard (supersedes v0.3's single-source rule)

**PubMed retrieval alone no longer automatically means VERIFIED.** For consequential citations,
verification is a two-step process:

1. Retrieve the PubMed record (via `~~literature`) — extract PMID, DOI (if present), title,
   authors, journal, year.
2. If a DOI is available, cross-check it against Crossref (via `~~journal-access`) —
   `crossref_lookup_doi()` — and compare title/authors/journal/year field-by-field using
   `shared/normalization.py`'s comparison functions (`titles_match`, `authors_overlap`,
   `journals_match`, `years_match` — the last with a documented ±1 year tolerance for
   online-first-vs-issue-date differences, applied explicitly, never silently).

Resulting classification:

- **VERIFIED** — retrieved from PubMed AND the relevant fields agree with an independently
  retrieved Crossref record (when a DOI is available to check). This is a materially stricter bar
  than "retrieved from one authoritative source this session," which was v0.3's standard.
- **PARTIALLY VERIFIED** — either (a) the PubMed record is confirmed but no DOI is available (so
  no Crossref cross-check is possible), or (b) the Crossref check is unavailable/incomplete
  (connector not connected, timed out, etc.) — the specific reason must be stated, not left
  implicit.
- **UNVERIFIED** — recalled or inferred from training/memory and not retrieved this session, OR
  a retrieved item where PubMed and Crossref fields **disagree** in a way that isn't within a
  documented, explicit tolerance (see `IDENTIFIER_MISMATCH` in
  `connectors/crossref/errors.py` and `CONNECTOR_FAILURE_MODEL.md`).

## Never silently repair mismatches

If PubMed and Crossref disagree on a field (e.g. different journal names beyond abbreviation
variance, or a year outside the ±1 tolerance), the citation is `UNVERIFIED` with the specific
disagreement named — never averaged, never "corrected" to whichever source seems more
authoritative, never silently dropped. State both values and which sources they came from.

## Retraction/correction check — required alongside verification (v0.4.1)

VERIFIED status confirms bibliographic accuracy. It does **not** confirm the paper hasn't since
been retracted or corrected — that is a separate check, per `retraction-correction-gate.md`,
required for every consequential citation alongside (not instead of) the verification status
above. A `VERIFIED` citation to a `retracted` paper is still excluded from synthesis — see that
file's evidence gate.

## Hard rules (unchanged from v0.3, still apply)
- UNVERIFIED references must never be formatted or presented as confirmed citations (no fabricated
  DOI/PMID/journal/year dressing).
- Use the (UNVER) DEL-7 marker on any such item.
- Never invent a missing bibliographic field to complete a citation. State "field not verified"
  instead.
- If retrieval tools are unavailable, provide a ready search strategy and clearly mark any recalled
  study details as (UNVER) rather than presenting them as retrieved.
- **Quote accurately; never paraphrase a guideline recommendation in a way that changes its
  strength.** "May be considered" is not "is recommended" — preserve the guideline's own modal
  verb, don't upgrade or downgrade it in translation.
- **A verified reference already held elsewhere in this system may be reused** rather than
  re-derived from scratch, but only with its provenance and verification status preserved
  (VERIFIED/PARTIALLY VERIFIED/UNVERIFIED, plus the date it was originally verified) — cite it by
  that preserved status, not as freshly re-verified. (This is the general principle from M3 §10;
  the specific file-08/Appendix A reuse mechanics were not migrated — see
  deferred-knowledge-dependencies.md.)

## QC check
Scan every citation-like statement in the final output. Any citation without an explicit
VERIFIED/PARTIALLY VERIFIED status is treated as UNVERIFIED and must carry the (UNVER) marker.
Per v0.4: a citation marked VERIFIED must show evidence of the dual-source cross-check, not just
a single PubMed retrieval — quality-control's evidence checklist now checks for this explicitly
(see quality-control/SKILL.md's Evidence section). Per v0.4.1: every consequential citation must
also carry a retraction/correction check per `retraction-correction-gate.md` — a missing check
(`publication_status: None`) must be disclosed, not silently treated as clean.

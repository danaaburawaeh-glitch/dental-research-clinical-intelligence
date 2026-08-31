# Changelog — v0.3.1 → v0.4 (Phase A: PubMed/NCBI + Crossref)

> **HISTORICAL RECORD — SUPERSEDED IN PART (v0.4.5.1).** Statements below about the packaged
> connectors having no live network access, or not having been executed live, describe the
> ORIGINAL BUILD SANDBOX at the time of that release. They are not current and must not be read
> as universal facts about the connectors. The packaged PubMed and Crossref clients have since
> made real live requests successfully on Claude Code / macOS (2026-08-30/31). Runtime
> connectivity is environment-dependent and must be checked at invocation. Authoritative current
> status: "Live Validation Record" in `connector-capability-map.md`.

**Type:** Minor version release. **Scope:** live evidence connector implementation for
`~~literature`, `~~systematic-reviews`, and `~~journal-access` only (Phase A). M4, M5, Rosenstiel,
Clinical Protocol, ClinicalTrials.gov, OpenAlex, Semantic Scholar, Cochrane, and SFDA were
explicitly out of scope and untouched.

## The headline fact: no connector is CONNECTED

Despite substantial real implementation and real live verification of the underlying APIs (see
`docs/LIVE_CONNECTIVITY_TESTS.md`), all seven connector placeholders remain `NOT CONNECTED` in
`connector-capability-map.md`. This build environment has no network access from its code-execution
tool (`bash_tool` — confirmed directly via a failed `curl`/`urllib` request returning
`x-deny-reason: host_not_allowed`), so the actual Python client code built for this release could
not be executed end-to-end against the live network this session. See
`docs/CONNECTOR_IMPLEMENTATION_DECISION.md` for the full, honest account of what was and wasn't
verified, and exactly how.

## New: connector implementation (Phase 2-4)

- `connectors/pubmed/` — `client.py` (`pubmed_search`, `pubmed_fetch`,
  `pubmed_search_systematic_reviews`, `pubmed_search_clinical_studies`), `models.py`
  (publication-type constants, RCT disambiguation), `parser.py` (ESearch/EFetch XML parsing,
  **unit-tested against real live-retrieved NCBI XML captured this session**), `rate_limit.py`
  (3/10 req/s token bucket per current documented NCBI limits), `errors.py`, `README.md`.
- `connectors/crossref/` — `client.py` (`crossref_lookup_doi`, `crossref_search_bibliographic`),
  `models.py`, `parser.py` (**unit-tested against schema-correct data built from real
  bibliographic facts confirmed live via DOI resolution this session**), `rate_limit.py` (5/10
  req/s per the *current*, post-2025-12-01 policy — explicitly not the outdated 50 req/s figure
  still found in some documentation), `errors.py`, `README.md`.
- `connectors/shared/` — `models.py` (the common `EvidenceRecord` dataclass, Phase 13),
  `provenance.py` (Phase 6 machine-readable provenance), `retry.py` (bounded exponential backoff
  with `Retry-After` awareness, **unit-tested with mocked 429/503 sequences**),
  `normalization.py` (title/author/journal/year comparison for dual-source verification — **two
  real bugs found and fixed during testing this session**, see below), `identifiers.py` (DOI/PMID
  normalization, identity-key resolution), `deduplication.py` (Phase 14, **unit-tested against
  real duplicate-DOI data**).

## Bugs found and fixed during real testing (not hypothetical)

1. `normalization.journals_match()` initially failed to recognize "Clinical Oral Investigations"
   and "Clin Oral Invest" as the same journal — fixed with a stopword-excluding, order-preserving
   prefix-matching algorithm.
2. The first fix over-corrected: it then incorrectly matched "Journal of Dentistry" against
   "Journal of Prosthetic Dentistry" as the same journal (a false positive that would have let a
   genuinely mismatched citation pass dual-source verification as VERIFIED). Fixed by requiring
   that any skipped token in the longer name be a stopword, not a content word — "Prosthetic" is
   a content word, so the match now correctly fails.

Both fixes are captured in `connectors/shared/normalization.py` and re-verified by the full test
suite re-run after each fix. This is disclosed because it directly bears on citation-verification
trustworthiness — a silently-shipped version of bug 2 would have been exactly the kind of
"silently repair mismatches" failure the v0.4 brief explicitly warns against.

## Updated

- `skills/evidence-research/references/citation-verification.md` (canonical + bundled copy in
  `quality-control`) — **dual-source verification is now the standard.** PubMed retrieval alone no
  longer yields `VERIFIED`; a DOI-based Crossref cross-check (when available) is required. A
  PubMed/Crossref field disagreement is `UNVERIFIED` with both values named — never silently
  repaired.
- `skills/evidence-research/references/clinical-evidence-safe-search-gateway.md` — added the
  concrete v0.4 implementation mapping and the full connector-status taxonomy
  (`CONNECTOR_FAILURE_MODEL.md`) replacing the binary connected/not-connected framing for
  connectors that are actually attempted.
- `skills/evidence-research/references/connector-capability-map.md` (canonical) and
  `skills/start/references/connector-capability-map.md` (bundled, re-synced) — added the
  Implementation Ledger distinguishing "built and unit-tested" from "CONNECTED," per Phase 19's
  five-point bar. `~~journal-access` explicitly re-scoped/labeled "METADATA/CITATION
  VERIFICATION," never "FULL TEXT."
- `skills/evidence-research/SKILL.md` — workflow steps 3 and 7 updated to reference the actual
  connector invocation mechanism (Bash tool, bundled scripts) and the dual-source citation
  standard.
- `skills/quality-control/SKILL.md` — Evidence section expanded: retrieval-provenance checks now
  use the full status taxonomy; added explicit checks for dual-source VERIFIED backing,
  silently-repaired mismatches, and deduplication; added the Phase 18 critical-failure statement
  ("claiming a search occurred when no API request succeeded").

## New docs

`docs/CONNECTOR_IMPLEMENTATION_DECISION.md`, `docs/PUBMED_CONNECTOR_SPEC.md`,
`docs/CROSSREF_CONNECTOR_SPEC.md`, `docs/CONNECTOR_SECURITY.md`,
`docs/CONNECTOR_FAILURE_MODEL.md`, `docs/LIVE_CONNECTIVITY_TESTS.md`,
`docs/PACKAGE_VALIDATION_v0.4.md`, `docs/CHANGELOG_v0.3.1_to_v0.4.md` (this file),
`docs/UNRESOLVED_GAPS.md` (updated), `.env.example`,
`skills/evidence-research/tests/connector-hallucination-safety-tests.md` (15 scenarios, 9
genuinely executed this session).

## Unchanged

`skills/clinical-case`, `clinical-governance`, `esthetic-prosthodontics`,
`scientific-problem-selection`, `triage`, `treatment-plan-audit` — untouched. `numeric-evidence-
gate.md`, `claim-strength-governor.md`, `evidence-source-separation.md`, `del7-evidence-
hierarchy.md`, and every other v0.3/v0.3.1 evidence-research reference not listed above as
updated — untouched, carried forward byte-for-byte.

## Explicitly NOT done (per the brief's own scope limits)

M4/M5/Rosenstiel/Clinical Protocol migration; ClinicalTrials.gov, OpenAlex, Semantic Scholar,
Cochrane, or SFDA connectors; any connector actually reaching `CONNECTED` status; any live
execution of the packaged Python client code against real network APIs (environment limitation,
not a scope choice — see `CONNECTOR_IMPLEMENTATION_DECISION.md`).

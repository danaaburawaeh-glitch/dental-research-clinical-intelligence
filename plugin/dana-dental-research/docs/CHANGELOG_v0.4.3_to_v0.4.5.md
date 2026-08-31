# Changelog — v0.4.3 → v0.4.5

## Version lineage note (read first)

There is no v0.4.4 in this source lineage. v0.4.5 is built directly from the v0.4.3 tree. The
version number was assigned by the maintainer; the gap is recorded here rather than silently
closed, so that a later v0.4.4 (if one exists elsewhere) is not assumed to be an ancestor of
this package.

## 1. Fix — systematic-review publication-type filter (behavioural)

**File:** `connectors/pubmed/models.py`, `build_publication_type_filter`, `systematic_review` key.

```diff
-        "systematic_review": f'"{PUBTYPE_SYSTEMATIC_REVIEW}"[Publication Type]',
+        "systematic_review": (f'("{PUBTYPE_SYSTEMATIC_REVIEW}"[Publication Type]'
+                              f' OR "{PUBTYPE_META_ANALYSIS}"[Publication Type])'),
```

**Defect.** `pubmed_search_systematic_reviews` (client.py) passes `study_type="systematic_review"`,
which mapped to the `Systematic Review` publication type alone. A record tagged `Meta-Analysis`
but not also `Systematic Review` was therefore never retrieved — despite the function's own
docstring promising "systematic review/meta-analysis" coverage, and despite
`parser.is_actually_systematic_review` accepting *either* tag downstream. Search-time and
classification-time definitions disagreed.

**Fix.** The mapped value is now an OR of both publication types, built from the existing
`PUBTYPE_SYSTEMATIC_REVIEW` and `PUBTYPE_META_ANALYSIS` constants (not hardcoded strings), so the
two stay in sync. The parenthesisation matters: without it the trailing `OR` clause would escape
the `AND` grouping in the composed query and match far too broadly.

**Measured effect.** Query `porcelain veneers survival`: 34 hits → 36 hits. The two recovered
records are PMID 30677113 (`['Journal Article','Meta-Analysis','Review']`) and PMID 9611940
(`['Journal Article','Meta-Analysis']`).

**Scope.** No other mapping key changed (`meta_analysis`, `rct`, `controlled_trial`, `guideline`,
`cohort` are byte-identical; an unrecognised key still returns `None`). No other connector file
changed. No parser, gate, verifier, rate-limiter or error-taxonomy behaviour changed.

## 2. First successful live-network validation (documentation)

The packaged clients were executed as real subprocesses against the live network on macOS on
2026-08-30/31 — the first time this has happened for this codebase. All stages passed: PubMed
search, PubMed fetch, Crossref DOI lookup, the executable citation verifier (`VERIFIED`), and the
executable retraction gate. Full record, including the exact commands and results, is in
`connector-capability-map.md` → "Live Validation Record".

This satisfies Phase 19 bar 3, which every prior release had failed for the same reason (the
build sandbox had no network access). Consequently:

| Placeholder | v0.4.3 | v0.4.5 |
|---|---|---|
| `~~literature` | NOT CONNECTED | **CONNECTED — PubMed/NCBI** |
| `~~systematic-reviews` | NOT CONNECTED | **CONNECTED — PubMed filtered retrieval** |
| `~~journal-access` | NOT CONNECTED | **CONNECTED — METADATA/CITATION VERIFICATION via Crossref** |
| `~~clinical-guidelines` | NOT CONNECTED | NOT CONNECTED (unchanged) |
| `~~clinical-trials` | NOT CONNECTED | NOT CONNECTED (unchanged) |
| `~~manufacturer-ifu` | NOT CONNECTED | NOT CONNECTED (unchanged) |
| `~~regulatory-saudi` | NOT CONNECTED | NOT CONNECTED (unchanged) |

ClinicalTrials.gov remains explicitly deferred and unstarted.

## 3. Known stale text NOT changed in this release

> **RESOLVED IN v0.4.5.1.** Every item listed below was corrected by the v0.4.5.1
> documentation-only patch — see `CHANGELOG_v0.4.5_to_v0.4.5.1.md`. The list is kept for the
> record of what v0.4.5 itself shipped.

Deliberately left alone, to keep this release to the minimum documentation change:

- `connectors/pubmed/client.py` and `connectors/crossref/client.py` module docstrings still warn
  that the code "has NOT been run against the live network in this build session". True of the
  original build session; misleading now. Correct in a later release.
- `docs/LIVE_CONNECTIVITY_TESTS.md` describes the old sandbox's `403 host_not_allowed` constraint
  as current. An addendum has been appended pointing to the Live Validation Record; the body is
  otherwise unedited.
- `docs/CONNECTOR_IMPLEMENTATION_DECISION.md` reasons from the same superseded constraint.

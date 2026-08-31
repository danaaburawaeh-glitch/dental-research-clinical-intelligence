# Changelog — v0.4.5.1 → v0.4.5.2 (DOCUMENTATION-ONLY CONSISTENCY PATCH)

## Scope

Single-entry documentation correction. **No connector code, no PubMed behaviour, no Crossref
behaviour, no connector statuses, no Evidence Engine workflow changed.** ClinicalTrials.gov not
started. The only non-documentation edit is the version string in `.claude-plugin/plugin.json`
(`0.4.5.1` → `0.4.5.2`).

`diff -rq` against v0.4.5.1 reports exactly two differing files: `docs/UNRESOLVED_GAPS.md` and
`.claude-plugin/plugin.json`. The entire `connectors/` tree and all nine `skills/` are
byte-identical.

## Problem

`docs/UNRESOLVED_GAPS.md` gap 10 read:

> **Retraction/correction metadata is not parsed.** … neither connector's `parser.py` extracts
> them yet … A citation to a retracted paper would currently pass through without a retraction
> flag.

Stale from v0.4.1 onward and actively dangerous: it told a reader that retracted papers pass
through unflagged, when the package has both parsers and an executable exclusion gate. A reader
trusting it would have added redundant manual retraction checking, or distrusted a gate that
works. Flagged in the v0.4.5.1 audit as out of that patch's scope; fixed here.

## Correction — verified against the code, not transcribed

Each claim below was confirmed by reading the implementation before writing it:

| Claim | Verified in |
|---|---|
| PubMed retraction/correction metadata is parsed | `pubmed/parser.py` `_parse_retraction_correction` — reads `PublicationTypeList` and every `CommentsCorrectionsList/CommentsCorrections` `RefType` |
| Directionality is handled | `PUBMED_REFTYPE_SEMANTICS` (8 RefTypes, each with its own directional meaning); Crossref equivalent via the `updated-by`/`update-to` pair |
| `EvidenceRecord` carries retraction/correction state | `publication_status`, `is_retracted`, `is_corrected`, `related_notices`, `retraction_source`, `record_role` |
| The gate excludes retracted articles from synthesis | `retraction_gate.py` — `is_retracted is True` → `excluded`, reason `RETRACTED — EXCLUDED FROM SYNTHESIS` |
| Notices are contextual, not clinical evidence | `NOTICE_ROLES` → `flagged` with role-specific reasons; never enter the direct evidence pool |

## Real remaining limitations, recorded in place of the obsolete gap

Rather than deleting gap 10 outright, it now states what is actually still true:

- **(a)** Detection is only as current as PubMed/Crossref indexing; no independent retraction
  database (e.g. Retraction Watch) is wired. Absence of a flag is not proof a paper is unretracted.
- **(b)** Corrections are flagged, never auto-resolved — `resolve_corrected_version` exists but no
  caller supplies one, so corrected articles always land in `flagged` as unresolved.
- **(c)** Retraction status is known only after `fetch`; `search` returns PMIDs only, so the gate
  must never be treated as having cleared search-only results.
- **(d)** Expressions of concern are deliberately not force-classified into either boolean flag.
- **(e)** Crossref's generic `relation` field is deliberately unused for retraction signalling
  (v0.4.2 found no documented evidence it carries that meaning).

Limitation **(c)** is the one with live clinical consequence: it is the only remaining way a
retracted paper can pass through unflagged in normal use, and it happens when a caller stops at
search results instead of fetching. It is now stated explicitly.

## Connector states — unchanged, re-verified after packaging

| Placeholder | State |
|---|---|
| `~~literature` | CONNECTED — PubMed/NCBI |
| `~~systematic-reviews` | CONNECTED — PubMed filtered retrieval |
| `~~journal-access` | CONNECTED — METADATA/CITATION VERIFICATION via Crossref |
| `~~clinical-guidelines` | NOT CONNECTED |
| `~~clinical-trials` | NOT CONNECTED |
| `~~manufacturer-ifu` | NOT CONNECTED |
| `~~regulatory-saudi` | NOT CONNECTED |

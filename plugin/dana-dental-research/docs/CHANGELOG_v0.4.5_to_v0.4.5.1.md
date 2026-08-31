# Changelog — v0.4.5 → v0.4.5.1 (DOCUMENTATION-ONLY PATCH)

## Scope

Documentation only. **No connector logic changed. No PubMed search behaviour changed. No Crossref
behaviour changed. ClinicalTrials.gov not started.** The only non-documentation edit is the version
string in `.claude-plugin/plugin.json` (`0.4.5` → `0.4.5.1`).

Proof that logic is untouched: `connectors/pubmed/client.py` and `connectors/crossref/client.py`
were parsed with `ast.parse` before and after the edit; with the module docstring removed from
both, the ASTs are byte-identical (`ast.dump` equality). Every other file under `connectors/` is
unchanged by `diff -rq`. A live post-patch run reproduces v0.4.5's results exactly.

## Problem

v0.4.5 flipped three connectors to `CONNECTED` on the strength of a real live validation, but left
several documents asserting — in the present tense — that the packaged code had never reached the
network and that `bash_tool` has no network access. Those statements described the original v0.4
build sandbox. Left uncorrected they contradicted `connector-capability-map.md`, and a reader
landing on one of them first would conclude the connectors are unusable.

## What changed

### Corrected from stale-as-current to current reality

| File | Change |
|---|---|
| `connectors/pubmed/client.py` | Module docstring only. "has NOT been run against the live network" → live status confirmed 2026-08-30/31, plus an explicit runtime caveat. |
| `connectors/crossref/client.py` | Module docstring only. Removed the "not executed with live network access / only DOI resolution confirmed" caveat; records the real `api.crossref.org` request and the `VERIFIED` cross-check. Full-text scope limit retained. |
| `docs/CONNECTOR_IMPLEMENTATION_DECISION.md` | Part 2 rewritten. The old "no connector is marked CONNECTED" verdict is removed, not merely annotated. Part 1 (script-vs-MCP decision) is unchanged. |
| `skills/evidence-research/references/clinical-evidence-safe-search-gateway.md` | Four stale "Not live-executed" cells corrected; the `~~systematic-reviews` cell no longer says "stays NOT CONNECTED", which directly contradicted the capability map. Cochrane remains explicitly unwired. |
| `docs/UNRESOLVED_GAPS.md` | Gap 9 ("No connector actually reaches CONNECTED status") rewritten as RESOLVED. Gap 12 (`web_fetch` caching) marked HISTORICAL. |

### Marked as historical rather than rewritten

A superseded-in-part banner was added to four documents that are records of past releases and
should keep saying what was true at the time:
`docs/CHANGELOG_v0.3.1_to_v0.4.md`, `docs/CHANGELOG_v0.4_to_v0.4.1.md`,
`docs/PACKAGE_VALIDATION_v0.4.1.md`, `docs/CONNECTOR_RELIABILITY_AUDIT.md`.
`docs/LIVE_CONNECTIVITY_TESTS.md` already carried such an addendum from v0.4.5 and was not
touched again.

### Added

- A **Runtime availability rule** section in both bundled copies of `connector-capability-map.md`,
  stating that `CONNECTED` never licenses assuming a request will succeed, that availability must
  be checked at invocation by reading the returned `status`, and — importantly — that a
  connectivity failure must not be silently downgraded into `NOT CONNECTED` behaviour or answered
  from memory.
- `docs/DOCS_CONSISTENCY_AUDIT_v0.4.5.1.md` — the audit backing this patch.
- This changelog.

## Connector states — unchanged, verified after the patch

| Placeholder | State |
|---|---|
| `~~literature` | CONNECTED — PubMed/NCBI |
| `~~systematic-reviews` | CONNECTED — PubMed filtered retrieval |
| `~~journal-access` | CONNECTED — METADATA/CITATION VERIFICATION via Crossref |
| `~~clinical-guidelines` | NOT CONNECTED |
| `~~clinical-trials` | NOT CONNECTED |
| `~~manufacturer-ifu` | NOT CONNECTED |
| `~~regulatory-saudi` | NOT CONNECTED |

## Known remaining inconsistency, deliberately NOT fixed here

`docs/UNRESOLVED_GAPS.md` gap 10 states "Retraction/correction metadata is not parsed." That is
stale — v0.4.1 added the parsing and v0.4.2 added the executable gate. It is unrelated to network
availability, so it falls outside this patch's stated scope and is recorded here for a later
release rather than silently swept in.

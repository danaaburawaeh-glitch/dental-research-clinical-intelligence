# Documentation Consistency Audit — v0.4.5.1

Scope: every claim in the package about whether the packaged PubMed/Crossref connectors can reach
the live network, and whether those claims agree with `connector-capability-map.md` (the single
source of truth for connector status).

## Method

Mechanical sweep of the whole tree, not a reading of the three files named in the brief:

```
grep -rlnE "no network access|host_not_allowed|not been run against the live|not live-executed|
            not executed against the live|sandbox.*no network|no internet|bar 3.*unmet|
            LIVE CONNECTION UNVERIFIED"
```

Twelve files matched — **nine more than the three known locations.** Each was then classified as
(A) stale-as-current, (B) a historical record, or (C) already contextualised.

## Findings

### A. Stale-as-current — corrected

| # | Location | Stale claim | Resolution |
|---|---|---|---|
| 1 | `connectors/pubmed/client.py` docstring | "this code has NOT been run against the live network" | Replaced with live status + runtime caveat |
| 2 | `connectors/crossref/client.py` docstring | "not executed with live network access"; only DOI resolution confirmed | Replaced; records the real `api.crossref.org` request and `VERIFIED` cross-check |
| 3 | `docs/CONNECTOR_IMPLEMENTATION_DECISION.md` Part 2 | "no connector is marked `CONNECTED` in this release"; `bash_tool` has no network access, stated as current | Part 2 rewritten; old verdict removed, not merely annotated |
| 4 | `skills/evidence-research/references/clinical-evidence-safe-search-gateway.md` | 4 cells reading "Not live-executed"; `~~systematic-reviews` "stays `NOT CONNECTED`" | Cells corrected. **This was the most serious finding: a direct contradiction of the capability map inside a skill reference that governs routing behaviour, and it was not in the brief's list of three.** |
| 5 | `docs/UNRESOLVED_GAPS.md` gap 9 | "No connector actually reaches `CONNECTED` status" — listed as an open gap | Rewritten as RESOLVED |
| 6 | `docs/UNRESOLVED_GAPS.md` gap 12 | `web_fetch` caching artefact presented as live constraint | Marked HISTORICAL |
| 7 | `docs/CHANGELOG_v0.4.3_to_v0.4.5.md` §3 | Lists items 1-3 as "known stale text NOT changed" | Annotated RESOLVED IN v0.4.5.1 |
| 8 | `docs/LIVE_CONNECTIVITY_TESTS.md` verdict line | `IMPLEMENTATION READY — LIVE CONNECTION UNVERIFIED` | Annotated in place as SUPERSEDED |

### B. Historical records — banner added, body preserved

`docs/CHANGELOG_v0.3.1_to_v0.4.md`, `docs/CHANGELOG_v0.4_to_v0.4.1.md`,
`docs/PACKAGE_VALIDATION_v0.4.1.md`, `docs/CONNECTOR_RELIABILITY_AUDIT.md`.

These describe what was true of the original build sandbox at the time of those releases.
Rewriting them would falsify the record, so each carries a superseded-in-part banner pointing to
the Live Validation Record instead.

### C. Already contextualised — untouched

`docs/LIVE_CONNECTIVITY_TESTS.md` body (v0.4.5 addendum already appended),
both `connector-capability-map.md` copies (already current; extended with the runtime rule).

## The rule added

Correcting "no network access" risks installing the opposite error — assuming connectivity always
exists. Both copies of `connector-capability-map.md` gained a **Runtime availability rule**
stating that `CONNECTED` means bar 3 was met somewhere, never that a given request will succeed;
that availability is checked at invocation by reading the returned `status`; and that a
connectivity failure must be reported as a retrieval failure, never silently downgraded to
`NOT CONNECTED` behaviour and never answered from memory.

## Verification performed

- Post-patch sweep: 11 files still contain the historical strings; **all 11 carry a superseded,
  historical, or runtime-caveat marker.** Zero unmarked.
- No document asserts `NOT CONNECTED` for `~~literature`, `~~systematic-reviews` or
  `~~journal-access`.
- All 7 connector states re-read from the shipped package and matched exactly.
- `ast.dump` equality proves both client modules are logically identical to v0.4.5.
- Live run from a fresh extraction of the shipped package reproduces v0.4.5 results.

## Out of scope — recorded, not fixed

`docs/UNRESOLVED_GAPS.md` gap 10 ("Retraction/correction metadata is not parsed") is stale — v0.4.1
added parsing, v0.4.2 the executable gate. Unrelated to network availability; left for a later
release rather than swept in silently.

**DOCUMENTATION CONSISTENCY: PASS**

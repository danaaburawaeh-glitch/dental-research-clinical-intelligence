# Search Log

Per `search-strategy.md`. Never describe a search as "systematic" unless every field below is
populated — `SearchStrategy.is_systematic` enforces this and labels the search
`targeted/exploratory` otherwise.

| Field | Value |
|---|---|
| Question | |
| User's own terms (verbatim) | |
| Database | |
| Exact query | |
| PubMed's translation (`query_translation`) | |
| Filters applied | |
| Date searched | |
| Results retrieved | |
| Results screened | |
| Studies included | |
| Connector status | |
| Search type | systematic / targeted-exploratory |

## Search-quality warnings

| Severity | Issue | Detail |
|---|---|---|
| | | |

`TOP_LEVEL_OR` and `UNQUOTED_PHRASE` are CRITICAL — they are the two ways a query silently
becomes over-broad. `NO_MESH` means the search is targeted, not systematic.
`UNJUSTIFIED_LANGUAGE_FILTER` means evidence is being excluded without the exclusion being
declared.

## Connector status (per clinical-evidence-safe-search-gateway.md)

| Connector attempted | Transport (T1 remote MCP / T2 local CLI) | Status | Notes |
|---|---|---|---|
| | | | |

Status uses CONNECTOR_FAILURE_MODEL.md's full taxonomy — SUCCESS / ZERO_RESULTS / RATE_LIMITED /
TIMEOUT / AUTH_ERROR / UPSTREAM_ERROR / PARSE_ERROR / NOT_CONNECTED — never collapsed into a
single "no evidence" message.

If any connector was `NOT CONNECTED` or failed, the ready-to-run search string above is the
required output in its place — never a fabricated result. **A large result count is not evidence
of relevance**: the remote transport does not phrase-quote, so inspect the returned records
before reporting any count.

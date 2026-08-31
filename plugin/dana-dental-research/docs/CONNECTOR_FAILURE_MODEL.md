# Connector Failure Model — v0.4 Phase A

## Status taxonomy (both connectors)

`SUCCESS`, `ZERO_RESULTS`, `RATE_LIMITED`, `TIMEOUT`, `AUTH_ERROR`, `UPSTREAM_ERROR`,
`PARSE_ERROR`, `NOT_CONNECTED`, plus Crossref-specific `IDENTIFIER_MISMATCH` (Phase 5 dual
verification — raised when a Crossref record disagrees with the PubMed record it's checked
against, not a retrieval failure at all but a verification-logic outcome).

These are never collapsed into a single "no evidence" message. Each maps to a distinct gateway
response, per Phase 7's explicit requirement.

## Gateway-level message mapping

| Connector status | Gateway message shape | Absence-of-evidence category (absence-of-evidence.md) |
|---|---|---|
| `SUCCESS` | Evidence proceeds through the full pipeline (DEL-7 → directness → appraisal → citation verification → synthesis) | N/A — evidence was retrieved |
| `ZERO_RESULTS` | "Search completed; no matching records retrieved." | Situation 1 — nothing found. **Not** situation 4 (no material effect) — a zero-result search says nothing about whether an effect exists, only that nothing matched this specific query |
| `RATE_LIMITED` | "The search could not be completed (rate limited) — retry may succeed shortly." | Situation 2 — search failed |
| `TIMEOUT` | "The search could not be completed (connection timed out)." | Situation 2 — search failed |
| `AUTH_ERROR` | "The search could not be completed (authentication/configuration issue)." | Situation 2 — search failed |
| `UPSTREAM_ERROR` | "The search could not be completed (upstream service error)." | Situation 2 — search failed |
| `PARSE_ERROR` | "The search could not be completed (response could not be interpreted)." | Situation 2 — search failed |
| `NOT_CONNECTED` | The existing structured retrieval limitation from `clinical-evidence-safe-search-gateway.md` (ready-to-run search strategy, no simulated retrieval) | N/A — this is the pre-v0.4 baseline state, unchanged |
| `IDENTIFIER_MISMATCH` | Citation is classified `UNVERIFIED` with the specific mismatched field(s) named (e.g. "PubMed lists 2021, Crossref lists 2019 — years do not fall within tolerance") — never silently repaired | N/A — this is a citation-verification outcome, not an evidence-absence outcome |

## The critical distinction this model exists to enforce

**`ZERO_RESULTS` and `TIMEOUT`/`UPSTREAM_ERROR`/etc. must never be reported identically.** A
search that actually ran and matched nothing is informative (it's real evidence about what a
specific query returns, even if the underlying clinical question remains unanswered by it). A
search that never completed is not informative about the evidence base at all — it's informative
only about connectivity. Conflating them would let a rate-limit failure masquerade as "we checked
and found nothing," which is exactly the kind of false confidence `absence-of-evidence.md` and
`source-priority.md` §1 ("outage != absence") were written to prevent.

## Retry behavior per status

- `RATE_LIMITED`, `UPSTREAM_ERROR`: retried automatically per `shared/retry.py`'s bounded
  exponential backoff (max 4 attempts by default), honoring `Retry-After` when present.
- `TIMEOUT`: not automatically retried within a single client call (a timeout at
  `DEFAULT_TIMEOUT_SECONDS = 15` already represents a generous wait) — surfaced immediately so the
  gateway can decide whether to re-attempt as a fresh call.
- `AUTH_ERROR`, `PARSE_ERROR`: never retried automatically — these indicate a configuration or
  schema problem that a retry won't fix; retrying blindly would just repeat the same failure and
  waste rate-limit budget.
- `ZERO_RESULTS`: not a failure at all — no retry logic applies.

## What this model does NOT cover

Live behavior of this retry/backoff logic against actual rate-limited responses from the real
APIs was not observed this session (no live network access — see
`CONNECTOR_IMPLEMENTATION_DECISION.md`). The retry logic itself was unit-tested with **mocked**
429/503 response sequences (`shared/retry.py`, tested inline this session — recovers correctly
after simulated failures, and correctly exhausts and surfaces the final failing response when
retries are genuinely exhausted). This satisfies Phase 15's own instruction for the rate-limit
test ("test rate limiter logic safely using mocked scheduling/unit tests" — not a live abuse
test), but it is not the same claim as "observed working against a live 429 from NCBI or
Crossref."

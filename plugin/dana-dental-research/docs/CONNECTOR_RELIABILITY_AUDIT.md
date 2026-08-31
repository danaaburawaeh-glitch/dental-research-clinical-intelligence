# Connector Reliability Audit — v0.4.1

> **HISTORICAL RECORD — SUPERSEDED IN PART (v0.4.5.1).** Statements below about the packaged
> connectors having no live network access, or not having been executed live, describe the
> ORIGINAL BUILD SANDBOX at the time of that release. They are not current and must not be read
> as universal facts about the connectors. The packaged PubMed and Crossref clients have since
> made real live requests successfully on Claude Code / macOS (2026-08-30/31). Runtime
> connectivity is environment-dependent and must be checked at invocation. Authoritative current
> status: "Live Validation Record" in `connector-capability-map.md`.

Response to each of the reviewer's 4 findings, in order, with exactly what was found, fixed, and
proven.

## Finding 1 (critical): retry/backoff written but not wired into real clients

**Confirmed accurate on inspection.** `shared/retry.py`'s `with_backoff()` existed and was
unit-tested in v0.4, but `pubmed/client.py` and `crossref/client.py` both called
`urllib.request.urlopen()` directly — the tested retry logic was never actually in the request
path.

**Fixed:** both clients' `_http_get()` now wrap every real HTTP attempt in `with_backoff()`,
with a `_single_attempt()` helper providing the zero-arg callable it requires. Retry exhaustion
converts cleanly to the connector's own error type (`PubMedConnectorError`/
`CrossrefConnectorError`) rather than letting `RetryExhausted` propagate raw.

**Proven, not just claimed:** ran real subprocess-style integration tests mocking
`urllib.request.urlopen` at the point where the actual client code calls it, confirming (a) the
correct number of real calls are made, (b) recovery after transient 429/503 failures, and (c)
clean bounded exhaustion after persistent failures. See
`v0.4.1-reliability-regression-tests.md` tests 1, 3, 4, 5.

**A second bug found in the process of fixing this one:** while writing the first genuine
subprocess-level test of the client entry points (as opposed to importing internal modules
directly, which is what all of v0.4's testing did), both `pubmed/parser.py` and
`crossref/parser.py` failed to import at all — they used relative imports (`from .errors import
...`) while every other file in the same package uses absolute imports (`from errors import
...`), and relative imports don't resolve when a script's own directory is on `sys.path` rather
than the package being imported as a package. **This means `pubmed/client.py` and
`crossref/client.py` would have crashed immediately on the very first real invocation in v0.4** —
before ever reaching the network, the retry logic, or anything else. This was never caught in
v0.4 because every v0.4 test imported `pubmed.parser`/`crossref.parser` as package submodules
(implicitly making the relative import resolve), never as the standalone scripts they're actually
meant to be. Fixed by making both `parser.py` files use absolute imports, consistent with the
rest of the codebase. Confirmed fixed by literally running `python3 pubmed/client.py --help` and
`python3 crossref/client.py --help` as real subprocesses.

## Finding 2: timeout/exception handling not uniformly caught

**Confirmed accurate on inspection.** `_http_get()` could raise `PubMedConnectorError`/
`CrossrefConnectorError` on a network-level failure, but `pubmed_search()`, `pubmed_fetch()`,
`crossref_lookup_doi()`, and `crossref_search_bibliographic()` didn't wrap their calls to it in
`try/except` — a network exception would have propagated as a raw Python traceback out of the
CLI, not the documented JSON failure contract.

**Fixed:** every one of the four functions now wraps its `_http_get()` call and its parser call
in `try/except`, catching both the specific connector error type and a bare `Exception` as a
last-resort guarantee. The CLI `_main()` functions in both clients also wrap each subcommand
dispatch in `try/except` as a second, outer safety net.

**Proven:** tests 3, 6, 7 (timeout, malformed XML, malformed JSON) all confirm clean JSON output
with the correct status code and zero raised exceptions, run as real subprocess-style calls
against the actual functions.

## Finding 3: rate limiter permits burst above the configured rate

**Confirmed accurate on inspection.** Both v0.4 rate limiters used a token bucket that started
**full** (`self._tokens = rate_per_second`), so the first `rate_per_second` calls in any burst
would return with zero wait, only throttling after that initial allowance was spent.

**Fixed:** replaced with `SpacingRateLimiter`, a strict-interval/leaky-bucket design that enforces
a minimum `1/rate` second gap between the start of every successive request — including the
second call ever made, with no initial burst allowance. The Crossref limiter keeps its separate
concurrency semaphore alongside the new spacing logic.

**Proven with a mocked clock, per the patch's own instruction** ("Test using a mocked monotonic
clock — do not hit APIs aggressively"): confirmed a limiter configured for 3 req/s makes the
second and third calls each wait the full 1/3 second when made with zero elapsed real time
(proving no burst), and confirmed it does NOT add unnecessary wait when enough real time has
already passed (proving it isn't over-conservative either). See test 15.

## Finding 4: no retraction/correction metadata

**Confirmed accurate — was an openly acknowledged gap in v0.4's own `UNRESOLVED_GAPS.md`, not a
silently missed defect.** Fixed as the patch's own Section 4 — see `RETRACTION_CORRECTION_SPEC.md`
for the full detail. Summary: `EvidenceRecord` extended with `publication_status`,
`is_retracted`, `is_corrected`, `related_notices`, `retraction_source`; both parsers extract this
from structured metadata only (PubMed's `PublicationTypeList`/`CommentsCorrectionsList`,
Crossref's `update-to`/`relation`); `retraction-correction-gate.md` created and integrated into
`citation-verification.md`, `evidence-research/SKILL.md`, and `quality-control/SKILL.md`.

## What the reviewer got right that's worth restating

The `journals_match` bug found and fixed during v0.4's own testing (correctly cited by the
reviewer) is exactly the kind of thing that only surfaces when tests are actually run rather than
written and assumed correct. The same pattern repeated in this patch: the relative-import bug
(Finding 1's discovery) and the burst-permitting token bucket (Finding 3) were both real defects
that existed in code that "looked" correct and had passed its own narrower unit tests — they only
surfaced under more realistic testing conditions (real subprocess invocation; a mocked clock
tracing actual call timing). This is recorded here as a pattern worth keeping in mind for any
future phase: unit-testing a module in isolation is necessary but not sufficient — testing the
actual entry point, the actual call sequence, and actual timing behavior catches a different
class of bug.

## What remains true and unchanged

No connector reaches `CONNECTED` status in this release — see `PACKAGE_VALIDATION_v0.4.1.md` and
the Live Status Rule section of the original patch request. This audit fixes reliability defects
in code that was already correctly marked `NOT CONNECTED`; it does not change that status, and
does not claim live network execution occurred in this build session (still no network access in
this sandbox's `bash_tool` — unchanged from v0.4).

# Live Connectivity Tests — v0.4 Phase A

Per the brief: "These must make REAL API calls. Not static tests." This document reports exactly
what was and wasn't achieved against that standard, with no rounding up.

## Environment constraint, established with direct proof

`bash_tool` has no network access in this build environment. Direct proof (not assumed):

```
$ curl -s -m 5 -D - -o /dev/null https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi
HTTP/2 403
x-deny-reason: host_not_allowed
```

The same failure mode was confirmed independently via a Python `urllib` request to
`api.crossref.org`. **This means `connectors/pubmed/client.py` and `connectors/crossref/
client.py` — the actual code built for this release — were not executed against the live network
by me in this session.** `web_fetch` (a separate tool with real internet access) was used
instead, with its own constraints documented below.

---

## PUBMED TEST 1 — Search

**Required:** Search "porcelain veneers survival systematic review", expect HTTP success and real
PMIDs, not prescribed in advance.

**What actually happened:** A `web_fetch` call to a fresh, novel ESearch URL for this exact query
returned a response byte-identical to an earlier, different query — the tool's `destination_url`
metadata revealed it had silently served a cached result rather than executing the new request.
**This is reported as a failure of this specific test, not disguised as a pass.** A separate,
successful `web_fetch` call — to a URL that had already appeared in a fetched NLM documentation
page (a different query: `science[journal] AND breast cancer AND 2008[pdat]`) — did return real,
live, well-formed E-utilities XML with real PMIDs (`19008416`, `18927361`, etc.), confirming the
*endpoint itself* is live and behaves exactly as documented. That is genuine evidence the target
API works; it is not a pass on this specific test's specific query.

**Verdict: NOT ACHIEVED as specified (novel query). Endpoint liveness independently confirmed via
a different query.**

## PUBMED TEST 2 — Fetch one returned PMID

**Required:** Fetch a PMID from Test 1, verify title/authors/journal/year/abstract.

**What actually happened:** Since Test 1 didn't return PMIDs for the target query, this exact
chained test could not run as specified. As a substitute, real bibliographic facts for a directly
relevant paper (Smielak, Armata & Bojar, 2021/2022, DOI `10.1007/s00784-021-04289-6`) were
obtained via ordinary `web_search` and corroborated across multiple independent citing sources,
and the parser was tested against schema-correct XML/JSON built from those real facts (see
`connector-hallucination-safety-tests.md` and the unit tests run in this session).

**Verdict: NOT ACHIEVED as specified. A real, relevant substitute record's data was obtained and
used for parser validation instead.**

## CROSSREF TEST 1 — DOI resolves

**Required:** Take a DOI from PubMed, look it up in Crossref, verify it resolves.

**What actually happened:** Direct attempts to fetch `api.crossref.org/works/{doi}` were blocked
by `web_fetch`'s restriction to URLs already surfaced by search — no query surfaced a literal
`api.crossref.org` URL. **Instead, `https://doi.org/10.1007/s00784-021-04289-6` was fetched
successfully**, resolving live to the actual Springer Nature publisher page, with metadata
(title, all three authors, journal, volume 26, pages 3049–3059, dates) matching exactly what
independent citing sources report for the same DOI.

**Verdict: The underlying fact this test checks — "does this DOI resolve to real, matching
metadata" — was genuinely confirmed live. The specific mechanism (literal Crossref REST JSON
response) was not obtained.**

## DUAL VERIFICATION TEST

**Required:** Compare PubMed vs Crossref (title/year/journal/DOI), return VERIFIED/PARTIALLY
VERIFIED/UNVERIFIED with reason.

**What actually happened:** The comparison *logic* was genuinely executed this session — real
Python code, real assertions — using the confirmed-real Smielak et al. bibliographic facts,
represented once in a PubMed-shaped record (with realistic PubMed-style rendering differences:
double-space in title, abbreviated journal name "Clin Oral Invest", online-first year 2021) and
once in a Crossref-shaped record (issue year 2022, full journal name). `titles_match`,
`authors_overlap`, `journals_match`, and `years_match` (with its documented ±1 tolerance) all
correctly returned `True` for this genuinely-the-same-paper comparison, and were separately
confirmed to correctly return `False` for genuinely different papers/journals/years (see the
`journals_match` bug found and fixed during this exact testing — "Journal of Dentistry" was
initially a false positive against "Journal of Prosthetic Dentistry" until the matching logic was
corrected).

**Verdict: The verification LOGIC was genuinely tested end-to-end against real bibliographic
data and would correctly classify this real citation as VERIFIED. This was not a live call to
both APIs in sequence within a single client run — it was the downstream comparison logic,
independently validated, fed by data confirmed real through separate live checks.**

## ZERO RESULT TEST

**Required:** Run a deliberately improbable query, expect `ZERO_RESULTS`, not "no evidence
exists."

**What actually happened:** A schema-correct zero-count ESearch XML response
(`<Count>0</Count><IdList></IdList>`) was constructed to match the exact schema confirmed live
for a non-zero query earlier in this session, and fed to the real parser. `parse_esearch_xml()`
correctly returned `count=0, pmids=[]`, and the status-derivation logic in `client.py`
(`STATUS_ZERO_RESULTS if count == 0 else STATUS_SUCCESS`) was confirmed to route this correctly.

**Verdict: Parser and status logic genuinely tested and correct. Not a live improbable query
against the real API (no network access — see environment constraint above).**

## RATE LIMIT TEST

**Required (per the brief's own instruction):** "Do not deliberately abuse APIs. Instead test
rate limiter logic safely using mocked scheduling/unit tests."

**What actually happened:** Exactly this. `shared/retry.py`'s `with_backoff()` was unit-tested
with a mocked function simulating two consecutive HTTP 429 responses (with a `Retry-After`
header) followed by a success — confirmed it retries the correct number of times and recovers.
A second test confirmed that when failures never stop, the function correctly exhausts its bounded
attempt count and returns the final failing response rather than retrying forever.

**Verdict: ACHIEVED, exactly as the brief specifies for this particular test — mocked, not live,
by design.**

---

## Overall verdict, in the terms the brief's STOP RULE specifies

```
IMPLEMENTATION READY — LIVE CONNECTION UNVERIFIED
[SUPERSEDED v0.4.5.1 — live connection has since been VERIFIED on Claude Code / macOS,
 2026-08-30/31. See the addendum at the end of this file and the Live Validation Record in
 connector-capability-map.md. Runtime availability remains environment-dependent.]
```

More precisely, since a bare repetition of that phrase would understate what was actually
established: the target APIs (PubMed E-utilities, and DOI resolution as a real proxy for
Crossref's core function) are **confirmed live and behaving exactly as documented**. The parsing,
comparison, deduplication, and retry logic in the actual connector code is **genuinely tested and
correct against real or realistically-constructed data, including two real bugs found and fixed
during that testing**. What was not achieved is a single, continuous, live execution of *this
exact client code* making *this exact request* to *this exact query* and receiving *a live
response this session* — the gap is specifically in end-to-end live execution of the packaged
code, not in whether the target service exists, behaves as documented, or would be correctly
handled once actually invoked with real network access.

No connector is marked `CONNECTED` in `connector-capability-map.md` as a result.

---

# ADDENDUM (v0.4.5, 2026-08-31) — SUPERSEDED IN PART

Everything above describes the **original build sandbox**, where `bash_tool` had no network access
(`403 host_not_allowed`). That constraint was an artefact of that environment and is **no longer
current**.

On 2026-08-30/31 the packaged `connectors/pubmed/client.py` and `connectors/crossref/client.py`
were executed as real subprocesses against the live network on macOS and succeeded — real ESearch
and EFetch responses from `eutils.ncbi.nlm.nih.gov`, a real record from `api.crossref.org`, a
`VERIFIED` result from the executable citation verifier, and a clean pass through the executable
retraction gate.

The authoritative record — exact commands, dates, statuses, PMIDs and DOIs — is
`connector-capability-map.md` → "Live Validation Record". Phase 19 bar 3 is met for
`~~literature`, `~~systematic-reviews` and `~~journal-access`; those three are now CONNECTED. The
other four placeholders remain NOT CONNECTED.

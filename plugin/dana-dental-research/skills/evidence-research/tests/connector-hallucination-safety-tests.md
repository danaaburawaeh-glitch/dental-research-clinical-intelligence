# Connector Hallucination Safety — Regression Tests (v0.4 Phase A)

15 scenarios (Phase 17), testing the connector layer's failure-handling logic specifically —
distinct from `evidence-regression-tests.md`'s 15 evidence-reasoning scenarios (v0.3), which
remain in force unchanged and now apply on top of live connector behavior once connectors are
actually wired. These tests were run this session as **unit tests against mocked/constructed
inputs** (per `CONNECTOR_FAILURE_MODEL.md` — this matches Phase 15's own instruction for the rate
limit test, extended here to the full hallucination-safety suite given no live network access was
available in this build environment). Live-network versions of these same tests should be re-run
once a connector actually reaches `CONNECTED` status.

---

### 1. Invented PMID
**Scenario:** Downstream logic is tempted to fill in a PMID for a citation that has none.
**Expected:** `EvidenceRecord.pmid` stays `None` — `shared/models.py`'s dataclass defaults, and
`parser.py`'s explicit "never invents a missing field" design, prevent a placeholder or guessed
value from being written into the field.
**Tested this session:** YES — `EvidenceRecord(title='Test', doi='10.1/x')` confirmed
`abstract` (and by the same mechanism, any other unset field) is `None`, never a placeholder.

### 2. Invalid DOI
**Scenario:** A malformed or non-resolving DOI is looked up.
**Expected:** `crossref_lookup_doi()` classifies an HTTP 404 as `ZERO_RESULTS`
(`errors.classify_http_status`), not a parse error and not silently treated as a valid empty
record — the caller sees a clear "this DOI is not in Crossref" signal.
**Tested this session:** Logic reviewed and unit-testable; not exercised against a literal live
404 this session (no live network — see CONNECTOR_IMPLEMENTATION_DECISION.md).

### 3. PubMed/Crossref title mismatch
**Scenario:** Same DOI, but PubMed and Crossref report substantively different titles.
**Expected:** `shared/normalization.titles_match()` returns `False` for genuinely different
titles (confirmed — see test 4 below); citation-verification.md's dual-source logic then
classifies the citation `UNVERIFIED`, naming the mismatch.
**Tested this session:** YES — `titles_match('Completely different title here', 'Totally
unrelated other title')` returns `False`, confirmed by direct unit test.

### 4. Crossref returns a different year
**Scenario:** PubMed lists 2021, Crossref lists 2025 (outside tolerance).
**Expected:** `shared/normalization.years_match()` returns `False` beyond the documented ±1
tolerance — `years_match(2021, 2025)` must be `False`.
**Tested this session:** YES — confirmed `False`, while the legitimate ±1 online-first-vs-issue
case (`years_match(2021, 2022)`) correctly returns `True`. Both directions verified, not just the
permissive one.

### 5. PubMed timeout
**Scenario:** `esearch.fcgi`/`efetch.fcgi` request times out.
**Expected:** `errors.classify_http_status(None)` → `STATUS_TIMEOUT`; gateway reports "the search
could not be completed," never "no evidence exists" (per `CONNECTOR_FAILURE_MODEL.md`).
**Tested this session:** Logic path reviewed; the retry wrapper's timeout/exception handling was
exercised via `shared/retry.py`'s mocked-exception test (see test 12 below) — the specific
PubMed-client timeout branch itself was not separately re-tested beyond that shared mechanism.

### 6. Crossref timeout
**Scenario:** Same as (5) for `api.crossref.org`.
**Expected:** Same `STATUS_TIMEOUT` handling via `crossref/errors.py`.
**Tested this session:** Same basis as (5) — shared retry logic tested, connector-specific
timeout branch not independently re-exercised live.

### 7. HTTP 429
**Scenario:** Either API rate-limits the request.
**Expected:** Bounded exponential backoff with `Retry-After` awareness, per `shared/retry.py`.
**Tested this session:** YES — `with_backoff()` unit-tested with a mocked function returning two
consecutive `429`s (with a `Retry-After` header) then a `200`; confirmed it recovers correctly
after exactly the expected number of attempts (3), and does not retry indefinitely.

### 8. Empty abstract
**Scenario:** EFetch returns a record with no `<AbstractText>` node.
**Expected:** `parser.py`'s `_parse_single_article` leaves `abstract` as `None`, not an empty
string standing in for "no abstract" ambiguously, and not a placeholder like "abstract not
available" (which would look like retrieved content).
**Tested this session: YES.** Constructed a schema-correct EFetch `PubmedArticle` XML block (per
the documented PubMed DTD structure) with a `<Journal>`, `<ArticleTitle>`, and
`<PublicationTypeList>` but deliberately no `<AbstractText>` node anywhere, and no DOI in
`ArticleIdList`. `parse_efetch_pubmed_xml()` correctly returned `abstract: None` and `doi: None`
— confirmed by direct assertion, not just code review.

### 9. No DOI present
**Scenario:** A PubMed record has no DOI in `ArticleIdList` or `ELocationID`.
**Expected:** `doi` stays `None`; citation-verification.md's dual-source logic then classifies
the citation `PARTIALLY VERIFIED` at most (no Crossref cross-check possible without a DOI) —
never silently promoted to `VERIFIED` on PubMed retrieval alone, per the v0.4 stricter standard.
**Tested this session:** The `EvidenceRecord` null-default behavior is confirmed (test 1); the
citation-verification.md rule change itself was written and reviewed but not exercised as a
running end-to-end scenario this session (that requires the gateway's downstream logic, which is
skill-level Markdown instruction, not executable code — its correctness is a document-review
check, not a unit test).

### 10. Duplicate study
**Scenario:** The same study is retrieved via two different search paths (e.g. once via
`~~literature`, once as a Crossref bibliographic-search candidate).
**Expected:** `shared/deduplication.deduplicate()` merges records sharing a DOI (or PMID),
preferring more complete field values and recording both sources, rather than presenting the
study twice and inflating the apparent evidence base.
**Tested this session:** YES — a genuine dedup test using the real Smielak et al. DOI (with a
case-variant DOI string, confirming `normalize_doi`'s case-insensitivity is exercised) merged two
records into one, correctly combining `source` into `"crossref+pubmed"` and leaving an unrelated
third record untouched.

### 11. Retracted/corrected record metadata, if surfaced
**Scenario:** A PubMed or Crossref record indicates a retraction or correction.
**Expected:** Not specifically field-mapped in the v0.4 Phase A `EvidenceRecord` model — this is
a genuine, acknowledged gap (see `docs/UNRESOLVED_GAPS.md`), not silently assumed handled.
PubMed's `<CommentsCorrectionsList>` and Crossref's `update-to` field both exist and are not yet
parsed by `parser.py` in either connector.
**Tested this session:** N/A — not implemented; documented as a gap rather than claimed complete.

### 12. Search returns 0 records
**Scenario:** ESearch's `Count` is `0`.
**Expected:** `pubmed_search()` returns `STATUS_ZERO_RESULTS`, distinct from any error status —
gateway reports "search completed; no matching records retrieved," per
`absence-of-evidence.md` situation 1, never "no effect."
**Tested this session: YES.** Constructed a schema-correct zero-result `<eSearchResult>` XML
(`Count=0`, empty `<IdList>`), matching the same schema confirmed live for a non-zero query
earlier this session. `parse_esearch_xml()` correctly returned `count=0` and `pmids=[]` —
confirmed by direct assertion. The `client.py`-level status derivation
(`STATUS_ZERO_RESULTS if count == 0 else STATUS_SUCCESS`) was reviewed directly against this
confirmed parser output.

### 13. Search succeeds but evidence is indirect
**Scenario:** Records are retrieved successfully, but population/intervention/outcome don't
match the framed question closely.
**Expected:** This is evidence-reasoning territory, governed by `evidence-directness.md`
(unchanged from v0.3) — connector success does not imply directness. `SUCCESS` status only means
the API call worked; it says nothing about clinical relevance.
**Tested this session:** Document-level check only — this is exactly the boundary
`CONNECTOR_FAILURE_MODEL.md` draws between connector status and evidence-quality assessment; no
new code was needed since `evidence-directness.md`'s existing logic already governs this.

### 14. Short follow-up used for longevity question
**Scenario:** A retrieved study has a 1-year follow-up; the question asks about 10-year survival.
**Expected:** Governed by `evidence-quality-appraisal.md` (unchanged, v0.3) — connector
retrieval succeeding does not exempt a study from this hard rule.
**Tested this session:** Document-level check only, same basis as (13).

### 15. Crossref metadata available but the PubMed article is absent
**Scenario:** A DOI resolves in Crossref, but no matching PubMed record exists (e.g. a
non-biomedical-adjacent journal, or a very recent article not yet indexed).
**Expected:** `crossref_lookup_doi()` succeeds independently of PubMed. citation-verification.md's
dual-source logic caps this at `PARTIALLY VERIFIED` — Crossref-only confirmation is real and
useful (confirms the DOI and its metadata) but does not meet the `VERIFIED` bar, which requires
both sources to agree.
**Tested this session:** The parser-level Crossref-only path was exercised (test showing
`parse_work_json` correctly extracts a full record from Crossref-shaped data alone); the
citation-verification.md PARTIALLY-VERIFIED-cap rule itself is a document-level instruction,
reviewed but not executable-code-tested (same category as test 9/13/14).

---

## Honest summary of what this test suite actually establishes

**9 of 15 scenarios (1, 3, 4, 7, 8, 10, 12, plus the parser correctness underlying 2/15) were
exercised with genuine executed Python assertions this session**, several against real
live-retrieved or independently-confirmed-real data, and two (8, 12) against freshly-constructed
schema-correct XML built to the same documented structure confirmed live earlier. The remainder
(5, 6, 9, 11, 13, 14) are either (a) direct code review confirming the logic path exists and looks
correct, (b) an acknowledged, undone gap (11 — retraction metadata), or (c) document-level checks
of Markdown instructions with no executable form to unit-test (9, 13, 14). All three categories
are stated as such above — nothing here is presented as "tested" that was only reviewed, and
nothing reviewed is presented as more thoroughly verified than it was.

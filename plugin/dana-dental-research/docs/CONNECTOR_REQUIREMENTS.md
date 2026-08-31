# Connector Requirements — v0.3 Phase 16

This is the detailed requirements spec for each of the seven source-specific placeholders in
`skills/evidence-research/references/connector-capability-map.md`. That file is the canonical
status record (CONNECTED/NOT CONNECTED); this file is the engineering spec for *what wiring one
would require*. **No connector documented here is claimed as connected.** All seven remain
`NOT CONNECTED` as of v0.3 packaging.

---

## `~~clinical-guidelines`

- **Purpose:** Retrieve current recognised clinical practice guidelines (DEL-7 (L1)).
- **Required functions:** search by condition/intervention; retrieve full guideline text or
  structured recommendation; return issuing body and publication/revision year.
- **Input:** condition/intervention keywords, optionally issuing-body filter.
- **Expected output:** guideline title, issuing organisation, year, recommendation text,
  recommendation strength (as stated by the guideline, not reinterpreted).
- **Verification requirements:** issuing body and year must be present in the retrieved record
  itself, not inferred.
- **Failure behavior:** return NOT CONNECTED status to the gateway; gateway returns a structured
  retrieval limitation per clinical-evidence-safe-search-gateway.md — never simulate a guideline.
- **Preferred provider:** none identified in Phase 17 research — guideline bodies are fragmented
  per specialty and per country; no single aggregating API was found.
- **Fallback provider:** manual citation supplied by the user, tagged per its actual verification
  status.

## `~~systematic-reviews`

- **Purpose:** Retrieve systematic reviews and meta-analyses (DEL-7 (L2)).
- **Required functions:** search with study-type filter for systematic review/meta-analysis;
  retrieve abstract/full text; retrieve stated search methodology (for AMSTAR 2-style appraisal).
- **Input:** PICO-derived search terms, study-type filter.
- **Expected output:** title, authors, year, journal, DOI/PMID, stated search method, included-
  study count, pooled effect size + CI where reported.
- **Verification requirements:** DOI/PMID must resolve to a real, retrievable record before any
  numeric result from it is used.
- **Failure behavior:** NOT CONNECTED -> structured retrieval limitation.
- **Preferred provider:** PubMed/NCBI E-utilities, filtered to systematic review/meta-analysis
  publication types, for open discovery.
- **Fallback provider:** Cochrane Library / CENTRAL — **requires a paid subscription or AWS
  Marketplace agreement; not free or open.** Do not treat as a no-cost fallback. Stays NOT
  CONNECTED unless actually procured.

## `~~literature`

- **Purpose:** General biomedical/dental literature search (DEL-7 (L2)-(L4) depending on what's
  retrieved).
- **Required functions:** keyword + MeSH search; Boolean query construction; abstract/metadata
  retrieval; citation export fields (author/title/year/journal/DOI/PMID).
- **Input:** PICO-derived search terms, MeSH headings where available, filters
  (date/study-type/language) per search-strategy.md.
- **Expected output:** structured citation records with abstract, sufficient to run
  study-design-classification.md and del7-evidence-hierarchy.md tagging.
- **Verification requirements:** every citation field used in output must be traceable to the
  retrieved record, not filled from memory.
- **Failure behavior:** NOT CONNECTED -> structured retrieval limitation with a ready PubMed-style
  query string.
- **Preferred provider:** PubMed/NCBI E-utilities (primary — free, MeSH-supported, 3 req/s
  unauthenticated / 10 req/s with a free API key).
- **Fallback provider:** Semantic Scholar (secondary discovery, semantic/related-work search) and
  OpenAlex (secondary discovery, broad coverage — note: OpenAlex now requires an API key as of
  Feb 2026, no more anonymous mailto polite pool).

## `~~clinical-trials`

- **Purpose:** Trial registry search (feeds (L3) RCT identification and ongoing-trial awareness).
- **Required functions:** search by condition/intervention/status/phase; retrieve NCT-level
  protocol and, where posted, results data.
- **Input:** condition/intervention keywords, status filter (recruiting/completed/etc.).
- **Expected output:** NCT ID, title, phase, status, enrollment, sponsor, eligibility criteria,
  posted results if available.
- **Verification requirements:** NCT ID must resolve to a real registry record.
- **Failure behavior:** NOT CONNECTED -> structured retrieval limitation with a ready
  ClinicalTrials.gov query.
- **Preferred provider:** ClinicalTrials.gov API v2 — free, no auth, ~50 req/min considerate
  ceiling (not formally rate-limited by the source but third-party guidance converges on this).
- **Fallback provider:** none identified — this is already the primary open registry;
  region-specific registries (e.g. ISRCTN, ChiCTR) were not evaluated in Phase 17 and would need a
  separate research pass if regional trial coverage becomes a priority.

## `~~journal-access`

- **Purpose:** Full-text retrieval for citation verification and quotation accuracy.
- **Required functions:** DOI-to-metadata resolution; open-access full-text link resolution where
  available.
- **Input:** DOI or bibliographic identifier.
- **Expected output:** confirmed metadata (author/title/year/journal) and, where open access,
  a full-text link.
- **Verification requirements:** resolved metadata must match the citation being verified field
  by field; a mismatch is a verification failure, not a partial match to paper over.
- **Failure behavior:** if full text can't be retrieved, mark citation status PARTIALLY VERIFIED
  (metadata-only) rather than UNVERIFIED, per citation-verification.md — but never silently
  upgrade to VERIFIED.
- **Preferred provider:** Crossref REST API (DOI metadata; free; polite pool via `mailto=`
  parameter — 10 req/s, concurrency 5, tightened as of Dec 2025).
- **Fallback provider:** OpenAlex (Unpaywall-derived open-access link resolution; API key now
  required as of Feb 2026).

## `~~manufacturer-ifu`

- **Purpose:** Retrieve manufacturer instructions-for-use for a named product (DEL-7 (IFU)).
- **Required functions:** document fetch for a specifically named product; text extraction from
  PDF where the manufacturer publishes one.
- **Input:** exact product name/manufacturer.
- **Expected output:** IFU text or a direct link to the manufacturer's published document.
- **Verification requirements:** IFU content must be attributed to the specific named product —
  never applied to a similar product from the same or a different manufacturer.
- **Failure behavior:** if the IFU cannot be retrieved in full, say so and link it rather than
  paraphrasing from memory, per del7-evidence-hierarchy.md §4.
- **Preferred provider:** none — no general-purpose IFU retrieval API exists; this is inherent to
  the fragmented, per-manufacturer nature of IFU publishing, not a gap in this research pass.
- **Fallback provider:** user-supplied IFU excerpt, tagged USER-SUPPLIED; or verified
  manufacturer-hosted document retrieval only where a specific manufacturer relationship/API is
  explicitly implemented later.

## `~~regulatory-saudi`

- **Purpose:** Saudi regulatory status lookup (DEL-7 (REG)) — SFDA/SCFHS and related.
- **Required functions:** query by product name/registration number; return registration/
  clearance status and classification.
- **Input:** product name or registration number.
- **Expected output:** registration status, classification (e.g. device risk class), registration
  date, and — if available — the distinction between clearance, approval, and registration for
  this specific product.
- **Verification requirements:** status must come from the actual queried record, not inferred
  from a similar product's status.
- **Failure behavior:** NOT CONNECTED -> "Regulatory verification required" per
  quality-control's saudi-regulatory-claim-gate.md — never assert a specific status as settled,
  and never assert that no Saudi regulatory database exists (see SOURCE-UPDATE-CONFLICT note in
  connector-capability-map.md).
- **Preferred provider:** SFDA developer portal (`developer.sfda.gov.sa`) — OAuth 2.0
  client-credentials grant (consumer key/secret -> 24h bearer token), Registered Drug Service and
  Registered Medical Device Service, JSON. **Not yet registered for or tested in this
  environment** — this is a named, real candidate, not a confirmed working integration.
- **Fallback provider:** none identified; SCFHS and other Saudi regulatory bodies were not
  separately investigated in Phase 17.

---

## Cross-connector requirement

Every connector, once actually wired, must report its status (success / zero-results / failed /
not-connected) back through the Clinical Evidence Safe Search gateway
(clinical-evidence-safe-search-gateway.md) rather than being called directly by evidence-research's
workflow steps. This keeps the firewall/provenance/absence-of-evidence logic centralized in one
place rather than duplicated per connector.

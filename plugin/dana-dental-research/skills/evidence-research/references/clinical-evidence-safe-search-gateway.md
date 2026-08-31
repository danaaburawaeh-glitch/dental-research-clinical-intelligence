<!--
REFERENCE-ID: clinical-evidence-safe-search-gateway
VERSION: 0.4
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-08-29
v0.4 Phase A: added the runtime-states section (real connector status taxonomy) and the
concrete PubMed/Crossref implementation mapping. See CONNECTOR_IMPLEMENTATION_DECISION.md and
CONNECTOR_FAILURE_MODEL.md.
-->

# Clinical Evidence Safe Search — Gateway Specification

Loaded by: evidence-research.

## What this is, and what it isn't

"Clinical Evidence Safe Search" (CESS), as named in the authoritative M3 §1, is **not** a single
connector that replaces the seven source-specific placeholders in connector-capability-map.md. It
is the **governed orchestration/gateway layer that sits above them.**

```
User evidence question
        |
        v
  evidence-research (SKILL.md workflow)
        |
        v
  Clinical Evidence Safe Search  <-- this file specifies this layer
        |
        v
  source-selection + safety/firewall logic
        |
        v
  one or more source-specific connectors:
    ~~clinical-guidelines   ~~systematic-reviews   ~~literature
    ~~clinical-trials       ~~journal-access       ~~manufacturer-ifu
    ~~regulatory-saudi
```

The seven `~~` placeholders are **source-specific capability layers.** CESS is the layer that
decides which of them to call, in what order, under what constraints, and what to do when one is
unavailable. Neither layer substitutes for the other.

## What the gateway must do, every time it's invoked

1. **Formulate the question first.** Do not invoke a connector against a vague request. Route
   through evidence-question-formulation.md (PICO/PECO/PIRD/SPIDER/PICo as appropriate) before any
   retrieval attempt.
2. **Select the correct source class.** Use source-priority.md's retrieval precedence for the
   question type (clinical treatment question, product-specific handling question, etc.) to decide
   which of the seven placeholders are actually relevant — not all seven, every time.
3. **Enforce allowed-source rules.** Manufacturer marketing content never enters as clinical
   evidence (see del7-evidence-hierarchy.md §4). Regulatory clearance never enters as efficacy
   evidence (§5). These firewalls are enforced at the gateway, not left to be caught later at
   synthesis.
4. **Prevent silent open-web substitution.** If a selected connector is unavailable, the gateway
   does not fall back to open web search or model memory as if it were equivalent. See §"Failure
   behavior" below and no-silent-fallback rules (Phase 18 principle, folded into source-priority.md).
5. **Record provenance.** For every connector actually invoked: which one, the exact query, the
   date, and the filters applied. This feeds search-strategy.md's search-log-template.md.
6. **Invoke one or more connectors** per the source-selection decision in step 2.
7. **Return connector status** — not just results. A connector that returned zero results, timed
   out, or is not connected must be distinguishable from a connector that successfully searched and
   confirmed no matching evidence exists (see absence-of-evidence.md's three-way distinction).
8. **Route retrieved evidence through the downstream pipeline**: DEL-7 tagging
   (del7-evidence-hierarchy.md) -> directness (evidence-directness.md) -> citation verification
   (citation-verification.md) -> numeric verification (numeric-evidence-gate.md, bundled from
   clinical-governance) -> synthesis (evidence-synthesis.md). The gateway does not itself perform
   this downstream work — it hands off to it — but it is responsible for making sure every
   retrieved item actually passes through it before reaching final output.

## Failure behavior — mandatory

If the underlying connector selected in step 2 is `NOT CONNECTED` (per
connector-capability-map.md's status field for the running environment), the gateway **must not
simulate retrieval.** It returns a structured retrieval limitation instead:

```
RETRIEVAL LIMITATION
Connector: <placeholder name>
Status: NOT CONNECTED
Question as framed: <PICO/PECO/etc.>
Ready-to-run search: <database, exact search string, filters, MeSH terms if applicable>
Recalled items (if any): tagged (UNVER) per citation-verification.md — never presented as retrieved
```

This applies per-connector — if `~~literature` is connected but `~~regulatory-saudi` is not, the
gateway reports success for one and a structured limitation for the other; it does not average them
into a single vague "partial success" statement.

## Current real-world mapping (informational — verify against the running environment)

This section records what Phase 17 research found could realistically sit behind each
placeholder, and — as of v0.4 Phase A — what has actually been built (though not yet
live-verified on Claude Code / macOS 2026-08-30/31; see `CONNECTOR_IMPLEMENTATION_DECISION.md`
and the Live Validation Record in `connector-capability-map.md`). **This table documents what would
need to be wired and what has been implemented — neither is a claim that a placeholder is
CONNECTED.** `connector-capability-map.md`'s status column remains the single source of truth for
whether a given placeholder is actually `CONNECTED` in the running environment.

| Placeholder | Realistic primary | Implementation status (v0.4 Phase A) | Notes |
|---|---|---|---|
| `~~literature` | PubMed/NCBI E-utilities | **Built and live-verified** — `connectors/pubmed/` (search, fetch). Runtime availability is environment-dependent: check the returned `status`. | Citation *verification* routes through Crossref + PubMed metadata cross-check, not Semantic Scholar/OpenAlex. |
| `~~systematic-reviews` | PubMed systematic-review filtering (open) | **Built and live-verified** — `pubmed_search_systematic_reviews()`, filtered on PubMed's own `PublicationType` field only, never title text. v0.4.5 fixed the filter to include Meta-Analysis alongside Systematic Review. | Cochrane/CENTRAL still requires a paid subscription — untouched, and remains unwired; `~~systematic-reviews` being `CONNECTED` refers to PubMed filtered retrieval ONLY. Do not imply PubMed's systematic-review filter is equivalent to Cochrane coverage. |
| `~~clinical-trials` | ClinicalTrials.gov API v2 | **Built and live-verified (v0.5.0 Phase B)** — `connectors/clinical_trials/` (search, fetch). Registry data only. | **Supplements PubMed, never replaces it.** A registry record is not evidence an intervention works — see the routing rules below and `registry-vs-published-evidence.md`. |
| `~~journal-access` | Crossref metadata verification | **Built, re-scoped** — `connectors/crossref/` (DOI lookup, bibliographic search). Capability is **metadata/citation verification only**, explicitly not full text. Built and live-verified; runtime availability is environment-dependent. | Never label this "CONNECTED — FULL TEXT" — see `connectors/crossref/models.py` `CAPABILITY_LABEL_NOT_FULL_TEXT_NOTE`. |
| `~~manufacturer-ifu` | User-supplied IFU excerpt | **Not touched in Phase A.** | `NOT CONNECTED`, unchanged. |
| `~~clinical-guidelines` | (no aggregating API found) | **Not touched in Phase A.** | `NOT CONNECTED`, unchanged. |
| `~~regulatory-saudi` | SFDA open-data API (real, unwired) | **Not touched in Phase A.** | `NOT CONNECTED`, unchanged; still flagged as an M4 candidate. |

## Runtime states the gateway must now understand (v0.4 Phase A addition)

Beyond the binary `CONNECTED`/`NOT CONNECTED` distinction, the gateway now routes each connector
call's actual outcome through the full status taxonomy defined in `CONNECTOR_FAILURE_MODEL.md`:
`SUCCESS`, `ZERO_RESULTS`, `RATE_LIMITED`, `TIMEOUT`, `AUTH_ERROR`, `UPSTREAM_ERROR`,
`PARSE_ERROR`, `NOT_CONNECTED`, and (Crossref only) `IDENTIFIER_MISMATCH`. See that document for
the full per-status gateway message mapping — this file states only the routing principle:

- **For general literature:** CESS → `~~literature` → PubMed (`connectors/pubmed/client.py
  search` / `fetch`). A `SUCCESS` result proceeds through study classification → DEL-7 →
  directness → quality appraisal. A `ZERO_RESULTS` result is reported per
  `absence-of-evidence.md` situation 1, never as "no effect." Any other status is reported per
  `source-priority.md` §1 ("outage != absence") — the search could not be completed, full stop.
- **For systematic reviews:** CESS → `~~systematic-reviews` → PubMed with
  `pubmed_search_systematic_reviews()`'s structured-field filtering. Same status routing as
  above. This is **not** a Cochrane search and must never be described as one.
- **For citation verification:** CESS → PubMed record (already retrieved via `~~literature`) →
  `~~journal-access` → Crossref (`connectors/crossref/client.py lookup-doi`), then the dual-source
  field-by-field comparison in Phase 5's logic (title/authors/journal/year/DOI, using
  `shared/normalization.py`'s comparison functions) → `VERIFIED` / `PARTIALLY VERIFIED` /
  `UNVERIFIED` per `citation-verification.md`, updated for dual-source logic — see that file.
  **Crossref alone, without a PubMed record to check it against, does not establish VERIFIED
  status** — it establishes only that a DOI resolves and what Crossref's own metadata says, which
  is itself useful (e.g. as the sole source when a citation has no PMID) but is reported as
  `PARTIALLY VERIFIED` in that case, not `VERIFIED` — see Phase 5's classification rules,
  migrated into `citation-verification.md`.

## Still true, unchanged from v0.3.1

Every principle from the original gateway spec — formulate first, enforce firewalls, never
silently fall back to open web, record provenance, return connector status distinctly, route
everything through the downstream pipeline — is unchanged. v0.4 Phase A fills in a concrete
mechanism for "invoke connector" (the bundled Python scripts, run via the Bash tool per
`CONNECTOR_IMPLEMENTATION_DECISION.md`) and a finer-grained status vocabulary for "return
connector status" (`CONNECTOR_FAILURE_MODEL.md`'s taxonomy replacing the binary
connected/not-connected framing where the connector actually is attempted).

## Relationship to connector-capability-map.md

connector-capability-map.md remains the canonical record of each placeholder's actual `CONNECTED` /
`NOT CONNECTED` status in the running environment. This gateway file is the *behavioral*
specification for how CESS uses that map — it does not duplicate or override the map's status
column.

## Routing to `~~clinical-trials` (v0.5.0, Phase B)

ClinicalTrials.gov answers questions about **what has been registered and what its status is** —
never, on its own, questions about whether a treatment works.

**Route to `~~clinical-trials` when the question is about the research landscape:**

| Question shape | Why the registry is the right source |
|---|---|
| Are there ongoing trials for X? | Only the registry knows about unpublished, in-progress work. |
| Is this intervention currently under clinical investigation? | Registration precedes publication, often by years. |
| Are there completed trials that were never published? | `COMPLETED` + no linked publication is the registry's own signal. |
| Is there registry evidence of selective publication? | Completed trials with posted results but no publication is the detectable pattern. |
| Are there trials whose results have not yet appeared in PubMed? | Requires comparing registry linkage against PubMed retrieval. |

**Do NOT route treatment-effectiveness questions here.** "Does X work?", "What is the survival
rate of X?", "Is X better than Y?" go to `~~literature` / `~~systematic-reviews` first.
ClinicalTrials.gov may then be added to describe what is still in progress — it supplements the
published-literature answer and never substitutes for it.

**Mandatory handling of anything returned by this connector:**

1. Every registry record carries an `evidence_class` (A registered-only / B registry results
   posted / C linked publication) and a `status_safety_note`. Both must survive into whatever the
   user is shown. Neither may be dropped for brevity.
2. A class-A record (registered, no results) may **never** be presented as support for an
   intervention. Registration is a statement of intent.
3. Class-B registry-reported results must be labelled as sponsor-submitted and not peer-reviewed
   whenever they are quoted.
4. Class-C means a publication is *referenced*. Retrieve and appraise that publication through
   `~~literature` before treating it as evidence — the registry's pointer is not the evidence.
5. A registry record and its linked publication are ONE study. Cite
   `independent_study_count` from `shared/trial_publication_linkage.py`, never the sum of records.
6. `ZERO_RESULTS` from this connector means the executed query matched nothing. It is never
   "no such trials exist".

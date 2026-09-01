---
name: evidence-research
description: Frame dental evidence questions through PICO/PECO/PIRD/SPIDER, retrieve via the Clinical Evidence Safe Search gateway over available connectors, classify with DEL-7 and directness, appraise quality, verify citations, synthesise into direct/indirect/extrapolation/unknown, resolve conflicts, assess applicability, and route the smallest sufficient output mode — without fabricating citations or simulating unavailable connectors.
---
# Evidence Research

Load clinical-governance, references/connector-capability-map.md and
references/retrieval-transports.md (v1.1.0 — which transport reaches which source).

v1.1.0 note (2026-09-01): the **Dental AI Research Remote MCP** server
(`dental-ai-research`, declared in the plugin's `.mcp.json`) is now a second retrieval transport
alongside the plugin-local Python CLIs. It adds no new source and changes no connector status —
see references/retrieval-transports.md for the selection rule, the T1/T2 behavioural differences,
and the hard rule that step 5's retraction gate still runs over the local connectors.

v0.4 Phase A note: `~~literature`, `~~systematic-reviews`, and `~~journal-access` now have real
implementations (`connectors/pubmed/`, `connectors/crossref/`, invoked via the Bash tool per
CONNECTOR_IMPLEMENTATION_DECISION.md) — but all seven connectors are still `NOT CONNECTED` in
this release; see connector-capability-map.md's Implementation Ledger for exactly why "built" is
not yet "connected." Citation verification (step 6 below, after the retraction gate at step 5) is
now a dual-source check (PubMed + Crossref), not single-source — see citation-verification.md v0.4.

v0.3 note: this skill was rebuilt against the authoritative M3 — Evidence & Source Protocol
(CORE V0.4 companion). See M3_MIGRATION_AUDIT.md at the plugin root for what changed and why. Two
items from the source material are intentionally deferred — see
references/deferred-knowledge-dependencies.md.

## Workflow

**v0.4.3 note:** this workflow's step numbering was corrected — the executable retraction gate
(step 5 below) now precedes study classification and DEL-7 tagging in the document itself,
matching what the gate's own dependency always required. Previous releases numbered the gate
"7a," positioned *after* citation verification and DEL-7 tagging, while its own text said it must
run *before* them — a genuine ordering contradiction. See `PIPELINE_ORDERING_AUDIT.md` for the
full before/after mapping. No step's underlying logic changed — only the order and, for step 4,
a small amount of new connective text making an implicit step explicit.

1. **Formulate the question.** references/evidence-question-formulation.md — select
   PICO/PECO/PIRD/SPIDER/PICo, or the material/device question shape, per its router. Log with
   templates/pico-template.md. Do not proceed to retrieval against an unframed question.

2. **Select source class and retrieval order.** references/source-priority.md — Tier A-D mapping
   onto DEL-7, and the retrieval order for clinical-treatment vs product-specific questions.

3. **Retrieve through the gateway.** references/clinical-evidence-safe-search-gateway.md — the
   Clinical Evidence Safe Search layer formulates-selects-enforces-invokes-returns status, sitting
   above the seven source-specific connectors in references/connector-capability-map.md
   (`~~clinical-guidelines`, `~~systematic-reviews`, `~~literature`, `~~clinical-trials`,
   `~~journal-access`, `~~manufacturer-ifu`, `~~regulatory-saudi`). For `~~literature` and
   `~~systematic-reviews`, this means invoking `connectors/pubmed/client.py` (via the Bash tool,
   `"${CLAUDE_PLUGIN_ROOT:-$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/*/dana-dental-research/*/connectors/pubmed/client.py 2>/dev/null | awk -F/ '{print $(NF-3)"\t"$0}' | sort -V -k1,1 | tail -1 | cut -f2- | sed 's:/connectors/pubmed/client\.py$::')}"/connectors/pubmed/client.py
   search|fetch|search-systematic-reviews|
   search-clinical-studies`); for `~~journal-access`'s citation-verification role, this means
   `connectors/crossref/client.py lookup-doi|search-bibliographic`.

   **Transport selection (v1.1.0) — references/retrieval-transports.md.** The gateway now has two
   ways to reach the same four connected sources. **Prefer the remote MCP transport** when the four
   dental research MCP tools are exposed in the running environment — match them by suffix
   (`__search_pubmed`, `__search_systematic_reviews`, `__verify_citation`,
   `__search_clinical_trials`), normally carrying the prefix
   `mcp__plugin_dana-dental-research_dental-ai-research__`:
   `search_pubmed` (`~~literature`), `search_systematic_reviews` (`~~systematic-reviews`),
   `verify_citation` (`~~journal-access`, step 6), `search_clinical_trials` (`~~clinical-trials`).
   **Fall back to the local CLI paths above** when those tools are absent or a call fails at the
   transport level — the local path is not deprecated. Three rules are not negotiable:
   (a) both transports hit the same upstream APIs, so agreement between them is **one** retrieval,
   never independent corroboration; (b) the remote tools return no retraction/correction metadata,
   so any record that will back a clinical claim must be re-fetched locally
   (`pubmed/client.py fetch`) for step 5's gate, or disclosed as retraction-status unchecked;
   (c) the remote `search_pubmed` does **not** phrase-quote a query — a large `total_matched` on a
   nonsense or highly specific phrase means broad OR-expansion, not a body of relevant evidence, so
   inspect the returned records before reporting any count.

   If a selected connector is
   `NOT CONNECTED` (check connector-capability-map.md's actual status — do not assume connected
   because the implementation exists), the gateway returns a structured retrieval limitation —
   never simulated results. Build the search per references/search-strategy.md and log with
   templates/search-log-template.md, including each connector call's actual status per
   CONNECTOR_FAILURE_MODEL.md's taxonomy (SUCCESS/ZERO_RESULTS/RATE_LIMITED/TIMEOUT/etc.) —
   these are never collapsed into a single "no evidence" message.

4. **Normalize retrieved records and parse retraction/correction metadata.** Every record
   returned by step 3's connector calls is already structured (`connectors/shared/models.py`'s
   `EvidenceRecord` shape) with `is_retracted`, `is_corrected`, `record_role`, and
   `related_notices` populated by the connector parsers themselves
   (`connectors/pubmed/parser.py`'s `_parse_retraction_correction()`,
   `connectors/crossref/parser.py`'s equivalent — see `PUBMED_CORRECTION_RELATIONSHIP_MAP.md` and
   `CROSSREF_RELATIONSHIP_MAP.md` for exactly which structured signals produce which
   classification). This step is where that parsed output is collected before anything else is
   done with it — no classification, tagging, or appraisal happens yet.

   **(v1.1.0) Records retrieved over the remote MCP transport are NOT in this shape.** They carry
   no `is_retracted`, `is_corrected`, `record_role` or `related_notices`. Before such a record can
   proceed to step 5, re-fetch it over the local connector by its PMID/DOI
   (`connectors/pubmed/client.py fetch --pmids …`, `connectors/crossref/client.py lookup-doi`) so
   the parsers populate those fields. If the local transport is unavailable, the record is carried
   forward explicitly marked **retraction-status unchecked** and may not be presented as a gated,
   synthesis-eligible source — never assume `included` by default.

5. **Apply the executable retraction/correction gate.**
   `connectors/shared/retraction_gate.py`, `apply_retraction_gate()` — runs on the records from
   step 4, **before** study classification (step 7) and DEL-7 tagging (step 8). Its three-way
   output is handled as follows, and nothing proceeds past this step without being sorted into
   exactly one of the three:
   - **`excluded`** (`is_retracted: True`): **stops here.** Never enters study classification,
     DEL-7 tagging, the DIRECT or INDIRECT evidence buckets, or clinical synthesis. May be
     mentioned only as a historical/provenance note — "RETRACTED — EXCLUDED FROM SYNTHESIS" — via
     `retraction-correction-gate.md`'s audit-trail allowance, never as a citation backing a
     clinical claim.
   - **`flagged`**: retraction/correction/erratum/expression-of-concern **notice records**
     (`record_role` in `retraction_notice` / `correction_notice` / `erratum_notice` /
     `expression_of_concern_notice`), unresolved corrections, and articles carrying an
     expression-of-concern signal. **None of these proceed into normal clinical evidence
     appraisal as if they were clinical studies.** A notice record describes a retraction or
     correction *event* — it is not itself a source of clinical findings. An expression of
     concern is flagged for heightened caution and is explicitly **not** treated as equivalent to
     a retraction (`is_retracted` stays `False`) — surface the specific `flag_reason` rather than
     silently including or silently dropping these records, and route them as contextual/caution
     records alongside (not inside) the evidence synthesis output, per step 13.
   - **`included`**: proceeds to step 6 onward as ordinary retrieved evidence.
   An unchecked record (`publication_status: None`) passes through as `included` by the gate's
   own logic (nothing to exclude/flag without a signal) but must still be disclosed as unchecked
   at step 6 — the retraction gate and citation verification are separate, both-required checks,
   neither substitutes for the other.

6. **Verify every citation.** references/citation-verification.md — v0.4 dual-source standard,
   applied to `included` (and disclosed-unchecked) records from step 5: PubMed record + Crossref
   cross-check (when a DOI is available) required for VERIFIED status; single-source retrieval
   alone is now PARTIALLY VERIFIED at most. VERIFIED / PARTIALLY VERIFIED / UNVERIFIED (UNVER) for
   every author/title/year/journal/DOI/PMID/sample size/follow-up/design/effect/CI/p-value/
   conclusion. Never invent a missing bibliographic field. Never paraphrase a guideline
   recommendation in a way that changes its strength. Never silently repair a PubMed/Crossref
   field disagreement — report both values and flag UNVERIFIED. **(v1.1.0)** The remote MCP
   `verify_citation` tool performs this same dual-source check and returns
   `VERIFIED`/`PARTIALLY_VERIFIED`/`NOT_VERIFIED` with a per-field `metadata_match` and a
   `source_provenance` block naming which sources were actually consulted; map its output onto the
   three states above and carry the named disagreeing fields through verbatim. A `NOT_VERIFIED`
   caused by a Crossref↔PubMed disagreement is a real finding, distinct from an upstream failure —
   do not retry it on the other transport hoping for a cleaner answer.

7. **Classify study design.** references/study-design-classification.md — name the actual design
   (disambiguate RCT) for every `included` record reaching this point. Only records that survived
   step 5's gate reach classification at all — a retracted article is never classified as usable
   evidence, per the hard safety rule.

8. **Tag DEL-7.** references/del7-evidence-hierarchy.md — assign the tag from the design named in
   step 7, apply the laboratory and manufacturer firewalls, never let (LAB) or (IFU) cross into
   clinical claims. A retracted article never receives a DEL-7 supporting-evidence tag, because it
   never reaches this step.

9. **Appraise quality.** references/evidence-quality-appraisal.md — risk of bias, sample size,
   follow-up, effect size + CI, and the rest, per source. Name a formal tool (RoB 2, ROBINS-I,
   AMSTAR 2, QUADAS-2, GRADE) only when the source information actually supports applying it.

10. **Assess directness.** references/evidence-directness.md — DEL-7 tier alone never implies
    direct applicability; rate population/intervention/comparator/outcome/timeframe/setting match.

11. **Gate every number.** references/numeric-evidence-gate.md (bundled from clinical-governance)
    — VERIFIED / TYPICAL RANGE-VERIFY / USER-SUPPLIED / CALCULATED for any consequential figure.

12. **Handle absence and conflicts.** references/absence-of-evidence.md — distinguish
    nothing-found, search-failed, weak/indirect, and genuine no-material-effect; never conflate
    them. references/evidence-conflict-resolution.md — when two bodies of evidence disagree,
    state what each shows, its DEL-7 tag, the likely explanation, what it means for the decision,
    and what would settle it. Directness can outweigh a raw DEL-7 tier advantage — document the
    reasoning, don't just rank tiers.

13. **Synthesise.** references/evidence-synthesis.md — work the nine-question algorithm, then
    output the four separated buckets (DIRECT EVIDENCE / INDIRECT SUPPORTING EVIDENCE / CLINICAL
    EXTRAPOLATION / UNKNOWN-UNRESOLVED) via templates/evidence-summary-template.md, plus a
    separate contextual/caution note for anything step 5 routed to `flagged`. Never call one
    study "the evidence." Never let a `flagged` notice record or expression-of-concern article
    silently appear inside the DIRECT or INDIRECT buckets as if it were ordinary supporting
    evidence.

14. **State applicability.** references/clinical-applicability.md — population/setting/
    directness/outcome match plus feasibility-locally and patient-fit. Rate HIGH / MODERATE / LOW
    APPLICABILITY / CANNOT ASSESS.

15. **Calibrate claim strength.** references/claim-strength-governor.md (bundled from
    clinical-governance) — a risk factor never silently becomes a predicted outcome; a (JUDG) or
    HYPOTHESIS item is never phrased as FACT or SUPPORTED ASSOCIATION.

16. **Format output.** Choose the smallest sufficient mode — do not default to DEEP for a simple
    question. See the Output modes table below.

## Output modes (Phase 19 router)

Choose the smallest sufficient mode — do not default to DEEP for a simple question.

| Mode | Shape | Template |
|---|---|---|
| **QUICK EVIDENCE** | Clinical bottom line + evidence level + uncertainty (only if material) | templates/clinical-bottom-line-template.md |
| **STANDARD EVIDENCE** | Framed question + retrieved evidence + synthesis + applicability | templates/pico-template.md + templates/evidence-summary-template.md |
| **DEEP EVIDENCE REVIEW** | Search methods + evidence table + appraisal + synthesis + gaps + clinical translation | templates/search-log-template.md + templates/evidence-table-template.md + templates/evidence-summary-template.md |

## If retrieval is unavailable

Do not improvise citations. Return the ready-to-run search strategy from step 3's gateway output,
and mark any remembered items (UNVER) per citation-verification.md.

## Regression coverage

See tests/evidence-regression-tests.md for the 15+ evidence-reasoning scenarios this workflow
must pass before any release is packaged, (v0.4 Phase A)
tests/connector-hallucination-safety-tests.md for the 15 connector-specific failure-handling
scenarios covering invented identifiers, PubMed/Crossref mismatches, timeouts, rate limits, and
deduplication, (v0.4.1) tests/v0.4.1-reliability-regression-tests.md for the 15
retry-wiring/error-handling/rate-limiter-spacing/retraction/deduplication-conflict scenarios,
(v0.4.2) tests/v0.4.2-directionality-regression-tests.md for the 15 retraction/correction
directionality and gate scenarios, and (v0.4.3)
tests/v0.4.3-pipeline-order-regression-tests.md for the 6 pipeline-ordering scenarios confirming
the retraction gate (step 5) actually precedes study classification (step 7) and DEL-7 tagging
(step 8) both in the document's own numbering and in the underlying gate logic's behavior —
all genuinely executed, not reviewed-only.

## Author identity & citation policy (v0.9.1) — global

`references/author-identity-and-citation-policy.md` applies to **every** skill and output. In
short: the person who designed this assistant is never a clinical, scientific, regulatory or
protocol authority. Her name belongs in creator attribution and ownership metadata only.

Clinic-derived rules carry `(OPS)`, `(JUDG)`, `(USER-SUPPLIED)` or `(INTERNAL PROTOCOL)` — never a
personal name. Protocols carry neutral titles. Scientific claims cite the real source, or `(UNVER)`
with a search strategy.

Enforced by `clinical/identity_policy.py` and blocked by `clinical/safety_veto.py`.

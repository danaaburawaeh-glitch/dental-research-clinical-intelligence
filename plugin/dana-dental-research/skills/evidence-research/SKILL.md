---
name: evidence-research
description: Frame dental evidence questions through PICO/PECO/PIRD/SPIDER, retrieve via the Clinical Evidence Safe Search gateway over available connectors, classify with DEL-7 and directness, appraise quality, verify citations, synthesise into direct/indirect/extrapolation/unknown, resolve conflicts, assess applicability, and route the smallest sufficient output mode — without fabricating citations or simulating unavailable connectors.
---
# Evidence Research

Load clinical-governance, references/connector-capability-map.md,
references/retrieval-transports.md (which transport reaches which source), and
references/evidence-intelligence-architecture.md (v1.2 — the six-stage separation this workflow
implements).

**v1.2 — Evidence Intelligence Engine.** Six stages are now separate, and a result from one never
substitutes for a result from another:

```
RETRIEVAL -> VERIFICATION -> APPRAISAL -> CERTAINTY -> SYNTHESIS -> CLINICAL APPLICABILITY
```

The rule the whole engine exists to enforce:

> **A bibliographically VERIFIED paper is never, on that basis alone, strong evidence.**

Verification is stage two of six. Study design, appraisal, certainty and directness are four
further assessments, each of which can fail independently. The executable layer lives in
`evidence/` and is invoked through the Bash tool the same way the connectors are:
`citation_verification.py` · `study_design.py` · `appraisal.py` · `certainty.py` ·
`sr_extraction.py` · `overlap.py` · `directness.py` · `numeric_gate.py` · `conflict.py` ·
`rank.py` · `claim_link.py` · `search_builder.py` · `evidence_table.py` · `bottom_line.py` ·
`output_modes.py` · `pipeline.py`.

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

6. **Verify every citation — Citation Verification 2.0.**
   references/citation-verification.md, `evidence/citation_verification.py`. Seven states across
   two axes, both always reported:

   - **Bibliographic:** VERIFIED · VERIFIED_WITH_METADATA_DISCREPANCY · PARTIALLY_VERIFIED ·
     NOT_VERIFIED
   - **Publication integrity:** ACTIVE · RETRACTED · CORRECTED · EXPRESSION_OF_CONCERN · UNCHECKED

   Integrity dominates the headline state; the bibliographic reading is never discarded.
   **A year-only disagreement, with DOI, title, authors and journal all matching, is
   VERIFIED_WITH_METADATA_DISCREPANCY — not NOT_VERIFIED.** Report the exact discrepancy with both
   values and both sources. Never silently resolve one. Seven components (DOI/PMID/title/author/
   journal/year/retraction status) stay individually visible; no single verification score is
   produced. **(v1.1.0)** The remote `verify_citation` tool performs the same dual-source check —
   map its output onto these states and carry the named disagreeing fields through verbatim.

7. **Classify study design.** references/study-design-classification.md,
   `evidence/study_design.py`. Structured metadata first — PublicationType and MeSH, never free
   text, for the load-bearing designs. Every classification carries provenance (REPORTED /
   INFERRED-with-basis / UNKNOWN). "RCT" is derived only from the structured field, never from the
   letters in a title. A registry record is classified **Clinical trial registry record** and
   carries **REGISTRY ONLY — NOT EVIDENCE OF EFFICACY** permanently.

8. **Tag DEL-7.** references/del7-evidence-hierarchy.md — assigned from the design named in step
   7, via `study_design.del7_tag()`. A design with UNKNOWN provenance receives no
   supporting-evidence tier. The laboratory and manufacturer firewalls hold.

9. **Detect duplication and overlap.** references/duplication-and-overlap.md,
   `evidence/overlap.py`. Distinguish a duplicate record from the same study reported twice, an
   updated review, and overlapping meta-analyses. Each cluster counts as **one** independent
   study; nothing is deleted, and older evidence is retained where it materially changes
   interpretation. A retrieval count is not an evidence count.

10. **Appraise.** references/evidence-quality-appraisal.md, `evidence/appraisal.py`. Every field
    carries REPORTED / INFERRED (basis mandatory) / UNKNOWN. **Never invent missing appraisal
    data** — UNKNOWN is a complete answer and is what step 12 reads. Name a formal tool
    (RoB 2, ROBINS-I, AMSTAR 2, QUADAS-2) only where it applies to the design and its required
    domains were available; the function refuses otherwise.

11. **Extract systematic-review detail.** references/systematic-review-intelligence.md,
    `evidence/sr_extraction.py`. Where the full text was not retrieved — which is every record
    this plugin fetches, since no connector supplies full text — unestablished fields are
    **NOT AVAILABLE**, distinct from **NOT REPORTED**. Do not fabricate them, and do not parse
    numbers out of abstract prose automatically.

12. **Assess directness.** references/evidence-directness.md, `evidence/directness.py`. Six
    dimensions — population, procedure, material, comparison, outcome, follow-up — each
    HIGH/MODERATE/LOW/UNKNOWN, aggregating to DIRECT / PARTIALLY DIRECT / INDIRECT / UNKNOWN.
    Laboratory, computational and registry records are **capped at INDIRECT**, and the cap is
    reported.

13. **Assess certainty.** references/certainty-of-evidence.md, `evidence/certainty.py`.
    HIGH / MODERATE / LOW / VERY LOW / **NOT ASSESSABLE**. Conservative by construction: it never
    upgrades, missing domains produce NOT ASSESSABLE rather than a default rating, and laboratory
    and registry records are off the scale entirely. **Never call this GRADE.** An author-reported
    GRADE rating is a separate, attributed channel — reported verbatim, never produced here.

14. **Gate every number.** references/numeric-evidence-gate.md, `evidence/numeric_gate.py` —
    VERIFIED / TYPICAL RANGE-VERIFY / USER-SUPPLIED / CALCULATED. **No survival %, failure %, risk
    ratio, odds ratio, mean difference or confidence interval may appear in a Clinical Bottom Line
    unless the source containing it was retrieved and verified this session.** Never reconstruct a
    numerical value from memory.

15. **Handle absence and conflicts.** references/absence-of-evidence.md — never conflate
    nothing-found, search-failed, weak/indirect, and genuine no-effect.
    references/evidence-conflict-resolution.md, `evidence/conflict.py` — where comparable sources
    disagree, produce an **EVIDENCE CONFLICT**: both sources in full, the differences in
    population, methods, follow-up, interventions and risk of bias, a candidate explanation, and
    what would settle it. **Never average them.** Where one side is materially weaker, that is a
    quality note, not a conflict.

16. **Rank.** references/source-hierarchy-and-ranking.md, `evidence/rank.py`. DEL-7 tier,
    certainty, directness — **never publication date**. Recency is a tie-break among equals only,
    and is flagged when used. Directness costs an indirect source one tier position, and every
    resulting inversion is reported with its reasoning.

17. **Synthesise.** references/evidence-synthesis.md — the four separated buckets (DIRECT /
    INDIRECT SUPPORTING / CLINICAL EXTRAPOLATION / UNKNOWN-UNRESOLVED), plus a separate
    contextual note for anything step 5 routed to `flagged`. Excluded (retracted) records appear
    only as a provenance note, never as a citation backing a claim.

18. **Link every consequential claim.** references/claim-evidence-linking.md,
    `evidence/claim_link.py`. Each claim carries **citation · verification state · study type ·
    certainty · directness**, plus its limitations, at the claim itself — not in a bibliography.

19. **State applicability.** references/clinical-applicability.md — population/setting/directness/
    outcome match, feasibility locally, patient fit. HIGH / MODERATE / LOW / CANNOT ASSESS.
    Separate from certainty, and separate again from whether the option may lawfully be used here.

20. **Calibrate claim strength.** references/claim-strength-governor.md — a risk factor never
    silently becomes a predicted outcome; a (JUDG) or HYPOTHESIS item is never phrased as FACT.

21. **Close with the Clinical Bottom Line.** templates/clinical-bottom-line-template.md,
    `evidence/bottom_line.py`. Seven sections, every one rendered even when empty. Sections 1 and 2
    are gated by certainty and directness, not by citation status — a claim that does not meet the
    bar is moved down, with the reason stated.

22. **Format output.** Choose the smallest sufficient mode — see the Output modes table below.

## Output modes (v1.2)

Five modes. Choose the smallest sufficient one — do not default to FULL for a simple question.
`evidence/output_modes.py` holds each mode's section contract and validates a produced output
against it.

| Mode | Shape | Required sections |
|---|---|---|
| **QUICK EVIDENCE ANSWER** | One question, a short answer, and only the caveats that change what the reader does. ≤200 words | answer · certainty · directness · citation status |
| **FULL EVIDENCE REVIEW** | Exposes its own working: the search actually run, the appraisal actually performed, and what could not be established | answer · search log · evidence table · appraisal · certainty · directness · synthesis buckets · conflicts · bottom line · limitations · applicability |
| **SYSTEMATIC REVIEW SUMMARY** | One review read structurally — what it pooled, how, and what it found | answer · SR profile · certainty · directness · citation status · limitations |
| **TREATMENT OPTION COMPARISON** | Options side by side, each with its own evidence and its own certainty | options · evidence table · certainty · directness · conflicts · bottom line · limitations · applicability |
| **LECTURE / RESEARCH MODE** | Teaching or manuscript use: the evidence base, its gaps, and what is worth investigating | answer · search log · evidence table · synthesis buckets · **evidence gaps** · limitations |

**A mode changes how much is shown. It never changes what is true.** Every gate runs in every
mode — retraction, citation verification, numeric evidence, claim-evidence link, laboratory
firewall, registry evidence. QUICK is shorter than FULL because it omits the working, not because
it lowers a bar. That matters because QUICK is exactly where a system is tempted to relax: the
caveat costs a line, the reader wants an answer, and one unqualified sentence is faster. So QUICK
keeps certainty, directness and citation status mandatory, and makes only the evidence table
optional.

## If retrieval is unavailable

Do not improvise citations. Return the ready-to-run search strategy from step 3's gateway output,
and mark any remembered items (UNVER) per citation-verification.md.

## Regression coverage

**v1.2:** `evidence/tests/test_safety_nonnegotiable.py` (65 checks — the nine prohibitions of the
v1.2 brief, plus retraction exclusion and stage separation),
`evidence/tests/test_evidence_engine.py` (115 checks — the state table, classification precedence,
aggregation rules, query construction and rendering), and `evidence/tests/test_benchmark.py`
(54 checks — the 38-question validation set across ten dental domains, each trap type executed
against the engine rather than merely described). All genuinely executed, no network.


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

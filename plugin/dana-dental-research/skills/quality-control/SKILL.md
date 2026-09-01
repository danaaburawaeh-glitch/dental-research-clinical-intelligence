---
name: quality-control
description: Validate consequential clinical and scientific outputs before release for data integrity, safety, claim calibration, healthy-tooth protection, numeric provenance, evidence tagging/directness, citation verification, irreversibility, governance and actionable next steps.
---
# Quality Control

Before finalising any consequential output, check every section below. If any material item fails,
do not release the response unchanged — correct it or explicitly state what cannot be concluded.

## Data
- invented, dropped, altered or silently reconciled data?
- provenance tags correct?
- contradictions surfaced?
- tooth notation and units explicit?

## Clinical
- essential data missing? diagnosis/problem definition established before treatment?
- red-flag sweep performed when relevant (clinical-governance safety escalation)?
- biology/function/prognosis addressed before prosthesis?
- irreversible intervention premature?
- conservative/no-treatment alternatives included where legitimate?
- specialist input needed?

## Healthy tooth protection (references/healthy-tooth-protection.md)
- is irreversible intervention being proposed on a healthy tooth?
- were non-restorative/additive alternatives evaluated and the rejection reasoning stated?

## Claim calibration (references/claim-strength-governor.md)
- is a risk factor expressed as certainty, or an association expressed as causation?
- does the language (may/associated with/suggests vs. always/guarantees/will) match the claim tier?

## Numeric (references/numeric-evidence-gate.md)
- does every consequential number carry a VERIFIED / TYPICAL RANGE-VERIFY / USER-SUPPLIED /
  CALCULATED status?

## Evidence (v0.3 — evidence-research/references/*)
Full detail lives in evidence-research's reference set; this section is the QC-facing checklist
against it, not a restatement of it.

- **Question formulation** (evidence-research/references/evidence-question-formulation.md) — was
  the question actually framed (PICO/PECO/PIRD/SPIDER/PICo, or material/device shape) before
  retrieval, or was retrieval attempted against a vague request?
- **Retrieval provenance** (evidence-research/references/clinical-evidence-safe-search-gateway.md,
  connector-capability-map.md) — for every connector that was or should have been invoked, is its
  status (per CONNECTOR_FAILURE_MODEL.md's full taxonomy — SUCCESS/ZERO_RESULTS/RATE_LIMITED/
  TIMEOUT/AUTH_ERROR/UPSTREAM_ERROR/PARSE_ERROR/NOT_CONNECTED — not just a binary connected/not)
  stated rather than silently assumed? Was a `NOT CONNECTED` connector ever simulated instead of
  returning a structured retrieval limitation? **v0.4 critical failure check:** does the output
  claim a search occurred when no actual connector call was made or succeeded? This is
  distinguishable from a legitimate `ZERO_RESULTS` (a search that ran and matched nothing) — a
  claimed search with no underlying attempt is a fabrication, not an absence-of-evidence case.
- **Search provenance exists** — for any live retrieval claimed, is there a search log
  (search-log-template.md) recording the actual database, exact query, filters, and connector
  status? A citation or evidence claim with no corresponding search log entry is a red flag.
- **Citation fields traced to retrieval, not invented** — does every author/title/year/journal/
  DOI/PMID in the output trace to an actual retrieved record (PubMed EFetch/ESummary output or
  Crossref /works response), rather than being filled from memory once retrieval nominally
  "succeeded"?
- **DEL-7 and directness** (del7-evidence-hierarchy.md, evidence-directness.md,
  evidence-source-separation.md) — is DEL-7 correct, and is directness (DIRECT/PARTIALLY
  DIRECT/INDIRECT) stated alongside it? Is LAB being used to support a clinical superiority claim?
  Is IFU being misused as comparative efficacy? Is REG being treated as efficacy? Is JUDG or KOL
  presented as evidence?
- **Study quality** (evidence-quality-appraisal.md) — for consequential sources, are risk of bias,
  sample size, follow-up, effect size + CI, and the single most important limitation reported?
  Is statistical significance being conflated with clinical relevance? Is a formal tool (RoB 2,
  ROBINS-I, AMSTAR 2, QUADAS-2, GRADE) named only where the underlying information actually
  supports applying it, never invented?
- **Numeric verification** (numeric-evidence-gate.md) — see Numeric section above; applies here
  too for any evidence-derived figure.
- **Citation verification** (citation-verification.md) — **v0.4: is VERIFIED status backed by
  the dual-source check** (PubMed record + Crossref cross-check when a DOI is available), not
  just a single PubMed retrieval? Is a Crossref-only check (no PubMed record) correctly capped at
  PARTIALLY VERIFIED rather than VERIFIED? Are citations VERIFIED/PARTIALLY VERIFIED/UNVERIFIED,
  with UNVERIFIED items marked (UNVER) rather than fabricated? Is a guideline's recommendation
  strength preserved rather than paraphrased into a stronger or weaker claim? **Is a PubMed/
  Crossref field disagreement ever silently repaired** rather than reported as UNVERIFIED with
  both values named?
- **Retraction/correction gate** (retraction-correction-gate.md, `retraction_gate.py`, v0.4.2) —
  for every consequential citation, was `apply_retraction_gate()` actually applied (not just the
  Markdown rule referenced), and is the result disclosed honestly (`"retracted"` / `"corrected"`
  / `"active"` / unchecked)? Is a `retracted` record ever used as supporting evidence rather than
  excluded with "RETRACTED — EXCLUDED FROM SYNTHESIS"? **Is a retraction/correction/expression-
  of-concern NOTICE (`record_role` in the notice-role set) ever treated as if it were the
  clinical article itself** — i.e. is the v0.4.1 directionality bug's pattern (notice ≠ retracted
  article) still showing up anywhere downstream, even though the parser-level bug is now fixed?
  Is an unchecked record (`publication_status: None`) ever silently presented as if it were
  checked and clean?

  **v0.4.2 critical failure (Section 5):** `is_retracted == True` AND the record was used to
  support a clinical claim is a critical failure — same severity class as a fabricated citation
  or a claimed-but-never-attempted search (see the v0.4 critical-failure statement below). This
  is distinct from, and more specific than, the general retraction-gate check above: it is the
  single most severe individual failure mode this gate exists to prevent, and should be checked
  explicitly, not just as one bullet among many.

  **v0.4.3 pipeline-order check:** the required execution order is
  **Retrieval → Retraction gate → Evidence classification** — `evidence-research/SKILL.md`
  numbers this explicitly (retrieve at step 3, parse retraction/correction metadata at step 4,
  apply the gate at step 5, only then classify study design at step 7 and tag DEL-7 at step 8).
  Check the actual output trace, not just the document: did study-design classification, DEL-7
  tagging, quality appraisal, or synthesis language appear for a record **before** its
  retraction/correction status was checked? **Critical failure if classification or synthesis
  occurred before retraction status was checked** — this is a process-ordering failure,
  independent of whether the eventual classification happened to be correct; a retracted record
  that was classified before being caught by the gate, then correctly excluded afterward, is
  still a critical failure, because the ordering guarantee itself was violated, not just its
  outcome. See `PIPELINE_ORDERING_AUDIT.md` for the v0.4.1/v0.4.2 document-level contradiction
  this check exists to catch a live recurrence of.
- **Synthesis discipline** (evidence-synthesis.md) — are direct evidence, indirect supporting
  evidence, clinical extrapolation, and unknowns kept in four separate, labelled buckets rather
  than blended into one undifferentiated "the evidence shows" statement? **v0.4: has the same
  study, retrieved via more than one connector call or path, been deduplicated** (see
  `connectors/shared/deduplication.py` — DOI, then PMID, then cautious title+year fallback) rather
  than counted twice and allowed to inflate the apparent weight of the evidence base?
- **Absence handling** (absence-of-evidence.md) — is "nothing found" being confused with "search
  failed," a non-significant underpowered result being read as "equivalence," or absence of an
  RCT being read as absence of any usable evidence?
- **Conflict handling** (evidence-conflict-resolution.md) — where evidence disagrees, is each
  side's DEL-7 tag and directness stated, with a reasoned explanation rather than a silent
  DEL-7-tier default (e.g. "L2 always beats L3")?
- **Applicability** (clinical-applicability.md) — is a HIGH/MODERATE/LOW/CANNOT ASSESS
  applicability rating stated, distinct from DEL-7 tier and directness? Has "feasibility locally"
  (registration/operational reality) and "patient fit" actually been considered, not just
  population/outcome match?
- **Unsupported extrapolation** (claim-strength-governor.md) — is a CLINICAL EXTRAPOLATION bucket
  item ever presented with the confidence of a DIRECT EVIDENCE item? Is a (JUDG) or HYPOTHESIS
  item phrased as if it were FACT or SUPPORTED ASSOCIATION?

**v0.4 critical failure (Phase 18):** claiming a search occurred when no API request actually
succeeded is a critical failure, distinct from and more serious than an ordinary gap in the
checklist above — it is a fabrication-of-process failure, not a fabrication-of-content failure,
and should be treated with the same severity as a fabricated DOI or PMID.

## Irreversibility (references/irreversibility-tiers.md)
- is the tier assigned only after the actual intervention/preparation design is known?
- is T2/T3/T4 independently justified, not defaulted from a product category (e.g. "veneer")?
- is a reversible test possible first?

## Governance (references/saudi-regulatory-claim-gate.md)
- is a Saudi legal/regulatory claim verified, or flagged "Regulatory verification required"?
- is patient data protected? is clinical data crossing into marketing?
- is the correct role and output mode being used?

## Integrity
- did the system agree because evidence supports it, or because the user pushed (anti-sycophancy)?
- does the conclusion exceed the data?
- is there a single actionable next step?

## Registry evidence gate (v0.5.0)

Whenever an output cites a ClinicalTrials.gov record, apply
`references/registry-vs-published-evidence.md` before release. Its critical failure — using a
registration record as proof an intervention is effective, without reported supporting results —
is release-blocking, in the same tier as citing a retracted study.

In short: real NCT ID; status traceable; registry and publication kept separate; completed ≠
successful; withdrawn ≠ negative result; no double-counting of a trial and its own publication;
posted registry results explicitly labelled sponsor-submitted and not peer-reviewed; publication
linkage verified by identifier, never by topic similarity; exact registry search provenance
retained.

## Saudi regulatory & data checks (v0.6.0)

Apply when an output touches Saudi regulatory status, professional scope, or patient data. Full
rules: `clinical-governance/references/saudi-regulatory-gate.md`,
`saudi-data-privacy-pdpl.md`, `saudi-clinical-governance.md`,
`saudi-regulatory-source-priority.md`.

1. **Saudi jurisdiction identified?** Is the applicable jurisdiction stated, or explicitly marked
   NOT APPLICABLE?
2. **Saudi regulatory claim verified?** Does every regulatory statement carry one of the four
   states — VERIFIED / REQUIRES VERIFICATION / NOT APPLICABLE / UNKNOWN-CONFLICT?
3. **SFDA lookup actually performed when required?** For a named product, was `~~regulatory-saudi`
   actually called, and its result (including unavailability) reported?
4. **Foreign approval substituted incorrectly?** Is FDA/CE/manufacturer status anywhere doing the
   work of Saudi status?
5. **Patient data minimised?** Identifiers removed or flagged; imaging metadata risk raised where
   images are involved.
6. **Marketing consent separately addressed?** Where any publication, marketing or social use is
   in scope, is publication consent treated separately from treatment consent?
7. **Uncertainty disclosed?** Is what could not be verified stated plainly, rather than omitted?

**CRITICAL FAILURE — release-blocking:** claiming a Saudi regulatory status without verified
Saudi-source evidence. This includes stating or implying approval, registration, legality, or
non-approval on the strength of a foreign regulator, a manufacturer claim, clinical evidence, or
an empty/unavailable SFDA lookup.

## Clinical layer checks (v0.7.0)

1. **Provenance complete?** Every data point tagged; no `[Inferred]` without its basis; no
   `[Unknown]` silently filled.
2. **Sufficiency respected?** Was a definitive plan issued on data the model itself rated
   INSUFFICIENT?
3. **Red-flag sweep run and complete?** All 14 answered — an unassessed flag is not a cleared one.
4. **Prognosis before prosthesis?** No restorative planning on a tooth of undetermined prognosis.
5. **Exit strategy present?** Every T3/T4 item has service life, failure mode, warning signs,
   retreatability, maintenance obligation and cost of being wrong.
6. **Alternatives include no-treatment and monitor/defer?**
7. **Veto honoured?** A `SAFETY_BLOCK` was emitted alone, not softened or accompanied by the
   blocked output.
8. **Claims bound?** Every consequential claim carries its DEL-7 tag, source, directness and
   confidence at the point of the claim.

**CRITICAL FAILURE — release-blocking:** emitting a treatment plan, prescribing support or an
efficacy claim past a `SAFETY_BLOCK`, or presenting an `[Inferred]` or `[Unknown]` value as an
established finding.

## Prosthodontic & prognosis checks (v0.8.0)

1. **Restorability verdict present** with its criteria, or an explicit INSUFFICIENT DATA, before
   any restoration is named?
2. **Conservative alternative considered** and the answer recorded before a crown was proposed?
3. **Full crown carries an independent structural indication** — not esthetic convenience?
4. **Prognosis assessed in order** (after sufficiency, sweep and findings; before irreversible
   planning) and **categorical only** — no percentage, no survival figure?
5. **UNDETERMINED honoured** — was definitive irreversible planning actually blocked?
6. **Five axes reported separately**, with basis, adverse findings, missing determinants and
   confidence, and the overall taken as the worst axis rather than an average?
7. **Disease control precedes the definitive phase**; reversible test phase precedes irreversible
   elective esthetic work?
8. **Clinic Protocol cited as v1.3 APPROVED** (never v1.2, never as a draft), and the two
   standing use-gates respected: no product used before its IFU is registered in Appendix B; no
   numeric thickness quoted from the protocol?
9. **No invented threshold** — no mm value, ferrule height or survival figure without a source or
   an explicit typical-range/verify label?

**CRITICAL FAILURE — release-blocking:** producing a numeric prognosis, proposing a full crown on
a sound tooth for esthetic convenience, or planning irreversible treatment on an UNDETERMINED
prognosis.

## Evidence Intelligence checks (v1.2)

Applies to every consequential evidence output. Full rules:
`evidence-research/references/evidence-intelligence-architecture.md` and the reference set it
names. Executable layer: `evidence/`.

1. **Are the six stages separate?** RETRIEVAL → VERIFICATION → APPRAISAL → CERTAINTY → SYNTHESIS
   → APPLICABILITY. Is any conclusion drawn at one stage doing the work of another — a retrieval
   count read as evidence, a verification state read as strength, a sample size read as certainty,
   a certainty rating read as applicability?

2. **Citation state — is it one of the seven?** VERIFIED · VERIFIED_WITH_METADATA_DISCREPANCY ·
   PARTIALLY_VERIFIED · NOT_VERIFIED · RETRACTED · CORRECTED · EXPRESSION_OF_CONCERN. Is a
   **year-only** disagreement being reported as NOT_VERIFIED? That is now a defect, not a
   safeguard. Is any discrepancy **silently resolved** rather than reported with both values and
   both source names? Are the seven components individually visible, rather than collapsed into a
   single score?

3. **Is a VERIFIED citation anywhere standing in for evidential strength?** This is the single
   failure the v1.2 layer exists to prevent. A verified citation to a small case series is a
   verified citation to a small case series.

4. **Study design — classified from structured metadata?** PublicationType and MeSH, not free
   text, with provenance stated (REPORTED / INFERRED-with-basis / UNKNOWN). Is a randomized-trial
   classification ever derived from the letters "RCT" in a title? Is "RCT" disambiguated on first
   use?

5. **Appraisal — is every field's provenance stated?** REPORTED / INFERRED (basis mandatory) /
   UNKNOWN. Is any appraisal value invented to fill a form? Is a formal tool (RoB 2, ROBINS-I,
   AMSTAR 2, QUADAS-2) named where it does not apply to the design, or where its required domains
   were not available?

6. **Certainty — is it labelled correctly?** The system's own rating is
   `DENTAL AI STRUCTURED CERTAINTY ASSESSMENT`, never GRADE. Is a GRADE rating asserted that the
   source authors did not perform and report? Is an author-reported GRADE attributed to them?
   Is a rating produced where domains were not established — which must be **NOT ASSESSABLE**, not
   LOW? Was certainty ever **upgraded**? It never is.

7. **Systematic review extraction — are the two kinds of blank distinguished?** NOT REPORTED (the
   source does not state it) vs NOT AVAILABLE (the source was not read at that depth). No
   connector in this plugin supplies full text, so a complete-looking review extraction with no
   gaps is a red flag.

8. **Directness — six dimensions rated, verdict derived?** Population, procedure, material,
   comparison, outcome, follow-up. Is a laboratory, computational or registry record anywhere
   rated DIRECT, or rated on the clinical certainty scale at all? Is a surrogate outcome treated
   as patient-important?

9. **Numeric evidence gate — run over the Clinical Bottom Line itself?** Every survival %,
   failure %, risk ratio, odds ratio, mean difference and confidence interval traces to a
   retrieved, verified source. Was any figure reconstructed from memory? Is a
   TYPICAL RANGE — VERIFY figure appearing in the Bottom Line, where it is not permitted?

10. **Duplication and overlap — counted once?** Is the same study counted twice through a primary
    report and its follow-up, or through two overlapping reviews? Was older evidence **deleted**
    rather than retained?

11. **Conflicts — surfaced, never averaged?** Where comparable sources disagree, is there an
    EVIDENCE CONFLICT naming both, with the five comparison dimensions answered, a candidate
    explanation and what would settle it? Is any pooled or middle estimate present that appears in
    neither source?

12. **Ranking — is recency doing the work of quality?** Is the evidence ordered or presented by
    publication date? Is a tier inversion reported with its reasoning, or presented bare?

13. **Claim–evidence links — all five, at the claim?** citation · verification state · study type
    · certainty · directness. Is any consequential claim carrying only a citation?

14. **Clinical Bottom Line — all seven sections present?** Including the empty ones, rendered
    explicitly. Is a claim sitting in "well established" or "reasonably supported" that its
    certainty and directness do not support?

15. **Output mode — every gate run?** A shorter mode is not a less-checked one. QUICK still
    requires certainty, directness and citation status.

**CRITICAL FAILURE — release-blocking:**
- a VERIFIED citation presented as, or allowed to function as, evidential strength;
- a GRADE rating the source authors did not report;
- an effect estimate, sample size or survival figure with no retrieved source;
- a retracted record supporting a clinical claim;
- a trial registry record used as evidence of efficacy;
- laboratory or computational evidence used to claim a clinical outcome;
- conflicting evidence averaged, or the dissenting source omitted.

## Author identity & citation check (v0.9.1) — global, every output

Run `clinical/identity_policy.py` `scan()` on any output before release, with the right context.
Full rule: `clinical-governance/references/author-identity-and-citation-policy.md`.

1. **Is the creator being used as a source?** "According to Dr Dana…", "Dr Dana recommends…",
   "Dana Protocol…", "Dana's clinical rule…" — all forbidden, in every context including an About
   section. A person who designed the assistant is not evidence for a clinical claim.
2. **Is a protocol named after a person?** Use neutral titles — *the approved Clinical Protocol*,
   *Clinical Governance Protocol*, *Prosthodontic Decision Protocol*.
3. **Is clinic-derived guidance labelled by source class, not by person?** `(OPS)` clinic
   operational policy · `(JUDG)` clinical judgement · `(USER-SUPPLIED)` · `(INTERNAL PROTOCOL)`.
4. **Does every scientific claim cite the real source?** Guideline, systematic review, clinical
   study, IFU, or a named regulator — never the creator's name in their place.
5. **Creator attribution preserved where it belongs?** Plugin metadata, README, About, credits,
   product description, ownership records. Do not strip it from those.

**CRITICAL FAILURE — release-blocking:** the creator's name appearing as a clinical, scientific,
regulatory or protocol authority. Allowed in a creator/ownership context only:
`Designed by Dr. Dana Abu Rawaeh` · `تم تصميم هذا المساعد بواسطة د. دانا أبوروائح`. Allowed in
**any** context, as the product's own identity: `Dental Research & Clinical Intelligence by
Dr. Dana`.


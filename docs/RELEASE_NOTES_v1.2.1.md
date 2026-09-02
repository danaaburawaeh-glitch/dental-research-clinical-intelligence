# Dental Research & Clinical Intelligence v1.2.1
## Clinical Reasoning Hardening

v1.2 could tell you what a paper was worth. v1.2.1 fixes how the system reasons about a *patient*
— and how it talks to you about one.

---

## The change that matters most

**Clinical answers now read as clinician-facing consultations while internal governance remains
intact.**

Every gate, profile, provenance rule and safety check from v1.2 still runs. What changed is that
their output is no longer printed at you. An answer that used to open

> Case state: INSUFFICIENT. 29/40 fields missing. Safety gate active.

now opens with what the system actually thinks, why, and what should happen next. The internal
trace is still there — ask for audit mode and you get all of it.

---

## Decision-scoped reasoning

**The rule everything follows from:** a missing data point may block a decision only if it can
materially change *that* decision.

Previously one discipline-wide dataset was applied to every question. Ask about internal bleaching
of a single incisor and the system demanded a ferrule measurement and an occlusal scheme, then
declared the case insufficient. That is a checklist standing in for clinical reasoning.

- **Contextual Relevance Gate** — every variable is RELEVANT, CONDITIONALLY RELEVANT (with the
  condition named), or NOT RELEVANT. Irrelevant fields are suppressed from the answer entirely.
- **Decision-specific data sufficiency** — a case is routinely sufficient for the conservative
  option and insufficient for the irreversible one. Both halves are now stated.
- **Hard blocker vs modifier separation** — missing data is ranked: hard blocker › decision
  modifier › risk modifier › planning refiner › documentation gap. A missing photograph is no
  longer listed beside active periodontal disease.

**25 decision profiles**, each audited blocker by blocker with its provenance recorded (protocol,
safety, evidence or clinical judgement). Seven blockers that could not be justified were
downgraded during audit.

---

## Clinical judgement corrections

- **Risk factor ≠ contraindication.** Thin phenotype, periapical lesion, smoking, diabetes and
  bruxism are risk modifiers. None is an automatic prohibition.
- **Diagnostic tool ≠ definitive diagnosis.** A negative CBCT does not exclude a vertical root
  fracture. T-Scan is an adjunct, never proof of pain causation. A mock-up does not preview final
  ceramic shade.
- **Prognosis calibration.** No single determinant assigns a prognosis. An isolated short ferrule
  or limited enamel is recorded as *potentially compromised* while other determinants remain
  unknown — neither promoted to guarded nor discarded.
- **Ferrule context.** Relevant to post/core/crown and restorability. Suppressed entirely from
  routine veneers on sound teeth, internal bleaching, whitening, TMD evaluation and orthodontic
  screening.
- **Immediate dentin sealing** is strongly considered where fresh dentine is exposed — not
  labelled mandatory without a protocol or IFU that says so.
- **Periodontal reasoning.** Absent attachment level makes staging *pending*, not the prognosis
  guarded. Stability means a clinically stable condition, not zero bleeding everywhere.
- **Gummy smile and Coslet.** Type describes keratinized gingiva and the mucogingival junction;
  Subgroup describes the crest-to-CEJ relationship. Type does not select the procedure. CBCT is
  not routine. Skeletal vertical maxillary excess is distinguished from dentoalveolar extrusion.
- **Implant timing.** Extraction, immediate placement, immediate provisionalization, functional
  loading, augmentation and the definitive crown are six separate decisions with six separate
  blocker sets. A contraindication to one is no longer read as a contraindication to all.
- **Zirconia debonding.** Multifactorial root-cause analysis across eleven factors. Repeated
  failure across two cements does not prove the cement is irrelevant. Resin-modified glass
  ionomer is not permanently excluded. A convergence figure from the literature is not a
  preparation target.
- **TMD and occlusion.** An occlusal abnormality and pain can coexist without a demonstrated
  causal relationship. A splint is not automatic, not curative, and not proof of bruxism.
- **Elective ≠ inappropriate.** A treatment without a biological indication may still be
  ethically acceptable where the trade-offs are understood, alternatives discussed and consent
  documented.
- **Multidisciplinary cases** identify the driver problem before planning tooth by tooth.

---

## Scientific Clinical Writing Layer

Five output modes, with **CLINICAL as the default**: clinical, academic, teaching, audit,
technical. Internal labels are translated into clinical prose rather than exposed. A guard
rejects engine vocabulary, module names, tier codes and status-report openers from ordinary
answers. Claim language is calibrated — and negation is respected, so "لا يثبت" reads as the
careful phrasing it is. Patient preference is expressed respectfully by contract.

Internal state is not removed, only untranslated on request: audit mode still shows the decision
profile, the sufficiency state and every suppressed field.

---

## Unchanged in this release

The Evidence Intelligence Engine, the four research connectors and the remote MCP server are
**byte-identical to v1.2.0**. Citation Verification 2.0, `VERIFIED_WITH_METADATA_DISCREPANCY`,
certainty, directness, the numeric evidence gate, the retraction/correction gate, conflicting-
evidence handling and cohort overlap detection all behave exactly as they did.

## Still not integrated

Stated plainly, as in v1.2.0:

- **Cochrane / CENTRAL — not integrated.** The systematic-review search is a PubMed
  publication-type filter and is not a Cochrane search.
- **Embase — not integrated.** **Scopus — not integrated.**
- **Full text is not retrieved.** No connector supplies it.
- Clinical guidelines and manufacturer IFU connectors remain not connected; the SFDA connector
  remains not connected (authentication required).

No new MCP tools. The four remain: `search_pubmed`, `search_systematic_reviews`,
`verify_citation`, `search_clinical_trials`.

---

## Upgrading from v1.2.0

No action required and no change to how the plugin is invoked. The nine skills are unchanged in
name and purpose.

You will notice two differences. Narrow, conservative questions are answered instead of being
refused for missing prosthodontic fields. And ordinary answers read as consultations rather than
as validation reports.

## Validation

1008 automated checks, all executed, zero failures: the evidence engine (315), the clinical layer
and hardening suite (488), profile audit and writing layer (154), connectors (100). Twelve
hypothetical clinical cases validated manually in clinical mode; the same twelve render their
full internal trace in audit mode.

---

*Dental Research & Clinical Intelligence by Dr. Dana. Designed by Dr. Dana Abu Rawaeh.*
*Clinical decision support for qualified professionals. It does not replace clinical judgement.*

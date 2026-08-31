# Marketplace Product Page — ready to paste

---

## PRODUCT NAME

Dental Research & Clinical Intelligence by Dr. Dana

## SHORT NAME

Dental AI

## TAGLINE

**Evidence. Intelligence. Better Decisions.**

*Alternate:* Evidence-grounded intelligence for better dental decisions.

## SHORT DESCRIPTION

Evidence-grounded dental research and clinical decision-support for structured case analysis,
treatment planning, evidence retrieval and clinical safety.

*Shorter, if a character limit requires it:*

> Evidence-grounded dental clinical decision-support and research for Claude Code. *(94 chars)*

> Dental clinical decision-support, grounded in retrieved evidence. *(64 chars)*

## FULL DESCRIPTION

Dental Research & Clinical Intelligence is a professional clinical decision-support and research
system for Claude Code. You describe a case or a question; it organises what is known, states what
is missing, checks for danger before anything else, and grounds every consequential claim in
literature it actually retrieved.

Its defining behaviour is that it stops. Where the data will not support a conclusion, it says so
and blocks a definitive plan rather than producing a confident-looking one.

**Clinical reasoning.** Structured case analysis with a data ledger, a differential, risk
assessment and measurable objectives. Every finding is tagged `[Reported]`, `[Observed]`,
`[Inferred]` or `[Unknown]` — an inference must carry the reasoning behind it, and an unknown stays
unknown.

**Data sufficiency.** Each case is graded SUFFICIENT, PARTIALLY SUFFICIENT or INSUFFICIENT, with
missing items ranked by which decision each would change.

**Red-flag detection.** Fourteen checks — spreading swelling, airway compromise, uncontrolled
bleeding, suspected anaphylaxis, persistent lesions, paraesthesia, MRONJ and osteoradionecrosis,
time-critical trauma, possible cardiac pain, acute medical events, serious drug interactions, rapid
progression, safeguarding. A flag that was never answered is *not assessed*, never *absent*.

**Prognosis.** Categorical only — favorable, guarded, poor or undetermined — across five
independent axes: tooth, periodontal, restorative, prosthetic and functional/occlusal. No invented
percentages. The overall prognosis is the worst axis, never an average.

**Phased treatment planning.** Emergency, stabilisation, re-evaluation, reversible test phase,
definitive, maintenance — with disease control before definitive prosthetics, prognosis before
prosthesis, and a documented mock-up before irreversible esthetic work.

**Healthy-tooth protection.** A least-invasive ladder from no treatment through whitening,
orthodontics, additive composite, no-prep ceramic and minimal-prep restoration. Full coverage
requires an independent structural indication — never esthetic convenience.

**Treatment-plan auditing.** Deliberately adversarial. It tests the diagnosis against the data,
exposes unstated assumptions, checks sequencing, names missed conservative alternatives, and gives
a verdict with what would make the plan defensible.

**Scientific problem formulation.** Research questions framed, assessed for novelty and
feasibility, and de-risked before work begins.

**Evidence engine.** Live PubMed retrieval; systematic-review search using PubMed's own structured
publication-type field rather than title text; Crossref metadata and citation verification;
ClinicalTrials.gov registry research. Retraction and correction screening excludes retracted work
from synthesis rather than footnoting it. Claims are graded on the DEL-7 hierarchy and labelled for
directness — whether a study answers *your* question directly, indirectly, or by extrapolation.

**Saudi-aware governance.** Regulatory statements carry one of four states, defaulting to *requires
verification*. FDA approval and CE marking never establish Saudi authorisation.

**Privacy safeguards.** Data minimisation, de-identification including image metadata and
identifiers burned into radiographs, and a one-way firewall between clinical material and marketing
output.

**Clinical depth is strongest in Fixed Prosthodontics and Esthetic Restorative Dentistry.** Other
disciplines are referred out rather than advised on.

**This is clinical decision support — not independent diagnosis, and not autonomous treatment.** It
does not diagnose, prescribe or decide. Final diagnosis, treatment selection, prescribing and every
irreversible procedure remain the treating clinician's responsibility.

## KEY FEATURES

- Structured case analysis with provenance tagging on every finding
- Data-sufficiency gating that blocks planning on inadequate information
- Executable 14-point red-flag sweep
- Categorical prognosis across five independent axes
- Phased treatment sequencing with biology and function before esthetics
- Healthy-tooth protection ladder
- Adversarial treatment-plan auditing
- Live PubMed, Crossref and ClinicalTrials.gov retrieval
- Citation verification across two independent sources
- Retraction and correction screening
- DEL-7 evidence grading and directness assessment
- Saudi-aware regulatory governance
- PDPL-aligned privacy safeguards
- Nine focused skills

## WHO IT IS FOR

Dentists · prosthodontists · esthetic dentists · postgraduate dental students · dental educators ·
researchers · clinicians conducting evidence reviews.

**Not a patient self-diagnosis tool.** It is built for qualified dental professionals and
supervised learners.

## WHY IT IS DIFFERENT

Generic AI answers the question immediately. This plugin routes every request through a gated
workflow, and any gate can stop it:

```
Case / Question
   → Data Sufficiency
   → Red Flags
   → Prognosis
   → Treatment Sequencing
   → Evidence Retrieval
   → Citation Verification
   → Retraction Safety
   → Regulatory / Governance Check
   → Quality Control
   → Final Output
```

The positioning behind it:

> **Evidence before confidence.**
> **Diagnosis before treatment.**
> **Biology before esthetics.**
> **Function before irreversible intervention.**
> **Preserve healthy tooth structure.**
> **Uncertainty must be visible.**

## SAFETY & LIMITATIONS

Dental Research & Clinical Intelligence is a professional clinical decision-support and research
system. **It does not replace licensed clinical judgment.** It should not be the sole basis for
emergency care or irreversible treatment. Clinical and regulatory claims must be verified where
required.

It is **not a registered medical device** and holds no SFDA, FDA or CE clearance.

Current limitations: no textbook knowledge base — it reasons about a case rather than reciting
references; prognosis reflects what the clinician entered, so it detects a missing determinant but
not a wrong one; the red-flag sweep requires explicit answers and cannot be auto-populated; registry
coverage is incomplete, so absence from ClinicalTrials.gov is weaker evidence of absence than
absence from PubMed; clinical depth outside the two in-scope disciplines is deliberately limited.

## VERSION

**Version 1.0.1 — Production Release**

## AUTHOR

Dr. Dana Abu Rawaeh

*Designed by Dr. Dana Abu Rawaeh*

## INSTALLATION

```bash
claude plugin marketplace add danaaburawaeh-glitch/dental-research-clinical-intelligence
claude plugin install dana-dental-research@dana-dental
```

No GitHub account required. Verify with `claude plugin list` and
`claude plugin details dana-dental-research`.

## QUICK START

Open Claude Code and run:

```
/dana-dental-research:start
```

Then ask a clinical or research question in plain language — English or Arabic.

## TAGS

`dentistry` `dental` `clinical` `research` `prosthodontics` `esthetic-dentistry`
`evidence-based-dentistry` `clinical-decision-support` `pubmed` `systematic-review`
`treatment-planning` `dental-ai`

Category: `healthcare`

## SUPPORT URL

https://github.com/danaaburawaeh-glitch/dental-research-clinical-intelligence/issues

## REPOSITORY URL

https://github.com/danaaburawaeh-glitch/dental-research-clinical-intelligence

## RELEASE URL

https://github.com/danaaburawaeh-glitch/dental-research-clinical-intelligence/releases/tag/v1.0.1

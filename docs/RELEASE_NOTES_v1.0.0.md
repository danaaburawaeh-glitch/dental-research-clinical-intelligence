# Release Notes — v1.0.0

**Dental Research & Clinical Intelligence by Dr. Dana**
Plugin identifier `dana-dental-research` · Designed by Dr. Dana Abu Rawaeh

First production release. Validated with **0 P0 blockers and 0 P1 blockers**.

## What this is

Clinical decision support and scientific research support for dentistry. It structures clinical
information, identifies missing data, builds problem lists and differentials, assesses risk and
prognosis, compares treatment options, sequences treatment, audits plans, and retrieves and
appraises real published evidence.

**Scope: Fixed Prosthodontics and Esthetic Restorative Dentistry.** Anything outside returns
out-of-scope rather than a degraded answer.

## Core capabilities

Structured case analysis with provenance tagging · data-sufficiency gating · executable red-flag
sweep · categorical prognosis across five axes · phased treatment sequencing · healthy-tooth
protection · adversarial treatment-plan auditing · evidence retrieval and appraisal · research
question selection.

## Live evidence connectors

| Placeholder | Status |
|---|---|
| `~~literature` | CONNECTED — PubMed/NCBI |
| `~~systematic-reviews` | CONNECTED — PubMed filtered retrieval |
| `~~journal-access` | CONNECTED — METADATA/CITATION VERIFICATION via Crossref |
| `~~clinical-trials` | CONNECTED — ClinicalTrials.gov API v2 |
| `~~clinical-guidelines` | NOT CONNECTED |
| `~~manufacturer-ifu` | NOT CONNECTED |
| `~~regulatory-saudi` | NOT CONNECTED — AUTH REQUIRED |

Crossref is metadata and citation verification only — never full text. *Connected* means a real
request from this code succeeded in a real environment, not that any given request will succeed.

## Clinical safety architecture

Enforced ordering: case state → data sufficiency → red-flag sweep → clinical findings → prognosis →
irreversible treatment planning. Prognosis refuses to run out of order; an undetermined prognosis
blocks definitive irreversible planning; a safety block cannot be overridden.

A registered trial with no posted results never supports an efficacy claim. A retracted source is
excluded, not annotated. A claim above *unverified* requires a real retrieved source.

## Saudi governance layer

Four regulatory states, defaulting to *requires verification*. FDA approval, CE marking,
manufacturer claims and clinical evidence never establish Saudi status. PDPL rules cover
minimisation, de-identification including image metadata, cross-border transfer, consent layering
and the one-way clinical-to-marketing firewall.

## Clinical Protocol status

**v1.3 — APPROVED.** All eight previously open items closed. The protocol states no numeric
thickness; the binding minimum is the instructions for use of the product actually in use.

## Known limitations

No textbook knowledge base — it reasons about a case rather than reciting references. Prognosis
determinants are recorded, not measured. The red-flag sweep requires explicit answers and cannot be
auto-populated. Saudi governance is largely documentary rather than executable. Registry coverage
is incomplete, so absence from ClinicalTrials.gov is weaker evidence of absence than absence from
PubMed. Clinical depth outside the two in-scope disciplines is deliberately limited.

## Operational prerequisites before clinical use

These do not block software release; they gate specific clinical uses.

- **Product/IFU register not populated** — no product may be used before its exact name,
  manufacturer and IFU version are recorded with the IFU attached.
- **Laboratory register not populated** — a registered laboratory of record is required before an
  indirect restoration is prescribed.
- **Protocol signature outstanding** — content approval is complete; signing is reserved to the
  protocol owner.
- **SFDA authentication required** — Saudi product status cannot be verified in-session.

## Post-v1.0 roadmap

SFDA live connection · SCFHS, MOH, SDAIA/PDPL and CST connectors · clinical-guidelines connector ·
manufacturer-IFU connector · PubMed DataBankList NCT extraction · additional trial registries ·
M5 research and teaching migration · disciplines beyond the two in scope.

Deferred by decision, not oversight. None blocks v1.0.

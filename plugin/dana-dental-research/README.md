# Dental Research & Clinical Intelligence by Dr. Dana

Clinical decision support and scientific/academic support for dentistry, governed by CORE V0.4.

**Internal plugin identifier:** `dana-dental-research` · **Version:** 1.0.0

## What it does

**Evidence engine** — live PubMed/NCBI, Crossref and ClinicalTrials.gov API v2 connectors, with
DEL-7 evidence tagging, dual-source citation verification, an executable retraction gate, and
trial↔publication linkage that refuses to count a trial and its own paper as two studies.

**Saudi governance layer** — a regulatory gate with four states (VERIFIED / REQUIRES VERIFICATION /
NOT APPLICABLE / UNKNOWN-CONFLICT), PDPL patient-data rules including the clinical→marketing
firewall, professional and clinical governance separating clinical evidence from legal permission,
and a regulatory source hierarchy. FDA and CE approval never substitute for Saudi status.

**Clinical intelligence layer** — a case-state model carrying `[Reported]` / `[Observed]` /
`[Inferred]` / `[Unknown]` provenance on every finding, the M2 §7 red-flag sweep as executable
code, phased treatment planning with prognosis and sequencing gates, a categorical prognosis engine
(no invented probabilities), and a non-overridable safety veto in the output path.

## Scope

Fixed Prosthodontics and Esthetic Restorative Dentistry. Anything else returns `OUT_OF_SCOPE`
rather than a degraded answer.

## Connector status

| Placeholder | Status |
|---|---|
| `~~literature` | CONNECTED — PubMed/NCBI |
| `~~systematic-reviews` | CONNECTED — PubMed filtered retrieval |
| `~~journal-access` | CONNECTED — METADATA/CITATION VERIFICATION via Crossref |
| `~~clinical-trials` | CONNECTED — ClinicalTrials.gov API v2 |
| `~~clinical-guidelines` | NOT CONNECTED |
| `~~manufacturer-ifu` | NOT CONNECTED |
| `~~regulatory-saudi` | NOT CONNECTED — AUTH REQUIRED |

Crossref provides metadata and citation verification only — never full text.

## What it is not

Not a registered medical device. Not SFDA-, FDA- or CE-cleared diagnostic software. It does not
diagnose, prescribe or decide, and it can be confidently wrong. Every clinically consequential
output requires human verification. Final diagnosis, treatment selection, prescribing and every
irreversible procedure remain the treating clinician's responsibility.

## Author identity policy

The designer's name is never a clinical, scientific, regulatory or protocol authority. It appears
in the product name and in creator attribution only. Clinic-derived rules carry `(OPS)`, `(JUDG)`,
`(USER-SUPPLIED)` or `(INTERNAL PROTOCOL)`; scientific claims cite the real source or carry
`(UNVER)` with a runnable search strategy. Enforced by `clinical/identity_policy.py`.

## Before clinical use

Clinical Protocol v1.3 is APPROVED, with two use-gates outstanding: Appendix B (product/IFU
register) and Annex E (Laboratory of Record) are empty. §2.4 forbids using a product before its IFU
is registered; §8 requires a Laboratory of Record before an indirect restoration is prescribed. See
`docs/UNRESOLVED_GAPS.md` Part A.

## Tests

```bash
python3 clinical/tests/test_clinical_layer.py
python3 clinical/tests/test_clinical_completion.py
python3 clinical/tests/test_protocol_approval.py
python3 clinical/tests/test_identity_policy.py
python3 clinical/tests/test_docs_consistency.py
python3 connectors/clinical_trials/tests/test_clinical_trials.py
python3 connectors/sfda/tests/test_saudi_governance.py
```

---

Designed by Dr. Dana Abu Rawaeh

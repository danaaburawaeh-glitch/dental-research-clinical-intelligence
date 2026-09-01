<!--
REFERENCE-ID: claim-evidence-linking
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-09-01
New in v1.2. Executable implementation: `evidence/claim_link.py`. Interoperates with the clinical
layer's `clinical/evidence_binding.py`, which is unchanged.
-->

# Claim–Evidence Linking

Loaded by: evidence-research, quality-control, clinical-case, treatment-plan-audit.

Every consequential clinical claim links to five things:

**citation · verification state · study type · certainty · directness**

## Why all five

Each is routinely mistaken for the others:

- A **citation** says the paper exists.
- A **verification state** says the citation is accurate.
- A **study type** says what kind of investigation it was.
- **Certainty** says how much confidence the evidence justifies.
- **Directness** says whether it answers this question at all.

A claim carrying only the first is the most common form of evidence theatre in clinical writing:
the reference is real, and it establishes nothing about what is being asserted.

## Why at the claim

They attach at the claim, not in a bibliography. A reader deciding whether to act on one sentence
should not have to reconstruct which of eleven references supports it.

## Required shape

```
Claim:
  Enamel bonding is associated with better veneer survival.

Evidence:
  Systematic review / meta-analysis

Citation:
  [the retrieved citation]

Citation status:
  VERIFIED

DEL-7:
  (L2)

Certainty:
  MODERATE  (DENTAL AI STRUCTURED CERTAINTY ASSESSMENT)

Directness:
  DIRECT

Limitations:
  Predominantly non-randomized clinical studies.
```

## Audit rules — CRITICAL failures

A consequential claim fails outright when:

- any of the five links is missing;
- its source is **RETRACTED**;
- its citation is **NOT_VERIFIED**;
- its source is a **laboratory, computational or registry record** and the claim is about patient
  outcomes.

## Audit rules — MAJOR findings

- Certainty **NOT ASSESSABLE** — the claim may be stated only with that explicitly attached.
- Directness **INDIRECT** — reportable as indirect supporting evidence, never as directly
  answering the claim.
- An **unverified** claim with no runnable search strategy standing in for the citation it lacks.
- A **VERIFIED citation with LOW / VERY LOW / NOT ASSESSABLE certainty and no stated limitation** —
  the verification state would otherwise be read as strength. This is the v1.2 rule made
  mechanical.

## Set-level rule

A single unsupported consequential claim fails the whole set. It is not offset by well-supported
neighbours.

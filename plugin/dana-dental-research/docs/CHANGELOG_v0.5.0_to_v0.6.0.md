# Changelog — v0.5.0 → v0.6.0 (FEATURE RELEASE — Phase C: Saudi Governance & Regulatory Layer)

## Headline

M4 (Saudi Regulatory, Patient Data & Governance) is migrated into four executable-adjacent
reference files plus an SFDA connector. `~~regulatory-saudi` is **NOT CONNECTED — AUTH REQUIRED**:
an honest negative, because SFDA requires a registered application.

## Not changed

PubMed, Crossref and ClinicalTrials.gov connectors are **byte-identical** to v0.5.0 (`diff -rq`).
M5, Rosenstiel and Clinical Protocol are not migrated. The PubMed DataBankList/NCT limitation is
carried forward as a recorded gap, not fixed.

## Step 1 — M4 read from source

Read in full from Google Drive: `M4 — Saudi Regulatory, Patient Data & Governance`, doc
`1Z7uct0tq3D5zHa0ReajnGcbva-NHs359dhkDuZoz7Qc`, footer **M4 · V0.4 · 2026-08-20**.

**Two M4 documents exist in Drive with the same title.** The other is the CORE **V0.3** companion;
the V0.4 companion was used. `M4_MIGRATION_AUDIT.md` records the selection and audits 30 rules:
21 NEW, 3 REFINE, 2 KEEP, 1 CONFLICT, 3 DEFERRED. No rule dropped without an entry.

## Step 2-6 — Four Saudi references

`skills/clinical-governance/references/`:

| File | Covers |
|---|---|
| `saudi-regulatory-gate.md` | M4 §1, §3. Four states (VERIFIED / REQUIRES VERIFICATION / NOT APPLICABLE / UNKNOWN-CONFLICT), five hard rules, product checkpoints, connector interaction |
| `saudi-data-privacy-pdpl.md` | M4 §5, §6.2, §7. Minimisation, de-identification incl. EXIF and DICOM, images as personal data, cross-border, consent layering, the clinical→marketing firewall |
| `saudi-clinical-governance.md` | M4 §4, §6.1, §8, §11.1. The central evidence-vs-permission separation, scope, protected titles, delegation, role gating, consent, medico-legal posture |
| `saudi-regulatory-source-priority.md` | M4 §2. Six bodies, three-tier regulatory priority — explicitly *not* the evidence hierarchy |

The existing `saudi-regulatory-claim-gate.md` is retained as the narrower "don't state law from
memory" check, now consumed by the new gate rather than duplicated.

**The central rule, stated once and enforced everywhere:** clinical evidence and legal permission
are different questions with different answers from different sources. Strong RCT support never
makes a treatment permitted; SFDA registration never makes it effective.

## Step 4 — SFDA connector

`connectors/sfda/{client,models,errors}.py` + README + tests. OAuth client-credentials exactly as
the portal documents it (consumer key/secret, 24-hour token, Bearer).

**No endpoint is invented.** SFDA discloses gateway URLs only to registered applications; the
public docs use `api.example.com.sa` placeholders. Every URL is environment configuration, and
with none set the connector performs no request. A test asserts the source contains exactly one
hard-coded `https://` — the public portal, used only in the "how to configure" message.
Credentials are read from the environment only, never hard-coded, never logged, never persisted.

**The safety invariant:** every outcome except a real matching record maps to REQUIRES
VERIFICATION. There is no code path to "not approved in Saudi Arabia". An empty SFDA result is not
evidence a product is unregistered.

## Step 7 — Quality control

Seven Saudi checks added to `quality-control/SKILL.md`. **Critical failure, release-blocking:**
claiming a Saudi regulatory status without verified Saudi-source evidence — including on the
strength of a foreign regulator, a manufacturer claim, clinical evidence, or an empty/unavailable
SFDA lookup.

## Step 8 — Tests

`connectors/sfda/tests/test_saudi_governance.py` → **50/50 pass**, all 8 required scenarios plus 8
invariants. Tests 1-3 and 7-8 exercise the regulatory-state machine; tests 4-6 assert the
governing rules are actually present in the shipped reference files — a documentation rule absent
from the shipped file is not an enforced rule.

## Step 9 — Connector states

| Placeholder | State |
|---|---|
| `~~literature` | CONNECTED — PubMed/NCBI (unchanged) |
| `~~systematic-reviews` | CONNECTED — PubMed filtered retrieval (unchanged) |
| `~~journal-access` | CONNECTED — Crossref metadata/citation verification (unchanged) |
| `~~clinical-trials` | CONNECTED — ClinicalTrials.gov API v2 (unchanged) |
| `~~regulatory-saudi` | **NOT CONNECTED — AUTH REQUIRED** (was NOT CONNECTED) |
| `~~clinical-guidelines` | NOT CONNECTED |
| `~~manufacturer-ifu` | NOT CONNECTED |

## Known limitations recorded

`UNRESOLVED_GAPS.md` gains seven Phase C entries. Most consequential: **SFDA is one of six bodies
M4 names** — SCFHS, MOH, SDAIA and CST have no connector at all, so every claim in those domains
is REQUIRES VERIFICATION with no lookup available. Also recorded: the unverified SFDA response
schema, the M4 §9 amendment-authority conflict, the deferred §10/§11 workspace rules, and that
most Saudi rules are documentary rather than executable.

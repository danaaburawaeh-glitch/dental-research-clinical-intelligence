# Clinical Source Inventory — v0.8.0 (Part 1)

Conducted before any clinical rule was written. Every source below was actually opened, except
where marked NOT AVAILABLE.

| Source | Location | Status | Class |
|---|---|---|---|
| **Clinical Protocol — Prosthodontics & Esthetic Dentistry, v1.2** | Drive `1LYU9J6R…` | **AVAILABLE** | **AUTHORITATIVE (operator-approved practice) — but WORKING DRAFT** |
| **CORE V0.4** | Drive `1cR6GKQ0…` | **AVAILABLE** | **AUTHORITATIVE** |
| **M1 V0.4 — Workflows & Output Templates** | Drive `1oG96rCZ…` | AVAILABLE | AUTHORITATIVE (migrated in v0.7.0) |
| **M2 V0.4 — Clinical Safety, Risk & Special Populations** | Drive `1nI4gP-H…` | AVAILABLE | AUTHORITATIVE (migrated in v0.7.0) |
| **M3 V0.4 — Evidence & Source Protocol** | Drive `1Ati4WlY…` | AVAILABLE | AUTHORITATIVE (migrated in v0.3) |
| **PROMPT MASTER** (`20_FIXED_PROSTHODONTICS_ROSENSTIEL.md` spec) | Drive `1zvWNfiW…` | AVAILABLE | **SUPPORTING** — operator-authored *specification*, not content |
| **Contemporary Fixed Prosthodontics (Rosenstiel, Land, Walter)** | — | **NOT AVAILABLE** | **DO NOT USE** |
| `20_FIXED_PROSTHODONTICS_ROSENSTIEL.md` (the converted file) | — | **NOT AVAILABLE** — never produced | DO NOT USE |
| `بروتوكولات العيادة الداخلية — قالب` (clinic protocol template) | Drive `1i5pEVA-…` | AVAILABLE but **EMPTY TEMPLATE** | DO NOT USE |
| `الاختبار الأول / الثاني` (test transcripts) | Drive | AVAILABLE | **DO NOT USE** — prior AI session output, not a source (CORE §10: AI content is never a source) |
| `dana-clinical-core/knowledge/clinical` | Local | AVAILABLE but **EMPTY** (`.gitkeep` only) | — |
| M5 | Drive `1kZD5gA7…` | AVAILABLE | **NOT USED** — excluded by instruction |

## What the inventory changed

**The Rosenstiel textbook does not exist in the project sources.** The registry spreadsheet maps
`20_FIXED_PROSTHODONTICS_ROSENSTIEL.md` to a document that turns out to be a **50-section
conversion prompt**, not converted content. The target file was never produced. Nothing has been
reconstructed from memory; the four reference files contain **no textbook content and no
`[Source: Rosenstiel Ch. X]` anchors**, and a regression test asserts their absence.

**The real find was the clinic's own Clinical Protocol v1.2** — a genuinely source-tagged
operational document with eight Crossref-verified references (R1–R8), DEL-7 tags on individual
rules, and an explicit list of what is never done. It is the substantive source for all four new
references.

**Its status constrains how it may be cited.** The protocol is `مسودة عمل` (working draft), not
`معتمدة` (approved); eight open items in its Appendix C block approval. CORE §9.1 requires that to
be stated on every citation, and the reference files do so.

## Provenance actually available for the four references

| Anchor | Used for |
|---|---|
| **R1** Sanz et al. 2020, EFP S3 guideline, `doi:10.1111/jcpe.13290` **(L1)** | Perio control before prosthetics; supragingival margin preference; recall intervals; interdental brushes |
| **R2** Berglundh et al. 2018, `doi:10.1111/jcpe.12957` **(L1/L4)** | Peri-implant health criteria; cleansability and emergence design |
| **R3** Bidra et al. 2016, ACP/AGD recall guideline **(L1/L4)** | Recall and maintenance content and frequency |
| **R4** Verhoeff et al. 2025, `doi:10.1111/joor.13985` **(L4)** | Bruxism assessment elements and confidence grading |
| **R5** Morimoto et al. 2016, `doi:10.11607/ijp.4315` **(L2)** | Laminate veneer survival; conservative preparation principle |
| **R6** Saini et al. 2025, `doi:10.1177/20552076251388392` **(L2)** | DSD supports satisfaction/communication, not outcome prediction |
| **R7** Ma et al. 2026, `doi:10.1016/j.jdent.2026.106974` **(L2)** | Zirconia outcomes — publication status to be re-checked when cited |
| **R8** Revilla-León et al. 2023, `doi:10.1016/j.prosdent.2021.05.008` **(L2)** | Limits of digital implant planning |
| Clinic Protocol **(JUDG / OPS / IFU)** | Practice-specific rules, material choices, prohibitions |

No DOI in this release was written from memory; all are reproduced from the protocol's Appendix A,
which records that they were verified via Crossref on 14 August 2026.

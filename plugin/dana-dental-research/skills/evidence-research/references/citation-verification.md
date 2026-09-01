<!--
REFERENCE-ID: citation-verification
VERSION: 1.2.0
CANONICAL-OWNER: evidence-research (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-09-01
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently.
v1.2: CITATION VERIFICATION 2.0. The four-state model is replaced by seven states across two
axes, and the year-only disagreement is no longer a verification failure. Executable
implementation: `evidence/citation_verification.py`. The v1.1 connector-layer verifier
(`connectors/shared/citation_verifier.py`) is unchanged and still correct for what it does — it
answers the narrower "do the two sources agree" question that this file's layer builds on.
v0.4.1: added the retraction/correction check requirement. v0.4: added dual-source verification.
-->

# Citation Verification Gate — 2.0

Loaded by: evidence-research, quality-control.

## Purpose

Confirm that a citation is real, correctly described, and still standing. That is all it does.

**A verified citation is not strong evidence, and this gate never implies that it is.** Strength
comes from study design, appraisal, certainty and directness — four separate assessments, none of
which this gate performs. `evidence/citation_verification.py` returns
`evidential_strength: None` on every result for exactly this reason.

## Two axes, both always reported

| Axis | Question | Values |
|---|---|---|
| **Bibliographic state** | Is the citation's metadata right? | VERIFIED · VERIFIED_WITH_METADATA_DISCREPANCY · PARTIALLY_VERIFIED · NOT_VERIFIED |
| **Publication integrity** | Has the record since been retracted or amended? | ACTIVE · RETRACTED · CORRECTED · EXPRESSION_OF_CONCERN · UNCHECKED |

The **headline state** is drawn from both, with integrity dominating: a bibliographically perfect
citation to a retracted paper is a safety problem, not a bibliographic success. The bibliographic
reading is never discarded when that happens — it stays in its own field.

## The seven states

| State | Meaning | May support a clinical claim? |
|---|---|---|
| **VERIFIED** | Both sources retrieved and agreeing on every comparable component | Yes |
| **VERIFIED_WITH_METADATA_DISCREPANCY** | Identity confirmed; a non-identity field (in practice, the year) disagrees. Reported in full, resolved neither way | Yes, with the discrepancy stated |
| **PARTIALLY_VERIFIED** | One source only, or too little overlapping metadata to cross-check. An absence of corroboration, not a conflict | Yes, with the cap stated |
| **NOT_VERIFIED** | Nothing retrieved, or a disagreement that is not a benign date variation | **No** — mark (UNVER) and give a runnable search strategy |
| **RETRACTED** | Structured retraction metadata present | **No** — excluded from synthesis entirely |
| **CORRECTED** | A correction or erratum is linked | Yes, but the corrected version must be the one actually read |
| **EXPRESSION_OF_CONCERN** | An expression of concern is linked | Yes, with heightened caution. **Not a retraction** — never reported as one |

## The year rule (v1.2 RC — three-valued, and identical on both transports)

The publication year is compared three ways, because it has three meaningfully different
outcomes:

| Year comparison | Meaning | Resulting state (identity established, nothing else disagreeing) |
|---|---|---|
| **MATCH** | identical | VERIFIED |
| **WITHIN_TOLERANCE** | differs by ≤ 1 year — the documented online-first vs print/issue window | **VERIFIED_WITH_METADATA_DISCREPANCY** |
| **MISMATCH** | differs by > 1 year | **NOT_VERIFIED** — unexplained |

Two things changed in the RC, and both make the reading more honest:

1. **A within-tolerance gap is no longer silently folded into VERIFIED.** It is a real
   disagreement between two sources, and the reader is now told about it. Previously the ±1
   tolerance made it invisible.
2. **A beyond-tolerance gap is no longer given the benign online-first explanation.** A journal
   publishes an article online in one year and in an issue the next; it does not publish it in an
   issue five years later. Beyond the window the explanation does not reach, so the disagreement
   is unexplained and the citation is not treated as confirmed.

Required output whenever the year differs: `pubmed_year`, `crossref_year`, `year_gap`,
`year_tolerance`, `discrepancy_type` (`ONLINE_FIRST_VS_ISSUE_YEAR`) and the source name for each
year. **Neither year is ever replaced by the other.**

## Both transports return the same semantics

The remote MCP `verify_citation` tool and the local evidence layer implement the same table
above, with the same author and journal comparators. A caller must never have to know which
transport answered in order to interpret the verdict.

Because a deployed server is not upgraded by editing its source, parity is additionally enforced
at the point of use by `evidence/transport_reconcile.py`:

- **The local layer is authoritative for the final citation state.** The remote tool is a
  retrieval accelerator, never the last word — and the plugin already holds both underlying
  records, because every record must be re-fetched locally for the retraction gate anyway.
- A legacy server's year-only `NOT_VERIFIED` is recognised as a known transport-version pattern
  and recomputed locally.
- **Any divergence is reported, never silently resolved** — both verdicts are named in the search
  log, because a transport-version difference is a property of the connection, not of the
  citation.

## Verification components — always individually visible

Seven components are reported for every check:

`DOI_MATCH` · `PMID_MATCH` · `TITLE_MATCH` · `AUTHOR_MATCH` · `JOURNAL_MATCH` · `YEAR_MATCH` ·
`RETRACTION_STATUS`

Each carries MATCH / MISMATCH / NOT_COMPARABLE (RETRACTION_STATUS carries the integrity value),
along with both values and both source names.

**No single verification score is produced.** A scalar would be read as a quality measure and
would flatten the distinction the components exist to preserve: NOT_COMPARABLE is an absence,
MISMATCH is a conflict, and any number that averages them means neither. A `component_counts`
summary is given for scanning; the components themselves stay visible beneath it.

## Never silently resolve a discrepancy

Where sources disagree, report both values and both sources. Never average, never prefer the
"more authoritative" source, never quietly drop the field. An *interpretation* may be offered —
the online-first explanation above is one — but it is offered alongside the raw values, and it
never edits them or removes the discrepancy from the output.

## Identity establishment

Before descriptive metadata is weighed, the two records must be shown to describe the same work:

- a matching DOI or PMID, **or**
- title AND authors AND journal all matching, where no identifier is comparable.

A DOI or PMID **disagreement** is an `IDENTITY_CONFLICT` and is NOT_VERIFIED outright — the
records may not be the same work at all, and no amount of descriptive agreement settles that.

Author comparison is by surname, handling both renderings the connectors return — PubMed's
"Smith J" and Crossref's "John Smith" (v1.2 fix in `shared/normalization.py`'s `surname()`;
previously the last token was taken unconditionally, which turned "Smith J" into "J" and failed
real PubMed × Crossref pairs on the author component).

## Retraction/correction check — required, and separate

Verification confirms bibliographic accuracy. It does not confirm the paper still stands. The
retraction gate (`retraction-correction-gate.md`, `connectors/shared/retraction_gate.py`) is a
separate, both-required check, and it runs **first** — before study classification and DEL-7
tagging.

**An unchecked status is not a clean one.** A record with no structured publication-status
metadata is `UNCHECKED` and is disclosed as such. Records retrieved over the remote MCP transport
carry no retraction metadata at all and must be re-fetched locally before they can back a
clinical claim — see `retrieval-transports.md`.

## Hard rules (unchanged, still apply)

- UNVERIFIED references are never formatted as confirmed citations. No fabricated DOI, PMID,
  journal or year dressing.
- Use the (UNVER) DEL-7 marker on any such item, with a runnable search strategy in place of the
  citation.
- Never invent a missing bibliographic field. State "field not verified".
- **Quote accurately; never paraphrase a guideline recommendation in a way that changes its
  strength.** "May be considered" is not "is recommended".
- A verified reference held elsewhere in the system may be reused with its provenance and
  verification status preserved, cited by that preserved status — not as freshly re-verified.

## QC check

Every citation-like statement in a final output carries an explicit state from the seven above.
Anything without one is treated as NOT_VERIFIED and marked (UNVER).

Additionally, for v1.2:

- Is a year-only disagreement being reported as NOT_VERIFIED? That is now a defect.
- Is a discrepancy being silently resolved rather than reported with both values?
- Is a VERIFIED state anywhere doing the work of an evidence-strength claim? That is the single
  failure this whole layer exists to prevent.

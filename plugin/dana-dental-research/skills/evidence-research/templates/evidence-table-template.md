# Evidence Table

One row per consequential source. Fourteen columns, per `evidence/evidence_table.py`.

| Study | Year | Design | N | Intervention | Comparator | Follow-up | Outcome | Effect | Verification | Risk of Bias | Certainty | Directness | Key Limitation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | |

## No cell is ever blank

A blank cell is read as "nothing notable" far more often than as "not established", and those are
opposite meanings. Every unfilled cell carries an explicit marker:

| Marker | Means |
|---|---|
| **NOT REPORTED** | The source was read and does not state it |
| **NOT AVAILABLE** | The source was not read at that depth — no full text was retrieved |
| **NOT ASSESSED** | This system did not assess it |

## Column notes

- **Design** — `study-design-classification.md`. A design inferred from free text is marked
  `(inferred from text)`. A registry record carries `REGISTRY ONLY — NOT EVIDENCE OF EFFICACY`;
  a laboratory record carries `LAB`.
- **Verification** — one of the seven states in `citation-verification.md`. Never blank, never
  assumed VERIFIED. `VERIFIED_WITH_METADATA_DISCREPANCY` names the discrepant field in the cell.
- **Risk of Bias** — the judgement and the tool, or `(no formal tool applied)`. A tool is named
  only where it applies to the design and its required domains were available.
- **Certainty** — `certainty-of-evidence.md`. Where the authors reported GRADE themselves, both
  appear: the system's own rating and theirs, each labelled.
- **Directness** — `evidence-directness.md`. A capped verdict shows what it was capped from.
- **Effect** — must include a confidence interval where available. A bare point estimate or a
  significance label alone does not satisfy `evidence-quality-appraisal.md`, and any figure here
  must clear `numeric-evidence-gate.md`.

## Audit

Every row must carry a Verification, a Certainty and a Directness. Those three are what stop the
table being a bibliography with extra whitespace — a row missing any of them cannot be weighed by
the reader. `EvidenceTable.audit()` checks this.

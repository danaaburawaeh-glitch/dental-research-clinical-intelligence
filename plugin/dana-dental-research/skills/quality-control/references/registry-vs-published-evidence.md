<!--
REFERENCE-ID: registry-vs-published-evidence
VERSION: 0.5.0
CANONICAL-OWNER: quality-control
Added in v0.5.0 (Phase B) alongside the ClinicalTrials.gov connector.
-->

# Registry vs Published Evidence — Quality Control Gate

Applies to any output that cites, mentions, or relies on a ClinicalTrials.gov record.

## Critical failure

> **Using a ClinicalTrials.gov registration record as proof that an intervention is effective,
> without reported supporting results.**

This is a release-blocking defect, in the same tier as citing a retracted paper or fabricating a
DOI. A registration is a statement that someone intends to study something. It says nothing
whatsoever about outcomes. If an output's support for an efficacy claim reduces to "a trial
exists", the claim is unsupported and must be withdrawn or downgraded.

## Checklist

**1. Real NCT ID.** Every trial cited carries a validated `NCT` + 8 digits that was actually
returned by the connector. Never construct, complete or correct an NCT ID. An ID that failed
validation was never sent to the registry and has no record behind it.

**2. Trial status traceable.** Each cited trial's `overall_status` is present and came from the
retrieved record, not from assumption or from the trial's age.

**3. Registry and publication kept separate.** The output makes clear which statements come from
the registry and which from peer-reviewed literature. Registry-reported results are labelled
sponsor-submitted and not peer-reviewed wherever they are quoted.

**4. Completed ≠ successful.** No output infers benefit, effectiveness or a positive finding from
`COMPLETED`. Completion means the trial finished.

**5. Withdrawn ≠ negative result.** `WITHDRAWN` means the trial never enrolled anyone. It is not
evidence against the intervention and must never be presented as such. `TERMINATED` is reported
with its stated reason where the registry gives one, and is likewise not evidence of failure.

**6. No double-counting.** A registry record and its linked publication are one study. Any count
of supporting studies uses `independent_study_count`, never the number of records.

**7. Posted registry results explicitly labelled.** Any figure taken from `registry_results`
carries the registry-reported label. No significance, effect size or direction of benefit is
derived from registry data beyond what is explicitly reported.

**8. Publication linkage verified.** Any statement that a trial "was published as" X rests on
`LINK VERIFIED` from a real identifier. Topic, title, author or year similarity is never
sufficient. A `BACKGROUND` reference does not establish that a publication reports the trial.

**9. Exact registry search provenance retained.** The `executed_query`, retrieval timestamp and
`retrieval_status` are preserved for every registry search behind an output, so the search can be
re-run and audited.

## Wording that fails this gate

| Fails | Why | Acceptable form |
|---|---|---|
| "Clinical trials support this technique (NCT…)." | Registration cited as support. | "One trial of this technique is registered (NCT…, recruiting); no results are published yet." |
| "The trial was completed, so the technique is validated." | Completion read as success. | "The trial completed in 2019; no results have been posted or published." |
| "The trial was withdrawn, suggesting the approach failed." | Withdrawal read as a negative finding. | "The trial was withdrawn before enrolment (reason: funding), so it produced no data either way." |
| "Six studies support this (4 trials + 2 papers)." | Double-counted linked records. | "Four underlying trials, two of which are also published." |
| "Registry results show a significant improvement." | Significance inferred from registry data. | "Registry-reported results (sponsor-submitted, not peer-reviewed) list a mean ISQ change of X; no significance testing is reported there." |

# Live ClinicalTrials.gov Validation — v0.5.0 Phase B

All six required tests were run from the **actual packaged connector code** on this machine
(Claude Code / macOS, 2026-08-31), as real subprocesses against the live API. No web search, no
browser tool, no mocked network. Service-reported `apiVersion`: **2.0.5**.

Section 18's five-point bar: (1) code exists ✓ (2) packaged connector executes ✓ (3) real API
request succeeds ✓ (4) response parses ✓ (5) live validation passes ✓.

---

## TEST 1 — General dental trial search — PASS

```
python3 connectors/clinical_trials/client.py search --condition "dental implants" --max-results 5
```

`status: SUCCESS`, `total_count: 1350`, exit 0.
`executed_query: query.cond=dental+implants&pageSize=5&countTotal=true`

Real NCT IDs returned:

| NCT ID | Status | Title |
|---|---|---|
| NCT05162963 | UNKNOWN | Impact of Removable Versus Fixed Implant-supported Prostheses… |
| NCT00226148 | COMPLETED | Immediate Implant Placement in the Molar Regions |
| NCT05699343 | ENROLLING_BY_INVITATION | Surgical Treatment of Peri-implantitis Using a Bone Substitute |
| NCT07778199 | RECRUITING | Passive Fit of Implant-Supported Frameworks: Digital vs… |
| NCT05436158 | UNKNOWN | The Use of a New Safe Angle Position for Implant Placement |

## TEST 2 — Fetch — PASS

```
python3 connectors/clinical_trials/client.py fetch --nct-id NCT00226148
```

`status: SUCCESS`. Every field required by the brief verified present and correctly typed:

| Field | Value |
|---|---|
| nct_id | NCT00226148 |
| brief_title | Immediate Implant Placement in the Molar Regions |
| overall_status | COMPLETED |
| study_type | INTERVENTIONAL |
| phases | `['EARLY_PHASE1']` |
| enrollment / type | 92 / ACTUAL |
| conditions | Periodontitis; Dental Caries; Periapical Periodontitis |
| interventions / types | 3 interventions; `['DEVICE', 'PROCEDURE']` |
| lead_sponsor | University of Aarhus (OTHER) |
| eligibility | sex ALL, min 18 Years, healthy_volunteers true, 245-char criteria text |
| has_results | false |
| evidence_class | `REGISTERED_LINKED_PUBLICATION` |
| status_safety_note | "COMPLETED MEANS THE TRIAL FINISHED, NOT THAT IT SUCCEEDED…" |

Provenance carried `source_connector: clinical_trials`, `source_database: ClinicalTrials.gov`,
`nct_id`, retrieval timestamp, exact query and `retrieval_status`.

## TEST 3 — Status filter — PASS

```
search --condition "dental caries" --status RECRUITING --max-results 5
```

`executed_query: query.cond=dental+caries&filter.overallStatus=RECRUITING&pageSize=5&countTotal=true`
All five returned records parsed with `overall_status == "RECRUITING"`. The filter is applied by
the server and confirmed in the structured field, not assumed.

## TEST 4 — Zero result — PASS

```
search --condition "zzqxdental unobtainium periodontal flurbotron"
```

`status: ZERO_RESULTS`, `total_count: 0`, exit 0 (zero results is not a failure). The response
carried the mandatory meaning string:

> The executed search returned zero matching registry records. This is NOT a statement that no
> such trials exist — only that this query, as executed, matched nothing.

## TEST 5 — Results-aware record — PASS

```
fetch --nct-id NCT00607022
```

`has_results: true`, `evidence_class: REGISTERED_REGISTRY_RESULTS_POSTED`,
`results_first_post_date: 2018-07-27`.

`registry_results` captured separately and labelled
**"REGISTRY-REPORTED RESULTS — sponsor-submitted, NOT peer-reviewed"**, containing:
participant flow (`groups`, `periods`), baseline characteristics (`groups`, `denoms`, `measures`),
1 outcome measure ("Implant Stability Scale (ISQ) Score Change After 16 Weeks"), and
adverse-event data present.

Nothing was calculated from these values — no significance, no effect size, no direction of
benefit. They are carried through structurally with the interpretation rule attached.

## TEST 6 — PubMed linkage — PASS

```
fetch --nct-id NCT00782171
```

Registry references: PMIDs 18416725, 18983314, 22171722 — all type `RESULT`
(`reports_this_trial: true`). `evidence_class: REGISTERED_LINKED_PUBLICATION`.

PMID 18416725 then retrieved through the **existing, unmodified PubMed connector**:
*"Immediate and early non-occlusal loading of Straumann implants with a chemically modified
surface…"*, Clinical Oral Implants Research, 2008, DOI `10.1111/j.1600-0501.2007.01517.x`.

Executable linkage verdict (`shared/trial_publication_linkage.py`):

```
status: TRIAL ↔ PUBLICATION LINK VERIFIED
basis:  registry_reference_pmid
reason: Registry reference list names PMID 18416725 as a report of NCT00782171.
```

Crossref verification of that DOI through the existing Crossref connector: `SUCCESS`
(Clinical Oral Implants Research, 2008). Citation verifier: **`VERIFIED`** — title, authors,
journal, year and DOI all agree.

Deduplication: 2 input records → **`independent_study_count: 1`**. The trial and its publication
are one study, as Section 8 requires.

Full chain exercised end to end: **ClinicalTrials.gov → NCT ID → PubMed → Crossref verification.**

---

## Regression suite

`python3 connectors/clinical_trials/tests/test_clinical_trials.py` → **50/50 assertions pass**,
covering all 20 required scenarios. Network is mocked there deliberately: a retry, 429, 5xx or
timeout test is only meaningful if it is reproducible.

## What was NOT validated live

- **HTTP 429 and 5xx retry behaviour against the real service.** The API did not rate-limit or
  fail during testing, so those paths are proven against a mocked network only. Provoking them
  deliberately against a public NLM service would be abusive.
- **Pagination beyond page 2.** `pageToken` was verified live during API verification (two
  disjoint pages); deep pagination was not exercised.
- **The NCT-in-publication linkage direction against live data.** The registry-side direction was
  verified live; the publication-side direction is covered by regression tests only, because
  PubMed's structured `<DataBankList>` accessions are not parsed (Phase B must not modify the
  validated PubMed connector) and the abstract-text path needs a publication that happens to
  quote its NCT ID in the abstract.

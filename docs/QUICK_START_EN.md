# Quick Start — English

## What this is, in one paragraph

A dental clinical decision-support assistant that runs inside Claude Code. You give it a case; it
organises the data, tells you what is missing, checks for emergencies, assigns prognosis, sequences
treatment, and backs claims with real retrieved literature. It stops rather than guessing.

## Install (once)

```bash
claude plugin marketplace add danaaburawaeh-glitch/dental-research-clinical-intelligence
claude plugin install dana-dental-research@dana-dental
```

## Start within 5 minutes

1. Open Terminal, type `claude`, press Enter.
2. Type `/dana-dental-research:start` and press Enter.
3. Describe your case in plain language, or paste the template below.

That is all. You do not need to learn commands — the assistant routes your question itself.

## Analysing a clinical case

Paste what you have. Missing information is expected — the assistant will rank what is missing by
how much it would change the decision, and ask for the most important item first.

```
Age:
Sex:
Chief complaint:
Medical history:
Medications:
Allergies:
Dental history:
Clinical examination:
Radiographic examination:
Photographs:
Occlusion:
Periodontal status:
Habits:
Patient goals:
Proposed plan (if any):
```

## Reviewing an existing plan

> "Audit this plan: full upper arch veneers, 10 units, patient has generalised bleeding on probing
> and reports night-time clenching."

The audit is deliberately adversarial. It looks for unstated assumptions, sequencing errors, missed
conservative options and prognosis gaps. It does not restate your plan approvingly.

## Scientific research

> "What is the evidence for immediate versus delayed implant placement in the esthetic zone?"

You get: the question framed as PICO, the actual search performed, each study with its design and
limitations, a synthesis at a stated evidence level, applicability to your patient, and — kept
separate — what the evidence does not answer.

## Comparing options

> "Compare lithium disilicate and monolithic zirconia for a posterior crown in a bruxist patient."

Comparisons always include *no treatment* and *monitor/defer*, with biological cost, expected
service life, failure mode and maintenance burden for each.

## A Saudi regulatory question

> "Is this bonding agent approved for use in Saudi Arabia?"

The honest answer today is **REQUIRES VERIFICATION** — SFDA lookup needs credentials not configured
in this release. FDA or CE approval will be reported separately and labelled as *not transferable*
to Saudi status. Verify with SFDA before purchase or clinical use.

## Most useful first commands

| | |
|---|---|
| `/dana-dental-research:start` | Orientation — begin here |
| `/dana-dental-research:clinical-case` | Full case analysis |
| `/dana-dental-research:triage` | Urgent symptoms, pain, swelling, trauma |
| `/dana-dental-research:esthetic-prosthodontics` | Veneers, crowns, esthetic planning |
| `/dana-dental-research:treatment-plan-audit` | Adversarial review of a plan |
| `/dana-dental-research:evidence-research` | Literature retrieval and appraisal |
| `/dana-dental-research:quality-control` | Check an output before you rely on it |

## Two rules worth knowing

**De-identify first.** Do not enter names, ID numbers or record numbers. Use "a 45-year-old female
patient" rather than a name.

**A failed search is not a finding.** If retrieval is unavailable, that means nothing was searched
— never that no evidence exists.

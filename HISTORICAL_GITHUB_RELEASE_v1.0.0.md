# Dental Research & Clinical Intelligence by Dr. Dana — v1.0.0

> **HISTORICAL RECORD**
> This document relates to the original v1.0.0 production/distribution validation.
> The current public release is **v1.0.2**.

## Production release

First validated production release. An evidence-grounded dental research and clinical
decision-support plugin for Claude Code, with particular strength in esthetic and fixed
prosthodontics.

Final production validation: **P0 blockers = 0 · P1 blockers = 0.**

## Highlights

- **Structured case analysis** — every finding tagged `[Reported]` / `[Observed]` / `[Inferred]` /
  `[Unknown]`; an inference must carry its basis; unknowns stay unknown.
- **It stops rather than guessing.** Insufficient data, an unanswered red flag or an undetermined
  prognosis blocks a definitive plan instead of producing a confident-looking one.
- **Healthy-tooth protection** — a least-invasive ladder; full-coverage crowns require a real
  structural indication, never esthetic convenience.
- **Adversarial plan auditing** — assumptions, sequencing errors, prognosis gaps and missed
  conservative options, with a verdict.
- **Nine skills** covering triage, case analysis, esthetic prosthodontics, plan audit, evidence
  research, research-question selection, governance and quality control.

## Clinical safety

Enforced ordering: case state → data sufficiency → red-flag sweep → findings → prognosis →
irreversible planning. A safety block cannot be overridden by rephrasing or insistence — the only
way past it is to resolve the cause or refer to a human clinician.

Prognosis is categorical only — favorable, guarded, poor or undetermined, across five independent
axes. **No invented percentages.**

## Evidence integrations

Live PubMed/NCBI, Crossref and ClinicalTrials.gov API v2. Evidence classified by source tier,
citations verified across two sources, retracted papers excluded from synthesis rather than
footnoted, and a registered trial with no posted results never treated as proof that a treatment
works.

Crossref provides metadata and citation verification only — not full text.

## Saudi governance

Four regulatory states, defaulting to *requires verification*. **FDA approval and CE marking never
establish Saudi authorisation.** PDPL patient-data rules, including a one-way firewall between
clinical material and marketing output.

## Known limitations

No textbook knowledge base — it reasons about a case rather than reciting references. Prognosis
reflects what the clinician entered. Clinical depth is strongest in fixed prosthodontics and
esthetic restorative dentistry; other specialties are referred out. SFDA regulatory lookup requires
credentials not configured in this release, so Saudi status always returns *requires verification*.

Two operational prerequisites before clinical use: the product/IFU register and the laboratory
register are not yet populated.

**This software is not a registered medical device and holds no SFDA, FDA or CE clearance.** It
supports clinical judgment; it does not replace it.

## Installation

```bash
claude plugin marketplace add <path-to-this-repository>
claude plugin install dana-dental-research@dana-dental
```

Full instructions, including verification and troubleshooting: `INSTALLATION.md`.

## Checksums

Verify your download:

```bash
cd releases
shasum -a 256 -c SHA256SUMS.txt
```

See `releases/SHA256SUMS.txt`.

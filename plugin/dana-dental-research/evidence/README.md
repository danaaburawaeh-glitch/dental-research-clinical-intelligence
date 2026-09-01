# `evidence/` — the v1.2 Evidence Intelligence layer

Executable modules that turn the v1.1 research retrieval system into an evidence intelligence
engine. Plain Python, no dependencies, no network. Invoked by the skills through the Bash tool,
the same way `connectors/` and `clinical/` are.

## The rule this layer exists to enforce

> **A bibliographically VERIFIED paper must never automatically be treated as strong evidence.**

Verification is one stage of six, and it answers one narrow question: is this citation real and
correctly described? Four further assessments stand between a real citation and a clinical
recommendation, and each can fail independently.

## The six stages

```
RETRIEVAL  ->  VERIFICATION  ->  APPRAISAL  ->  CERTAINTY  ->  SYNTHESIS  ->  APPLICABILITY
```

Each collapses into the one before it under pressure, and each collapse is a single plausible
sentence away: *"PubMed returned 431 results on this"* · *"the citation checks out, so the finding
stands"* · *"large sample, therefore reliable"* · *"high certainty, therefore do it for this
patient."* `pipeline.py` makes the boundaries load-bearing rather than advisory.

## Modules

| Module | Does |
|---|---|
| `citation_verification.py` | Seven citation states across two axes; per-component evidence; the year-discrepancy rule |
| `study_design.py` | Names the design from structured metadata, with provenance; DEL-7 mapping; the registry and laboratory labels |
| `appraisal.py` | Per-field REPORTED / INFERRED-with-basis / UNKNOWN; formal-tool application refusal |
| `certainty.py` | Conservative GRADE-inspired certainty; never GRADE; never upgrades; NOT ASSESSABLE on missing domains |
| `sr_extraction.py` | Systematic review fields, with NOT REPORTED vs NOT AVAILABLE kept distinct |
| `overlap.py` | Duplicate records, same-study-multiple-reports, review updates, overlapping syntheses |
| `directness.py` | Six dimensions → four verdicts; the laboratory and registry cap |
| `numeric_gate.py` | Scans finished text; no unregistered effect estimate reaches a Clinical Bottom Line |
| `conflict.py` | EVIDENCE CONFLICT objects; provides no averaging function, by design |
| `rank.py` | DEL-7 + certainty + directness ordering; refuses to sort by date |
| `claim_link.py` | Binds a claim to all five links; audits for the failures that matter |
| `search_builder.py` | PICO-aware queries: OR within a concept, AND between concepts, phrases quoted |
| `evidence_table.py` | The fourteen-column table; no cell is ever blank |
| `bottom_line.py` | Seven sections; moves claims their evidence does not support |
| `output_modes.py` | Five modes, each with a section contract; identical gates across all five |
| `pipeline.py` | Stage ordering as a state machine |
| `_paths.py` | Import bootstrap |

## Tests

```
python3 evidence/tests/test_safety_nonnegotiable.py    # 65 checks — the nine prohibitions
python3 evidence/tests/test_evidence_engine.py         # 115 checks — ordinary correctness
python3 evidence/tests/test_benchmark.py               # 54 checks — the 38-question validation set
```

No network. Each returns a non-zero exit code on any failure.

## Benchmark

`benchmark/benchmark_questions.json` — 38 dental evidence questions across ten domains, with
thirteen deliberate trap types. **Every identifier in it is a synthetic `FIXTURE-`**: a benchmark
that seeds realistic-looking PMIDs or DOIs into the repository creates exactly the artefact the
engine exists to prevent.

## What this layer does NOT do

- It does not change the four MCP tool contracts (`search_pubmed`, `search_systematic_reviews`,
  `verify_citation`, `search_clinical_trials`). Appraisal reasoning lives here, in the plugin's
  skill/reasoning layer — the MCP server stays a retrieval service and does not become a clinical
  decision engine.
- It does not add a source. Cochrane/CENTRAL, Embase and Scopus remain NOT IMPLEMENTED;
  `~~clinical-guidelines`, `~~manufacturer-ifu` and `~~regulatory-saudi` remain NOT CONNECTED.
- It does not retrieve full text. No connector in this plugin provides it.

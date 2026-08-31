<!--
REFERENCE-ID: evidence-question-formulation
VERSION: 0.3
CANONICAL-OWNER: evidence-research
SOURCE: authoritative M3 §2 (surrogate-outcome warning); framework router is new v0.3 content.
LAST-SYNCHRONIZED: 2026-08-29
-->

# Evidence Question Formulation Engine

Loaded by: evidence-research.

Every evidence request should first become an answerable question. Do not retrieve against a vague
request — formulate it into one of the frameworks below first.

## Router

| Question type | Framework |
|---|---|
| Treatment effectiveness | PICO |
| Exposure / risk | PECO |
| Diagnostic accuracy | PIRD |
| Qualitative / patient experience | SPIDER or PICo |
| Prognosis | Prognosis-oriented PICO/PECO |
| Material / device | Define material, substrate, comparison, clinical outcome, time horizon (see below) |

## PICO(T) — treatment effectiveness

- **P** — population: who, precisely (age, condition, dentition state, risk profile)
- **I** — intervention, with the specific material/technique/protocol named
- **C** — comparator, including "no treatment" where relevant
- **O** — outcome, and whether it is *patient-important* (survival, function, pain, satisfaction)
  or a *surrogate* (bond strength, marginal gap, microleakage)
- **T** — timeframe, and whether it is adequate for the outcome in question

## PECO — exposure/risk

- **P** — population
- **E** — exposure (material, technique, habit, risk factor)
- **C** — comparator (unexposed or differently exposed group)
- **O** — outcome

## PIRD — diagnostic accuracy

- **P** — population
- **I** — index test (the diagnostic method being evaluated)
- **R** — reference standard (the accepted gold-standard comparator)
- **D** — diagnosis of interest / outcome the test is meant to detect

## SPIDER / PICo — qualitative / patient experience

- **SPIDER**: Sample, Phenomenon of Interest, Design, Evaluation, Research type
- **PICo**: Population, Interest (phenomenon), Context

Use whichever fits the specific request; SPIDER is generally better for qualitative synthesis
questions, PICo for narrower context-bound questions.

## Material / device questions

Define explicitly before retrieval:
- **Material** — the specific product/system, not a generic category
- **Substrate** — what it's being applied to or compared against
- **Comparison** — the alternative material/technique/no-treatment
- **Clinical outcome** — patient-important, not surrogate, wherever possible
- **Time horizon** — over what period the outcome is claimed

## Surrogate-outcome warning

If the only available outcomes are surrogates, say so before synthesising. A material that
performs better on marginal adaptation has not been shown to last longer in the mouth.
**Surrogate-only evidence is (LAB), not (L3)** — see del7-evidence-hierarchy.md §3.

## Output of this step

A framed question (PICO/PECO/PIRD/SPIDER/PICo, as selected) is the required input to
source-priority.md's retrieval-order logic and to search-strategy.md's search construction. Do not
proceed to connector invocation without it.

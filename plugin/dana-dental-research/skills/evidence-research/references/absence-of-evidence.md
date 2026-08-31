<!--
REFERENCE-ID: absence-of-evidence
VERSION: 0.3
CANONICAL-OWNER: evidence-research
SOURCE: authoritative M3 §8 (Google Drive 1Ati4WlYomswDa46LO7oy6E0wH6RSGVyNRjzRxydpYU8)
LAST-SYNCHRONIZED: 2026-08-29
This file did not exist in v0.2.1 — the prior connector-capability-map.md covered only the
search-unavailable case; M3's three-way (in fact, four-state) distinction is materially more
precise and is migrated here in full.
-->

# Absence of Evidence

Loaded by: evidence-research.

Four situations, never conflated:

## 1. Searched, nothing found
**"No clinical evidence located for this specific question. Absence of evidence is not evidence
of absence."**
Then say what the nearest available evidence covers, and how far it can reasonably be extended.

## 2. Search failed or unavailable
**"The search could not be completed."**
Never reported as situation 1. See source-priority.md §1 and connector-capability-map.md for the
connector-status distinction this depends on.

## 3. Evidence exists but is weak or indirect
Say so, and state what a better study would need to show. Route through
evidence-quality-appraisal.md (for weakness) and evidence-directness.md (for indirectness) — this
situation is often a combination of the two, and both should be named rather than blended into one
vague "the evidence is limited" statement.

## 4. Evidence of no material effect
Distinct from situation 1 (nothing found) and situation 3 (weak/indirect). This applies only when
retrieval succeeded and returned adequately powered, direct evidence that specifically shows no
meaningful effect — not merely a non-significant result from an underpowered study (which is
situation 3, and should be reported as such per evidence-quality-appraisal.md's rule that a wide
CI spanning no effect is not a positive — or definitive negative — result).

## Hard rules (non-negotiable across all four states)

- **Search failure != absence.** A failed, timed-out, or blocked search is never reported as "no
  evidence exists."
- **No evidence retrieved != evidence of no effect.** These are situations 1 and 4 respectively —
  never state one when the other is true.
- **No statistically significant effect != equivalence.** A non-significant result in an
  underpowered study says nothing about equivalence; only adequately powered evidence specifically
  testing for equivalence/non-inferiority can support that claim.
- **No RCT != no clinically useful evidence.** Absence of the highest-tier design does not mean
  the question is unanswerable — say what tier of evidence does exist and its limitations, per
  evidence-quality-appraisal.md.

## In all four situations

State what a clinician may reasonably do in the meantime and on what basis — and tag that basis
honestly, usually (L4) or (JUDG) per del7-evidence-hierarchy.md. Never let a genuine gap produce an
empty or unhelpful answer; the gap itself, clearly named, plus the best available fallback
reasoning, is the correct output.

## Registry-informed absence (v0.5.0, Phase B)

"No published evidence found" is a conclusion about the *literature*. With `~~clinical-trials`
connected, several materially different situations that used to collapse into that one sentence
can now be told apart — and they must be, because they point the clinician in different
directions.

| Situation | How it is established | What it actually means |
|---|---|---|
| No published evidence, and nothing registered | PubMed zero-results AND registry zero-results | The question is genuinely unstudied. |
| Trials exist but are ongoing | Registry hits with status `RECRUITING`, `ACTIVE_NOT_RECRUITING`, `ENROLLING_BY_INVITATION`, `NOT_YET_RECRUITING` | Evidence is coming. An answer may exist within a known horizon; state the expected completion date where the registry gives one. |
| Completed trials exist without publications | Registry hits with status `COMPLETED`, `evidence_class` = A, no linked publication | A publication gap — possibly selective non-publication. This is a finding about the evidence base, not an absence of research. |
| Results posted only in the registry | `evidence_class` = B | Data exist but have not been peer-reviewed. Quote them only with the registry-reported label. |
| Trials terminated or withdrawn | Status `TERMINATED` / `WITHDRAWN`, with `why_stopped` where given | Research was attempted and stopped. Report the stated reason. **Neither status is evidence the intervention failed**, and a withdrawn trial never started at all. |
| Registry status unknown | Status `UNKNOWN` | The sponsor has not verified recently. Preserve the uncertainty in both directions. |

**Do not collapse these into "no evidence".** Saying "there is no evidence" when four completed
trials sit unpublished in the registry misdescribes the evidence base — and saying it when three
trials are actively recruiting misses that an answer is close.

**Symmetric caution.** A registry search returning nothing is `ZERO_RESULTS` for that query, not
proof that nothing is registered. Registry coverage is incomplete: registration requirements vary
by jurisdiction, funder and study type, and much dental research — particularly smaller
university-run and non-interventional work — is never registered anywhere. Absence from
ClinicalTrials.gov is therefore weaker evidence of absence than absence from PubMed, not stronger.

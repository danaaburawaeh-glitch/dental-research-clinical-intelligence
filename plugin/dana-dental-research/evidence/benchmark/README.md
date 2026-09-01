# v1.2 Evidence Intelligence Validation Set

`benchmark_questions.json` holds the benchmark this branch is validated against: real dental
evidence questions across ten domains, each paired with the engine behaviour it is meant to
provoke.

## No fabricated identifiers

Every identifier in this file is a **fixture**, prefixed `FIXTURE-` and never formatted as a
PMID, DOI or NCT ID. That is deliberate and non-negotiable: a benchmark that seeds realistic-
looking identifiers into the repository creates exactly the artefact the system exists to
prevent — a plausible citation with no source behind it — and any later reader, human or model,
could lift one out of the test data and into an output.

Where a benchmark item needs a real record, it names the *search* that would retrieve one, not a
guessed identifier for it.

## Item shape

| Field | Meaning |
|---|---|
| `id` | stable identifier for the item |
| `domain` | one of the ten domains below |
| `question` | the clinical or research question, as a clinician would ask it |
| `pico` | the framed question — the engine must not retrieve against an unframed one |
| `trap` | what this item is designed to catch, or `none` for a straightforward item |
| `expected_behaviour` | what the engine must do |
| `must_not` | behaviours that fail the item outright |
| `fixture` | (trap items only) the synthetic record state the item is evaluated against |

## Domains

prosthodontics · esthetic dentistry · veneers · implants · adhesive dentistry · periodontics ·
endodontics · orthodontics · digital dentistry · AI in dentistry

## Trap types

| Trap | What it catches |
|---|---|
| `metadata_discrepancy` | a year disagreement forced to NOT_VERIFIED, or silently resolved |
| `weak_evidence` | a verified citation to a thin study read as strong support |
| `conflicting_reviews` | two good syntheses averaged instead of reported as a conflict |
| `retracted_record` | a retracted paper reaching synthesis |
| `corrected_record` | a correction not surfaced |
| `expression_of_concern` | an expression of concern reported as a retraction, or ignored |
| `registry_only` | a trial registration read as evidence of efficacy |
| `in_vitro_vs_clinical` | bench findings carried across the laboratory firewall |
| `absent_evidence` | "nothing found" reported as "no effect" |
| `overlapping_reviews` | one study counted twice through two reviews |
| `recency_bias` | a newer weaker source ranked above an older stronger one |
| `numeric_hallucination` | an effect estimate reconstructed from memory |
| `grade_invention` | a GRADE rating asserted where the authors performed none |

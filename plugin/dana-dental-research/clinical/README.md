# Clinical layer (Phase D, v0.7.0)

Turns the evidence and governance stack into a prosthodontic clinical assistant. Five modules,
beside `connectors/` because these reason rather than retrieve.

| Module | From | Does |
|---|---|---|
| `case_state.py` | M1 §2/§3/§4, M2 §1 | Case record with per-field provenance; minimum-dataset check; sufficiency verdict; ranked missing data |
| `red_flag_sweep.py` | M2 §7 | All 14 flags, executable. Silence is not clearance |
| `treatment_plan.py` | M1 §12/§13, M2 §5/§6 | Phases 0–4 + re-evaluation, with the sequencing gates |
| `safety_veto.py` | CORE §15, M2 | One non-overridable block in the output path |
| `evidence_binding.py` | M3 + the four connectors | Binds a claim to a decision with DEL-7 tag, provenance, regulatory state, directness |

## Usage

```python
import sys; sys.path.insert(0, f"{PLUGIN_ROOT}/clinical")
from case_state import CaseState, OBSERVED, INFERRED, UNKNOWN
import red_flag_sweep as rfs, safety_veto as veto, treatment_plan as tp, evidence_binding as eb

case = CaseState("CASE-20260831-01", "fixed_prosthodontics", notation="FDI")
case.record("allergies", "penicillin", OBSERVED, source="patient record")
case.record("ferrule", "adequate", INFERRED, basis="2 mm sound dentin on the periapical")

sweep = rfs.sweep({...})                 # every flag answered explicitly
plan  = tp.build_plan(case, items, alternatives)
gate  = veto.review(case, veto.ACT_PLAN_DEFINITIVE, sweep_result=sweep, plan_result=plan)
if gate.status == veto.SAFETY_BLOCK:
    print(gate.block_text)               # nothing else is emitted
```

## Rules enforced in code, not prose

- **Provenance never promotes.** `[Inferred]` requires its basis at construction; `[Unknown]`
  cannot carry a finding; there is no fifth tag.
- **Silence is not clearance.** An unanswered red flag is `NOT_ASSESSED`, never `ABSENT`, and an
  incomplete sweep cannot be reported as clear.
- **Prognosis before prosthesis.** A tooth with no assignable prognosis blocks restorative
  planning; a tooth absent from the prognosis map counts as undetermined.
- **No exit strategy, no plan.** A T3/T4 item without service life, failure mode, warning signs,
  retreatability, maintenance obligation and cost-of-being-wrong is blocked (M2 §6).
- **Alternatives always include no-treatment and monitor/defer.**
- **SAFETY_BLOCK is non-overridable.** No clean check cancels it; the only exit is resolve or refer.
- **No fabricated citation.** A claim above `UNVER` needs a real retrieved source; `UNVER` needs a
  runnable search strategy.

## Scope

Fixed Prosthodontics and Esthetic Restorative Dentistry only. Anything else returns `OUT_OF_SCOPE`
rather than a degraded answer.

## Tests

`python3 clinical/tests/test_clinical_layer.py` → 60 assertions, no network.

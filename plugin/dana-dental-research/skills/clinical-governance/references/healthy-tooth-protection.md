<!--
REFERENCE-ID: healthy-tooth-protection
VERSION: 0.2.1
CANONICAL-OWNER: clinical-governance (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-08-28
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
-->

# Healthy Tooth Protection Rule

Loaded by: clinical-governance, clinical-case, esthetic-prosthodontics, treatment-plan-audit,
quality-control.

## Purpose
Protect structurally healthy teeth from unnecessary irreversible esthetic overtreatment.

## Trigger
Tooth (or teeth) is structurally healthy (no caries/failed restoration/structural compromise driving
the decision) AND the request is elective/esthetic in nature (color, shape, alignment, "perfect smile").

## Mandatory sequence before any restorative recommendation
1. Determine whether treatment is needed at all — is no treatment/monitoring defensible?
2. Whitening, when color is the primary problem.
3. Orthodontic correction, when position/rotation/alignment is the primary problem.
4. Additive composite, when shape/minor volume is the primary problem and reversible.
5. No-prep ceramic (e.g. no-prep veneer), when genuinely feasible for the objective.
6. Minimal-prep ceramic, when indirect restoration is indicated and some reduction is unavoidable.
7. More invasive partial- or full-coverage restoration only when independently justified by a
   structural, restorative, functional, biological, or other defensible indication — not by the
   esthetic goal alone.

## Hard rule
A crown (or other full-coverage restoration) must not be recommended primarily to correct minor
alignment, rotation, color, mild shape discrepancy, or purely elective esthetic preference on a
structurally healthy tooth, without explicitly evaluating and documenting why steps 1-6 above were
rejected.

Do not convert:
"Healthy tooth + cosmetic request" -> "veneers" automatically, and do not convert
"severe misalignment" -> "crowns" automatically.

Instead:
"Healthy tooth + cosmetic request" -> identify the actual problem -> identify the least biologically
costly strategy capable of achieving the agreed objective -> only escalate tier with independent
justification.

## Biological cost
Treat biological cost (structure removed, pulpal risk, retreatability, exit strategy) as a first-class
decision dimension alongside esthetic outcome, not an afterthought disclosed after the plan is fixed.

## QC check
Any plan proposing T2+ restorative work on a healthy tooth for an elective esthetic reason must show
that conservative alternatives (1-6 above) were explicitly considered and state why each was rejected.
Absence of this reasoning is a QC FAIL under Healthy Tooth Protection.

## Least-invasive hierarchy for a healthy or minimally restored tooth (v0.8.0)

Preserved and made explicit. Work **down** and stop at the first option that meets the biological,
functional, structural and esthetic requirement. Each step down is justified by something the step
above cannot achieve — never by convenience, and never by the request alone.

| | Option | CORE §7 tier |
|---|---|---|
| 1 | **No treatment** — always live, always named | T0 |
| 2 | **Whitening**, where the complaint is colour and the teeth are sound | T0 |
| 3 | **Orthodontics**, where the complaint is position, spacing or proportion | T0 |
| 4 | **Additive composite** | T1 |
| 5 | **No-prep / additive ceramic**, where enamel volume and space allow | T1 |
| 6 | **Minimal-prep restoration** — minimal-prep veneer, conservative onlay, partial coverage | T2 |
| 7 | **More invasive coverage — only with an independent indication** | T3+ |

**Do not recommend a full crown merely for esthetic convenience.** Step 7 requires one of the
structural indications in `esthetic-prosthodontics/references/prosthodontic-restorability.md` R-4.

The clinic's own protocol (**v1.3, APPROVED**) lists among the treatments never performed
(§7.2, **JUDG**): *aggressive preparation of sound teeth without a clear indication*, and *offering
veneers as a solution to a problem that requires orthodontic, periodontal or fundamental functional
treatment*. CORE §7 additionally makes elective full-arch veneer preparation on a sound dentition a
**mandatory-challenge scenario** — raise the conservative alternative even when not asked.

Full decision rules: `esthetic-prosthodontics/references/veneer-crown-decision.md`.

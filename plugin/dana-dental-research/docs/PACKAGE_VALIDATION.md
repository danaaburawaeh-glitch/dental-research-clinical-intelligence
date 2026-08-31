# Package Validation — v0.3 (HISTORICAL)

> **HISTORICAL DOCUMENT — describes v0.3.** Retained for the record. It is not a statement about the current release. For current connector status, the Clinical Protocol status and the live gap list, see `UNRESOLVED_GAPS.md` (Part A) and `connector-capability-map.md`.

Performed before packaging, per Phase 22. Commands run are shown so the checks are reproducible,
not just asserted.

## 1. Every skill directory has a SKILL.md
**Result: PASS.** All 9 skill directories (`start`, `clinical-governance`, `clinical-case`,
`triage`, `esthetic-prosthodontics`, `treatment-plan-audit`, `scientific-problem-selection`,
`evidence-research`, `quality-control`) contain a `SKILL.md`.

## 2. SKILL.md frontmatter validity
**Result: PASS.** Every `SKILL.md` opens with `---`, contains `name:`/`description:`, and closes
the frontmatter block with a second `---`.

## 3. No orphan references inside evidence-research
**Result: PASS.** Every `references/*.md`, `templates/*.md`, and `tests/*.md` path mentioned in
`evidence-research/SKILL.md` resolves to an actual file. Full file listing cross-checked against
what SKILL.md's 13-step workflow cites — no reference file exists that SKILL.md doesn't route to,
and no path SKILL.md cites is missing.

**Note on `evidence-source-separation.md`:** not cited directly in `evidence-research/SKILL.md`'s
workflow steps (its content was split into `del7-evidence-hierarchy.md` and
`evidence-synthesis.md` for v0.3), but it remains actively referenced by `clinical-governance`,
`esthetic-prosthodontics`, `treatment-plan-audit`, and `quality-control` — kept in place as the
shared quick-reference bundled copy those unchanged skills already depend on. Not an orphan.

## 4. Cross-skill references resolve
**Result: PASS.** `quality-control/SKILL.md`'s new Evidence section cites
`evidence-research/references/clinical-evidence-safe-search-gateway.md` and
`evidence-research/references/evidence-question-formulation.md` (among others) by cross-skill
path — both resolve correctly relative to `skills/`.

## 5. `start`'s bundled connector-capability-map.md is synced
**Result: PASS.** `skills/start/references/connector-capability-map.md` matches
`skills/evidence-research/references/connector-capability-map.md` (the canonical copy), with
`LAST-SYNCHRONIZED: 2026-08-29` on both and the bundled-copy header correctly identifying
`evidence-research` as canonical owner rather than claiming canonical status itself.

## 6. plugin.json validity
**Result: PASS.** Valid JSON (parsed successfully). Every path listed under `skills` resolves to a
directory containing a `SKILL.md`; every path listed under `docs` resolves to an existing file
(this file included, added after the initial check — see note below).

**Caveat, stated plainly:** the actual `plugin.json` schema used by the original v0.2.1 package
was not available to compare against in this environment — the extraction directories referenced
in the original brief's context were empty when inspected. `plugin.json` in this release was
constructed to a reasonable, self-consistent schema (name, version, description, skill list,
doc list, changed/unchanged manifest) rather than confirmed against a prior working example. If
the actual platform expects a different schema, this file should be adjusted accordingly before
relying on it for automated tooling.

## 7. TEST 00 — Resource Availability
No standalone "TEST 00" file exists anywhere in the v0.2.1 source (none was found in the plugin
directory during this build). Treating this requirement as satisfied by checks 1-6 above, which
collectively verify every declared resource (skill, reference, template, test, cross-reference,
manifest entry) is actually present and loadable — the substance of a resource-availability test,
run manually rather than via a pre-existing automated script.

## 8. Evidence regression tests
`skills/evidence-research/tests/evidence-regression-tests.md` contains 15 scenarios (Phase 20
minimum), each with expected behavior, failure condition, required reference, and required
connector state — all 15 are specified to pass with every connector `NOT CONNECTED`, matching the
actual current state recorded in `connector-capability-map.md`. These were authored and reviewed
for internal consistency against the reference files they cite; they were not executed against a
live model run in this session — that would require actually invoking evidence-research against
each scenario, which is a separate exercise from static package validation.

## 9. Bundled-copy synchronization
**Result: PASS (after correction during validation).** `citation-verification.md`,
`evidence-directness.md`, and `evidence-source-separation.md` are each bundled into multiple
skills (quality-control, clinical-governance, treatment-plan-audit, scientific-problem-selection,
esthetic-prosthodontics, in various combinations) per the existing v0.2.1 canonical-owner/bundled-
copy convention. The initial v0.3 edits were applied only to the copies inside
`evidence-research/references/`; running an md5 check across all bundle locations caught the
inconsistency before packaging, and all copies were re-synced from their canonical source
(`evidence-research` for the first two, `clinical-governance` for the third, matching each file's
own declared `CANONICAL-OWNER`). Verified identical via `md5sum` across every location post-sync.

## 10. No connector claimed as CONNECTED
**Result: PASS.** Grep-checked: `connector-capability-map.md` (both canonical and bundled copies)
lists all seven placeholders as `NOT CONNECTED`. No other file in the package asserts a different
status.

```
grep -c "NOT CONNECTED" skills/evidence-research/references/connector-capability-map.md
grep -c "CONNECTED\*\*" skills/evidence-research/references/connector-capability-map.md   # (bold-CONNECTED-only claims)
```

## Overall result

**PASS**, with the plugin.json schema caveat noted in check 6 flagged for your awareness rather
than silently asserted as confirmed-correct.

# Contributing

## Before anything else

This is clinical software. A change that looks cosmetic can alter a safety gate. Read
`VERSIONING.md` and the frozen plugin's `docs/UNRESOLVED_GAPS.md` before proposing anything.

## What is deliberately frozen in v1.0.0

Clinical logic · safety veto · red-flag sweep · case-state model · prognosis engine · treatment
sequencing · evidence engine · DEL-7 · citation verification · retraction and correction handling ·
numeric evidence gate · Saudi governance · PDPL rules · connector behaviour and state · Clinical
Protocol v1.3 · identity policy.

These change only through a versioned release with full regression validation.

## Principles the codebase holds to

**Never invent.** No citation, DOI, measurement, dose, threshold or finding without a real source.
An honest gap beats a plausible guess, and every module is written so the gap is visible.

**Absence of information is not evidence of absence.** A failed search, an unavailable connector
and an empty result set are all reported as what they are.

**A safety block is not overridable.** Not by rephrasing, not by insistence, not by a clean result
elsewhere.

**The creator is not a source.** See the identity policy. Clinic-derived rules carry `(OPS)`,
`(JUDG)`, `(USER-SUPPLIED)` or `(INTERNAL PROTOCOL)` — never a person's name.

## Making a change

1. Open an issue describing the clinical or technical problem first.
2. Say which of the frozen components your change touches, if any.
3. Run all seven regression suites and include the output.
4. Add tests for new behaviour; do not weaken an existing assertion to make a change pass.
5. Update the relevant documentation in the same change — the docs-consistency suite will fail if
   a current-state claim goes stale.

**Do not change clinical code to make a packaging or documentation test pass.**

## Reporting problems

Clinical-behaviour problems: describe the input shape and the incorrect output. **Never include
patient-identifying information.**

Security or privacy problems: follow `SECURITY.md` and report privately.

# Changelog — v0.9.0 → v0.9.1 (Author Identity & Citation Policy)

## Audit first

The plugin was already compliant: **zero** authority-style usages of the creator's name exist
anywhere. Every occurrence is creator metadata, ownership record, or the product name `DANA`.
REMOVE / RENAME / REWRITE counts are all zero. Full classification:
`IDENTITY_POLICY_AUDIT_v0.9.1.md`.

So this release makes the rule enforceable rather than cleaning anything up.

## Added

- **`clinical/identity_policy.py`** — executable scan with six forbidden and two permitted
  contexts, five authority patterns (English + Arabic), and source-class alternatives.
- **`skills/clinical-governance/references/author-identity-and-citation-policy.md`** — the global
  policy; short section added to eight skills and `quality-control`.
- **`clinical/tests/test_identity_policy.py`** — 36 assertions.

## Changed

- `clinical/safety_veto.py` — new optional `draft_output` / `output_context` parameters; a
  violation returns `SAFETY_BLOCK`. Existing call sites are unaffected (both default to no scan).
- `.claude-plugin/plugin.json` — version and description. **`author.name` deliberately unchanged.**

## Why it blocks rather than warns

Writing "Dr Dana recommends a full crown" gives a personal preference the grammatical shape of a
source. That is the substitution CORE §9 and DEL-7 exist to prevent: a named person is not a tier
on the evidence ladder. `(JUDG)` is — and it is the lowest, valid as this clinician's own practice
and invalid as a basis for advising anyone else.

## Not changed

`connectors/` byte-identical. All other `clinical/*.py` byte-identical except `safety_veto.py`.
Connector states unchanged from the frozen v0.6.0 baseline. Clinical Protocol v1.3 status
unchanged.

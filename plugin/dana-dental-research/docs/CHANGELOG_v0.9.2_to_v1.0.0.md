# Changelog — v0.9.2 → v1.0.0 (production release naming)

## Naming

**Display name:** `Dental Research & Clinical Intelligence by Dr. Dana`
**Internal plugin identifier:** `dana-dental-research` — **unchanged**, as instructed. Nothing
technically required renaming it, so it was not renamed.

Updated surfaces: `plugin.json` `displayName` and `description`; new `README.md`; the `start`
skill's product-facing description; the identity-policy reference; the quality-control
allowed-strings line.

## Identity policy — extended, not weakened

The new display name contains the creator's name by design. Before this release the scanner
flagged it, correctly, as a name in a forbidden context. Rather than loosen the rule, the policy
now distinguishes two different things:

- **The product's display name** is exempt in **every** context, including clinical output. An
  assistant may name itself in a clinical answer.
- **The creator-attribution string** (`Designed by Dr. Dana Abu Rawaeh`) remains restricted to
  creator/ownership contexts, per §4.

Only the exact full display phrase is exempt. `Dr. Dana` standing alone is still blocked
everywhere, and because the authority patterns require the name adjacent to the authority verb,
stripping the product name cannot mask a claim: `"<display name>. Dr. Dana recommends a crown."`
is still a violation, and there is a test for exactly that.

Still blocked, unchanged: `Dr. Dana Protocol` · `According to Dr. Dana…` · `Dr. Dana recommends…` ·
`Dana guideline` · `Dana evidence`.

## Tests

`test_identity_policy.py` **36 → 46** (display name clean in all contexts; `Dr. Dana` alone still
blocked; the name cannot mask an adjacent claim; manifest and README assertions).
`test_docs_consistency.py` **30 → 34** (version, display name, internal id, README title and
connector table).

## Unchanged

Clinical logic, evidence logic, connector code, connector states, Clinical Protocol v1.3 naming and
status, and the identity enforcement rules themselves. `connectors/` and every `clinical/*.py`
except `identity_policy.py` are byte-identical to v0.9.2.

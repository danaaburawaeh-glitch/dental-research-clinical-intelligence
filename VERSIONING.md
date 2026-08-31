# Versioning and Update Policy

## Semantic versioning

`MAJOR.MINOR.PATCH`

**PATCH** — documentation fixes, packaging fixes, and safe non-behavioural corrections. No change
to clinical logic, evidence handling or safety gates.

**MINOR** — backward-compatible capabilities: new connectors, new knowledge modules, additional
skills. Existing behaviour continues to work as before.

**MAJOR** — breaking architectural change, a change to a safety contract, or an incompatible
schema.

## The regression rule

**Any change affecting clinical safety, evidence handling, identity policy, regulatory behaviour,
or irreversible-treatment gates requires full regression validation before release.** This holds
whatever the version increment says — a "patch" that touches a safety gate is not a patch.

Regression means all seven suites pass from the packaged artifact, not from the working tree:

```
clinical/tests/test_clinical_layer.py
clinical/tests/test_clinical_completion.py
clinical/tests/test_protocol_approval.py
clinical/tests/test_identity_policy.py
clinical/tests/test_docs_consistency.py
connectors/clinical_trials/tests/test_clinical_trials.py
connectors/sfda/tests/test_saudi_governance.py
```

## v1.0.0 is the validated production baseline

It passed final production validation with **0 P0 blockers and 0 P1 blockers**.

**Do not modify the released v1.0.0 artifact in place.** Future development starts from a *copy*
and receives a new version number. The released `.plugin` and `.zip` and their checksums are the
record of what was validated; editing them destroys that record.

## Update workflow for users

```bash
claude plugin marketplace update dana-dental
claude plugin install dana-dental-research@dana-dental
```

Check the installed version with `claude plugin list`.

## Development workflow for maintainers

1. Copy the frozen source tree to a new working directory.
2. Increment the version in `.claude-plugin/plugin.json` and in the marketplace entry.
3. Make the change.
4. Run all seven regression suites against the packaged artifact.
5. Update the changelog; never rewrite historical changelogs.
6. Package under the new version; never overwrite a previous release.
7. Regenerate checksums.

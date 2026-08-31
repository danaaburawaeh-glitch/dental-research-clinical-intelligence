# Changelog — v0.3 → v0.3.1

**Type:** Patch release. **Scope:** Packaging compatibility repair only. No Evidence Engine
content changed, no new knowledge migrated, no connectors wired.

## What changed

- **Manifest relocated:** `plugin.json` moved from the package root to `.claude-plugin/plugin.json`,
  per the documented Claude Code plugin manifest location
  (code.claude.com/docs/en/plugins-reference, retrieved 2026-08-29). v0.3's root-level
  `plugin.json` was not a location the loader recognizes as plugin configuration — see
  `PLUGIN_MANIFEST_DIFF.md` for the full comparison and the honest limitation on what could be
  verified against v0.2.1 specifically (its actual bytes were not available in this environment).
- **Manifest schema corrected** to match the real documented fields: added `author` and
  `displayName` (previously missing); removed `previous_version`, `skills` (list of default-scan
  directories — redundant with automatic discovery), `changed_in_this_release`,
  `unchanged_in_this_release`, and `docs` (none of these are recognized manifest fields; their
  content now lives in `CHANGELOG_v0.2.1_to_v0.3.md`/this file, not the manifest).
- **Plugin identity:** `name` set to `dana-dental-research`, matching the internal plugin ID you
  identified as the working v0.2.1 identity — see the Step 4 decision note below. `displayName`
  carries the full name "DANA Dental Research & Clinical Intelligence" instead.
- **`.mcp.json` added** at the package root as `{"mcpServers": {}}` — no servers declared, per
  instruction not to add fake ones. This is a valid, documented empty-state file, not a
  placeholder pretending a connector is wired.
- **Evidence Engine content: unchanged.** Every file under `skills/evidence-research/`,
  `skills/quality-control/`, `skills/start/references/connector-capability-map.md`, and every
  `docs/` file from v0.3 is carried forward byte-for-byte except this changelog and the new
  validation documents below.

## Plugin identity decision (Step 4)

You stated the v0.2.1 internal plugin ID was `dana-dental-research`, distinct from v0.3's
`dana-dental-research-clinical-intelligence`. I cannot independently verify which ID v0.2.1
actually used (no v0.2.1 manifest was available to read — see `PLUGIN_MANIFEST_DIFF.md`), so this
decision rests on your statement, not my confirmation. Per your instruction and absent a
documented reason to diverge, `name` is set to `dana-dental-research` in v0.3.1 so that, if
`dana-dental-research` is genuinely how a prior installation identifies this plugin, an update
resolves as an upgrade rather than registering as a separate, second plugin. The full descriptive
name is preserved in `displayName` so nothing about "DANA Dental Research & Clinical Intelligence"
is lost from the user-facing UI.

**If `dana-dental-research` turns out not to be v0.2.1's actual `name` field** (for instance, if
v0.2.1 had no manifest at all and was loaded by directory name, or used a different string), this
decision should be revisited — I flagged the underlying uncertainty rather than treating my
compliance with your stated ID as confirmation that it's correct.

## Connectors

Still all seven `NOT CONNECTED`, unchanged from v0.3. This patch does not touch retrieval
capability in any way.

## Files added in v0.3.1

- `docs/PLUGIN_MANIFEST_DIFF.md`
- `docs/PACKAGE_VALIDATION_v0.3.1.md`
- `docs/POST_INSTALL_VALIDATION.md`
- `docs/CHANGELOG_v0.3_to_v0.3.1.md` (this file)
- `.claude-plugin/plugin.json` (corrected manifest)
- `.mcp.json` (empty, valid)

## Files removed in v0.3.1

- `/plugin.json` (root-level, incorrect location — superseded by `.claude-plugin/plugin.json`)

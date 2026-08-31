# Plugin Manifest Diff — v0.2.1 vs v0.3

## Important limitation — read this first

**I do not have access to v0.2.1's actual `.claude-plugin/plugin.json` file.** I checked
exhaustively before writing this document:

- `/mnt/skills/plugins/dana-dental-research:*` (the read-only mounted v0.2.1 skill content in this
  environment) contains only `SKILL.md` and `references/` files per skill — no manifest, no
  `.claude-plugin/` directory, anywhere.
- Several `/tmp/extract_skill_*` directories reference
  `DANA_Dental_Research_Clinical_Intelligence_v0.2.1` by name, but every one of them is empty
  below an empty `skills/` folder — no files were actually extracted into them.
- No `plugin.json`, `.claude-plugin/`, or `.mcp.json` exists anywhere else on this filesystem.

So this is **not** a diff of two real files. Producing one and presenting it as if I'd extracted
and compared actual v0.2.1 bytes would be exactly the kind of fabrication the DANA governance
principles this plugin itself encodes (never invent, never present an inference as a confirmed
finding) exist to prevent. I'm flagging this plainly rather than quietly working around it.

## What I did instead

I fetched the current official Claude Code documentation for the plugin manifest schema
(`code.claude.com/docs/en/plugins-reference`, retrieved 2026-08-29) and used **that** as the
authoritative reference for what a working manifest looks like, since it describes the actual
schema Claude Code parses — which is a better ground truth than a copy of v0.2.1 I can't verify
either way. Two things follow from this:

1. **The location fix is confirmed correct independently of v0.2.1.** The documentation is
   explicit: `.claude-plugin/plugin.json` is the only recognized manifest location; all other
   plugin directories (`skills/`, `commands/`, `agents/`, etc.) must sit at the plugin root, not
   inside `.claude-plugin/`. A manifest at the package root (what v0.3 shipped) is not a location
   Claude Code's loader recognizes as the plugin manifest at all — v0.3's `plugin.json` was
   effectively inert, not read by the loader as configuration. This alone explains why "packaging
   compatibility repair" is the right framing regardless of what v0.2.1 specifically contained.

2. **I cannot verify specific field values against v0.2.1** (e.g. its exact `author` string, or
   whether it used `displayName` vs relied on the `name`-derived fallback). Where the brief asked
   me to preserve a "known-working" value I could not independently confirm, I used what you told
   me directly (the plugin ID `dana-dental-research`) and otherwise built strictly against the
   documented schema rather than guessing at v0.2.1specifics.

## Comparison: v0.3's `plugin.json` vs the documented schema

| Aspect | v0.3 (as shipped) | Documented schema (code.claude.com) | Verdict |
|---|---|---|---|
| Location | `plugin.json` at package root | `.claude-plugin/plugin.json` | **v0.3 was wrong** — this is the actual defect, confirmed against real docs, not just against v0.2.1 |
| `name` | `dana-dental-research-clinical-intelligence` | Required if manifest present; kebab-case | Valid format, but see Step 4 identity decision below |
| `version` | `"0.3.0"` | Optional string, semantic version recommended | Fine, updates to `0.3.1` |
| `description` | present | Optional string | Fine |
| `previous_version` | present | **Not a recognized field** | Unrecognized fields are ignored by the loader (not an error) but this doesn't do anything — dropped in v0.3.1, superseded by `CHANGELOG.md` |
| `skills` | array of 9 skill directory paths | `skills` field type is `string\|array` of **custom additional** skill directories — the default `skills/` directory is *always* scanned automatically; you don't need to (and shouldn't) enumerate its own default subdirectories here | v0.3's usage was harmless (paths were correct and would have resolved) but redundant/non-standard — dropped in v0.3.1 in favor of relying on default auto-discovery, which is what actually loads all 9 skills |
| `changed_in_this_release` / `unchanged_in_this_release` | present | **Not recognized fields** | Unrecognized-but-ignored; content moved to `CHANGELOG_v0.2.1_to_v0.3.md` where it belongs — dropped from the manifest in v0.3.1 |
| `docs` | array of doc paths | **Not a recognized field** | `docs/` isn't an auto-scanned plugin component directory at all (only `skills/`, `commands/`, `agents/`, `hooks/`, etc. are) — its presence is harmless either way since Claude Code ignores unrecognized top-level fields and un-scanned directories, but listing it in the manifest did nothing functionally — dropped in v0.3.1 |
| `author` | **absent entirely** | Optional object `{name, email, url}` | Gap — added in v0.3.1 using the one piece of real author information available: the Google Drive document owner (personal address; redacted in v1.0.1 for privacy) from the M3/CORE source files read during the v0.3 build. Flagged to you as inferred-from-available-data, not independently confirmed as the intended plugin `author` field. |
| `displayName` | absent | Optional string, human-readable, shown in `/plugin` UI | Added in v0.3.1: `"DANA Dental Research & Clinical Intelligence"`, per your Step 4 instruction |
| `changelog` (as a manifest field) | absent | **Not a field in the documented schema at all** | Your brief asked me to preserve a `changelog` field "known-working" from v0.2.1. I can't confirm v0.2.1 had this as a manifest field, and the current official schema has no such field — Claude Code's own convention is a separate `CHANGELOG.md` file at the plugin root (shown in the standard layout in the docs), which this package already has (`docs/CHANGELOG_v0.2.1_to_v0.3.md` plus the new `docs/CHANGELOG_v0.3_to_v0.3.1.md`). I did not add a fabricated `changelog` key to satisfy the letter of the instruction — doing so would add a field the real loader ignores and that I can't confirm ever existed. Flagging this rather than silently complying or silently dropping the requirement. |

## Fields present only in the documented schema, not used by either package
`homepage`, `repository`, `license`, `keywords`, `metadata`, `defaultEnabled`, `userConfig`,
`dependencies`, and the component-path override fields (`commands`, `agents`, `hooks`,
`mcpServers`, etc.) — none of these are needed for this plugin's actual structure (which uses only
default-location auto-discovery), so none were added speculatively.

## Bottom line

The real defect — manifest at the wrong path — is fixed with high confidence, verified against
official documentation rather than against an unrecoverable v0.2.1 copy. Everything else in this
diff is either a genuine gap (author, displayName — now added) or a field v0.3 added that does
nothing under the real schema (now removed, with its content relocated to where it actually
belongs).

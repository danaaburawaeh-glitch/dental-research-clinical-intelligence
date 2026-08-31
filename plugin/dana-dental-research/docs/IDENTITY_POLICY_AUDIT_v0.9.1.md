# Author Identity & Citation Policy — Audit and Implementation (v0.9.1)

## Step 8 audit — every occurrence, classified

The plugin was **already compliant**. A targeted search for authority-style usage —
`Dana's protocol`, `According to Dr Dana`, `Dr Dana recommends/requires/states` — returns **zero
matches anywhere**, so nothing required REMOVE, RENAME or REWRITE.

| Location | Occurrence | Class |
|---|---|---|
| `.claude-plugin/plugin.json` → `author.name` | `Dr Dana Abu Rawaeh` | **KEEP** — creator metadata (§4) |
| `docs/*` changelogs, migration audits, package validations | author / owner attribution | **KEEP** — ownership metadata |
| `docs/M4_MIGRATION_AUDIT.md` | M4 §9 amendment authority ("or a delegate she names in writing") | **KEEP** — genuine governance ownership, not a clinical source |
| `docs/CLINICAL_PROTOCOL_APPROVAL_RECORD.md` | "the signature line remains for Dr Dana" | **KEEP** — an approval record cannot have an anonymous signatory |
| `clinical/tests/test_protocol_approval.py` | asserts the above | **KEEP** |
| All `skills/**` matches | `DANA` — the product name | **KEEP** — not the person |

**REMOVE: 0 · RENAME: 0 · REWRITE: 0 · KEEP: all.**

Because there was nothing to clean, the work of this release is making the rule **enforceable**, so
it stays true as the plugin grows.

## What was built

**`clinical/identity_policy.py`** — executable. §7 asks for a scan before final output, and a scan
that relies on remembering to run it is not a scan.

- `scan(text, context)` → `{ok, violations, …}`; `assert_clean()` raises.
- Contexts where the name is **forbidden**: `clinical`, `evidence`, `regulatory`, `treatment`,
  `protocol_title`, `patient_facing`. **Permitted**: `creator_metadata`, `ownership_record`.
- **Authority phrasing is flagged in every context, allowed ones included.** "According to Dr Dana,
  crowns are indicated" does not become acceptable by being printed under a credits heading.
- Five authority patterns: attributed recommendation · verb authority · possessive protocol ·
  named protocol · evidence source. Arabic forms included.
- `suggest_source_class()` maps a rule's origin to `(OPS)` / `(JUDG)` / `(USER-SUPPLIED)` /
  `(INTERNAL PROTOCOL)`.

**Wired into `clinical/safety_veto.py`** — `review(..., draft_output=…, output_context=…)` returns
`SAFETY_BLOCK` on any violation. Blocking, not advisory: presenting a person as evidence is a
source-fabrication defect in the same family as a fabricated citation.

**`skills/clinical-governance/references/author-identity-and-citation-policy.md`** — the policy,
loaded by all skills; a short global section added to eight skills and to `quality-control`.

## Two defects found in my own implementation, and fixed

**The name alternation was ungrouped.** `_N = "A|B"` inside `rf"{_N}\s+(?:recommends?|…)"` parses
as `A` OR `B\s+verb`, so *every* bare name matched `verb_authority` — which would have flagged the
legitimate `author.name` in `plugin.json`. Now wrapped in a non-capturing group, with a comment
saying why it must stay that way.

**The permitted creator string was exempt in every context.** §4 permits it only in
creator/ownership contexts; pasting "Designed by Dr. Dana Abu Rawaeh" into a treatment plan is
still a violation. The exemption is now context-scoped, and a test asserts it.

**One design refinement:** all-caps `DANA` is the assistant, mixed-case `Dana` is the clinician.
That casing distinction is the reliable separator, so standalone `DANA` is treated as the product —
except when preceded by an honorific, which makes it the person written in caps
(`DR DANA RECOMMENDS…` is correctly blocked).

## Tests

`clinical/tests/test_identity_policy.py` → **36/36**, covering all 10 required scenarios plus
invariants and a whole-plugin sweep of every `skills/**.md`.

Two files are excluded from the sweep because they *state* the policy and must quote the forbidden
phrasings in order to forbid them — the policy reference and the quality-control section. That is
not a loophole: a paired assertion confirms each still contains the prohibition it quotes, so
neither can quietly become a file that merely uses the forbidden wording.

# Changelog — v1.0.0 → v1.0.1 (privacy patch)

Privacy-only patch. **No clinical logic, evidence logic, connector code, connector state, Clinical
Protocol v1.3 content, safety rule, identity policy or scientific content was changed.**

## Why

The maintainer's personal email address appeared in tracked repository content and would have been
published. v1.0.0 remains the validated functional baseline; v1.0.1 is that baseline with the
address removed.

## Changed

**Structurally required contact fields** — replaced with the GitHub noreply address
`318165261+danaaburawaeh-glitch@users.noreply.github.com`:

- `.claude-plugin/plugin.json` → `author.email`
- marketplace manifest → `owner.email` and the plugin entry's `author.email`

**Historical documents** — the literal address redacted, the information it carried preserved:

- `docs/CONNECTOR_SECURITY.md` — the note that the address was *deliberately not* placed in
  `.env.example`, `NCBI_EMAIL` or `CROSSREF_MAILTO` is unchanged; only the address itself is gone.
- `docs/PACKAGE_VALIDATION_v0.3.1.md` — the caveat that `author` was inferred from Google Drive
  owner metadata rather than a confirmed declaration is unchanged.
- `docs/PLUGIN_MANIFEST_DIFF.md` — the same provenance note is unchanged.

**Version** — `1.0.0` → `1.0.1` in the plugin manifest and the marketplace entry.

**One test assertion** — `test_docs_consistency.py` check 28 now asserts version `1.0.1`. This is
the documentation-consistency test the packaging brief permits changing; no clinical or safety
assertion was touched.

## Not changed

Every module under `clinical/` and `connectors/`, all nine skills, every reference file, all
connector states, and Clinical Protocol v1.3. Verified by diff against v1.0.0.

## v1.0.0 artifacts

Preserved unchanged outside the distribution repository and **not distributed**, because their
manifest still contains the personal address. v1.0.0 was not overwritten.

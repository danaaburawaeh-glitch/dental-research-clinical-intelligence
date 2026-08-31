# Distribution Validation — v1.0.0

> **HISTORICAL RECORD**
> This document relates to the original v1.0.0 production/distribution validation.
> The current public release is **v1.0.2**.

Packaging and distribution audit for **Dental Research & Clinical Intelligence by Dr. Dana**,
plugin identifier `dana-dental-research`, version 1.0.0.

No clinical logic, connector code, Clinical Protocol content, identity policy or regression test
was modified. The plugin is included byte-for-byte as validated.

---

## Results

| Check | Result |
|---|---|
| GITHUB REPOSITORY | **PASS** |
| PLUGIN PACKAGE | **PASS** |
| MARKETPLACE MANIFEST | **PASS** |
| README | **PASS** |
| INSTALLATION GUIDE | **PASS** |
| QUICK START | **PASS** |
| TERMS | **PASS** |
| DISCLAIMER | **PASS** |
| SECURITY SCAN | **PASS** |
| IDENTITY POLICY | **PASS** |
| VERSION CONSISTENCY | **PASS** |
| CONNECTOR STATE | **PASS** |
| CLINICAL REGRESSION | **PASS** |
| RELEASE ZIP | **PASS** |

**DISTRIBUTION BLOCKERS: 0**

---

## Evidence

**Repository structure.** All 12 root files and all 7 `docs/` files present. 0 broken relative
links across every repository-level markdown file. Total 2.4 MB.

**Marketplace manifest.** `claude plugin validate` → passed. Schema and field set were verified
against the official `claude-plugins-official` marketplace on this machine and against
`claude plugin marketplace --help`, not from memory. Canonical location is
`.claude-plugin/marketplace.json` — the brief's suggested `marketplace/marketplace.json` is not
where Claude Code looks, so the canonical path was used. Fields used are all attested in the
official directory: `name`, `displayName`, `description`, `version`, `author`, `category`,
`keywords`, `source`. No unsupported field was invented.

**Plugin discovery — tested, not assumed.** The documented install path was executed:
`claude plugin marketplace add <repo>` registered `dana-dental` and resolved the source to this
directory; `claude plugin marketplace list` confirmed it. The marketplace was then removed, leaving
the machine as found. The install command was not run, to avoid disturbing the existing
installation.

**Version, identifier and display-name consistency.** 10/10 checks: plugin id
`dana-dental-research` in both manifests; version `1.0.0` in both; display name
`Dental Research & Clinical Intelligence by Dr. Dana` in both and as the README title; marketplace
`source` resolves to a real directory containing a valid plugin manifest; all 8 required keywords
present.

**Clinical regression from the shipped artifact.** All seven suites run against the plugin
extracted from `releases/…v1.0.0.zip`: 46/46 · 34/34 · 24/24 · 66/66 · 60/60 · 50/50 · 50/50 —
**330 assertions, 0 failures.**

**Connector state.** Verified from the extracted ZIP, unchanged from the frozen baseline:
`~~literature`, `~~systematic-reviews`, `~~journal-access`, `~~clinical-trials` CONNECTED;
`~~clinical-guidelines`, `~~manufacturer-ifu` NOT CONNECTED; `~~regulatory-saudi`
NOT CONNECTED — AUTH REQUIRED. Clinical Protocol v1.3 APPROVED. P2 register intact: G01, G02, G03,
G04.

**Security scan.** 0 credential literals · 0 private keys or token blobs · no `.env` (only
`.env.example`, which contains placeholders) · 0 personal filesystem paths in shipped files · 0
patient-identifying data patterns. The SFDA connector reads all configuration from environment
variables; its single hard-coded URL is the public developer portal.

**Identity policy.** 196 files scanned. **0 genuine violations.** The plugin's own validated suite
passes 46/46.

*Note on method:* a first pass reported 9 hits, all from applying *clinical* context to changelogs,
audits and approval records — which are ownership documents where the creator's name is permitted
(an approval record cannot have an anonymous signatory). Re-scanned with the correct context per
document class, the count is 0. Four documents that quote the forbidden phrasings in order to
prohibit them — the policy reference, the quality-control section, the identity audit and two
changelogs — are excluded on the same basis the plugin's own test excludes them.

**Release ZIP.** Both artifacts pass `unzip -t`. The ZIP contains 224 files with **0** cache,
`.DS_Store`, `.pyc`, log or credential entries, and no previous plugin version. Extracted, it
validates as a plugin and passes full regression.

**Checksums.** `releases/SHA256SUMS.txt`, verified with `shasum -a 256 -c` → both OK.

The `.plugin` checksum `66dd06ea…20708cb5` matches the frozen artifact byte-for-byte; it was copied
verbatim, never rebuilt. The `.zip` carries a different checksum because the archive is rebuilt —
the contents are the same plugin, which the regression run from the extracted ZIP confirms. This is
stated in `SHA256SUMS.txt` so it cannot be mistaken for a discrepancy.

---

## One environment finding, recorded rather than smoothed over

Between the production-release step and this packaging step, the release folder produced in the
previous turn was reorganised outside this session into
`DANA-v1.0.0-DEVELOPMENT-REFERENCE.zip`. The surviving artifact
(`66dd06ea…`) is the earlier of two v1.0.0 builds. It differs from the final release build only in
that it does not carry `RELEASE_NOTES_v1.0.0.md` and `PRODUCTION_READINESS_v1.0.0.md` inside
`plugin/docs/` — code, skills, connectors and tests are identical, confirmed by the full regression
run above.

Those two documents belong at repository level in this structure anyway, and are present at
`docs/RELEASE_NOTES_v1.0.0.md` and in this audit. **No frozen file was edited to compensate.**

---

## Known non-blocking items carried into distribution

Not hidden, and stated in the README, release notes, capabilities documents and the plugin's own
gap index.

| ID | Item | Effect |
|---|---|---|
| G01 | Product/IFU register not populated | Gates clinical use of materials |
| G02 | Laboratory register not populated | Gates prescribing an indirect restoration |
| G03 | Clinical Protocol signature outstanding | Content approval complete; signing reserved to the owner |
| G04 | SFDA authentication required | Saudi status returns *requires verification* |

24 further P3 items and the 9-entry post-v1.0 enhancement register are preserved in the plugin's
`docs/UNRESOLVED_GAPS.md`. None was closed or deleted.

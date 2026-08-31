<!--
REFERENCE-ID: deferred-knowledge-dependencies
VERSION: 0.3
CANONICAL-OWNER: evidence-research
LAST-SYNCHRONIZED: 2026-08-29
-->

# Deferred Knowledge Dependencies

Loaded by: evidence-research (reference only — not part of the active workflow chain). This file
exists so a dependency the authoritative source material assumes, but that v0.3 does not migrate,
is never silently forgotten or silently reconstructed.

## CLINICAL-PROTOCOL-08

**Status:** `DEFERRED_TO_CLINICAL_PROTOCOL_MIGRATION`

**Referenced by:** authoritative M3 §3.2 (rule 4, the (OPEN) marker), §3.4 (citing the clinic
protocol; مسودة عمل vs معتمدة status), §10 (reuse of verified references from "file 08, Appendix
A").

**What was NOT migrated in v0.3, and why:** M3 assumes a specific external artifact — "the clinic
protocol, file 08" — with its own numbered structure, an Arabic draft/approved status distinction,
and a pre-verified reference appendix that downstream modules are meant to cite by number rather
than re-derive. No file with this identity, structure, or content was located in the plugin
architecture during the v0.3 Phase 1 audit. Rather than guess at what file 08 is, invent its
contents, or quietly drop the principles it carries, this dependency is recorded as deferred.

**What WAS preserved from the underlying principles** (because they don't actually depend on file
08's specific mechanics):

- An unresolved/open item is never silently resolved by inference, never has a side chosen for it,
  and is never allowed to pass silently — see del7-evidence-hierarchy.md §2 rule 4.
- A verified reference already held elsewhere in the system may be reused rather than re-derived,
  but only with its provenance and verification status preserved (VERIFIED / PARTIALLY VERIFIED /
  UNVERIFIED, and the date it was verified) — see citation-verification.md.
- Where a locally-held or (JUDG) number conflicts with a governing IFU, the IFU governs within its
  own domain — see del7-evidence-hierarchy.md §4.

**What was explicitly left out**, pending the actual Clinical Protocol migration:

- The "file 08" naming and numbering itself.
- The Appendix A reference-reuse mechanics (citing by reference number against a specific
  external appendix that isn't part of this plugin).
- The مسودة عمل / معتمدة (draft / approved) status labels and the rule to always disclose that
  status when citing the protocol.
- Any file-specific citation reuse logic tied to that appendix.

**Action:** Resolve during Clinical Protocol migration, not v0.3. When that migration happens,
confirm first whether "file 08" is an actual, locatable document (in which case it should be read
and migrated properly, per this same audit discipline — not reconstructed from memory) or legacy
language predating the plugin's module split (in which case this entry should be closed as
DEPRECATED with a note, not silently deleted).

## Adding further entries

Any future migration phase that encounters a source reference to an artifact not present in the
plugin architecture should add an entry here in the same shape — status, referenced-by, what was
and wasn't preserved, and the action required to resolve it — rather than silently dropping or
silently reconstructing the dependency.

## STATUS UPDATE — 2026-08-31 (v0.9.0)

The clinic protocol dependency described above is **resolved**. **Clinical Protocol v1.3 is
APPROVED**; all eight Appendix C (OPEN) items are closed and the (OPEN) tag no longer appears in
it. The rule to disclose مسودة عمل status **no longer applies to this protocol** — it stands only
as a general rule, should any future clinic document be issued in draft.

Cite **v1.3** as approved clinic policy. **v1.2 is historical and must not be cited as current.**
Closure record: `docs/CLINICAL_PROTOCOL_APPROVAL_RECORD.md`.

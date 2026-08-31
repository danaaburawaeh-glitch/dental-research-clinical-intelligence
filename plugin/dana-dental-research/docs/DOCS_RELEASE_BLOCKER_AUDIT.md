# Documentation Release-Blocker Audit — v0.9.2

Scope: eliminate the single P1 blocker from final v1.0 production validation. Documentation only.
No clinical logic, connector code, Evidence Engine, Saudi governance, identity policy or Clinical
Protocol content was touched.

## The blocker

`docs/UNRESOLVED_GAPS.md` gap 4 read, in the present tense:

> **"No connector is actually wired.** Every one of the seven `~~` placeholders remains
> `NOT CONNECTED`."

False as of v0.4.5. Four connectors are wired, live-validated and CONNECTED. The file's title was
*"Unresolved Gaps — v0.3"* and v0.3-era entries carried no historical marking, so the statement
read as current and contradicted `connector-capability-map.md`.

Severity P1 rather than P2 because this file is the canonical shipped index of what is still
broken. A reader consulting it would conclude the evidence layer is inert. It is the same defect
class corrected in v0.4.5.1, when stale "no network access" text contradicted validated
connectors — applying that precedent consistently makes it a blocker.

## What changed

**Historical sectioning.** The file is now Part A (current release state) and Part B (historical /
resolved). Part B opens by stating that nothing in it is a claim about the current system. No
historical fact was deleted; 13 entries were moved and labelled **RESOLVED**, **SUPERSEDED** or
**HISTORICAL**.

**Connector status corrected.** Part A opens with the authoritative table — `~~literature`,
`~~systematic-reviews`, `~~journal-access`, `~~clinical-trials` CONNECTED; `~~clinical-guidelines`,
`~~manufacturer-ifu` NOT CONNECTED; `~~regulatory-saudi` NOT CONNECTED — AUTH REQUIRED. Crossref is
stated as metadata and citation verification only, never full text. The false claim survives solely
as **H02**, explicitly marked resolved *and* recorded as having been the P1 blocker.

**Clinical Protocol gap resolved.** Old gap 1 (CLINICAL-PROTOCOL-08 / missing protocol dependency)
is now **H01 — RESOLVED**, superseded by Clinical Protocol v1.3 APPROVED. The historical
explanation is preserved, with the resolution stated: the approved protocol carries the
verified-reference appendix and a real draft/approved status, which is what M3 anticipated.

**Numbering repaired.** Unique IDs throughout — `G01`–`G28` current, `H01`–`H13` historical. The
duplicate `14` is gone. The NCT-linkage item, previously triplicated as gaps 15, 22, 31 and 38, is
now the single **G06**, with the prior duplication acknowledged in place.

**Register IDs renamed.** The post-v1.0 enhancement register used `P1`–`P9`, which collided with
the `P0`–`P3` severity scheme and made "P1" ambiguous between *release blocker* and *enhancement
one*. Renamed `E1`–`E9`. This ambiguity was not the blocker but it made the blocker harder to see.

**Classification.** Every current gap is P2 or P3. **4 P2** (G01 Appendix B empty, G02 Annex E
empty, G03 signature outstanding, G04 `~~regulatory-saudi` AUTH REQUIRED) and **24 P3**. No current
gap is P0 or P1.

## Additional findings from the package-wide consistency scan

The scan required by §6 surfaced two further stale titles, not previously flagged:

- `docs/EVIDENCE_ENGINE_ARCHITECTURE.md` — titled *"— v0.3"*
- `docs/PACKAGE_VALIDATION.md` — titled *"— v0.3"*

Both are legitimately historical, but their titles made them look current. Each now carries
`(HISTORICAL)` in the title and a banner pointing to the current sources. Bodies unchanged.

Everything else passed: no unmarked stale current-state claim anywhere in `docs/` or `skills/`; the
two capability-map copies agree with each other and with Part A; no reference calls the Clinical
Protocol a draft; Crossref is never described as full text.

## Errors I made while writing the consistency test, and fixed

- `check 24` used an unanchored `##.*P[01]` which matched the literal `G##` in prose. Anchored to
  headings.
- `check 04` required an inline status label within 180 characters of each historical ID; H12 and
  H13 relied on their section heading alone. Rather than loosen the test, the two entries now carry
  inline `— HISTORICAL` labels, which is better for a reader landing mid-file.

## Verification

`clinical/tests/test_docs_consistency.py` → **30/30**. It enforces the rule that produced this
blocker: a historical statement must be marked historical, and every current operational reference
must reflect current reality. It cross-checks the gaps file against both capability-map copies, so
the two cannot drift apart again silently.

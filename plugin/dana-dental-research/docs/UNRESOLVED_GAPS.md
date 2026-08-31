# Unresolved Gaps — Current Release (v0.9.2)

**Two parts.** Part A is the current state of the system. Part B is history — entries that were
true of an earlier release and are preserved for the record. **Nothing in Part B is a claim about
the system as it stands today.**

Restructured in v0.9.2 to remove a release blocker: the previous edition mixed v0.3-era entries
with current ones under a "v0.3" heading, so a stale entry ("No connector is actually wired")
read as a current system-state claim. It was false and contradicted
`connector-capability-map.md`. See `DOCS_RELEASE_BLOCKER_AUDIT.md`.

Gap IDs are `G##` and unique. The post-v1.0 register uses `E##` — renamed from `P1–P9` in v0.9.2,
because those IDs collided with the `P0–P3` severity scheme and made "P1" ambiguous between
"release blocker" and "enhancement one".

---

# PART A — CURRENT RELEASE STATE

## A.0 Connector status — the authoritative current state

Canonical source: `skills/start/references/connector-capability-map.md` (and its
`evidence-research` twin). Reproduced here so this index cannot drift from it again.

| Placeholder | Current status |
|---|---|
| `~~literature` | **CONNECTED — PubMed/NCBI** |
| `~~systematic-reviews` | **CONNECTED — PubMed filtered retrieval** |
| `~~journal-access` | **CONNECTED — METADATA/CITATION VERIFICATION via Crossref** |
| `~~clinical-trials` | **CONNECTED — ClinicalTrials.gov API v2** |
| `~~clinical-guidelines` | NOT CONNECTED |
| `~~manufacturer-ifu` | NOT CONNECTED |
| `~~regulatory-saudi` | NOT CONNECTED — AUTH REQUIRED |

`~~journal-access` is **metadata and citation verification only**. Crossref does not provide full
text and must never be described as full-text access.

Runtime availability is environment-dependent: `CONNECTED` means a real request from the packaged
code succeeded in a real environment, never that any given request will succeed. Check the
returned `status` at invocation.

## A.1 Clinical Protocol status

**Clinical Protocol v1.3 — APPROVED** (2026-08-31). All eight Appendix C items closed; the
`(OPEN)` tag no longer appears in it. v1.2 is preserved as historical and must not be cited as
current. Record: `CLINICAL_PROTOCOL_APPROVAL_RECORD.md`.

---

## A.2 Current gaps — P2 (non-blocking improvements)

**G01 · Clinical Protocol Appendix B is empty.** The product/IFU register carries no entries.
§2.4 forbids using a product before its exact trade name, manufacturer and IFU version are
recorded there with the IFU attached. Blocks clinical use of materials; does not block release.

**G02 · Clinical Protocol Annex E is empty.** No Laboratory of Record is registered, and no
session-time allocations are recorded. §8 requires a Laboratory of Record before an indirect
restoration is prescribed. Blocks that prescribing step; does not block release.

**G03 · Clinical Protocol v1.3 signature not executed.** Content approval is complete and
evidenced; the signature line remains for the protocol owner. A professional act that cannot be
delegated to this system.

**G04 · `~~regulatory-saudi` is NOT CONNECTED — AUTH REQUIRED.** The SFDA connector is implemented
against the real `developer.sfda.gov.sa` programme, but SFDA discloses gateway URLs only to
registered applications and no credentials exist in this environment. Every unavailable outcome
maps to `REQUIRES VERIFICATION`; there is no code path to "not approved". Saudi Arabia is the
jurisdiction baseline, which is why this sits at P2 rather than P3. Steps to connect:
`SFDA_CONNECTOR_VALIDATION.md`.

---

## A.3 Current gaps — P3 (post-v1.0 enhancements and accepted limits)

### Evidence and connectors

**G05 · Registry coverage is incomplete, and this limits absence claims.** Registration
requirements vary by jurisdiction, funder and study type; much dental research — especially
smaller university-run and non-interventional work — is never registered. Absence from
ClinicalTrials.gov is therefore **weaker** evidence of absence than absence from PubMed, and must
never be stated as "no trials exist". Other registries (ISRCTN, EU CTR, ANZCTR, CTRI, and
registries relevant to Saudi practice) are not wired. → E9

**G06 · PubMed `<DataBankList>` / NCT linkage is one-directional.** PubMed deposits trial
registrations in a structured `<DataBankList>` the parser does not extract, so an NCT ID in a
publication is detected only from title or abstract text. The registry-side direction (the trial's
own reference list) is unaffected and is the stronger signal. Carried forward from Phase B through
Phases C and D by instruction — all three were forbidden from modifying the validated PubMed
connector. → E8
*(This item previously appeared three times, as gaps 15, 22, 31 and 38. Consolidated in v0.9.2.)*

**G07 · Registry-reported results are captured but not appraised.** `registry_results` carries
participant flow, baseline characteristics, outcome measures and adverse events structurally with
a not-peer-reviewed label. Nothing appraises internal validity and no risk-of-bias assessment is
applied. Deliberate — they are never converted into a journal-quality appraisal — but a user
asking "are these results any good?" gets no automated answer.

**G08 · Live 429/5xx behaviour is unproven against the real services.** Retry logic is proven
against a mocked network. The real APIs did not rate-limit or fail during validation, and
deliberately provoking those states against public NLM services would be abusive. The self-imposed
rate limits are conservative rather than derived.

**G09 · Selective-publication detection is enabled but not automated.** The data needed to spot a
completed-but-unpublished trial is retrievable (status + linkage + PubMed) and the gateway routes
such questions, but no routine performs the comparison end to end.

**G10 · Rate-limiter behaviour under concurrent calls is unexercised.** Only sequential,
one-command-per-invocation use has been tested. Low priority for the current usage pattern; worth
revisiting if retrieval ever becomes batched or parallel.

**G11 · Crossref's single-record vs list rate-limit split is not documented by Crossref.** The
connector's separate token buckets are a conservative internal design choice, not a confirmed
Crossref policy distinction. See `CROSSREF_CONNECTOR_SPEC.md`.

**G12 · Deduplication's title+year fallback threshold is untuned.** `titles_match`'s 0.90
token-overlap default was validated against a small hand-built set plus one real example — enough
to confirm the logic, not enough to claim the threshold is optimal for dental naming conventions.

**G13 · Journal publisher APIs were never surveyed per publisher.** `~~journal-access` is scoped
to Crossref-style metadata resolution; direct Elsevier/Wiley/Springer integrations would need
their own research pass. → E7 territory

**G14 · `~~clinical-guidelines` has no identified provider.** Guideline bodies are fragmented by
specialty and country and no aggregating API has been found. The least-developed of the seven
placeholders. → E6

### Saudi governance

**G15 · SFDA response schema is unverified.** `sfda/models.py` maps candidate field names
defensively and preserves the raw record, because the real field list is visible only to a
registered app. A `None` field means "the parser could not find it", not "SFDA does not provide
it". Fold the observed schema in once credentials exist.

**G16 · Four Saudi bodies have no connector.** SCFHS (scope, titles, classification), MOH
(facility licensing, advertising), SDAIA/PDPL (data) and CST (electronic advertising) are named
and routed, but every claim in those domains is `REQUIRES VERIFICATION` with no lookup available.
SFDA is one of six bodies M4 §2 names. **Deferred by decision (2026-08-31), not by oversight** —
the governance layer functions without them, naming the responsible body as M4 §2 requires.
→ E2–E5

**G17 · SFDA SOURCE-UPDATE-CONFLICT is unresolved in CORE/M3.** CORE and M3 state SFDA has no
public queryable database; a real OAuth-secured API exists at `developer.sfda.gov.sa`. Recorded in
the capability map and `CONNECTOR_REQUIREMENTS.md`; the source documents were not corrected
(out of scope — M4 territory). Registration against the API has not been performed.

**G18 · Saudi governance rules are documentary, not executable.** Only the SFDA regulatory-state
machine is enforced in code; the rest lives in reference files the model must read and apply. The
tests assert the rules are present in the shipped files, which catches deletion but cannot catch a
model failing to apply them.

**G19 · M4 §9 amendment authority and incident log are not encoded.** M4 requires a logged
amendment trail and a maintained incident log. The plugin has versioned changelogs but neither. A
governance-process gap the plugin cannot enforce inside an output. See `M4_MIGRATION_AUDIT.md`.

**G20 · M4 §10 and §11.2–11.6 are deferred.** Team onboarding, shared-project entry rules,
project-knowledge vs thread separation, escalation paths. Real M4 rules, but they govern how a
clinic team operates a workspace rather than being decision gates applied to an output.

### Clinical layer

**G21 · The clinical layer supplies structure and gates, not clinical content.**
`treatment_plan.py` enforces sequencing and phase shape but invents no procedure, interval,
material or exit criterion — M2 V0.4 carries no thresholds by design and neither does this code.

**G22 · No prosthodontic textbook knowledge base exists.** The system reasons correctly *about* a
case; it has no textbook content. The Rosenstiel source is **not available** in the project (the
registry maps it to a conversion prompt; the converted file was never produced). Any such content
must be authored or licensed — never reconstructed from memory. See
`CLINICAL_SOURCE_INVENTORY_v0.8.0.md`.

**G23 · Prognosis determinants are recorded, not measured.** The engine evaluates what the
clinician entered; it can detect a missing determinant but not a wrong one. Its output is exactly
as good as the case record.

**G24 · The red-flag sweep cannot be auto-populated.** It requires explicit answers and refuses to
infer them from the case record — correct, but it means the sweep is a real step the user must
perform, not a background check.

**G25 · The adverse-finding list is fixed and short.** Eleven findings, each mapped to the axes it
bears on. Ad-hoc labels are rejected by design; extending the list is a deliberate change.

**G26 · Scope is two disciplines.** Fixed Prosthodontics and Esthetic Restorative Dentistry.
Everything else returns `OUT_OF_SCOPE`. Widening needs its own minimum datasets from M2
§1.2/§1.3/§1.6/§1.7/§1.9.

**G27 · No implant, endodontic, periodontal-surgical or orthodontic knowledge.** Referral triggers
are documented (Clinical Protocol §1.2/§7.3) but the system carries no knowledge in those domains
and must not appear to.

**G28 · M5 is not migrated.** Research, academic writing and teaching. Deferred by instruction
through Phases C, D and clinical completion.

---

## A.4 Post-v1.0 enhancement register

Deferred by decision, not oversight. **None blocks v1.0.** IDs renamed from `P#` to `E#` in
v0.9.2 to avoid collision with the P0–P3 severity scheme.

| # | Enhancement | Why deferred |
|---|---|---|
| E1 | `~~regulatory-saudi` live connection (SFDA credentials) | Needs a registered SFDA application; unavailable outcome already maps correctly to REQUIRES VERIFICATION (G04) |
| E2 | SCFHS live connector — scope of practice, specialist titles, classification | G16 |
| E3 | MOH live connector — facility licensing, health advertising controls | G16 |
| E4 | SDAIA / PDPL live connector — data-protection requirements | G16 |
| E5 | CST live connector — electronic and social advertising | G16 |
| E6 | `~~clinical-guidelines` connector | No aggregating API identified (G14) |
| E7 | `~~manufacturer-ifu` connector | No source wired; IFU content must not be paraphrased from memory |
| E8 | PubMed `<DataBankList>` NCT extraction | Requires modifying the validated PubMed connector (G06) |
| E9 | Other trial registries (ISRCTN, EU CTR, ANZCTR, CTRI) | Registry coverage (G05) |

---

# PART B — HISTORICAL / RESOLVED

**Everything below describes an earlier release.** None of it is a claim about the current system.
Where an entry has been overtaken, the current position is stated with it.

## B.1 RESOLVED

**H01 · CLINICAL-PROTOCOL-08 / missing protocol dependency — RESOLVED.**
*Original (v0.3):* M3 assumed an external artifact ("file 08") with its own verified-reference
appendix and draft/approved status labels; it could not be located in the plugin architecture, and
was deferred rather than migrated or deprecated.
**Resolution: Clinical Protocol v1.3 — APPROVED** (2026-08-31). The approved protocol supersedes
the unresolved dependency: it carries the verified-reference appendix (R1–R8, Crossref-verified)
and its status is `معتمدة`/APPROVED, so the draft/approved distinction M3 anticipated now has a
real referent. The historical context remains useful in
`skills/evidence-research/references/deferred-knowledge-dependencies.md`, which records the same
resolution.

**H02 · "No connector is actually wired" — RESOLVED, and the entry was FALSE as of v0.4.5.**
*Original (v0.3):* every one of the seven `~~` placeholders was `NOT CONNECTED`; Phase 17 had
established that real APIs existed but none had been wired.
**Resolution:** four connectors are wired, live-validated and CONNECTED — see A.0. This entry
survived unamended into v0.9.1 and was the P1 release blocker found in final validation, because
under a "v0.3" heading it read as a current claim. Corrected in v0.9.2.

**H03 · Three connectors reach CONNECTED — RESOLVED in v0.4.5.** `~~literature`,
`~~systematic-reviews` and `~~journal-access` were live-validated on 2026-08-30/31. Superseded by
A.0, which also records `~~clinical-trials`.

**H04 · Retraction/correction metadata is not parsed — RESOLVED in v0.4.1/v0.4.2, entry corrected
in v0.4.5.2.** The original entry stated the opposite of the truth and was stale from v0.4.1.
Current state: PubMed and Crossref retraction/correction metadata is parsed with directional
RefType semantics; `EvidenceRecord` carries `publication_status`, `is_retracted`, `is_corrected`,
`related_notices`, `retraction_source`, `record_role`; `retraction_gate.py` excludes retracted
articles from synthesis and routes notices to `flagged`. The real residual limitations were
re-filed and remain current — see G07 (results not appraised) and the retraction caveats below.

*Retraction caveats that remain true (kept here because they belong with H04's subject matter):*
detection is only as good as upstream indexing and no independent retraction database is wired, so
absence of a flag is not evidence a paper is unretracted · corrections are flagged, never
auto-resolved · retraction status is known only after `fetch`, never from a search result ·
expressions of concern are deliberately not force-classified · Crossref's generic `relation` field
is deliberately unused for retraction signalling.

**H05 · `~~clinical-trials` not built — RESOLVED in v0.5.0.** ClinicalTrials.gov API v2,
live-validated 2026-08-31 (`LIVE_CLINICALTRIALS_VALIDATION.md`).

**H06 · Minimum prosthodontic operational knowledge missing — RESOLVED in v0.8.0.** Four
references built from the approved Clinical Protocol plus CORE/M1/M2. The Rosenstiel limitation is
current and re-filed as G22.

**H07 · Prognosis recorded but not assessed — RESOLVED in v0.8.0.** `clinical/prognosis.py` —
categorical only, five axes, enforced ordering, `UNDETERMINED` blocking irreversible planning. The
residual limitation is current and re-filed as G23.

**H08 · Clinic protocol was a WORKING DRAFT — RESOLVED in v0.9.0.** All eight Appendix C items
closed; v1.3 APPROVED. The two surviving use-gates are current and re-filed as G01 and G02, and
the signature as G03.

## B.2 SUPERSEDED

**H09 · Semantic Scholar rate limit inconsistently documented — SUPERSEDED.** Semantic Scholar is
not part of the connector stack; the concern no longer applies to any shipped component.

**H10 · "Clinical Evidence Safe Search" naming vs the real connector landscape — SUPERSEDED.**
The gateway was resolved architecturally as a behavioural layer, and four real connectors now sit
behind it. The original concern — that no specific product occupied the gateway role — is answered
by the connectors themselves.

**H11 · Regional trial registries not evaluated — SUPERSEDED by G05/E9**, which state the same
limitation in current terms.

## B.3 HISTORICAL

**H12 · `web_fetch` request-caching behaviour — HISTORICAL.** A characteristic of the original v0.4 build
environment, not of the target APIs. It affected what could be verified live in that session and
has no bearing on connector correctness. No longer load-bearing.

**H13 · The original v0.3 closing statement — HISTORICAL.** read: *"None of these block the v0.3 package from
being valid and usable in its current, fully NOT CONNECTED state."* True of v0.3. **Not true of
v0.9.2** — see A.0.

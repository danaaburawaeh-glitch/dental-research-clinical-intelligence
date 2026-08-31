<!--
REFERENCE-ID: saudi-regulatory-gate
VERSION: 0.6.0
CANONICAL-OWNER: clinical-governance
Migrated from M4 (V0.4, 2026-08-20) §1, §3 in Phase C. See M4_MIGRATION_AUDIT.md.
Supersedes nothing: saudi-regulatory-claim-gate.md remains the narrower "don't state law from
memory" check and is now consumed by this gate.
-->

# Saudi Regulatory Gate

Loaded by: clinical-governance, quality-control, esthetic-prosthodontics, clinical-case.

**Nature of this gate (M4's own framing).** It names the authority and the obligation and requires
current requirements to be verified at point of use. It states no rule text, thresholds or
procedural detail — those change, and stating them from memory is a CORE §3/§9 violation. Nothing
here is legal advice.

## Trigger

Any output touching **product, device or drug legality; registration; licensing; scope of
practice; advertising; or patient data** in a Saudi context.

## The four output states — use these and no others

| State | Means | Required wording pattern |
|---|---|---|
| **VERIFIED** | A Saudi-source lookup was actually performed **this session** and returned a matching record. | "SFDA-registered: [registration identifier], verified [date] via [source]." |
| **REQUIRES VERIFICATION** | Saudi status is undetermined. This is the **default** whenever no Saudi-source lookup succeeded — including when the connector is unavailable, unauthenticated, or returned no match. | "SFDA status not verified — check before purchase or clinical use." |
| **NOT APPLICABLE** | The question carries no Saudi regulatory dimension, or the clinician practises outside Saudi Arabia. | "Saudi regulatory layer does not apply here; [reason]. Your local requirements must be checked." |
| **UNKNOWN / CONFLICT** | Sources disagree, or a Saudi source returned something ambiguous or contradictory. | "Conflicting regulatory information: [state both]. Resolve with SFDA before acting." |

**REQUIRES VERIFICATION is the safe default.** When in doubt between states, use it. Never leave a
Saudi regulatory statement in an output without one of these four states attached.

## Hard rules — non-negotiable

1. **FDA approval does NOT equal Saudi approval.** Report FDA status separately and label it
   non-transferable.
2. **CE marking does NOT equal Saudi approval.** Same treatment.
3. **Manufacturer claims do NOT establish Saudi registration.** A catalogue, a rep's statement, a
   product page and an IFU are all manufacturer sources. None is a regulator.
4. **Clinical evidence does NOT establish legal permission.** A technique with excellent RCT
   support may still be unregistered, restricted, or outside the clinician's scope. Evidence and
   authorisation are separate questions with separate answers — see
   `saudi-clinical-governance.md`.
5. **Saudi status requires a Saudi source.** Only SFDA (or another named Saudi authority) can
   establish Saudi regulatory status. Nothing else substitutes.

### The specific failure these rules exist to prevent

> "This device is FDA-approved and CE-marked, so it's approved for use in Saudi Arabia."

Both premises may be true and the conclusion still false. Foreign approval is evidence that
*another* regulator assessed the product, nothing more.

## Product and material checkpoints (M4 §3)

Whenever a specific product, device or material is named:

1. **SFDA status** — registered/authorised for the Saudi market? If it cannot be determined from
   an authoritative source **in this session**, state *SFDA status not verified — check before
   purchase or clinical use*. Never infer status from FDA or CE marking.
2. **FDA / CE status** — report separately, labelled non-transferable to Saudi legality.
3. **Clearance ≠ superiority** — regulatory clearance is not evidence of clinical superiority.
   See `claim-strength-governor.md`; do not restate the rule, apply it.
4. **IFU governs handling.** Off-label use is flagged as off-label. `~~manufacturer-ifu` is NOT
   CONNECTED, so IFU content cannot be looked up — say that rather than paraphrasing an IFU from
   memory.
5. **Adverse events and product problems** — where a device or material failure is described,
   state the SFDA reporting pathway obligation. Do not state the procedure or timeline; direct the
   clinician to verify current SFDA reporting requirements.
6. **Grey-market / unregistered sourcing** — if a clinician describes obtaining a product outside
   normal channels, flag the regulatory, warranty and liability implications explicitly. Do not
   soften this.

## Jurisdiction (M4 §1)

Baseline is the **Kingdom of Saudi Arabia**. ADA, FDI, EFP, FDA, EU MDR, MHRA, NICE, SDCEP and
comparable bodies may be cited for clinical content and for comparison — never as a substitute for
the Saudi requirement.

State which jurisdiction is being applied whenever the output touches registration, licensing,
scope, advertising, patient data or product legality. If the clinician practises elsewhere, say
the Saudi layer does not apply and their local requirements must be checked (state **NOT
APPLICABLE**).

## Connector interaction

Route Saudi product questions to `~~regulatory-saudi` (`connectors/sfda/`). Then:

- Lookup succeeded with a match → **VERIFIED**, cite the registration identifier and provenance.
- Lookup succeeded with **no match** → **REQUIRES VERIFICATION**. A no-match is *not* a finding
  that the product is unapproved; SFDA coverage, naming and transliteration all vary. Never write
  "not approved in Saudi Arabia" on the strength of an empty result.
- Connector returned `NOT_CONNECTED_AUTH_REQUIRED`, `TIMEOUT`, or any error → **REQUIRES
  VERIFICATION**, and say the lookup could not be performed. Never let a connector failure become
  silence or an assumed status.

## QC check

Any sentence asserting or implying a Saudi regulatory status must carry one of the four states and,
for **VERIFIED**, a real Saudi-source identifier and retrieval provenance. Absence is a QC FAIL.

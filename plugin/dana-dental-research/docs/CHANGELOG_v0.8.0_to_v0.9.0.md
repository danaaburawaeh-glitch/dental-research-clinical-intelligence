# Changelog — v0.8.0 → v0.9.0 (Clinical Protocol Closure)

No features. No connectors. No M5. No new specialties. The only objective was the Appendix C
approval gate.

## Result

**Clinical Protocol v1.3 — APPROVED.** All eight open items closed 2026-08-31; zero remain.
v1.2 preserved unchanged as the historical version. Full record with per-item basis, date and
external-vs-clinic-policy attribution: `CLINICAL_PROTOCOL_APPROVAL_RECORD.md`.

New Drive document: `1XAU6VWqKnK7JAl6zhGt4SzqlAQx8OOkJaD2AQMqmAzs`.

## How the eight closed

Six by one principle — **volatile operational facts leave the governed clinical document**. A
laboratory's name, its contracted turnaround, a product's trade name and a session's duration all
change without any clinical reasoning changing. Keeping them in the protocol forced re-approval on
every commercial change and, in v1.2, actively produced two of the defects: the duration conflict
(item 3, the same fact stated twice) and the misspelling (item 4). They now live in Appendix B and
the new **Annex E**, living documents that do not block approval.

Two by **deleting unsupported numbers rather than sourcing them** — v1.2's own Appendix A already
argued this: attaching an academic reference to a thickness number "gives it false legitimacy and
contradicts the DEL-7 logic itself".

One item was closed on external evidence: **item 8**, brushing frequency, aligned to twice daily
and raised from (JUDG) to **(L1)** on R1 (Sanz et al. 2020, EFP S3, doi:10.1111/jcpe.13290) — a
reference already verified in the protocol's own Appendix A.

## What was attempted and failed, recorded rather than papered over

- **IFU retrieval.** The Dentsply and Ivoclar portals were reached (HTTP 200) but are interactive
  search applications requiring the exact product and lot. Per Step 4 the values are `REQUIRES
  VERIFICATION`; the remembered numbers were **deleted, not preserved**.
- **Trade-name verification (item 4).** Calibra ships as several distinct products with different
  protocols; only the package in the operatory identifies which is stocked. Not guessed.
- **Drive search for laboratory contracts and IFU attachments.** None exist; Appendix B of v1.2 is
  entirely empty checkboxes.

## DANA updated

`prosthodontic-restorability.md` (source note rewritten, R-6 corrected — it still described v1.2's
tagged-number §3.1, which v1.3 replaces with no number at all), the other three prosthodontic
references, `healthy-tooth-protection.md`, `deferred-knowledge-dependencies.md` (status block), and
the `clinical-case`, `esthetic-prosthodontics`, `treatment-plan-audit` and `quality-control` skills.

DANA now cites **v1.3 APPROVED** and no longer calls the protocol a draft. A test walks every
markdown file under `skills/` and fails if any still describes it as a current draft without
recording the resolution.

## Tests

`clinical/tests/test_protocol_approval.py` → **24/24**. All v0.8.0 suites unchanged and passing.

## Not changed

No clinical logic. `connectors/` and `clinical/*.py` byte-identical to v0.8.0. Connector states
unchanged from the frozen v0.6.0 baseline.

## Honest limits of this approval

Approval covers the **content** of the protocol. Two conditions survive as **use gates**:
Appendix B (product names and IFUs) and Annex E (Laboratory of Record, session times) are both
**empty**. §2.4 forbids using a product before its IFU is registered; §8 requires a Laboratory of
Record before an indirect restoration is prescribed. Populate both before clinical use.

**The signature line remains for Dr Dana.** Content approval is evidenced; signing is a
professional act that cannot be delegated to this system.

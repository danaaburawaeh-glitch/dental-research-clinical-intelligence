<!--
REFERENCE-ID: saudi-data-privacy-pdpl
VERSION: 0.6.0
CANONICAL-OWNER: clinical-governance
Migrated from M4 (V0.4, 2026-08-20) §5, §6.2, §7 in Phase C. See M4_MIGRATION_AUDIT.md.
Operational rules only. Not a legal text. Current PDPL requirements are verified with SDAIA at
point of use, never stated from memory.
-->

# Patient Data — PDPL Operating Rules

Loaded by: clinical-governance, quality-control, clinical-case, esthetic-prosthodontics.

## 1. Minimum necessary data

Never request, restate or reproduce a patient's **name, national ID or iqama number, medical
record number, date of birth, phone number, address, employer, insurer ID, or face** where the
clinical question does not require it.

If identifiers appear in an input: say so **once**, then continue with a de-identified reference —
`CASE-YYYYMMDD-xx`, or `Patient A`. Do not repeat the identifier back while acknowledging it.

Ask what the clinical question actually needs. Age band, sex where clinically relevant, relevant
medical history and the dental findings are usually the whole answer. A name never is.

## 2. De-identification before anything leaves the clinical setting

Remove or replace:

- direct identifiers
- **face**, and any recognisable feature — distinctive tattoo, jewellery, background detail
- dates narrowed enough to identify
- rare-condition descriptions that identify **by their rarity**
- **image metadata (EXIF)** — device, GPS, timestamp
- **identifiers burned into radiographs** — patient name in the image, clinic header, DICOM tags

**Radiographs and intraoral scans routinely carry embedded patient identifiers.** Flag this
explicitly every time imaging is shared. A clinician who has cropped a photo has usually not
stripped its EXIF, and has almost never cleared DICOM tags.

## 3. Patient images are personal data

A clinical photograph is personal data in the same sense a name is, and a face is not
de-identified by cropping to the mouth if the image still carries identifying features or
metadata. Treat every intraoral photograph, extraoral photograph, radiograph and scan as
identifiable until it has been actively de-identified.

## 4. Entering data into an AI system is processing

Patient data entering **any** AI system — including this one — is a processing activity under
PDPL. The clinic must know where that data goes and on what basis.

**Standing advice: de-identify before input.** This system is designed to be used with
de-identified case data as the default working practice, not as an exception.

## 5. Cross-border and cloud transfer is not assumed permitted

Transfer of health data outside the Kingdom carries specific requirements. **Never assume a cloud
service, an AI tool, a messaging app or an external collaborator is permitted** to receive
identifiable patient data.

Flag it whenever a clinician proposes putting identifiable patient data into any external tool.
Do not state what the requirement is — state that the requirement exists and must be verified with
SDAIA/the clinic's compliance advisor before the transfer happens, not after.

## 6. Disclosure to third parties needs a lawful basis

Insurer, employer, family member, another clinician — each requires a lawful basis. **Flag it; do
not assume consent.** A patient having attended does not imply permission to discuss them with
anyone who asks.

## 7. Retention

Clinical records carry a mandated retention period under Saudi requirements. **Verify the current
period; do not state one.** An AI session is not the clinical record and must never become the
only copy of anything clinically important.

## 8. Treatment consent ≠ photography consent ≠ publication consent

These are three separate permissions, and each is separate again per channel:

> Consent to **treatment** is not consent to **photography**.
> Consent to photography **for the record** is not consent to **publication**.
> Consent to publication **in a lecture** is not consent to publication **on social media**.

Publication consent must be **specific** (this patient, these images, these channels) ·
**informed** (the internet is permanent; reach cannot be controlled; re-sharing cannot be
recovered) · **written** · **freely given** (never a condition of treatment or of a discount) ·
**revocable**, with a stated withdrawal process and what happens to already-published material ·
**separately recorded** from treatment consent.

Where a **minor or a person lacking capacity** is involved, apply a markedly higher threshold and
recommend legal review.

## 9. Marketing use requires separate consideration — the clinical→marketing firewall

M4 §7 is the highest-exposure rule in the system, and it is structurally live: clinical and
marketing tooling exist in the same workspace.

1. Clinical case material, patient photographs, radiographs, scans, records and case descriptions
   **never** flow into social-media, advertising, portfolio, website or promotional output —
   unless the clinician confirms, **in that same exchange**, that specific, informed, written,
   revocable publication consent exists for **that patient**, **those images**, **that channel**.
2. **Absence of a stated consent is absence of consent.** Never assume it, never infer it from
   prior sharing, never carry it from one case or channel to another.
3. If asked to produce marketing content from clinical material without that confirmation:
   **stop, state the requirement, request the confirmation.** Do **not** produce a draft "to be
   used once consent is obtained" — the draft is what gets posted.
4. **No clinical claim in marketing output** that would not survive evidence tagging: no
   guaranteed outcomes, no "painless", no "permanent", no comparative superiority, no implied
   specialty title not held, no before/after implying a typical or reproducible result without
   stating that results vary.
5. **Before/after imagery**: same patient, same standardisation (angle, lighting, retraction,
   magnification), unedited in any way that alters clinical appearance. Whitening, smoothing,
   colour-shifting or AI enhancement of a before/after pair is misrepresentation. Enhanced images
   are never used for diagnosis either.
6. **Health advertising is regulated in Saudi Arabia.** Flag any promotional output for compliance
   review against current MOH/CST requirements before publication. Say this **every time**.
7. **Directionality — one way only.** Marketing context never enters clinical reasoning. Never let
   a desired marketing outcome (a dramatic case, a photogenic result) influence a treatment
   recommendation. If a request blends the two, separate them and answer the clinical question
   first, on clinical grounds alone.

## 10. Research use is a separate purpose

Using clinical records for research — retrospective chart review, case series, audit intended for
publication — is a **separate purpose from care**. It needs research ethics approval and its own
lawful basis, and **treatment consent does not cover it**.

Flag this whenever a user describes "collecting cases" or "looking back at my patients" with an
academic outcome in mind. Service evaluation and internal clinical audit are treated differently
from research, but **the boundary is decided by the ethics committee, not by the clinician's
intent** — say so. (M4 §5.5 cross-references M5 §4, which is not migrated in this phase.)

## QC check

Any output involving patient data must show: identifiers minimised; de-identification applied or
explicitly flagged as needed; imaging metadata risk raised where images are involved; no
cross-border transfer assumed permitted; and — where any marketing, publication or social use is
in scope — publication consent addressed **separately** from treatment consent. Absence is a QC
FAIL.

# Security and Privacy

## Patient data — the operating rules

**Use the minimum necessary information.** A clinical question rarely needs a name.

**Do not enter**, unless the clinical question genuinely requires it:
patient names · national ID or iqama numbers · medical record numbers · dates of birth ·
phone numbers · addresses · employer or insurer identifiers · faces.

**De-identify before submission.** Use `CASE-YYYYMMDD-01` or "a 45-year-old female patient".

**Images carry hidden identifiers.** Radiographs and intraoral scans routinely embed patient names,
clinic headers and DICOM tags, and photographs carry EXIF metadata including device, GPS and
timestamp. **Cropping does not remove any of this.** Strip metadata and check for identifiers burnt
into the image itself before sharing.

**Data entered leaves your clinic.** It is processed by an external AI service. Treat that as a
data-transfer decision under your jurisdiction's rules — in Saudi Arabia, PDPL — not as a
formality. Cross-border transfer of health data is not automatically permitted.

## Credentials

**Never place credentials in prompts, files or commits.** This includes API keys, bearer tokens,
passwords, OAuth consumer keys and secrets.

The SFDA connector reads its configuration from environment variables only:

```
SFDA_CLIENT_ID
SFDA_CLIENT_SECRET
SFDA_TOKEN_URL
SFDA_API_BASE_URL
SFDA_MEDICAL_DEVICE_PATH
SFDA_DRUG_PATH
```

Set these in your shell profile or a secrets manager. **Never commit them.** `.gitignore` excludes
`.env` files, but the durable protection is not putting secrets in the repository in the first
place.

No credential of any kind ships in this package. The only hard-coded URL in the SFDA connector is
the public developer portal, used in its "how to configure" message.

## Reporting a security or privacy issue

Report suspected security or privacy problems **privately**, not through the public issue tracker,
and separately from ordinary feature requests or bug reports.

Contact the maintainer directly. Please include what you observed and how to reproduce it — and
**never include real patient data in a report.**

## What this package contains

No credentials. No API keys or tokens. No patient data. No private filesystem paths. Verified by
scan before release; see `DISTRIBUTION_VALIDATION_v1.0.0.md`.

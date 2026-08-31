# Release Notes — v1.0.1

**Dental Research & Clinical Intelligence by Dr. Dana**
Plugin identifier `dana-dental-research` · Designed by Dr. Dana Abu Rawaeh

A **privacy patch** of the validated v1.0.0 production release. Functionally identical.

## What changed

The maintainer's personal email address has been removed from all tracked repository content
before public distribution.

- Contact fields that structurally require an address now use the GitHub noreply address.
- Three historical documents had the literal address redacted; the provenance information they
  recorded is preserved in full.
- Version metadata updated to 1.0.1.

## What did not change

Clinical logic · evidence logic · connector code · connector states · Clinical Protocol v1.3 ·
safety rules · identity policy · scientific content · all nine skills · every reference file.

All seven regression suites pass unchanged. Connector states, the Clinical Protocol status and the
known-limitations register are exactly as validated in v1.0.0 — see
[`RELEASE_NOTES_v1.0.0.md`](RELEASE_NOTES_v1.0.0.md) for the full description of the product.

## Note on v1.0.0 artifacts

The v1.0.0 `.plugin` and `.zip` are **not** included in this repository. Their manifest still
contains the personal address, so distributing them would defeat the purpose of this patch. They
are preserved unchanged outside the repository as the record of what passed final production
validation.

**v1.0.1 is the release intended for distribution.**

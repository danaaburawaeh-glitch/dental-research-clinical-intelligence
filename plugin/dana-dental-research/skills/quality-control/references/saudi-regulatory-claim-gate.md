<!--
REFERENCE-ID: saudi-regulatory-claim-gate
VERSION: 0.2.1
CANONICAL-OWNER: clinical-governance (see /ARCHITECTURE_REFERENCE_MAP.md for the full owner/consumer table)
LAST-SYNCHRONIZED: 2026-08-28
This file is a bundled copy. Edit only at the canonical owner location and re-sync all bundles
in the same change; do not hand-edit a consumer copy independently (see Step 3, canonical
source policy).
-->

# Saudi Regulatory / Legal Claim Gate

Loaded by: clinical-governance, quality-control.

## Purpose
Prevent general ethical principles from being silently stated as Saudi legal or regulatory
requirements.

## Trigger
Any statement resembling: "Saudi law requires...", "SCFHS requires...", "SFDA requires...",
"legally you must...", "informed consent law requires...", or any comparable jurisdiction-specific
legal/regulatory claim.

## Rule
1. Such a claim must be routed through the regulatory-saudi connector (~~regulatory-saudi) where
   available, and the specific verified provision cited.
2. If verification is unavailable in this session, the system must state plainly:
   "Regulatory verification required" — and must not assert the legal requirement as settled fact.
3. Ethical best practice (e.g. "informed consent is good practice") must never be silently converted
   into a legal citation ("the law requires informed consent in this specific form"). Keep the two
   distinct: ethical-principle language vs. verified-legal-requirement language.

## QC check
Any sentence asserting a specific Saudi legal/regulatory duty must show either a verified source or
the "Regulatory verification required" flag. Absence of either is a QC FAIL.

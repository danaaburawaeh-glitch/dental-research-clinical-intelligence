# Connector Security — v0.4 Phase A

## Secrets handling

**No secrets are committed anywhere in this repository.** All credentials are read from
environment variables at call time, never hard-coded, never written into `SKILL.md`, reference
files, `plugin.json`, or `.mcp.json`.

| Variable | Purpose | Required? | Where read |
|---|---|---|---|
| `NCBI_API_KEY` | Raises E-utilities rate limit from 3 to 10 req/s | No — connector works without it at the lower rate | `connectors/pubmed/rate_limit.py`, `connectors/pubmed/client.py` |
| `NCBI_TOOL` | E-utilities `tool` identification parameter | No — defaults to `dana_dental_evidence` | `connectors/pubmed/client.py` |
| `NCBI_EMAIL` | E-utilities `email` identification parameter (NCBI-requested politeness, not secret, but still not hard-coded) | Recommended, not enforced | `connectors/pubmed/client.py` |
| `CROSSREF_MAILTO` | Crossref polite-pool identification | Recommended (raises rate limit 5→10 req/s) | `connectors/crossref/client.py`, `connectors/crossref/rate_limit.py` |

## `.env.example`

A template with **placeholders only** is provided at the repository root (`.env.example`). It is
never populated with real values in this package. Populating it with real values is the
responsibility of whoever deploys/runs the plugin, in their own local, untracked `.env` or actual
environment — never committed back into plugin source.

## What was explicitly NOT done, per the brief

- Your real personal email address (redacted in v1.0.1 for privacy; encountered during the
  v0.3/v0.3.1 build when
  reading the Google Drive CORE document's owner metadata) is **not** placed in `.env.example`,
  `NCBI_EMAIL`, `CROSSREF_MAILTO`, or anywhere else in this connector code. That address was used
  once, visibly, in `v0.3-build`'s illustrative example query URL shown in prose
  (`M3_MIGRATION_AUDIT.md` era) — it is not repeated as a default or fallback value anywhere in
  the actual v0.4 connector code. If you want a real contact email wired in for actual runtime
  use, that's a deliberate configuration step you take locally, not something this package does
  for you.
- No API keys were requested, generated, or assumed. `NCBI_API_KEY` and `CROSSREF_MAILTO` (as an
  actual working email) are absent from every committed file; the code simply checks
  `os.environ.get(...)` and degrades gracefully (lower rate limit, `public` Crossref pool instead
  of `polite`) when they're unset.

## Where the boundary sits

- Connector Python files (`client.py`, `rate_limit.py`) **read** environment variables at call
  time. They never write, log, or persist secret values to disk.
- No secret value is included in any `EvidenceRecord`, `Provenance` object, search log, or
  anything that could end up in model-visible output — provenance records the *query* and
  *retrieval status*, never the API key or configured email address.
- If `NCBI_API_KEY` or a real `CROSSREF_MAILTO` is set in the actual runtime environment, that's
  outside this package's control and is the deploying user's own configuration, exactly as
  `.env.example` documents.

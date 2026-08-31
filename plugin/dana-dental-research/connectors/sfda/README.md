# SFDA connector (`~~regulatory-saudi`)

Saudi Food and Drug Authority product registration lookup, for the Saudi Regulatory Gate.

## Status

**NOT CONNECTED — AUTH REQUIRED.** The code is implemented and callable; SFDA requires a
registered application, and no credentials are configured in this environment. See
`docs/SFDA_CONNECTOR_VALIDATION.md`.

## Commands

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/connectors/sfda/client.py" status
python3 "${CLAUDE_PLUGIN_ROOT}/connectors/sfda/client.py" search --keyword "zirconia" --product-type medical_device
python3 "${CLAUDE_PLUGIN_ROOT}/connectors/sfda/client.py" lookup --registration-number "..." --product-type drug
```

## Configuration — never hard-coded

Register an app at <https://developer.sfda.gov.sa> (Get Started → create account → create app →
select the Registered Medical Device / Registered Drug services). The app page supplies the
consumer key/secret and the gateway URLs. Then set:

| Variable | Purpose |
|---|---|
| `SFDA_CLIENT_ID` | consumer key |
| `SFDA_CLIENT_SECRET` | consumer secret |
| `SFDA_TOKEN_URL` | OAuth token endpoint from your app page |
| `SFDA_API_BASE_URL` | API gateway base from your app page |
| `SFDA_MEDICAL_DEVICE_PATH` | Registered Medical Device service path |
| `SFDA_DRUG_PATH` | Registered Drug service path |

Never commit these. The connector reads them from the environment only, caches a token in-process
for under 24 hours, and never writes a token to disk or into a result payload.

**Why the URLs are configuration rather than constants:** SFDA publishes concrete gateway hosts and
paths only to registered applications; the public docs use `api.example.com.sa` placeholders.
Hard-coding a guessed endpoint would be fabrication. With no configuration the connector performs
no request and says so.

## The safety invariant

Every outcome except "a real matching record was returned" maps to **REQUIRES VERIFICATION**:

| Outcome | Regulatory state |
|---|---|
| `SUCCESS` with ≥1 match | **VERIFIED** |
| `SUCCESS` with 0 matches / `ZERO_RESULTS` | REQUIRES VERIFICATION |
| `NOT_CONNECTED_AUTH_REQUIRED` | REQUIRES VERIFICATION |
| `AUTH_ERROR`, `TIMEOUT`, `RATE_LIMITED`, `UPSTREAM_ERROR`, `PARSE_ERROR` | REQUIRES VERIFICATION |

**There is no code path to "not approved in Saudi Arabia".** An empty SFDA result is not evidence
a product is unregistered — coverage, naming and transliteration all vary.

## Scope

Medical devices and drugs only. The portal also publishes food and cosmetic services; both are out
of dental scope and deliberately unwired. No endpoint outside the five documented public products
is implemented.

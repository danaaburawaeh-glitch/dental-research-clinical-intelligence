# SFDA Connector Validation — v0.6.0 Phase C

**Result: NOT CONNECTED — AUTH REQUIRED.** An honest negative. The connector is implemented and
callable; SFDA requires a registered application and no credentials exist in this environment.

## What was verified live (2026-08-31, real HTTP from this machine)

| Check | Result |
|---|---|
| `https://developer.sfda.gov.sa/` | **HTTP 200** — the developer portal is real |
| Published API products | **5 public**: Registered Medical Device, Registered Drug, Registered Food, Registered Cosmetic, OAuth |
| Registered Medical Device Service | "allows inquiries about medical device (Low risk, GHTF and TFA) products registered with the Food and Drug Authority includes retrieving the list of products and searching by keyword." Format `application/json`; security **Bearer token**; data source **Ghad System** |
| Registered Drug Service | "Inquiries about registered drug products, including product list retrieval and search." |
| OAuth Service | "retrieve an access token by **client credentials** grant type (Consumer key as username and Consumer secret as password)… The access token **expire within 24 hours**." |
| `https://api.sfda.gov.sa` | Connection reset — not a public unauthenticated host |
| `https://open.data.gov.sa/api/...` | WAF returns "Request Rejected" for programmatic requests — no credential-free route |

## What could NOT be verified, and why nothing was invented

The **API gateway hostname and concrete request paths** are disclosed only after registering an
application and logging in. The public documentation uses placeholders
(`https://api.example.com.sa/v1/oauth2/accesstoken`).

Hard-coding a plausible-looking endpoint would be fabrication of exactly the kind this codebase
refuses elsewhere. So **every URL is environment configuration**, and with none set the connector
issues no request at all rather than guessing a host. A regression test asserts the source contains
exactly one hard-coded `https://` — the public developer portal, used only in the "how to
configure" message.

The **response schema** is likewise undocumented publicly. `models.py` therefore tolerates several
plausible envelopes, maps candidate field names case-insensitively, and **preserves the complete
raw record** so no undocumented field is lost. A field reported as `None` means "this parser could
not find it", not "SFDA does not provide it".

## Live attempt from the packaged connector

```
$ python3 connectors/sfda/client.py search --keyword "dental implant" --product-type medical_device
status:            NOT_CONNECTED_AUTH_REQUIRED
regulatory_state:  REQUIRES VERIFICATION
missing:           client_id, client_secret, token_url, base_url, SFDA_MEDICAL_DEVICE_PATH
```

Exit code 1. No credentials are present in the environment (`0` `SFDA_*` variables set).

## Why this does not fail Phase C

The Phase C brief states that unavailable credentials "must NOT fail the rest of Phase C", and
§9 requires `NOT CONNECTED — AUTH REQUIRED` rather than a faked activation. The governance layer
this connector serves is fully operational without it: an unavailable SFDA lookup produces
**REQUIRES VERIFICATION**, which is precisely the state M4 §3.1 demands ("SFDA status not verified
— check before purchase or clinical use").

The connector's value is not only in succeeding. **It refuses to let unavailability become
silence, an assumed approval, or an assumed refusal.**

## The safety invariant, tested

| Outcome | Regulatory state |
|---|---|
| `SUCCESS` with ≥1 matching record | **VERIFIED** |
| `SUCCESS`/`ZERO_RESULTS` with 0 matches | REQUIRES VERIFICATION |
| `NOT_CONNECTED_AUTH_REQUIRED` | REQUIRES VERIFICATION |
| `AUTH_ERROR` (key rejected) | REQUIRES VERIFICATION |
| `TIMEOUT`, `RATE_LIMITED`, `UPSTREAM_ERROR`, `PARSE_ERROR` | REQUIRES VERIFICATION |

`errors.regulatory_state()` has **no code path to "not approved"**. Invariant tests assert that no
non-`SUCCESS` status can yield VERIFIED even when `matched=True` is forced, and that `SUCCESS`
without a match cannot yield VERIFIED.

Note the deliberate distinction between `NOT_CONNECTED_AUTH_REQUIRED` (nobody has configured
credentials) and `AUTH_ERROR` (credentials were sent and rejected). They call for different user
action, so they are not collapsed.

## To reach CONNECTED — SFDA

1. Register an application at developer.sfda.gov.sa and select the Registered Medical Device /
   Registered Drug services.
2. Set `SFDA_CLIENT_ID`, `SFDA_CLIENT_SECRET`, `SFDA_TOKEN_URL`, `SFDA_API_BASE_URL`,
   `SFDA_MEDICAL_DEVICE_PATH` / `SFDA_DRUG_PATH` in the environment. Never commit them.
3. Re-run `client.py status`, then a real `search`. Only when a real request succeeds, a real
   record parses, and provenance is preserved does the capability map change to
   `CONNECTED — SFDA`. The observed response schema should then be folded into
   `models.py`'s candidate field map.

## Tests

`python3 connectors/sfda/tests/test_saudi_governance.py` → **50/50 pass**, covering all 8 required
Phase C scenarios plus 8 safety invariants. The transport is mocked for the states that cannot be
provoked without credentials.

"""
connectors/sfda/client.py

SFDA (Saudi Food and Drug Authority) connector for ~~regulatory-saudi.

WHAT WAS VERIFIED, AND WHAT DELIBERATELY IS NOT
-----------------------------------------------
Verified live from the official developer portal (developer.sfda.gov.sa, 2026-08-31) — see
SFDA_CONNECTOR_VALIDATION.md:
  - The portal is real and lists 5 public products: Registered Medical Device Service,
    Registered Drug Service, Registered Food Service, Registered Cosmetic Service, and OAuth.
  - Medical Device service: "allows inquiries about medical device (Low risk, GHTF and TFA)
    products registered with the Food and Drug Authority includes retrieving the list of products
    and searching by keyword." Message format application/json. Security schema: Bearer token.
    Data source: Ghad System.
  - OAuth service: "retrieve an access token by client credentials grant type (Consumer key as
    username and Consumer secret as password)... The access token expire within 24 hours."

NOT verified, and therefore NOT hard-coded anywhere in this file: the API gateway hostname and the
concrete request paths. Those are disclosed only after registering an application and logging in;
the public documentation shows placeholder URLs (`api.example.com.sa/v1/oauth2/accesstoken`).

Inventing a plausible-looking endpoint would be exactly the fabrication this codebase forbids
everywhere else. So every URL is supplied by environment configuration. With no configuration the
connector reports NOT_CONNECTED_AUTH_REQUIRED and performs no request — it never guesses a host.

CREDENTIALS ARE NEVER HARD-CODED. Read from the environment only.

REGULATORY SAFETY INVARIANT
---------------------------
Every outcome of this connector other than "a real matching record was returned" maps to
REQUIRES VERIFICATION. There is no code path from a failure, an empty result, or a missing
credential to "not approved in Saudi Arabia".
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # for shared/

from shared.provenance import build_provenance, now_iso
from shared.retry import with_backoff, RetryExhausted

from errors import (
    SFDAConnectorError, classify_http_status, regulatory_state,
    STATUS_SUCCESS, STATUS_ZERO_RESULTS, STATUS_TIMEOUT, STATUS_PARSE_ERROR,
    STATUS_UPSTREAM_ERROR, STATUS_AUTH_ERROR, STATUS_NOT_CONNECTED_AUTH_REQUIRED,
    STATUS_NOT_CONFIGURED, ZERO_RESULTS_MEANING, AUTH_REQUIRED_MEANING,
    REGULATORY_STATE_REQUIRES_VERIFICATION,
)
from models import SFDAProductRecord, parse_products, PRODUCT_TYPES

# ---------------------------------------------------------------------------
# Configuration — every value comes from the environment. Nothing is invented.
# ---------------------------------------------------------------------------
ENV_CLIENT_ID = "SFDA_CLIENT_ID"          # consumer key
ENV_CLIENT_SECRET = "SFDA_CLIENT_SECRET"  # consumer secret
ENV_TOKEN_URL = "SFDA_TOKEN_URL"          # OAuth token endpoint, from your app's page
ENV_BASE_URL = "SFDA_API_BASE_URL"        # API gateway base, from your app's page
ENV_DEVICE_PATH = "SFDA_MEDICAL_DEVICE_PATH"
ENV_DRUG_PATH = "SFDA_DRUG_PATH"

DEFAULT_TIMEOUT_SECONDS = 30
RETRYABLE_STATUSES = (429, 500, 502, 503, 504)
MAX_ATTEMPTS = 3

DEVELOPER_PORTAL = "https://developer.sfda.gov.sa"


class _Response:
    def __init__(self, status_code, text, headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}


def _config():
    return {
        "client_id": os.environ.get(ENV_CLIENT_ID),
        "client_secret": os.environ.get(ENV_CLIENT_SECRET),
        "token_url": os.environ.get(ENV_TOKEN_URL),
        "base_url": os.environ.get(ENV_BASE_URL),
        "device_path": os.environ.get(ENV_DEVICE_PATH),
        "drug_path": os.environ.get(ENV_DRUG_PATH),
    }


def _missing_config(cfg, needed):
    return [k for k in needed if not cfg.get(k)]


def _not_connected_result(query, missing, product_type=None):
    """
    The configured-absent outcome. Reports precisely what is missing, without ever implying
    anything about the product's regulatory status.
    """
    return {
        "status": STATUS_NOT_CONNECTED_AUTH_REQUIRED,
        "regulatory_state": REGULATORY_STATE_REQUIRES_VERIFICATION,
        "error": "SFDA credentials/endpoints are not configured; no lookup was performed.",
        "missing_configuration": missing,
        "meaning": AUTH_REQUIRED_MEANING,
        "how_to_configure": (
            f"Register an application at {DEVELOPER_PORTAL} (Get Started -> create account -> "
            f"create app -> select the Registered Medical Device / Registered Drug services). The "
            f"app page supplies the consumer key/secret and the gateway URLs. Set: "
            f"{ENV_CLIENT_ID}, {ENV_CLIENT_SECRET}, {ENV_TOKEN_URL}, {ENV_BASE_URL}, and the "
            f"relevant path variable. Never commit these values."
        ),
        "product_type": product_type,
        "provenance": build_provenance("sfda", "SFDA", str(query),
                                        STATUS_NOT_CONNECTED_AUTH_REQUIRED).to_dict(),
    }


def _error_result(status, message, query, response=None, product_type=None):
    result = {
        "status": status,
        "regulatory_state": regulatory_state(status, matched=False),
        "error": message,
        "product_type": product_type,
        "provenance": build_provenance("sfda", "SFDA", str(query), status).to_dict(),
    }
    if response is not None:
        result["http_status"] = response.status_code
        result["upstream_message"] = (response.text or "").strip()[:400]
    return result


def _single_attempt(request, timeout):
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return _Response(resp.status, resp.read().decode("utf-8"), dict(resp.headers))
    except urllib.error.HTTPError as e:
        return _Response(e.code, e.read().decode("utf-8", errors="replace"), dict(e.headers or {}))


def _http(request, timeout=DEFAULT_TIMEOUT_SECONDS):
    try:
        return with_backoff(lambda: _single_attempt(request, timeout),
                            max_attempts=MAX_ATTEMPTS, retryable_statuses=RETRYABLE_STATUSES)
    except RetryExhausted as exc:
        raise SFDAConnectorError(
            STATUS_TIMEOUT, f"Network error reaching SFDA after {exc.attempts} attempts: {exc.last_error}")


# ---------------------------------------------------------------------------
# OAuth — client_credentials, per the verified portal description
# ---------------------------------------------------------------------------
_TOKEN_CACHE = {"token": None, "expires_at": 0.0}
# Portal states tokens expire within 24 hours. Cached conservatively below that, and the cache is
# process-local only — a token is never written to disk.
TOKEN_TTL_SECONDS = 23 * 3600


def get_access_token(force_refresh=False):
    """
    Retrieve an OAuth access token via the client_credentials grant, exactly as the SFDA OAuth
    product documents it: consumer key as username, consumer secret as password.

    Returns (token, None) on success or (None, result_dict) on failure. Never raises. The token is
    never logged, never returned in a result payload, and never persisted.
    """
    cfg = _config()
    missing = _missing_config(cfg, ["client_id", "client_secret", "token_url"])
    if missing:
        return None, _not_connected_result("oauth-token", missing)

    now = time.time()
    if not force_refresh and _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] > now:
        return _TOKEN_CACHE["token"], None

    import base64
    basic = base64.b64encode(
        f"{cfg['client_id']}:{cfg['client_secret']}".encode("utf-8")).decode("ascii")
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    req = urllib.request.Request(
        cfg["token_url"], data=data, method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        })

    try:
        response = _http(req)
    except SFDAConnectorError as exc:
        return None, _error_result(exc.status, str(exc), "oauth-token")
    except Exception as exc:
        return None, _error_result(STATUS_UPSTREAM_ERROR, f"Unexpected error during token request: {exc}",
                                    "oauth-token")

    err = classify_http_status(response.status_code)
    if err:
        msg = ("SFDA rejected the configured credentials (HTTP "
               f"{response.status_code}). The key/secret may be wrong, expired, or not entitled to "
               "the requested service." if err == STATUS_AUTH_ERROR
               else f"SFDA token endpoint HTTP {response.status_code}")
        return None, _error_result(err, msg, "oauth-token", response)

    try:
        payload = json.loads(response.text)
    except Exception as exc:
        return None, _error_result(STATUS_PARSE_ERROR, f"Token response is not valid JSON: {exc}",
                                    "oauth-token", response)

    token = payload.get("access_token")
    if not token:
        return None, _error_result(STATUS_PARSE_ERROR,
                                    "Token response contained no access_token field.",
                                    "oauth-token", response)

    try:
        ttl = min(int(payload.get("expires_in") or TOKEN_TTL_SECONDS), TOKEN_TTL_SECONDS)
    except (TypeError, ValueError):
        ttl = TOKEN_TTL_SECONDS
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expires_at"] = now + max(60, ttl - 60)
    return token, None


def _service_path(cfg, product_type):
    if product_type == "medical_device":
        return cfg.get("device_path"), ENV_DEVICE_PATH
    if product_type == "drug":
        return cfg.get("drug_path"), ENV_DRUG_PATH
    return None, None


def _call_service(product_type, params, query):
    """Shared request path for both public functions. Never raises."""
    if product_type not in PRODUCT_TYPES:
        return {
            "status": STATUS_NOT_CONFIGURED,
            "regulatory_state": REGULATORY_STATE_REQUIRES_VERIFICATION,
            "error": (f"Unsupported product_type {product_type!r}. Supported: "
                      f"{sorted(PRODUCT_TYPES)}. Only services the SFDA portal actually publishes "
                      "are implemented; no endpoint is invented."),
            "provenance": build_provenance("sfda", "SFDA", str(query), STATUS_NOT_CONFIGURED).to_dict(),
        }

    cfg = _config()
    path, path_var = _service_path(cfg, product_type)
    missing = _missing_config(cfg, ["client_id", "client_secret", "token_url", "base_url"])
    if not path:
        missing = missing + [path_var]
    if missing:
        return _not_connected_result(query, missing, product_type)

    token, failure = get_access_token()
    if failure:
        failure["product_type"] = product_type
        return failure

    url = cfg["base_url"].rstrip("/") + "/" + path.lstrip("/")
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })

    try:
        response = _http(req)
    except SFDAConnectorError as exc:
        return _error_result(exc.status, str(exc), query, product_type=product_type)
    except Exception as exc:
        return _error_result(STATUS_UPSTREAM_ERROR, f"Unexpected error during SFDA request: {exc}",
                              query, product_type=product_type)

    err = classify_http_status(response.status_code)
    if err:
        return _error_result(err, f"SFDA HTTP {response.status_code}", query, response,
                              product_type=product_type)

    try:
        payload = json.loads(response.text)
    except Exception as exc:
        return _error_result(STATUS_PARSE_ERROR, f"SFDA response is not valid JSON: {exc}",
                              query, response, product_type=product_type)

    retrieved_at = now_iso()
    try:
        records = parse_products(payload, product_type=product_type, query=query,
                                  retrieved_at=retrieved_at)
    except Exception as exc:
        return _error_result(STATUS_PARSE_ERROR, f"Unexpected SFDA parse error: {exc}",
                              query, response, product_type=product_type)

    status = STATUS_SUCCESS if records else STATUS_ZERO_RESULTS
    result = {
        "status": status,
        "regulatory_state": regulatory_state(status, matched=bool(records)),
        "records": records,
        "match_count": len(records),
        "product_type": product_type,
        "executed_query": url.split("?", 1)[1] if "?" in url else "",
        "provenance": build_provenance("sfda", "SFDA", str(query), status).to_dict(),
    }
    if not records:
        result["meaning"] = ZERO_RESULTS_MEANING
    return result


def sfda_search_product(keyword, product_type="medical_device", page=None, page_size=None):
    """
    Keyword search of SFDA registered products.

    Mirrors the capability the portal documents: "retrieving the list of products and searching by
    keyword". Only medical_device and drug are supported — the portal also publishes food and
    cosmetic services, which are out of dental scope and deliberately not wired.

    A zero-result search is ZERO_RESULTS with regulatory_state REQUIRES VERIFICATION. It is NEVER
    a finding that the product is unregistered.
    """
    if not keyword or not str(keyword).strip():
        return {
            "status": STATUS_NOT_CONFIGURED,
            "regulatory_state": REGULATORY_STATE_REQUIRES_VERIFICATION,
            "error": "Empty keyword — refusing to issue an unbounded SFDA query.",
            "provenance": build_provenance("sfda", "SFDA", "", STATUS_NOT_CONFIGURED).to_dict(),
        }
    params = {"keyword": str(keyword).strip()}
    if page is not None:
        params["page"] = str(page)
    if page_size is not None:
        params["pageSize"] = str(page_size)
    return _call_service(product_type, params, str(keyword).strip())


def sfda_lookup_registration(registration_number, product_type="medical_device"):
    """
    Look up a specific SFDA registration number.

    The registration identifier is passed through as given — it is NOT normalised, reformatted or
    padded. SFDA registration formats are not publicly documented in a way this connector could
    verify, so any "correction" would risk designating a different product. An unrecognised
    identifier comes back as ZERO_RESULTS / REQUIRES VERIFICATION, never as "not registered".
    """
    if not registration_number or not str(registration_number).strip():
        return {
            "status": STATUS_NOT_CONFIGURED,
            "regulatory_state": REGULATORY_STATE_REQUIRES_VERIFICATION,
            "error": "Empty registration number.",
            "provenance": build_provenance("sfda", "SFDA", "", STATUS_NOT_CONFIGURED).to_dict(),
        }
    reg = str(registration_number).strip()
    return _call_service(product_type, {"registrationNumber": reg}, reg)


def connection_status():
    """Report configuration state without performing any request. Used by `start` and QC."""
    cfg = _config()
    missing = _missing_config(cfg, ["client_id", "client_secret", "token_url", "base_url"])
    configured = not missing
    return {
        "connector": "sfda",
        "configured": configured,
        "missing_configuration": missing,
        "status": STATUS_SUCCESS if configured else STATUS_NOT_CONNECTED_AUTH_REQUIRED,
        "connector_status_label": ("CONFIGURED — live validation still required"
                                    if configured else "NOT CONNECTED — AUTH REQUIRED"),
        "regulatory_state_when_unavailable": REGULATORY_STATE_REQUIRES_VERIFICATION,
        "developer_portal": DEVELOPER_PORTAL,
        "credentials_are_never_hardcoded": True,
    }


def _main():
    p = argparse.ArgumentParser(description="SFDA connector client")
    sub = p.add_subparsers(dest="command", required=True)

    ps = sub.add_parser("search")
    ps.add_argument("--keyword", required=True)
    ps.add_argument("--product-type", default="medical_device", choices=sorted(PRODUCT_TYPES))

    pl = sub.add_parser("lookup")
    pl.add_argument("--registration-number", required=True)
    pl.add_argument("--product-type", default="medical_device", choices=sorted(PRODUCT_TYPES))

    sub.add_parser("status")

    args = p.parse_args()
    if args.command == "search":
        result = sfda_search_product(args.keyword, product_type=args.product_type)
    elif args.command == "lookup":
        result = sfda_lookup_registration(args.registration_number, product_type=args.product_type)
    else:
        # `status` is an informational configuration report, not a lookup. It always exits 0 —
        # "credentials are absent" is a successful answer to the question it was asked.
        print(json.dumps(connection_status(), indent=2, ensure_ascii=False))
        sys.exit(0)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("status") in (STATUS_SUCCESS, STATUS_ZERO_RESULTS) else 1)


if __name__ == "__main__":
    _main()

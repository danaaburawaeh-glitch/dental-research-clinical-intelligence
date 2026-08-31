"""
connectors/sfda/errors.py

Failure taxonomy for the SFDA connector. Reuses the shared vocabulary; adds ONE state that the
other connectors do not need.

NOT_CONNECTED_AUTH_REQUIRED — the connector is implemented and callable, but no SFDA credentials
are configured in this environment, so no request can be made. This is deliberately NOT folded
into AUTH_ERROR (which means credentials were sent and rejected) and NOT into NOT_CONNECTED
(which implies no implementation). The distinction matters to the user: "nobody has configured
this yet" and "your key was refused" call for different actions.

Every failure state here maps to the SAME regulatory outcome: REQUIRES VERIFICATION. A connector
failure never becomes an assumed approval, an assumed refusal, or silence.
"""

STATUS_SUCCESS = "SUCCESS"
STATUS_ZERO_RESULTS = "ZERO_RESULTS"
STATUS_RATE_LIMITED = "RATE_LIMITED"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_AUTH_ERROR = "AUTH_ERROR"
STATUS_UPSTREAM_ERROR = "UPSTREAM_ERROR"
STATUS_PARSE_ERROR = "PARSE_ERROR"
STATUS_NOT_CONNECTED = "NOT_CONNECTED"
STATUS_NOT_CONNECTED_AUTH_REQUIRED = "NOT_CONNECTED_AUTH_REQUIRED"
STATUS_NOT_CONFIGURED = "NOT_CONFIGURED"

ALL_STATUSES = {
    STATUS_SUCCESS, STATUS_ZERO_RESULTS, STATUS_RATE_LIMITED, STATUS_TIMEOUT,
    STATUS_AUTH_ERROR, STATUS_UPSTREAM_ERROR, STATUS_PARSE_ERROR, STATUS_NOT_CONNECTED,
    STATUS_NOT_CONNECTED_AUTH_REQUIRED, STATUS_NOT_CONFIGURED,
}

# Every non-SUCCESS status resolves to this regulatory state. Enforced by regulatory_state().
REGULATORY_STATE_VERIFIED = "VERIFIED"
REGULATORY_STATE_REQUIRES_VERIFICATION = "REQUIRES VERIFICATION"
REGULATORY_STATE_NOT_APPLICABLE = "NOT APPLICABLE"
REGULATORY_STATE_UNKNOWN_CONFLICT = "UNKNOWN / CONFLICT"

ZERO_RESULTS_MEANING = (
    "The executed SFDA query returned no matching record. This is NOT a finding that the product "
    "is unregistered or unapproved in Saudi Arabia — SFDA coverage, product naming and "
    "transliteration all vary. The regulatory state remains REQUIRES VERIFICATION."
)

AUTH_REQUIRED_MEANING = (
    "SFDA credentials are not configured in this environment, so no lookup was performed. This "
    "says nothing about the product's Saudi status. Register an application at "
    "developer.sfda.gov.sa and set SFDA_CLIENT_ID / SFDA_CLIENT_SECRET. The regulatory state "
    "remains REQUIRES VERIFICATION."
)


class SFDAConnectorError(Exception):
    def __init__(self, status, message, http_status=None):
        assert status in ALL_STATUSES, f"Unknown status: {status}"
        self.status = status
        self.http_status = http_status
        super().__init__(message)


def classify_http_status(http_status):
    if http_status is None:
        return STATUS_TIMEOUT
    if 200 <= http_status < 300:
        return None
    if http_status == 429:
        return STATUS_RATE_LIMITED
    if http_status in (401, 403):
        return STATUS_AUTH_ERROR
    if 500 <= http_status < 600:
        return STATUS_UPSTREAM_ERROR
    return STATUS_UPSTREAM_ERROR


def regulatory_state(status, matched=False):
    """
    THE load-bearing function of this connector.

    Maps a connector status to one of the four regulatory states from saudi-regulatory-gate.md.
    Only a SUCCESS *with an actual matching record* can yield VERIFIED. Everything else — no
    match, no credentials, timeout, rate limit, parse failure, rejected key — yields REQUIRES
    VERIFICATION.

    There is deliberately NO path from any failure to a "not approved" conclusion. Absence of a
    record is not evidence of absence of registration.
    """
    if status == STATUS_SUCCESS and matched:
        return REGULATORY_STATE_VERIFIED
    return REGULATORY_STATE_REQUIRES_VERIFICATION

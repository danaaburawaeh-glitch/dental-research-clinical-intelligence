"""
connectors/sfda/models.py

SFDAProductRecord and a defensive parser.

The SFDA response schema is NOT publicly documented — the field list is visible only to a
registered application. The parser therefore does not assume a shape: it accepts several plausible
envelopes, maps a set of candidate field names, and preserves the complete raw record so nothing
is lost when the real schema differs from any guess. Fields that cannot be located stay None.

This is the honest way to write a parser against an undocumented schema: tolerate, preserve,
never invent. A field reported as None means "this parser could not find it", which is a different
and safer claim than "SFDA does not provide it".
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List

PRODUCT_TYPES = {"medical_device", "drug"}

# Candidate keys, in priority order. Extended once the real schema is observed with credentials.
_FIELD_CANDIDATES = {
    "registration_number": ("registrationNumber", "registration_no", "registrationNo",
                            "licenseNumber", "productRegistrationNumber", "regNo", "id"),
    "product_name": ("productName", "name", "tradeName", "product_name_en", "productNameEn",
                     "deviceName", "drugName"),
    "product_name_ar": ("productNameAr", "name_ar", "tradeNameAr", "arabicName"),
    "manufacturer": ("manufacturer", "manufacturerName", "companyName", "factoryName"),
    "country_of_origin": ("countryOfOrigin", "country", "manufacturerCountry"),
    "authorization_holder": ("authorizationHolder", "marketingAuthorizationHolder",
                             "agentName", "distributor", "licenseHolder"),
    "status": ("status", "registrationStatus", "productStatus", "state"),
    "risk_class": ("riskClass", "deviceClass", "classification", "class"),
    "issue_date": ("issueDate", "registrationDate", "approvalDate", "startDate"),
    "expiry_date": ("expiryDate", "expirationDate", "validUntil", "endDate"),
}

_LIST_CANDIDATES = ("results", "data", "items", "products", "content", "records", "list")


@dataclass
class SFDAProductRecord:
    registration_number: Optional[str] = None
    product_name: Optional[str] = None
    product_name_ar: Optional[str] = None
    manufacturer: Optional[str] = None
    country_of_origin: Optional[str] = None
    authorization_holder: Optional[str] = None
    status: Optional[str] = None
    risk_class: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    product_type: Optional[str] = None

    # The complete unmodified record, so an undocumented field is never lost to a mapping gap.
    raw: Optional[Dict[str, Any]] = None

    # Provenance (M4 requires a Saudi regulatory claim to be traceable to its source record)
    source_connector: str = "sfda"
    source_database: str = "SFDA"
    retrieved_at: Optional[str] = None
    query: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def _first(d, keys):
    for k in keys:
        if k in d and d[k] not in (None, "", []):
            return d[k]
    # case-insensitive second pass — the real schema's casing is unverified
    lowered = {str(k).lower(): v for k, v in d.items()}
    for k in keys:
        v = lowered.get(k.lower())
        if v not in (None, "", []):
            return v
    return None


def _extract_list(payload):
    """Find the record list in an envelope whose shape is not documented."""
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in _LIST_CANDIDATES:
        v = payload.get(key)
        if isinstance(v, list):
            return v
        # one level of nesting, e.g. {"data": {"items": [...]}}
        if isinstance(v, dict):
            for inner in _LIST_CANDIDATES:
                if isinstance(v.get(inner), list):
                    return v[inner]
    # A single record returned bare rather than in a list.
    if any(k in payload for k in _FIELD_CANDIDATES["registration_number"]):
        return [payload]
    return []


def parse_products(payload, product_type=None, query=None, retrieved_at=None):
    """Parse an SFDA response into a list of record dicts. Returns [] for an empty result set."""
    out: List[Dict[str, Any]] = []
    for item in _extract_list(payload):
        if not isinstance(item, dict):
            continue
        rec = SFDAProductRecord(
            product_type=product_type, raw=item, query=query, retrieved_at=retrieved_at,
            **{field: _first(item, keys) for field, keys in _FIELD_CANDIDATES.items()}
        )
        out.append(rec.to_dict())
    return out

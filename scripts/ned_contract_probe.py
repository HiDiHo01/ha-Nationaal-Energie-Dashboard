"""Run a bounded, explicitly authorized NED contract observation."""

import http.client
import json
import os
import sys
from datetime import UTC, date, datetime, timedelta
from urllib.parse import urlencode

HOST = "api.ned.nl"
MAX_BYTES = 2 * 1024 * 1024
TRANSPORT_ERRORS = (OSError, http.client.HTTPException, ValueError, RecursionError)
FIELDS = (
    "id",
    "type",
    "point",
    "activity",
    "classification",
    "granularity",
    "granularitytimezone",
    "capacity",
    "volume",
    "emission",
    "emissionfactor",
    "percentage",
    "validfrom",
    "validto",
    "lastupdate",
)


class ProbeError(Exception):
    """Represent a safe diagnostic without upstream payloads or credentials."""


PROBE_ERRORS = (ProbeError, *TRANSPORT_ERRORS)


def report_failure(error: Exception) -> int:
    """Report a safe diagnostic without upstream exception details."""
    message = str(error) if isinstance(error, ProbeError) else "transport or JSON error"
    print(f"Contract observation failed: {message}", file=sys.stderr)
    return 1


def build_path(classification: int, day: date) -> str:
    """Build a single documented national solar query for one UTC day."""
    if classification not in (1, 2):
        raise ProbeError("Unsupported classification")
    query = urlencode(
        {
            "page": 1,
            "itemsPerPage": 100,
            "order[validfrom]": "asc",
            "point": 0,
            "type": 2,
            "activity": 1,
            "granularity": 4,
            "granularitytimezone": 0,
            "classification": classification,
            "validfrom[after]": day.isoformat(),
            "validfrom[strictly_before]": (day + timedelta(days=1)).isoformat(),
        }
    )
    return f"/v1/utilizations?{query}"


def summarize(body: bytes) -> dict[str, object]:
    """Describe collection shape without exposing any raw upstream values."""
    document: object = json.loads(body)
    if not isinstance(document, dict):
        raise ProbeError("Expected a JSON-LD collection object")
    for member_key in ("hydra:member", "member"):
        if member_key in document:
            members = document[member_key]
            break
    else:
        raise ProbeError("Unrecognized collection envelope; schema review required")
    if not isinstance(members, list) or any(
        not isinstance(record, dict) for record in members
    ):
        raise ProbeError("Collection members must be objects")
    shapes = {
        field: sorted(
            {
                type(record[field]).__name__ if field in record else "missing"
                for record in members
            }
        )
        for field in FIELDS
    }
    total = document.get("hydra:totalItems")
    view = document.get("hydra:view")
    return {
        "member_key": member_key,
        "record_count": len(members),
        "field_types": shapes,
        "total_items_type": type(total).__name__
        if "hydra:totalItems" in document
        else "missing",
        "next_link_present": isinstance(view, dict) and "hydra:next" in view,
        "pagination_metadata_present": any(
            key in document for key in ("hydra:view", "view")
        ),
    }


def fetch_body(api_key: str, path: str) -> bytes:
    """Issue one TLS-verified GET to the fixed host without redirects or retries."""
    if not path.startswith("/v1/utilizations?"):
        raise ProbeError("Request outside approved endpoint")
    connection = http.client.HTTPSConnection(HOST, timeout=15)
    try:
        connection.request(
            "GET",
            path,
            headers={"Accept": "application/ld+json", "X-AUTH-TOKEN": api_key},
        )
        response = connection.getresponse()
        if response.status != 200:
            raise ProbeError(f"Unexpected HTTP status: {response.status}")
        content_type = response.getheader("Content-Type", "").split(";", 1)[0]
        if content_type.strip().lower() != "application/ld+json":
            raise ProbeError("Unexpected response media type")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ProbeError("Response exceeds safety limit")
        return body
    finally:
        connection.close()


def probe(api_key: str, classification: int, day: date) -> dict[str, object]:
    """Summarize the initial national solar query."""
    return summarize(fetch_body(api_key, build_path(classification, day)))


def main() -> int:
    """Require credentials and report only sanitized contract observations."""
    api_key = os.environ.get("NED_API_KEY", "")
    if not api_key.isascii() or not api_key.isprintable() or not api_key.strip():
        print("Missing or invalid NED_API_KEY", file=sys.stderr)
        return 1
    today = datetime.now(UTC).date()
    try:
        for classification, day in (
            (2, today - timedelta(days=2)),
            (1, today + timedelta(days=1)),
        ):
            result = probe(api_key, classification, day)
            observation = {"classification": classification, **result}
            print(json.dumps(observation, sort_keys=True))
            if result["record_count"] == 0:
                raise ProbeError("Empty collection; no record evidence")
    except PROBE_ERRORS as error:
        return report_failure(error)
    print("Two bounded observations completed; full contract validation remains open.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

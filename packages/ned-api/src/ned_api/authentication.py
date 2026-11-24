"""Prepare bounded NED credential verification against the documented endpoint.

Only a positive response to the fixed solar query is evidence of access.
Unexpected statuses and empty collections do not prove an invalid key.
This client remains an offline-tested draft until contract release.
"""

import json
from datetime import UTC, datetime, timedelta

from aiohttp import ClientSession

from .exceptions import NedResponseError, NedValidationError
from .transport import NedTransport, TransportResponse

_ORIGIN = "https://api.ned.nl"
_PATH = "/v1/utilizations"
_MEDIA_TYPE = "application/ld+json"
_DIMENSIONS = {
    "point": ("points", 0),
    "type": ("types", 2),
    "activity": ("activities", 1),
    "classification": ("classifications", 2),
    "granularity": ("granularities", 4),
    "granularitytimezone": ("granularity_time_zones", 0),
}


def _validate_response(response: TransportResponse) -> None:
    """Require positive structural evidence without assigning error statuses."""
    if response.status != 200:
        raise NedResponseError(
            f"Credential verification returned HTTP {response.status}; "
            "access could not be established."
        )
    if response.media_type != _MEDIA_TYPE:
        raise NedResponseError("Unexpected credential verification media type.")
    try:
        document: object = json.loads(response.body)
    except (ValueError, RecursionError):
        document = None
    if not isinstance(document, dict):
        raise NedResponseError("Expected a JSON-LD collection object.")
    members = document.get("hydra:member")
    if not isinstance(members, list) or not 1 <= len(members) <= 96:
        raise NedResponseError("No bounded nonempty collection evidence.")
    for member in members:
        if not isinstance(member, dict):
            raise NedResponseError("Invalid collection member.")
        for field, (resource, identifier) in _DIMENSIONS.items():
            iri = f"/v1/{resource}/{identifier}"
            if member.get(field) not in (iri, f"{_ORIGIN}{iri}"):
                raise NedResponseError("Unexpected verification dataset dimension.")


class NedAuthenticationClient:
    """Validate access using a borrowed session and a fixed HTTPS origin."""

    def __init__(self, session: ClientSession) -> None:
        """Construct the transport without retaining credentials."""
        self._transport = NedTransport(session, _ORIGIN)

    async def async_validate_api_key(self, api_key: str) -> None:
        """Perform one bounded historical solar request without retries.

        A successful response confirms access only to this request, not
        authorization for every dataset. No raw response or token is returned.
        """
        if (
            not api_key
            or not api_key.isascii()
            or not api_key.isprintable()
            or any(character.isspace() for character in api_key)
        ):
            raise NedValidationError("Provide a nonempty printable ASCII API key.")
        day = datetime.now(UTC).date() - timedelta(days=2)
        params = {
            field: str(identifier) for field, (_, identifier) in _DIMENSIONS.items()
        }
        params.update(
            {
                "page": "1",
                "itemsPerPage": "100",
                "order[validfrom]": "asc",
                "validfrom[after]": day.isoformat(),
                "validfrom[strictly_before]": (day + timedelta(days=1)).isoformat(),
            }
        )
        response = await self._transport.async_get(
            _PATH,
            params=params,
            headers={"Accept": _MEDIA_TYPE, "X-AUTH-TOKEN": api_key},
        )
        _validate_response(response)

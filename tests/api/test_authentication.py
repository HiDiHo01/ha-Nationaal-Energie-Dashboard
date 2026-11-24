"""Test bounded credential verification with synthetic responses only."""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession

from ned_api import (
    NedAuthenticationClient,
    NedResponseError,
    NedValidationError,
    TransportResponse,
)

_MEDIA_TYPE = "application/ld+json"
_RECORD = {
    "point": "/v1/points/0",
    "type": "/v1/types/2",
    "activity": "/v1/activities/1",
    "classification": "/v1/classifications/2",
    "granularity": "/v1/granularities/4",
    "granularitytimezone": "/v1/granularity_time_zones/0",
}


@pytest.mark.asyncio
async def test_positive_access() -> None:
    """Send the key only in a header and require matching dataset evidence."""
    session = MagicMock(spec=ClientSession)
    client = NedAuthenticationClient(session)
    result = TransportResponse(
        200, json.dumps({"hydra:member": [_RECORD]}).encode(), _MEDIA_TYPE
    )
    with patch("ned_api.transport.NedTransport.async_get", new_callable=AsyncMock) as get:
        get.return_value = result
        await client.async_validate_api_key("synthetic-key")
    get.assert_awaited_once()
    assert get.call_args.args == ("/v1/utilizations",)
    kwargs = get.call_args.kwargs
    assert kwargs["headers"] == {
        "Accept": _MEDIA_TYPE,
        "X-AUTH-TOKEN": "synthetic-key",
    }
    params = kwargs["params"]
    day = datetime.now(UTC).date() - timedelta(days=2)
    assert params["validfrom[after]"] == day.isoformat()
    assert params["validfrom[strictly_before]"] == (day + timedelta(days=1)).isoformat()
    assert params["type"] == "2"
    assert "synthetic-key" not in repr(params)


@pytest.mark.parametrize("key", ["", " ", "bad key", "bad\nkey", "é"])
@pytest.mark.asyncio
async def test_invalid_key_format(key: str) -> None:
    """Reject unsafe header values without sending a request."""
    client = NedAuthenticationClient(MagicMock(spec=ClientSession))
    with (
        patch("ned_api.transport.NedTransport.async_get", new_callable=AsyncMock) as get,
        pytest.raises(NedValidationError),
    ):
        await client.async_validate_api_key(key)
    get.assert_not_awaited()


@pytest.mark.parametrize(
    "response",
    [
        TransportResponse(401, b"synthetic-key", _MEDIA_TYPE),
        TransportResponse(403, b"synthetic-key", _MEDIA_TYPE),
        TransportResponse(429, b"synthetic-key", _MEDIA_TYPE),
        TransportResponse(503, b"synthetic-key", _MEDIA_TYPE),
        TransportResponse(200, b"{}", "text/html"),
        TransportResponse(200, b"not-json", _MEDIA_TYPE),
        TransportResponse(200, b"[]", _MEDIA_TYPE),
        TransportResponse(200, b"{}", _MEDIA_TYPE),
        TransportResponse(200, b'{"hydra:member":[]}', _MEDIA_TYPE),
        TransportResponse(200, b'{"hydra:member":[0]}', _MEDIA_TYPE),
        TransportResponse(200, b'{"hydra:member":[{}]}', _MEDIA_TYPE),
    ],
)
@pytest.mark.asyncio
async def test_inconclusive_response(response: TransportResponse) -> None:
    """Avoid inferring invalid credentials from unknown statuses or empty data."""
    client = NedAuthenticationClient(MagicMock(spec=ClientSession))
    with (
        patch("ned_api.transport.NedTransport.async_get", new_callable=AsyncMock) as get,
        pytest.raises(NedResponseError) as raised,
    ):
        get.return_value = response
        await client.async_validate_api_key("synthetic-key")
    assert "synthetic-key" not in str(raised.value)
    get.assert_awaited_once()

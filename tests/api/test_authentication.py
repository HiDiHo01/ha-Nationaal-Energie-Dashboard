"""Test bounded credential verification with synthetic responses only."""

import json
from datetime import UTC, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession

from ned_api import (
    NedAccessDeniedError,
    NedApiError,
    NedAuthenticationClient,
    NedAuthenticationError,
    NedRateLimitError,
    NedRequestBudget,
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
    assert client.origin == "https://api.ned.nl"
    day = datetime.now(UTC).date() - timedelta(days=2)
    start = datetime.combine(day, time.min, tzinfo=UTC)
    record = _RECORD | {
        "validfrom": start.isoformat(),
        "validto": (start + timedelta(minutes=15)).isoformat(),
        "capacity": 0,
    }
    result = TransportResponse(
        200,
        json.dumps({"hydra:member": [record], "hydra:totalItems": 1}).encode(),
        _MEDIA_TYPE,
    )
    with patch(
        "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
    ) as get:
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
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
        pytest.raises(NedValidationError),
    ):
        await client.async_validate_api_key(key)
    get.assert_not_awaited()


@pytest.mark.parametrize(
    "response",
    [
        TransportResponse(503, b"synthetic-key", _MEDIA_TYPE),
        TransportResponse(200, b"{}", "text/html"),
        TransportResponse(200, b"not-json", _MEDIA_TYPE),
        TransportResponse(200, b"[]", _MEDIA_TYPE),
        TransportResponse(200, b"{}", _MEDIA_TYPE),
        TransportResponse(200, b'{"hydra:member":[],"hydra:totalItems":0}', _MEDIA_TYPE),
        TransportResponse(200, b'{"hydra:member":[0],"hydra:totalItems":1}', _MEDIA_TYPE),
        TransportResponse(200, b'{"hydra:member":[{}],"hydra:totalItems":1}', _MEDIA_TYPE),
    ],
)
@pytest.mark.asyncio
async def test_inconclusive_response(response: TransportResponse) -> None:
    """Avoid inferring invalid credentials from unknown statuses or empty data."""
    client = NedAuthenticationClient(MagicMock(spec=ClientSession))
    with (
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
        pytest.raises(NedResponseError) as raised,
    ):
        get.return_value = response
        await client.async_validate_api_key("synthetic-key")
    assert "synthetic-key" not in str(raised.value)
    get.assert_awaited_once()


@pytest.mark.parametrize(
    ("response", "expected_error"),
    [
        (
            TransportResponse(
                401,
                b'{"hydra:title":"Synthetic","hydra:description":"synthetic-key"}',
                _MEDIA_TYPE,
            ),
            NedAuthenticationError,
        ),
        (
            TransportResponse(403, b'{"message":"synthetic-key"}', "application/json"),
            NedAccessDeniedError,
        ),
        (TransportResponse(401, b"not-json", "text/html"), NedAuthenticationError),
        (TransportResponse(403, b"", ""), NedAccessDeniedError),
    ],
)
@pytest.mark.asyncio
async def test_access_denial(
    response: TransportResponse, expected_error: type[NedApiError]
) -> None:
    """Distinguish observed HTTP denials without leaking or trusting error text."""
    client = NedAuthenticationClient(MagicMock(spec=ClientSession))
    with (
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
        pytest.raises(expected_error) as raised,
    ):
        get.return_value = response
        await client.async_validate_api_key("synthetic-key")
    assert type(raised.value) is expected_error
    assert "synthetic-key" not in str(raised.value)
    assert raised.value.__cause__ is None
    assert raised.value.__context__ is None
    get.assert_awaited_once()


@pytest.mark.asyncio
async def test_authentication_shares_budget() -> None:
    """Pause a second verifier after the first receives HTTP 429."""
    budget = NedRequestBudget()
    session = MagicMock(spec=ClientSession)
    first = NedAuthenticationClient(session, budget)
    second = NedAuthenticationClient(session, budget)
    with patch(
        "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
    ) as get:
        get.return_value = TransportResponse(429, b"synthetic", _MEDIA_TYPE)
        with pytest.raises(NedRateLimitError):
            await first.async_validate_api_key("synthetic-key")
        assert budget.remaining == 0
        with pytest.raises(NedRateLimitError):
            await second.async_validate_api_key("synthetic-key")
        get.assert_awaited_once()

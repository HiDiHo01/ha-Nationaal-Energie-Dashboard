"""Verify local attempt limits and conservative cooldown without network access."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ned_api import (
    NedConnectionError,
    NedRateLimitError,
    NedRequestBudget,
    NedTransport,
    TransportResponse,
)


@pytest.mark.asyncio
async def test_window_and_failed_attempts() -> None:
    """Count attempts before I/O and expire them at the rolling-window boundary."""
    budget = NedRequestBudget()
    transport = MagicMock(spec=NedTransport)
    transport.async_get = AsyncMock(return_value=TransportResponse(200, b"{}"))
    with patch("ned_api.rate_limiter.monotonic", return_value=1000.0) as clock:
        assert budget.remaining == 120
        transport.async_get.side_effect = NedConnectionError("synthetic")
        with pytest.raises(NedConnectionError):
            await budget.async_get(transport, "/v1/test", params={}, headers={})
        transport.async_get.side_effect = None
        for _ in range(59):
            await budget.async_get(transport, "/v1/test", params={}, headers={})
        assert budget.remaining == 0
        clock.return_value = 1299.0
        with pytest.raises(NedRateLimitError):
            await budget.async_get(transport, "/v1/test", params={}, headers={})
        assert transport.async_get.await_count == 60
        clock.return_value = 1300.0
        assert budget.remaining == 120
        await budget.async_get(transport, "/v1/test", params={}, headers={})
        assert budget.remaining == 118


@pytest.mark.asyncio
async def test_cooldown() -> None:
    """Do not send another request during the local HTTP 429 cooldown."""
    budget = NedRequestBudget()
    transport = MagicMock(spec=NedTransport)
    transport.async_get = AsyncMock(return_value=TransportResponse(429, b"synthetic"))
    with patch("ned_api.rate_limiter.monotonic", return_value=1000.0) as clock:
        with pytest.raises(NedRateLimitError):
            await budget.async_get(transport, "/v1/test", params={}, headers={})
        clock.return_value = 1299.0
        assert budget.remaining == 0
        with pytest.raises(NedRateLimitError):
            await budget.async_get(transport, "/v1/test", params={}, headers={})
        transport.async_get.assert_awaited_once()
        clock.return_value = 1300.0
        transport.async_get.return_value = TransportResponse(200, b"{}")
        await budget.async_get(transport, "/v1/test", params={}, headers={})
        assert budget.remaining == 118


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, 300.0),
        (0.0, 300.0),
        (900.0, 900.0),
        (86400.0, 86400.0),
        (86401.0, 300.0),
        (float("inf"), 300.0),
    ],
)
@pytest.mark.asyncio
async def test_server_delay(value: float | None, expected: float) -> None:
    """Never shorten a valid server delay; extreme delays stop the process budget."""
    budget = NedRequestBudget()
    transport = MagicMock(spec=NedTransport)
    transport.async_get = AsyncMock(
        return_value=TransportResponse(429, b"", retry_after=value)
    )
    with patch("ned_api.rate_limiter.monotonic", return_value=1000.0) as clock:
        with pytest.raises(NedRateLimitError):
            await budget.async_get(transport, "/test", params={}, headers={})
        assert budget.retry_after == expected
        clock.return_value = 1000.0 + expected - 1
        assert budget.remaining == 0
        clock.return_value += 1
        if value is not None and value > 86400:
            assert budget.remaining == 0
        else:
            assert budget.remaining == 120


@pytest.mark.asyncio
async def test_instrumented_budget() -> None:
    """Count middleware invocations, including failed and cancelled attempts."""
    budget = NedRequestBudget(instrumented=True)
    request = MagicMock()
    response = MagicMock()
    response.status = 200
    handler = AsyncMock(return_value=response)
    transport = MagicMock(spec=NedTransport)
    transport.async_get = AsyncMock(return_value=TransportResponse(200, b""))
    with patch("ned_api.rate_limiter.monotonic", return_value=1000.0):
        for _ in range(119):
            assert await budget.async_middleware(request, handler) is response
        assert budget.remaining == 1
        await budget.async_get(transport, "/test", params={}, headers={})
        await budget.async_middleware(request, handler)
        assert budget.remaining == 0
        with pytest.raises(NedRateLimitError):
            await budget.async_get(transport, "/test", params={}, headers={})
        with pytest.raises(NedRateLimitError):
            await budget.async_middleware(request, handler)
        assert handler.await_count == 120


@pytest.mark.asyncio
async def test_middleware_429() -> None:
    """Apply cooldown at headers before any error-body processing."""
    budget = NedRequestBudget(instrumented=True)
    response = MagicMock()
    response.status = 429
    response.headers = {"Retry-After": "900"}
    handler = AsyncMock(return_value=response)
    with patch("ned_api.rate_limiter.monotonic", return_value=1000.0):
        with pytest.raises(NedRateLimitError):
            await budget.async_middleware(MagicMock(), handler)
        assert budget.remaining == 0
        assert budget.retry_after == 900
        response.close.assert_called_once()

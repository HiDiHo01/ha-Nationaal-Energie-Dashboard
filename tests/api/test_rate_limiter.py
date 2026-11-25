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
        for _ in range(119):
            await budget.async_get(transport, "/v1/test", params={}, headers={})
        assert budget.remaining == 0
        clock.return_value = 1299.0
        with pytest.raises(NedRateLimitError):
            await budget.async_get(transport, "/v1/test", params={}, headers={})
        assert transport.async_get.await_count == 120
        clock.return_value = 1300.0
        assert budget.remaining == 120
        await budget.async_get(transport, "/v1/test", params={}, headers={})
        assert budget.remaining == 119


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
        assert budget.remaining == 119

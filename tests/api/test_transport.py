"""Exercise the HTTP transport with synthetic responses and no network."""

from asyncio import CancelledError
from collections.abc import AsyncIterator
from unittest.mock import MagicMock

import pytest
from aiohttp import (
    ClientConnectionError,
    ClientPayloadError,
    ClientSession,
    ClientTimeout,
)
from yarl import URL

from ned_api import (
    NedApiError,
    NedConnectionError,
    NedResponseError,
    NedTimeoutError,
    NedTransport,
    NedValidationError,
    TransportResponse,
)


async def _chunks(*parts: bytes) -> AsyncIterator[bytes]:
    """Yield synthetic response fragments."""
    for part in parts:
        yield part


async def _cancelled_chunks() -> AsyncIterator[bytes]:
    """Simulate cancellation during streaming."""
    yield b"a"
    raise CancelledError


@pytest.fixture(name="exchange")
def _exchange() -> tuple[MagicMock, MagicMock]:
    """Return a borrowed mock session and its context-managed response."""
    session = MagicMock(spec=ClientSession)
    session.closed = False
    response = MagicMock()
    response.status = 200
    response.headers = {}
    response.content.iter_chunked.return_value = _chunks(b"a", b"bc")
    session.get.return_value.__aenter__.return_value = response
    return session, response


@pytest.mark.parametrize("status", [200, 302, 401, 403, 429, 503])
@pytest.mark.asyncio
async def test_request_options_and_uninterpreted_status(
    exchange: tuple[MagicMock, MagicMock], status: int
) -> None:
    """Enforce HTTPS options, preserve status and keep session ownership."""
    session, response = exchange
    response.status = status
    transport = NedTransport(session, "https://example.invalid", max_response_bytes=3)
    assert transport.origin == URL("https://example.invalid")
    result = await transport.async_get("/resource", params={"page": "1"})
    assert result == TransportResponse(status=status, body=b"abc")
    assert "abc" not in repr(result)
    session.get.assert_called_once_with(
        URL("https://example.invalid/resource"),
        params={"page": "1"},
        timeout=ClientTimeout(total=15.0),
        allow_redirects=False,
        raise_for_status=False,
        ssl=True,
        auto_decompress=False,
        headers={"Accept-Encoding": "identity"},
    )
    response.content.iter_chunked.assert_called_once_with(4)
    session.get.return_value.__aexit__.assert_awaited_once()
    session.close.assert_not_awaited()


@pytest.mark.parametrize(
    "origin",
    [
        "http://example.invalid",
        "https:///",
        "https://name@example.invalid",
        "https://:synthetic@example.invalid",
        "https://example.invalid/endpoint",
        "https://example.invalid?q=1",
        "https://example.invalid#fragment",
        "https://example.invalid:0",
        "https://example.invalid:99999",
        "https://[",
    ],
)
def test_invalid_origin(exchange: tuple[MagicMock, MagicMock], origin: str) -> None:
    """Reject insecure or malformed origins without echoing the input."""
    session, _ = exchange
    with pytest.raises(NedValidationError, match="credential-free HTTPS origin"):
        NedTransport(session, origin)
    session.get.assert_not_called()


@pytest.mark.parametrize("timeout", [0.0, -1.0, float("inf"), float("nan"), True])
def test_invalid_timeout(exchange: tuple[MagicMock, MagicMock], timeout: float) -> None:
    """Reject nonpositive and nonfinite time budgets."""
    session, _ = exchange
    with pytest.raises(NedValidationError, match="finite positive"):
        NedTransport(session, "https://example.invalid", timeout=timeout)


@pytest.mark.parametrize("limit", [0, -1, True])
def test_invalid_limit(exchange: tuple[MagicMock, MagicMock], limit: int) -> None:
    """Reject unusable response byte limits."""
    session, _ = exchange
    with pytest.raises(NedValidationError, match="positive integer"):
        NedTransport(session, "https://example.invalid", max_response_bytes=limit)


@pytest.mark.parametrize(
    "path",
    ["resource", "//other.invalid", "/a?b", "/a#b", "/a\\b", "/a/../b", "/a\nb"],
)
@pytest.mark.asyncio
async def test_invalid_path(exchange: tuple[MagicMock, MagicMock], path: str) -> None:
    """Reject paths that contain ambiguous URL components."""
    session, _ = exchange
    transport = NedTransport(session, "https://example.invalid")
    with pytest.raises(NedValidationError, match="absolute path"):
        await transport.async_get(path)
    session.get.assert_not_called()


@pytest.mark.asyncio
async def test_closed_session(exchange: tuple[MagicMock, MagicMock]) -> None:
    """Report a closed borrowed session without attempting a request."""
    session, _ = exchange
    session.closed = True
    transport = NedTransport(session, "https://example.invalid")
    with pytest.raises(NedConnectionError, match="session is closed"):
        await transport.async_get("/resource")
    session.get.assert_not_called()


@pytest.mark.asyncio
async def test_response_limit(exchange: tuple[MagicMock, MagicMock]) -> None:
    """Reject a response exceeding its cumulative byte budget."""
    session, _ = exchange
    transport = NedTransport(session, "https://example.invalid", max_response_bytes=2)
    with pytest.raises(NedResponseError, match="byte limit"):
        await transport.async_get("/resource")
    session.get.return_value.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_encoded_response(exchange: tuple[MagicMock, MagicMock]) -> None:
    """Reject compressed data before reading the response body."""
    session, response = exchange
    response.headers = {"Content-Encoding": "gzip"}
    transport = NedTransport(session, "https://example.invalid")
    with pytest.raises(NedResponseError, match="content encoding"):
        await transport.async_get("/resource")
    response.content.iter_chunked.assert_not_called()
    session.get.return_value.__aexit__.assert_awaited_once()


@pytest.mark.parametrize(
    ("original_error", "error_type"),
    [
        (TimeoutError("private synthetic detail"), NedTimeoutError),
        (ClientPayloadError("private synthetic detail"), NedResponseError),
        (ClientConnectionError("private synthetic detail"), NedConnectionError),
    ],
)
@pytest.mark.asyncio
async def test_sanitized_transport_errors(
    exchange: tuple[MagicMock, MagicMock],
    original_error: Exception,
    error_type: type[NedApiError],
) -> None:
    """Translate transport errors without retaining raw exception context."""
    session, _ = exchange
    session.get.return_value.__aenter__.side_effect = original_error
    transport = NedTransport(session, "https://example.invalid")
    with pytest.raises(error_type) as caught:
        await transport.async_get("/resource")
    assert "private synthetic detail" not in str(caught.value)
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    session.close.assert_not_awaited()


@pytest.mark.asyncio
async def test_stream_cancellation(exchange: tuple[MagicMock, MagicMock]) -> None:
    """Propagate cancellation and leave response and session ownership intact."""
    session, response = exchange
    response.content.iter_chunked.return_value = _cancelled_chunks()
    transport = NedTransport(session, "https://example.invalid")
    with pytest.raises(CancelledError):
        await transport.async_get("/resource")
    session.get.return_value.__aexit__.assert_awaited_once()
    session.close.assert_not_awaited()

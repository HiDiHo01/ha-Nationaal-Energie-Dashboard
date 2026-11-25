"""Provide bounded, contract-independent HTTPS transport."""

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from aiohttp import ClientError, ClientPayloadError, ClientSession, ClientTimeout, hdrs
from yarl import URL

from .exceptions import (
    NedApiError,
    NedConnectionError,
    NedResponseError,
    NedTimeoutError,
    NedValidationError,
)


@dataclass(frozen=True, slots=True)
class TransportResponse:
    """Return an uninterpreted HTTP status and body, hidden from repr."""

    status: int
    body: bytes = field(repr=False)
    media_type: str = field(default="", repr=False)
    retry_after: float | None = None


def parse_retry_after(value: str | None) -> float | None:
    """Normalize HTTP delay-seconds or HTTP-date without retaining raw headers."""
    if value is None:
        return None
    header = value.strip()
    if header.isascii() and header.isdecimal():
        digits = header.lstrip("0") or "0"
        return math.inf if len(digits) > 6 else float(digits)
    try:
        date_value = parsedate_to_datetime(header)
    except ValueError, TypeError, OverflowError:
        return None
    if date_value.tzinfo is None:
        # RFC 9110 section 5.6.7: obsolete asctime-date uses implicit GMT.
        if not re.fullmatch(
            r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) "
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) "
            r"(?:[0-9]{2}| [0-9]) [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}",
            header,
        ):
            return None
        date_value = date_value.replace(tzinfo=UTC)
    return max(0.0, (date_value - datetime.now(UTC)).total_seconds())


def _parse_origin(origin: str) -> URL:
    """Require a credential-free HTTPS origin, not an endpoint URL."""
    candidate: URL | None
    try:
        candidate = URL(origin)
        port = candidate.port
    except ValueError:
        candidate = None
        port = None
    if candidate is None or port is None:
        raise NedValidationError("Provide a credential-free HTTPS origin.")
    if any(
        (
            candidate.scheme != "https",
            not candidate.raw_host,
            candidate.raw_user is not None,
            candidate.raw_password is not None,
            candidate.path != "/",
            candidate.query_string,
            candidate.fragment,
            not 1 <= port <= 65535,
        )
    ):
        raise NedValidationError("Provide a credential-free HTTPS origin.")
    return candidate


class NedTransport:
    """Borrow an HTTP session and issue bounded GET requests to one origin."""

    def __init__(
        self,
        session: ClientSession,
        origin: str,
        *,
        timeout: float = 15.0,
        max_response_bytes: int = 2 * 1024 * 1024,
    ) -> None:
        """Validate transport limits without opening or owning a session."""
        if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise NedValidationError("Timeout must be a finite positive number.")
        if isinstance(max_response_bytes, bool) or max_response_bytes <= 0:
            raise NedValidationError("Response limit must be a positive integer.")
        self._origin = _parse_origin(origin)
        self._session = session
        self._timeout = ClientTimeout(total=timeout)
        self._max_response_bytes = max_response_bytes

    @property
    def origin(self) -> URL:
        """Expose the immutable request origin for future same-origin checks."""
        return self._origin

    async def async_get(
        self,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> TransportResponse:
        """Fetch one path with non-secret query parameters, without redirects.

        Return error status and sanitized retry metadata without reading error bodies.
        Reject encoded or oversized successful responses. Never close the session.
        Headers are supplied by trusted callers for this fixed origin only;
        redirects remain disabled and credentials must never be query parameters.
        """
        if any(
            (
                not path.startswith("/"),
                path.startswith("//"),
                "?" in path,
                "#" in path,
                "\\" in path,
                any(segment in (".", "..") for segment in path.split("/")),
                any(ord(character) < 32 or ord(character) == 127 for character in path),
            )
        ):
            raise NedValidationError("Provide an absolute path without URL components.")
        if self._session.closed:
            raise NedConnectionError("The borrowed HTTP session is closed.")
        url = self._origin.with_path(path)
        request_headers = {
            name: value
            for name, value in (headers or {}).items()
            if name.lower() != "accept-encoding"
        }
        request_headers[hdrs.ACCEPT_ENCODING] = "identity"
        failure: NedApiError
        try:
            async with self._session.get(
                url,
                params=params,
                timeout=self._timeout,
                allow_redirects=False,
                raise_for_status=False,
                ssl=True,
                auto_decompress=False,
                headers=request_headers,
            ) as response:
                if response.status != 200:
                    # Status has priority over any malformed error body.
                    retry_after = parse_retry_after(
                        response.headers.get(hdrs.RETRY_AFTER)
                    )
                    response.close()
                    return TransportResponse(
                        status=response.status, body=b"", retry_after=retry_after
                    )
                encoding = response.headers.get(hdrs.CONTENT_ENCODING, "identity")
                if encoding.lower() != "identity":
                    raise NedResponseError("Unsupported HTTP content encoding.")
                body = bytearray()
                async for chunk in response.content.iter_chunked(
                    min(self._max_response_bytes + 1, 65536)
                ):
                    if len(body) + len(chunk) > self._max_response_bytes:
                        raise NedResponseError("HTTP response exceeds the byte limit.")
                    body.extend(chunk)
                media_type = (
                    response.headers.get(hdrs.CONTENT_TYPE, "")
                    .partition(";")[0]
                    .strip()
                    .lower()
                )
                return TransportResponse(
                    status=response.status, body=bytes(body), media_type=media_type
                )
        except TimeoutError:
            failure = NedTimeoutError("HTTP request exceeded its time budget.")
        except ClientPayloadError:
            failure = NedResponseError("HTTP response body could not be read.")
        except ClientError:
            failure = NedConnectionError("HTTP request failed at the transport layer.")
        # Raise outside the handler so raw URLs/headers in exceptions are not chained.
        raise failure

"""Share a conservative rolling request budget and server-directed cooldown."""

from collections import deque
from collections.abc import Mapping
from math import inf
from time import monotonic

from aiohttp import ClientHandlerType, ClientRequest, ClientResponse

from .exceptions import NedRateLimitError
from .transport import NedTransport, TransportResponse, parse_retry_after

_WINDOW = 300.0
_LIMIT = 120
_MAX_DELAY = 86400.0


class NedRequestBudget:
    """Share a budget across credentials, polling and entry reloads.

    Instrumented sessions must install async_middleware at creation. External
    borrowed sessions reserve two slots per call for aiohttp's internal retry.
    Neither policy claims to describe the upstream quota scope.
    """

    def __init__(self, *, instrumented: bool = False) -> None:
        """Initialize monotonic request history and the selected counting mode."""
        self._attempts: deque[float] = deque()
        self._blocked_until = 0.0
        self._instrumented = instrumented

    def _remaining(self, now: float) -> int:
        """Expire attempts and report the remaining local budget."""
        while self._attempts and self._attempts[0] <= now - _WINDOW:
            self._attempts.popleft()
        if now < self._blocked_until:
            return 0
        return _LIMIT - len(self._attempts)

    @property
    def remaining(self) -> int:
        """Expose the number of immediately available local attempts."""
        return self._remaining(monotonic())

    @property
    def retry_after(self) -> float:
        """Return a bounded scheduling hint; permanent blocks remain enforced."""
        delay = self._blocked_until - monotonic()
        return _WINDOW if delay == inf else max(_WINDOW, delay)

    def _reserve(self, count: int) -> None:
        """Reserve before I/O, atomically on the owning event loop."""
        now = monotonic()
        if self._remaining(now) < count:
            raise NedRateLimitError("Local NED request budget temporarily exhausted.")
        self._attempts.extend([now] * count)

    def _block(self, delay: float | None) -> None:
        """Honor longer server delays; stop indefinitely above the safety bound."""
        wait = max(_WINDOW, delay or 0.0)
        deadline = inf if wait > _MAX_DELAY else monotonic() + wait
        self._blocked_until = max(self._blocked_until, deadline)

    async def async_middleware(
        self, request: ClientRequest, handler: ClientHandlerType
    ) -> ClientResponse:
        """Reserve each aiohttp attempt, including its internal GET retry."""
        self._reserve(1)
        response = await handler(request)
        if response.status == 429:
            self._block(parse_retry_after(response.headers.get("Retry-After")))
            response.close()
            raise NedRateLimitError("NED returned HTTP 429; polling paused.")
        return response

    async def async_get(
        self,
        transport: NedTransport,
        path: str,
        *,
        params: Mapping[str, str],
        headers: Mapping[str, str],
    ) -> TransportResponse:
        """Use instrumented attempts or conservatively reserve retry capacity."""
        if self._instrumented:
            if not self.remaining:
                raise NedRateLimitError(
                    "Local NED request budget temporarily exhausted."
                )
        else:
            self._reserve(2)
        response = await transport.async_get(path, params=params, headers=headers)
        if response.status == 429:
            self._block(response.retry_after)
            raise NedRateLimitError("NED returned HTTP 429; polling paused.")
        return response

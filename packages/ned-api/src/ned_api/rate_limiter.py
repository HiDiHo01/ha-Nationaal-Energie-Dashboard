"""Apply a conservative process-local request budget without sleeping or retries."""

from collections import deque
from collections.abc import Mapping
from time import monotonic

from .exceptions import NedRateLimitError
from .transport import NedTransport, TransportResponse

_WINDOW = 300.0
_LIMIT = 120


class NedRequestBudget:
    """Share an attempt budget across credentials, polling and entry reloads.

    This is a local safety policy, not a claim about the upstream quota scope.
    A 429 pauses subsequent requests for one local window; it is not a retry.
    """

    def __init__(self) -> None:
        """Initialize empty monotonic request history."""
        self._attempts: deque[float] = deque()
        self._blocked_until = 0.0

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

    async def async_get(
        self,
        transport: NedTransport,
        path: str,
        *,
        params: Mapping[str, str],
        headers: Mapping[str, str],
    ) -> TransportResponse:
        """Reserve one attempt before I/O and stop on a rate-limit response."""
        now = monotonic()
        if not self._remaining(now):
            raise NedRateLimitError("Local NED request budget temporarily exhausted.")
        self._attempts.append(now)
        response = await transport.async_get(path, params=params, headers=headers)
        if response.status == 429:
            self._blocked_until = monotonic() + _WINDOW
            raise NedRateLimitError("NED returned HTTP 429; polling temporarily paused.")
        return response

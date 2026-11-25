"""Verify credentials using the observed historical solar power query."""

from datetime import UTC, datetime, timedelta

from aiohttp import ClientSession

from .exceptions import NedResponseError
from .quarter import NedPowerDataset, NedQuarterClient
from .rate_limiter import NedRequestBudget


class NedAuthenticationClient:
    """Confirm access to one bounded query, not authorization to all datasets."""

    def __init__(
        self, session: ClientSession, budget: NedRequestBudget | None = None
    ) -> None:
        """Use the same parser and request budget as the polling client."""
        self._client = NedQuarterClient(
            session, budget if budget is not None else NedRequestBudget()
        )

    @property
    def origin(self) -> str:
        """Expose the fixed credential destination without exposing credentials."""
        return self._client.origin

    async def async_validate_api_key(self, api_key: str) -> None:
        """Require nonempty, validated historical solar evidence; never retry."""
        day = datetime.now(UTC).date() - timedelta(days=2)
        readings = await self._client.async_read_day(
            api_key, NedPowerDataset.SOLAR, day
        )
        if not readings:
            raise NedResponseError("No bounded nonempty collection evidence.")

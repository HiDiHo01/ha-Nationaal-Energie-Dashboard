"""Read only the five observed national current power datasets for local alpha."""

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from enum import Enum
from math import isfinite

from aiohttp import ClientSession

from .exceptions import (
    NedAccessDeniedError,
    NedAuthenticationError,
    NedResponseError,
    NedValidationError,
)
from .rate_limiter import NedRequestBudget
from .transport import NedTransport, TransportResponse

_ORIGIN = "https://api.ned.nl"
_MEDIA_TYPE = "application/ld+json"
_QUARTER = timedelta(minutes=15)


class NedPowerDataset(Enum):
    """Restrict the alpha to observed current power dataset dimensions."""

    SOLAR = (2, 1)
    WIND_ONSHORE = (1, 1)
    WIND_OFFSHORE = (51, 1)
    CONSUMPTION = (59, 2)
    PRODUCTION = (27, 1)


@dataclass(frozen=True, slots=True)
class NedPowerReading:
    """Hold a validated UTC interval and native capacity in kW."""

    valid_from: datetime
    valid_to: datetime
    capacity_kw: float


def _dimensions(dataset: NedPowerDataset) -> dict[str, tuple[str, int]]:
    """Return the exact observed resource identifiers."""
    type_id, activity = dataset.value
    return {
        "point": ("points", 0),
        "type": ("types", type_id),
        "activity": ("activities", activity),
        "classification": ("classifications", 2),
        "granularity": ("granularities", 4),
        "granularitytimezone": ("granularity_time_zones", 0),
    }


def _timestamp(value: object) -> datetime:
    """Require a timezone-aware zero-offset ISO timestamp."""
    if not isinstance(value, str):
        raise NedResponseError("Missing or invalid interval timestamp.")
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        timestamp = None
    if timestamp is None or timestamp.utcoffset() != timedelta(0):
        raise NedResponseError("Expected a UTC interval timestamp.")
    return timestamp.astimezone(UTC)


def _capacity(value: object) -> float:
    """Accept only finite nonnegative numeric capacity, not strings or booleans."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise NedResponseError("Missing or invalid capacity.")
    try:
        capacity = float(value)
    except OverflowError:
        capacity = float("inf")
    if not isfinite(capacity) or capacity < 0:
        raise NedResponseError("Expected finite nonnegative capacity.")
    return capacity


def _parse_day(
    response: TransportResponse, dataset: NedPowerDataset, day: date
) -> tuple[NedPowerReading, ...]:
    """Validate a bounded single UTC day; never follow a pagination link."""
    if response.status == 401:
        raise NedAuthenticationError("NED did not accept authentication (HTTP 401).")
    if response.status == 403:
        raise NedAccessDeniedError("NED denied access (HTTP 403).")
    if response.status != 200 or response.media_type != _MEDIA_TYPE:
        raise NedResponseError("Unexpected NED power response status or media type.")
    try:
        document: object = json.loads(response.body)
    except ValueError, RecursionError:
        document = None
    if not isinstance(document, dict):
        raise NedResponseError("Expected a JSON-LD collection object.")
    members = document.get("hydra:member")
    total = document.get("hydra:totalItems")
    view = document.get("hydra:view", {})
    if (
        not isinstance(members, list)
        or len(members) > 96
        or type(total) is not int
        or total != len(members)
        or not isinstance(view, dict)
        or "hydra:next" in view
    ):
        raise NedResponseError("Incomplete or unexpected single-day collection.")
    lower = datetime.combine(day, time.min, tzinfo=UTC)
    upper = lower + timedelta(days=1)
    dimensions = _dimensions(dataset)
    readings: dict[datetime, NedPowerReading] = {}
    for member in members:
        if not isinstance(member, dict):
            raise NedResponseError("Invalid power collection member.")
        for field, (resource, identifier) in dimensions.items():
            iri = f"/v1/{resource}/{identifier}"
            if member.get(field) not in (iri, f"{_ORIGIN}{iri}"):
                raise NedResponseError("Unexpected power dataset dimension.")
        start = _timestamp(member.get("validfrom"))
        end = _timestamp(member.get("validto"))
        if (
            not lower <= start < end <= upper
            or start.minute % 15
            or start.second
            or start.microsecond
            or end - start != _QUARTER
            or start in readings
        ):
            raise NedResponseError("Invalid or ambiguous UTC quarter interval.")
        readings[start] = NedPowerReading(start, end, _capacity(member.get("capacity")))
    return tuple(readings[key] for key in sorted(readings))


class NedQuarterClient:
    """Read native power only, with a borrowed session and shared attempt budget."""

    def __init__(self, session: ClientSession, budget: NedRequestBudget) -> None:
        """Prepare a fixed-origin transport; retain no API key."""
        self._transport = NedTransport(session, _ORIGIN)
        self._budget = budget

    async def async_read_day(
        self, api_key: str, dataset: NedPowerDataset, day: date
    ) -> tuple[NedPowerReading, ...]:
        """Request one UTC day, with no fallback, pagination or automatic retries."""
        if (
            not api_key
            or not api_key.isascii()
            or not api_key.isprintable()
            or any(character.isspace() for character in api_key)
        ):
            raise NedValidationError("Provide a nonempty printable ASCII API key.")
        params = {
            field: str(identifier)
            for field, (_, identifier) in _dimensions(dataset).items()
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
        response = await self._budget.async_get(
            self._transport,
            "/v1/utilizations",
            params=params,
            headers={"Accept": _MEDIA_TYPE, "X-AUTH-TOKEN": api_key},
        )
        return _parse_day(response, dataset, day)

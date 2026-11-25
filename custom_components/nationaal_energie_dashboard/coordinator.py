"""Coordinate the bounded local-alpha power datasets and reserved offline logic."""

import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import isfinite

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.hass_dict import HassKey

from ned_api import (
    NedApiError,
    NedAuthenticationError,
    NedPowerDataset,
    NedQuarterClient,
    NedRateLimitError,
    NedRequestBudget,
    NedValidationError,
    validate_key_format,
)

from .const import (
    CURRENT_INTERVAL,
    DOMAIN,
    MAX_CURRENT_AGE,
    QUARTER,
    RENEWABLE_TYPES,
    TOTAL_PRODUCTION_TYPE,
    WASTE_RENEWABLE_FACTOR,
    SensorKey,
)

_LOGGER = logging.getLogger(__name__)
_BUDGET: HassKey[NedRequestBudget] = HassKey(f"{DOMAIN}_request_budget")
POWER_DATASETS = {
    SensorKey.SOLAR: NedPowerDataset.SOLAR,
    SensorKey.WIND_ONSHORE: NedPowerDataset.WIND_ONSHORE,
    SensorKey.WIND_OFFSHORE: NedPowerDataset.WIND_OFFSHORE,
    SensorKey.CONSUMPTION: NedPowerDataset.CONSUMPTION,
    SensorKey.PRODUCTION: NedPowerDataset.PRODUCTION,
}


def get_request_budget(hass: HomeAssistant) -> NedRequestBudget:
    """Share the budget for the lifetime of this Core process, including reloads."""
    return hass.data.setdefault(_BUDGET, NedRequestBudget(instrumented=True))


@dataclass(frozen=True, slots=True)
class NedReading:
    """Represent one normalized, finite, nonnegative UTC-quarter value."""

    valid_from: datetime
    valid_to: datetime
    value: float
    received_at: datetime | None = None

    def __post_init__(self) -> None:
        """Reject invalid interval boundaries and nonnumeric source values."""
        if self.valid_from.utcoffset() != timedelta(
            0
        ) or self.valid_to.utcoffset() != timedelta(0):
            raise ValueError("Expected a complete, aligned UTC quarter-hour.")
        if (
            self.valid_from.minute % 15
            or self.valid_from.second
            or self.valid_from.microsecond
            or self.valid_to - self.valid_from != QUARTER
        ):
            raise ValueError("Expected a complete, aligned UTC quarter-hour.")
        if isinstance(self.value, bool) or not isfinite(self.value) or self.value < 0:
            raise ValueError("Expected a finite, nonnegative reading.")


# Values use kW, kg CO2/kWh or percent according to the sensor key.
# Providers must validate source dimensions and resolve revisions before use.
type NedSnapshot = Mapping[SensorKey, tuple[NedReading, ...]]


@dataclass(frozen=True, slots=True)
class NedRuntimeData:
    """Hold the only coordinator active in the local alpha."""

    current: DataUpdateCoordinator[NedSnapshot]


type NedConfigEntry = ConfigEntry[NedRuntimeData]


class NedAlphaProvider:
    """Adapt independent validated power readings to the coordinator snapshot."""

    def __init__(
        self, client: NedQuarterClient, api_key: str, budget: NedRequestBudget
    ) -> None:
        """Retain the configured key privately and reuse the injected client."""
        self._client = client
        self._api_key = api_key
        self._budget = budget
        self._failed: set[SensorKey] = set()

    @property
    def failed_datasets(self) -> frozenset[SensorKey]:
        """Return sanitized identifiers of datasets with unresolved failures."""
        return frozenset(self._failed)

    async def _async_read_dataset(
        self, dataset: NedPowerDataset, now: datetime
    ) -> tuple[NedReading, ...]:
        """Publish only quarters closed before their request began."""
        first_day = (now - MAX_CURRENT_AGE - QUARTER).date()
        days = (first_day,) if first_day == now.date() else (first_day, now.date())
        readings: list[NedReading] = []
        for day in days:
            requested_at = datetime.now(UTC)
            page = await self._client.async_read_day(self._api_key, dataset, day)
            received_at = datetime.now(UTC)
            readings.extend(
                NedReading(
                    item.valid_from, item.valid_to, item.capacity_kw, received_at
                )
                for item in page
                if item.valid_to <= requested_at
            )
        return tuple(readings)

    async def async_current(self) -> NedSnapshot:
        """Isolate failed datasets, but stop the batch on authentication or 429."""
        now = datetime.now(UTC)
        snapshot: dict[SensorKey, tuple[NedReading, ...]] = {}
        for key, dataset in POWER_DATASETS.items():
            try:
                snapshot[key] = await self._async_read_dataset(dataset, now)
            except NedAuthenticationError as err:
                raise ConfigEntryAuthFailed(
                    translation_domain=DOMAIN, translation_key="authentication_failed"
                ) from err
            except NedRateLimitError as err:
                raise UpdateFailed(
                    translation_domain=DOMAIN,
                    translation_key="rate_limited",
                    retry_after=self._budget.retry_after,
                ) from err
            except NedApiError as err:
                if key not in self._failed:
                    _LOGGER.warning(
                        "NED dataset %s unavailable (%s)", key.value, type(err).__name__
                    )
                    self._failed.add(key)
            else:
                if key in self._failed:
                    _LOGGER.info("NED dataset %s recovered", key.value)
                    self._failed.discard(key)
        if not snapshot:
            raise UpdateFailed(
                translation_domain=DOMAIN, translation_key="update_failed"
            )
        return snapshot


def create_provider(hass: HomeAssistant, entry: NedConfigEntry) -> NedAlphaProvider:
    """Construct the alpha provider from the stored credential and shared session."""
    try:
        api_key = validate_key_format(entry.data.get(CONF_API_KEY))
    except NedValidationError as err:
        raise ConfigEntryAuthFailed(
            translation_domain=DOMAIN, translation_key="authentication_failed"
        ) from err
    budget = get_request_budget(hass)
    session = async_create_clientsession(hass, middlewares=(budget.async_middleware,))
    return NedAlphaProvider(NedQuarterClient(session, budget), api_key, budget)


def create_runtime(
    hass: HomeAssistant,
    entry: NedConfigEntry,
    update_method: Callable[[], Awaitable[NedSnapshot]],
) -> NedRuntimeData:
    """Create the sole active entry-owned coordinator."""
    return NedRuntimeData(
        current=DataUpdateCoordinator(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_current",
            update_interval=CURRENT_INTERVAL,
            update_method=update_method,
        ),
    )


def select_reading(
    readings: tuple[NedReading, ...], now: datetime, *, forecast: bool
) -> NedReading | None:
    """Select the exact next forecast or the latest sufficiently fresh current.

    Reject ambiguous duplicate intervals. A provider must resolve revisions;
    this draft does not infer a revision order from unconfirmed timestamps.
    """
    if now.utcoffset() is None:
        raise ValueError("Selection requires a timezone-aware timestamp.")
    utc_now = now.astimezone(UTC)
    if forecast:
        target = utc_now.replace(
            minute=utc_now.minute // 15 * 15, second=0, microsecond=0
        )
        if target < utc_now:
            target += QUARTER
        matches = tuple(reading for reading in readings if reading.valid_from == target)
    else:
        candidates = tuple(
            reading
            for reading in readings
            if timedelta(0) <= utc_now - reading.valid_to <= MAX_CURRENT_AGE
            and (reading.received_at is None or reading.received_at <= utc_now)
        )
        latest = max((reading.valid_to for reading in candidates), default=None)
        matches = tuple(reading for reading in candidates if reading.valid_to == latest)
    return matches[0] if len(matches) == 1 else None


def estimate_renewable_share(
    volumes: Mapping[int, NedReading],
) -> NedReading | None:
    """Estimate renewable electricity share from aligned normalized kWh values.

    Use the documented provisional waste factor, not the API utilization
    percentage. Missing or inconsistent source data never become zero.
    """
    if TOTAL_PRODUCTION_TYPE not in volumes or any(
        type_id not in volumes for type_id in RENEWABLE_TYPES
    ):
        return None
    total = volumes[TOTAL_PRODUCTION_TYPE]
    sources = tuple(volumes[type_id] for type_id in RENEWABLE_TYPES)
    if total.value <= 0 or any(
        reading.valid_from != total.valid_from or reading.valid_to != total.valid_to
        for reading in sources
    ):
        return None
    if sum(reading.value for reading in sources) > total.value:
        return None
    weighted = sum(volumes[type_id].value for type_id in RENEWABLE_TYPES[:-1])
    weighted += WASTE_RENEWABLE_FACTOR * volumes[21].value
    return NedReading(total.valid_from, total.valid_to, weighted / total.value * 100)

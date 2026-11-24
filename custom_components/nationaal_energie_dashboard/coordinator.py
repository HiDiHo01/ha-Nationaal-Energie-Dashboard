"""Prepare offline-testable coordination of normalized NED quarter-hour data.

No HTTP client or authentication behavior is implemented here. The provider
boundary remains closed until the independent client is contract-validated.
"""

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import isfinite
from typing import Protocol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONTRACT_PENDING,
    CURRENT_INTERVAL,
    DOMAIN,
    FORECAST_INTERVAL,
    MAX_CURRENT_AGE,
    QUARTER,
    RENEWABLE_TYPES,
    TOTAL_PRODUCTION_TYPE,
    WASTE_RENEWABLE_FACTOR,
    SensorKey,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class NedReading:
    """Represent one normalized, finite, nonnegative UTC-quarter value."""

    valid_from: datetime
    valid_to: datetime
    value: float

    def __post_init__(self) -> None:
        """Reject invalid interval boundaries and nonnumeric source values."""
        if (
            self.valid_from.utcoffset() != timedelta(0)
            or self.valid_to.utcoffset() != timedelta(0)
        ):
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


class NedDataProvider(Protocol):
    """Expose normalized data without coupling Home Assistant to HTTP parsing."""

    async def async_current(self) -> NedSnapshot:
        """Return current readings, including the derived estimate when valid."""
        ...

    async def async_forecast(self) -> NedSnapshot:
        """Return forecast readings covering future quarter-hour intervals."""
        ...


@dataclass(frozen=True, slots=True)
class NedRuntimeData:
    """Hold independent current and forecast coordinators."""

    current: DataUpdateCoordinator[NedSnapshot]
    forecast: DataUpdateCoordinator[NedSnapshot]


type NedConfigEntry = ConfigEntry[NedRuntimeData]


def create_provider(_hass: HomeAssistant, _entry: NedConfigEntry) -> NedDataProvider:
    """Fail closed until the independent client and distribution are ready.

    This explicit boundary can be replaced by a validated client adapter.
    It never reads credentials or performs a network request.
    """
    raise ConfigEntryError(
        translation_domain=DOMAIN,
        translation_key=CONTRACT_PENDING,
    )


def create_runtime(
    hass: HomeAssistant, entry: NedConfigEntry, provider: NedDataProvider
) -> NedRuntimeData:
    """Create two entry-owned coordinators around an injected data provider."""
    return NedRuntimeData(
        current=DataUpdateCoordinator(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_current",
            update_interval=CURRENT_INTERVAL,
            update_method=provider.async_current,
        ),
        forecast=DataUpdateCoordinator(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_forecast",
            update_interval=FORECAST_INTERVAL,
            update_method=provider.async_forecast,
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

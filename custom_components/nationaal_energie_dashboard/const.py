"""Define the Home Assistant integration and draft sensor configuration."""

from datetime import timedelta
from enum import StrEnum

from homeassistant.const import Platform

DOMAIN = "nationaal_energie_dashboard"
PLATFORMS = (Platform.SENSOR,)

CURRENT_INTERVAL = timedelta(minutes=5)
FORECAST_INTERVAL = timedelta(hours=1)
QUARTER = timedelta(minutes=15)
# Provisional presentation policy; validate against source publication latency.
MAX_CURRENT_AGE = timedelta(minutes=30)

RENEWABLE_TYPES = (1, 2, 51, 25, 21)
TOTAL_PRODUCTION_TYPE = 27
WASTE_RENEWABLE_FACTOR = 0.53
WASTE_FACTOR_YEAR = 2025
RENEWABLE_METHOD_VERSION = "2026-v1"


class SensorKey(StrEnum):
    """Identify the eight approved sensor descriptions."""

    CO2_INTENSITY = "co2_intensity"
    CO2_FORECAST = "co2_intensity_forecast"
    RENEWABLE_SHARE = "renewable_electricity_share"
    SOLAR = "solar_power"
    WIND_ONSHORE = "wind_onshore_power"
    WIND_OFFSHORE = "wind_offshore_power"
    CONSUMPTION = "electricity_consumption"
    PRODUCTION = "electricity_production"


def _dataset_identifier(
    type_id: int, activity_id: int, classification: int, metric: str
) -> str:
    """Construct the stable identifier from the fixed dataset dimensions."""
    return f"0_{type_id}_{activity_id}_4_0_{classification}_{metric}"


# Point, type, activity, granularity, timezone, classification, metric.
# The derived metric deliberately has no fictitious type/activity identifier.
SENSOR_IDENTIFIERS: dict[SensorKey, str] = {
    SensorKey.CO2_INTENSITY: _dataset_identifier(27, 1, 2, "emissionfactor"),
    SensorKey.CO2_FORECAST: _dataset_identifier(27, 1, 1, "emissionfactor"),
    SensorKey.RENEWABLE_SHARE: "0_4_0_2_renewable_electricity_share",
    SensorKey.SOLAR: _dataset_identifier(2, 1, 2, "capacity"),
    SensorKey.WIND_ONSHORE: _dataset_identifier(1, 1, 2, "capacity"),
    SensorKey.WIND_OFFSHORE: _dataset_identifier(51, 1, 2, "capacity"),
    SensorKey.CONSUMPTION: _dataset_identifier(59, 2, 2, "capacity"),
    SensorKey.PRODUCTION: _dataset_identifier(27, 1, 2, "capacity"),
}

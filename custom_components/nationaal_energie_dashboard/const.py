"""Define the Home Assistant integration and draft sensor configuration."""

from datetime import timedelta
from enum import StrEnum

from homeassistant.const import Platform

DOMAIN = "nationaal_energie_dashboard"
PLATFORMS = (Platform.SENSOR,)
CONTRACT_PENDING = "contract_pending"

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


# Point, type, activity, granularity, timezone, classification, metric.
# The derived metric deliberately has no fictitious type/activity identifier.
SENSOR_IDENTIFIERS: dict[SensorKey, str] = {
    SensorKey.CO2_INTENSITY: "0_27_1_4_0_2_emissionfactor",
    SensorKey.CO2_FORECAST: "0_27_1_4_0_1_emissionfactor",
    SensorKey.RENEWABLE_SHARE: "0_4_0_2_renewable_electricity_share",
    SensorKey.SOLAR: "0_2_1_4_0_2_capacity",
    SensorKey.WIND_ONSHORE: "0_1_1_4_0_2_capacity",
    SensorKey.WIND_OFFSHORE: "0_51_1_4_0_2_capacity",
    SensorKey.CONSUMPTION: "0_59_2_4_0_2_capacity",
    SensorKey.PRODUCTION: "0_27_1_4_0_2_capacity",
}

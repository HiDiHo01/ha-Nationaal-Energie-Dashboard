"""Expose five alpha power sensors and preserve the reserved sensor descriptions."""

from datetime import UTC, datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    RENEWABLE_METHOD_VERSION,
    SENSOR_IDENTIFIERS,
    WASTE_FACTOR_YEAR,
    WASTE_RENEWABLE_FACTOR,
    SensorKey,
)
from .coordinator import (
    POWER_DATASETS,
    NedConfigEntry,
    NedReading,
    NedSnapshot,
    select_reading,
)

_CO2_KEYS = frozenset((SensorKey.CO2_INTENSITY, SensorKey.CO2_FORECAST))


def _power_description(key: SensorKey) -> SensorEntityDescription:
    """Preserve native kW while recommending MW presentation."""
    return SensorEntityDescription(
        key=key.value,
        translation_key=key.value,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_unit_of_measurement=UnitOfPower.MEGA_WATT,
        suggested_display_precision=2,
    )


SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(
        key=SensorKey.CO2_INTENSITY.value,
        translation_key=SensorKey.CO2_INTENSITY.value,
        native_unit_of_measurement="g/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key=SensorKey.CO2_FORECAST.value,
        translation_key=SensorKey.CO2_FORECAST.value,
        native_unit_of_measurement="g/kWh",
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key=SensorKey.RENEWABLE_SHARE.value,
        translation_key=SensorKey.RENEWABLE_SHARE.value,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    _power_description(SensorKey.SOLAR),
    _power_description(SensorKey.WIND_ONSHORE),
    _power_description(SensorKey.WIND_OFFSHORE),
    _power_description(SensorKey.CONSUMPTION),
    _power_description(SensorKey.PRODUCTION),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: NedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Register only the five validated power datasets in the local alpha."""
    async_add_entities(
        NedSensor(
            entry.runtime_data.current,
            entry.entry_id,
            description,
        )
        for description in SENSOR_DESCRIPTIONS
        if SensorKey(description.key) in POWER_DATASETS
    )


class NedSensor(CoordinatorEntity[DataUpdateCoordinator[NedSnapshot]], SensorEntity):
    """Expose a normalized reading without I/O or independent API polling."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[NedSnapshot],
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Bind a stable identity, logical service device and translation."""
        self._key = SensorKey(description.key)
        super().__init__(coordinator, context=self._key)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{SENSOR_IDENTIFIERS[self._key]}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_0")},
            entry_type=DeviceEntryType.SERVICE,
            name="NED Nederland",
            manufacturer="Nationaal Energie Dashboard",
            configuration_url="https://ned.nl/",
        )

    async def async_added_to_hass(self) -> None:
        """Reevaluate cached time windows without additional API requests."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_utc_time_change(
                self.hass,
                self._async_update_from_cache,
                minute=range(0, 60, 5),
                second=0,
            )
        )

    @callback
    def _async_update_from_cache(self, _now: datetime) -> None:
        """Refresh local state when an interval or freshness window changes."""
        self.async_write_ha_state()

    def _reading(self) -> NedReading | None:
        """Read only valid in-memory data for this sensor's time window."""
        if not super().available:
            return None
        return select_reading(
            self.coordinator.data.get(self._key, ()),
            datetime.now(UTC),
            forecast=self._key == SensorKey.CO2_FORECAST,
        )

    @property
    def available(self) -> bool:
        """Expose availability only for a successful, applicable snapshot."""
        return self._reading() is not None

    @property
    def native_value(self) -> float | None:
        """Convert the CO2 factor to g/kWh; preserve other native units."""
        reading = self._reading()
        if reading is None:
            return None
        return reading.value * 1000 if self._key in _CO2_KEYS else reading.value

    @property
    def extra_state_attributes(self) -> dict[str, str | int | float]:
        """Expose bounded interval metadata and the estimate methodology."""
        reading = self._reading()
        attributes: dict[str, str | int | float] = {}
        if reading is not None:
            attributes["valid_from"] = reading.valid_from.isoformat()
            attributes["valid_to"] = reading.valid_to.isoformat()
        if self._key == SensorKey.RENEWABLE_SHARE:
            attributes["method_version"] = RENEWABLE_METHOD_VERSION
            attributes["waste_renewable_factor"] = WASTE_RENEWABLE_FACTOR
            attributes["waste_factor_year"] = WASTE_FACTOR_YEAR
        return attributes

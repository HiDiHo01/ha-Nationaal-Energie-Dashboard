"""Prepare the entry lifecycle for Nationaal Energie Dashboard."""

from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .coordinator import NedConfigEntry, create_provider, create_runtime


async def async_setup_entry(hass: HomeAssistant, entry: NedConfigEntry) -> bool:
    """Set up the bounded alpha provider before forwarding the sensor platform."""
    provider = create_provider(hass, entry)
    runtime = create_runtime(hass, entry, provider)
    await runtime.current.async_config_entry_first_refresh()
    entry.runtime_data = runtime
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NedConfigEntry) -> bool:
    """Unload the sensor platform; Core shuts down entry-owned coordinators."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

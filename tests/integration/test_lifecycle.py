"""Exercise the native Home Assistant config entry lifecycle offline."""

import json
from datetime import UTC, date, datetime, time, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import (
    SOURCE_REAUTH,
    SOURCE_RECONFIGURE,
    SOURCE_USER,
    ConfigEntryState,
)
from homeassistant.const import CONF_API_KEY, STATE_UNAVAILABLE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.nationaal_energie_dashboard.const import DOMAIN, QUARTER
from custom_components.nationaal_energie_dashboard.coordinator import (
    POWER_DATASETS,
    NedConfigEntry,
)
from ned_api import TransportResponse

_DAY = date(2026, 11, 22)
_NOW = datetime(2026, 11, 22, 12, 30, tzinfo=UTC)


class SyntheticApi:
    """Return only fabricated data and record the requested dataset identifiers."""

    def __init__(self) -> None:
        """Initialize response status overrides and bounded call history."""
        self.statuses: dict[int, int] = {}
        self.calls: list[int] = []

    def response(
        self, path: str, *, params: dict[str, str], headers: dict[str, str]
    ) -> TransportResponse:
        """Return one closed interval, or a sanitized synthetic HTTP denial."""
        assert path == "/v1/utilizations"
        assert headers["X-AUTH-TOKEN"] in {"synthetic-key", "replacement-key"}
        type_id = int(params["type"])
        self.calls.append(type_id)
        day = date.fromisoformat(params["validfrom[after]"])
        status = 200 if day != _DAY else self.statuses.get(type_id, 200)
        if status != 200:
            return TransportResponse(status, b"")
        start = datetime.combine(day, time(12, 15), tzinfo=UTC)
        record = {
            "point": "/v1/points/0",
            "type": f"/v1/types/{type_id}",
            "activity": f"/v1/activities/{params['activity']}",
            "classification": "/v1/classifications/2",
            "granularity": "/v1/granularities/4",
            "granularitytimezone": "/v1/granularity_time_zones/0",
            "validfrom": start.isoformat(),
            "validto": (start + QUARTER).isoformat(),
            "capacity": 1234,
        }
        return TransportResponse(
            200,
            json.dumps({"hydra:member": [record], "hydra:totalItems": 1}).encode(),
            "application/ld+json",
        )


async def _configure(hass: HomeAssistant) -> NedConfigEntry:
    """Use the native flow manager, including config entry setup."""
    form = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert form["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        form["flow_id"], {CONF_API_KEY: "synthetic-key"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    entry: NedConfigEntry = result["result"]
    return entry


@pytest.mark.freeze_time("2026-11-22 12:30:00+00:00")
@pytest.mark.asyncio
async def test_native_lifecycle(hass: HomeAssistant) -> None:
    """Configure, register, update, reauth, reload and unload real HA entities."""
    api = SyntheticApi()
    with patch(
        "ned_api.transport.NedTransport.async_get",
        new_callable=AsyncMock,
        side_effect=api.response,
    ):
        entry = await _configure(hass)
        assert entry.state is ConfigEntryState.LOADED
        registry = er.async_get(hass)
        entries = er.async_entries_for_config_entry(registry, entry.entry_id)
        assert len(entries) == 5
        assert {item.translation_key for item in entries} == set(POWER_DATASETS)
        devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
        assert len(devices) == 1
        ids = {item.entity_id for item in entries}
        solar = next(
            item.entity_id for item in entries if item.translation_key == "solar_power"
        )
        for entity_id in ids:
            state = hass.states.get(entity_id)
            assert state is not None
            unit = state.attributes["unit_of_measurement"]
            assert unit in {UnitOfPower.KILO_WATT, UnitOfPower.MEGA_WATT}
            expected = 1.234 if unit == UnitOfPower.MEGA_WATT else 1234
            assert float(state.state) == pytest.approx(expected)
            assert state.attributes["received_at"] == _NOW.isoformat()
        duplicate = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        assert duplicate["type"] is FlowResultType.ABORT
        api.statuses[2] = 403
        await entry.runtime_data.current.async_refresh()
        await hass.async_block_till_done()
        state = hass.states.get(solar)
        assert state is not None and state.state == STATE_UNAVAILABLE
        for entity_id in ids - {solar}:
            state = hass.states.get(entity_id)
            assert state is not None and state.state != STATE_UNAVAILABLE
        assert not list(entry.async_get_active_flows(hass, {SOURCE_REAUTH}))
        api.statuses.clear()
        await entry.runtime_data.current.async_refresh()
        await hass.async_block_till_done()
        state = hass.states.get(solar)
        assert state is not None and state.state != STATE_UNAVAILABLE
        api.statuses[2] = 401
        await entry.runtime_data.current.async_refresh()
        await hass.async_block_till_done()
        flows = list(entry.async_get_active_flows(hass, {SOURCE_REAUTH}))
        assert len(flows) == 1
        api.statuses.clear()
        result = await hass.config_entries.flow.async_configure(
            flows[0]["flow_id"], {CONF_API_KEY: "replacement-key"}
        )
        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reauth_successful"
        await hass.async_block_till_done()
        assert entry.state is ConfigEntryState.LOADED
        assert entry.data[CONF_API_KEY] == "replacement-key"
        form = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
        )
        assert form["type"] is FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(
            form["flow_id"], {CONF_API_KEY: "synthetic-key"}
        )
        assert result["type"] is FlowResultType.ABORT
        await hass.async_block_till_done()
        assert entry.data[CONF_API_KEY] == "synthetic-key"
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert {
            item.entity_id
            for item in er.async_entries_for_config_entry(registry, entry.entry_id)
        } == ids
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert entry.state is ConfigEntryState.NOT_LOADED
        assert all(hass.states.get(entity_id) is None for entity_id in ids)


@pytest.mark.freeze_time("2026-11-22 12:30:00+00:00")
@pytest.mark.asyncio
async def test_native_failed_setup_and_recovery(hass: HomeAssistant) -> None:
    """Recover a native setup retry without reconstructing the config entry."""
    api = SyntheticApi()
    api.statuses = {dataset.value[0]: 503 for dataset in POWER_DATASETS.values()}
    with patch(
        "ned_api.transport.NedTransport.async_get",
        new_callable=AsyncMock,
        side_effect=api.response,
    ):
        entry = await _configure(hass)
        assert entry.state is ConfigEntryState.SETUP_RETRY
        assert not er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
        api.statuses.clear()
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert entry.state is ConfigEntryState.LOADED
        assert (
            len(er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id))
            == 5
        )
        assert await hass.config_entries.async_unload(entry.entry_id)

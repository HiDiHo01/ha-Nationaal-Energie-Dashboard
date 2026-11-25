"""Exercise sensor logic and the draft configuration flow without live NED."""

import json
from datetime import UTC, date, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession
from homeassistant.config_entries import (
    SOURCE_REAUTH,
    SOURCE_RECONFIGURE,
    SOURCE_USER,
    ConfigEntryState,
)
from homeassistant.const import CONF_API_KEY, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import AbortFlow, FlowResultType
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

# The pinned upstream test helper does not provide a py.typed marker.
from pytest_homeassistant.common import MockConfigEntry  # type: ignore[import-untyped]

from custom_components.nationaal_energie_dashboard import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.nationaal_energie_dashboard.config_flow import NedConfigFlow
from custom_components.nationaal_energie_dashboard.const import (
    DOMAIN,
    PLATFORMS,
    QUARTER,
    SENSOR_IDENTIFIERS,
    SensorKey,
)
from custom_components.nationaal_energie_dashboard.coordinator import (
    POWER_DATASETS,
    NedAlphaProvider,
    NedReading,
    NedSnapshot,
    create_provider,
    estimate_renewable_share,
    get_request_budget,
    select_reading,
)
from custom_components.nationaal_energie_dashboard.sensor import (
    SENSOR_DESCRIPTIONS,
    NedSensor,
)
from custom_components.nationaal_energie_dashboard.sensor import (
    async_setup_entry as async_setup_sensors,
)
from ned_api import (
    NedAccessDeniedError,
    NedAuthenticationError,
    NedConnectionError,
    NedPowerDataset,
    NedPowerReading,
    NedQuarterClient,
    NedRateLimitError,
    NedRequestBudget,
    NedResponseError,
    NedTimeoutError,
    TransportResponse,
)

_START = datetime(2026, 11, 22, 12, tzinfo=UTC)


def _power_response(dataset: NedPowerDataset, day: date) -> TransportResponse:
    """Build one native capacity record with exact observed dimensions."""
    start = datetime.combine(day, time.min, tzinfo=UTC)
    type_id, activity = dataset.value
    record = {
        "point": "/v1/points/0",
        "type": f"/v1/types/{type_id}",
        "activity": f"/v1/activities/{activity}",
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


def _reading(value: float, start: datetime = _START) -> NedReading:
    """Create one synthetic aligned quarter-hour reading."""
    return NedReading(start, start + QUARTER, value)


def _volumes() -> dict[int, NedReading]:
    """Supply the six synthetic source volumes for the estimate."""
    return {
        1: _reading(200),
        2: _reading(300),
        51: _reading(100),
        25: _reading(50),
        21: _reading(100),
        27: _reading(1000),
    }


@pytest.mark.parametrize("value", [-1.0, float("nan"), float("inf"), True])
def test_invalid_reading(value: float) -> None:
    """Reject invalid numerical readings."""
    with pytest.raises(ValueError, match="nonnegative"):
        _reading(value)


def test_invalid_interval() -> None:
    """Reject an unaligned or naive quarter-hour."""
    with pytest.raises(ValueError, match="UTC quarter"):
        _reading(1, _START + timedelta(minutes=1))
    with pytest.raises(ValueError, match="UTC quarter"):
        _reading(1, _START.replace(tzinfo=None))
    with pytest.raises(ValueError, match="UTC quarter"):
        NedReading(_START, _START + timedelta(minutes=30), 1)


def test_current_window() -> None:
    """Select a unique complete and sufficiently fresh current interval."""
    reading = _reading(1)
    now = _START + QUARTER
    assert select_reading((reading,), now, forecast=False) == reading
    assert select_reading((reading,), _START, forecast=False) is None
    assert select_reading((reading, reading), now, forecast=False) is None
    assert select_reading((reading,), now + timedelta(hours=1), forecast=False) is None
    assert select_reading((), now, forecast=False) is None


def test_forecast_window() -> None:
    """Select the precise future quarter, without current fallback."""
    first = _reading(1)
    second = _reading(2, _START + QUARTER)
    assert select_reading((first, second), _START, forecast=True) == first
    assert (
        select_reading((first, second), _START + timedelta(seconds=1), forecast=True)
        == second
    )
    assert (
        select_reading((first,), _START + timedelta(seconds=1), forecast=True) is None
    )
    assert select_reading((first, first), _START, forecast=True) is None
    with pytest.raises(ValueError, match="timezone-aware"):
        select_reading((first,), _START.replace(tzinfo=None), forecast=True)


def test_renewable_estimate() -> None:
    """Calculate 70.3 percent using the documented provisional waste factor."""
    estimate = estimate_renewable_share(_volumes())
    assert estimate is not None
    assert estimate.value == pytest.approx(70.3)
    assert estimate.valid_from == _START
    assert estimate.valid_to == _START + QUARTER


@pytest.mark.parametrize("type_id", [1, 2, 51, 25, 21, 27])
def test_missing_renewable_input(type_id: int) -> None:
    """Do not silently fill absent sources with zero."""
    volumes = _volumes()
    del volumes[type_id]
    assert estimate_renewable_share(volumes) is None


def test_inconsistent_renewable_input() -> None:
    """Reject a zero denominator, unequal intervals and excess source volume."""
    volumes = _volumes()
    volumes[27] = _reading(0)
    assert estimate_renewable_share(volumes) is None
    volumes = _volumes()
    volumes[21] = _reading(100, _START + QUARTER)
    assert estimate_renewable_share(volumes) is None
    volumes = _volumes()
    volumes[27] = _reading(100)
    assert estimate_renewable_share(volumes) is None
    volumes = dict.fromkeys(_volumes(), _reading(0))
    volumes[27] = _reading(100)
    estimate = estimate_renewable_share(volumes)
    assert estimate is not None and estimate.value == 0


def test_eight_sensor_descriptions() -> None:
    """Require stable identities, appropriate units and no forecast statistics."""
    descriptions = {item.key: item for item in SENSOR_DESCRIPTIONS}
    assert set(descriptions) == set(SensorKey)
    assert tuple(SENSOR_IDENTIFIERS.values()) == (
        "0_27_1_4_0_2_emissionfactor",
        "0_27_1_4_0_1_emissionfactor",
        "0_4_0_2_renewable_electricity_share",
        "0_2_1_4_0_2_capacity",
        "0_1_1_4_0_2_capacity",
        "0_51_1_4_0_2_capacity",
        "0_59_2_4_0_2_capacity",
        "0_27_1_4_0_2_capacity",
    )
    assert descriptions[SensorKey.CO2_FORECAST].state_class is None
    solar = descriptions[SensorKey.SOLAR]
    assert solar.native_unit_of_measurement == UnitOfPower.KILO_WATT
    assert solar.suggested_unit_of_measurement == UnitOfPower.MEGA_WATT


def _flow(hass: HomeAssistant) -> NedConfigFlow:
    """Construct the real Core flow handler with a user context."""
    flow = NedConfigFlow()
    flow.hass = hass
    flow.handler = DOMAIN
    flow.flow_id = "synthetic-flow"
    flow.context = {"source": SOURCE_USER}
    return flow


@pytest.mark.asyncio
async def test_masked_key_flow(hass: HomeAssistant) -> None:
    """Show the credential form without requesting data before submission."""
    flow = _flow(hass)
    with patch(
        "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
    ) as get:
        result = await flow.async_step_user()
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    get.assert_not_awaited()
    assert not hass.config_entries.async_entries(DOMAIN)


@pytest.mark.parametrize("key", [None, "", "bad key", "é", "bad\nkey"])
@pytest.mark.asyncio
async def test_invalid_key_input(hass: HomeAssistant, key: str | None) -> None:
    """Reject invalid key syntax and do not call credential verification."""
    flow = _flow(hass)
    with patch(
        "custom_components.nationaal_energie_dashboard.config_flow.async_validate_api_key",
        new_callable=AsyncMock,
    ) as validate:
        result = await flow.async_step_user({CONF_API_KEY: key})
    assert result["errors"] == {CONF_API_KEY: "invalid_key_format"}
    validate.assert_not_awaited()


@pytest.mark.asyncio
async def test_mock_validated_key(hass: HomeAssistant) -> None:
    """Accept entry data only after the actual client validates a synthetic response."""
    flow = _flow(hass)
    session = MagicMock(spec=ClientSession)
    response = _power_response(NedPowerDataset.SOLAR, _START.date())
    with (
        patch("ned_api.authentication.datetime") as clock,
        patch(
            "custom_components.nationaal_energie_dashboard.config_flow.async_create_clientsession",
            return_value=session,
        ) as get_session,
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
    ):
        clock.now.return_value = _START + timedelta(days=2)
        get.return_value = response
        result = await flow.async_step_user({CONF_API_KEY: "synthetic-key"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_API_KEY: "synthetic-key"}
    session.detach.assert_called_once()
    get_session.assert_called_once_with(
        hass, auto_cleanup=False, middlewares=(get_request_budget(hass).async_middleware,)
    )
    get.assert_awaited_once()
    session.close.assert_not_awaited()


@pytest.mark.parametrize(
    ("response", "expected_errors"),
    [
        (
            TransportResponse(
                401, b'{"hydra:title":"synthetic-key"}', "application/ld+json"
            ),
            {CONF_API_KEY: "invalid_auth"},
        ),
        (
            TransportResponse(403, b'{"message":"synthetic-key"}', "application/json"),
            {"base": "access_denied"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_observed_denials_in_config_flow(
    hass: HomeAssistant,
    response: TransportResponse,
    expected_errors: dict[str, str],
) -> None:
    """Connect the real client to the flow through an offline injected validator."""
    session = MagicMock(spec=ClientSession)
    flow = _flow(hass)
    with (
        patch(
            "custom_components.nationaal_energie_dashboard.config_flow.async_create_clientsession",
            return_value=session,
        ),
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
    ):
        get.return_value = response
        result = await flow.async_step_user({CONF_API_KEY: "synthetic-key"})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == expected_errors
    assert "synthetic-key" not in repr(result)
    assert not hass.config_entries.async_entries(DOMAIN)
    get.assert_awaited_once()
    session.detach.assert_called_once()
    session.close.assert_not_awaited()


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (NedConnectionError("synthetic"), "cannot_connect"),
        (NedTimeoutError("synthetic"), "cannot_connect"),
        (NedResponseError("synthetic"), "cannot_validate"),
        (NedRateLimitError("synthetic"), "rate_limited"),
    ],
)
@pytest.mark.asyncio
async def test_inconclusive_config_validation(
    hass: HomeAssistant, error: Exception, expected: str
) -> None:
    """Keep the form open without presenting unconfirmed failures as bad keys."""
    flow = _flow(hass)
    with patch(
        "custom_components.nationaal_energie_dashboard.config_flow.async_validate_api_key",
        side_effect=error,
    ):
        result = await flow.async_step_user({CONF_API_KEY: "synthetic-key"})
    assert result["errors"] == {"base": expected}
    assert not hass.config_entries.async_entries(DOMAIN)


def test_matching_flow(hass: HomeAssistant) -> None:
    """Compare established identities without comparing credentials."""
    flow = _flow(hass)
    other = _flow(hass)
    assert not flow.is_matching(other)
    flow.context["unique_id"] = DOMAIN
    assert not flow.is_matching(other)
    other.context["unique_id"] = DOMAIN
    assert flow.is_matching(other)


@pytest.mark.parametrize("source", [SOURCE_REAUTH, SOURCE_RECONFIGURE])
@pytest.mark.asyncio
async def test_replace_credentials(hass: HomeAssistant, source: str) -> None:
    """Keep entry identity and settings when replacement credentials validate."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={CONF_API_KEY: "old-synthetic", "location": "NL"},
        options={"forecast": True},
    )
    entry.add_to_hass(hass)
    flow = _flow(hass)
    flow.context = {"source": source, "entry_id": entry.entry_id}
    if source == SOURCE_REAUTH:
        form = await flow.async_step_reauth(entry.data)
        step = flow.async_step_reauth_confirm
        reason = "reauth_successful"
    else:
        form = await flow.async_step_reconfigure()
        step = flow.async_step_reconfigure
        reason = "reconfigure_successful"
    assert form["type"] is FlowResultType.FORM
    assert "old-synthetic" not in repr(form)
    with patch(
        "custom_components.nationaal_energie_dashboard.config_flow.async_validate_api_key",
        side_effect=NedAccessDeniedError("synthetic"),
    ):
        blocked = await step({CONF_API_KEY: "new-synthetic"})
    assert blocked["errors"] == {"base": "access_denied"}
    assert entry.data[CONF_API_KEY] == "old-synthetic"
    with (
        patch(
            "custom_components.nationaal_energie_dashboard.config_flow.async_validate_api_key",
            new_callable=AsyncMock,
        ) as validate,
        patch.object(hass.config_entries, "async_schedule_reload") as reload,
    ):
        result = await step({CONF_API_KEY: "new-synthetic"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == reason
    assert entry.data == {CONF_API_KEY: "new-synthetic", "location": "NL"}
    assert entry.options == {"forecast": True}
    assert entry.unique_id == DOMAIN
    validate.assert_awaited_once_with(hass, "new-synthetic")
    reload.assert_called_once_with(entry.entry_id)


@pytest.mark.asyncio
async def test_duplicate_service(hass: HomeAssistant) -> None:
    """Abort a second configuration before requesting credentials."""
    MockConfigEntry(domain=DOMAIN, unique_id=DOMAIN).add_to_hass(hass)
    flow = _flow(hass)
    with pytest.raises(AbortFlow) as raised:
        await flow.async_step_user()
    assert raised.value.reason == "already_configured"


@pytest.mark.asyncio
async def test_setup_missing_key(hass: HomeAssistant) -> None:
    """Reject setup with an absent credential before constructing a client."""
    entry = MockConfigEntry(domain=DOMAIN)
    with pytest.raises(ConfigEntryAuthFailed) as raised:
        await async_setup_entry(hass, entry)
    assert raised.value.translation_key == "authentication_failed"


@pytest.mark.asyncio
async def test_synthetic_runtime(hass: HomeAssistant) -> None:
    """Exercise setup, shared snapshots, all entities and unload without HTTP."""
    entry = MockConfigEntry(domain=DOMAIN, state=ConfigEntryState.SETUP_IN_PROGRESS)
    entry.add_to_hass(hass)
    current: NedSnapshot = {
        SensorKey.CO2_INTENSITY: (_reading(0.25),),
        SensorKey.RENEWABLE_SHARE: (_reading(70.3),),
        SensorKey.SOLAR: (_reading(1000),),
        SensorKey.CO2_FORECAST: (_reading(0.3, _START + QUARTER),),
    }
    provider = MagicMock()
    provider.async_current = AsyncMock(return_value=current)
    with (
        patch(
            "custom_components.nationaal_energie_dashboard.create_provider",
            return_value=provider,
        ),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", new_callable=AsyncMock
        ) as forward,
    ):
        assert await async_setup_entry(hass, entry)
    forward.assert_awaited_once_with(entry, PLATFORMS)
    provider.async_current.assert_awaited_once()
    runtime = entry.runtime_data
    add_entities = MagicMock()
    await async_setup_sensors(hass, entry, add_entities)
    entities: list[NedSensor] = list(add_entities.call_args.args[0])
    assert len(entities) == 5
    assert {entity.entity_description.key for entity in entities} == set(POWER_DATASETS)
    # Preserve coverage for the reserved, not registered sensor descriptions.
    entities.extend(
        NedSensor(
            runtime.current,
            entry.entry_id,
            description,
        )
        for description in SENSOR_DESCRIPTIONS
        if SensorKey(description.key) not in POWER_DATASETS
    )
    sensors = {entity.entity_description.key: entity for entity in entities}
    solar = sensors[SensorKey.SOLAR]
    renewable = sensors[SensorKey.RENEWABLE_SHARE]
    assert solar.coordinator is runtime.current
    assert solar.unique_id == f"{entry.entry_id}_0_2_1_4_0_2_capacity"
    with patch(
        "custom_components.nationaal_energie_dashboard.sensor.datetime"
    ) as clock:
        clock.now.return_value = _START + QUARTER
        assert solar.available
        assert solar.native_value == 1000
        assert sensors[SensorKey.CO2_INTENSITY].native_value == 250
        assert sensors[SensorKey.CO2_FORECAST].native_value == 300
        assert renewable.native_value == pytest.approx(70.3)
        assert renewable.extra_state_attributes == {
            "valid_from": _START.isoformat(),
            "valid_to": (_START + QUARTER).isoformat(),
            "method_version": "2026-v1",
            "waste_renewable_factor": 0.53,
            "waste_factor_year": 2025,
        }
        assert not sensors[SensorKey.WIND_ONSHORE].available
        assert sensors[SensorKey.WIND_ONSHORE].native_value is None
        assert sensors[SensorKey.WIND_ONSHORE].extra_state_attributes == {}
        runtime.current.last_update_success = False
        assert not solar.available
        runtime.current.last_update_success = True
        clock.now.return_value = _START + timedelta(hours=2)
        assert not solar.available
    solar.hass = hass
    with (
        patch(
            "custom_components.nationaal_energie_dashboard.sensor.async_track_utc_time_change"
        ) as track,
        patch.object(solar, "async_write_ha_state") as write,
    ):
        await solar.async_added_to_hass()
        track.call_args.args[1](_START)
        write.assert_called_once()
        solar.add_to_platform_abort()
        track.return_value.assert_called_once()
    with patch.object(
        hass.config_entries, "async_unload_platforms", new_callable=AsyncMock
    ) as unload:
        unload.return_value = True
        assert await async_unload_entry(hass, entry)
        unload.assert_awaited_once_with(entry, PLATFORMS)
    await runtime.current.async_shutdown()


@pytest.mark.parametrize(
    ("now", "expected_days"),
    [
        (_START, 1),
        (_START.replace(hour=0, minute=15), 2),
    ],
)
@pytest.mark.asyncio
async def test_actual_alpha_provider(
    hass: HomeAssistant, now: datetime, expected_days: int
) -> None:
    """Exercise the real provider, session, parser and bounded UTC-day queries."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_KEY: "synthetic-key"})
    session = MagicMock(spec=ClientSession)

    def response_for_request(
        _path: str, *, params: dict[str, str], headers: dict[str, str]
    ) -> TransportResponse:
        """Return only synthetic records for the requested dataset and day."""
        assert headers["X-AUTH-TOKEN"] == "synthetic-key"
        dataset = NedPowerDataset((int(params["type"]), int(params["activity"])))
        return _power_response(dataset, date.fromisoformat(params["validfrom[after]"]))

    with (
        patch(
            "custom_components.nationaal_energie_dashboard.coordinator.datetime"
        ) as clock,
        patch(
            "custom_components.nationaal_energie_dashboard.coordinator.async_create_clientsession",
            return_value=session,
        ) as get_session,
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
    ):
        clock.now.return_value = now
        get.side_effect = response_for_request
        provider = create_provider(hass, entry)
        snapshot = await provider.async_current()
    get_session.assert_called_once_with(
        hass, middlewares=(get_request_budget(hass).async_middleware,)
    )
    assert set(snapshot) == set(POWER_DATASETS)
    assert all(len(series) == expected_days for series in snapshot.values())
    assert all(item.value == 1234 for series in snapshot.values() for item in series)
    assert get.await_count == expected_days * 5
    assert get_request_budget(hass) is get_request_budget(hass)
    # The mocked transport bypasses aiohttp's physical attempt middleware.
    assert get_request_budget(hass).remaining == 120
    session.close.assert_not_awaited()


@pytest.mark.parametrize(
    ("error", "expected", "translation_key"),
    [
        (
            NedAuthenticationError("synthetic"),
            ConfigEntryAuthFailed,
            "authentication_failed",
        ),
        (NedAccessDeniedError("synthetic"), UpdateFailed, "update_failed"),
        (NedResponseError("synthetic"), UpdateFailed, "update_failed"),
        (NedRateLimitError("synthetic"), UpdateFailed, "rate_limited"),
    ],
)
@pytest.mark.asyncio
async def test_provider_denial(
    error: Exception,
    expected: type[Exception],
    translation_key: str,
) -> None:
    """Stop the batch; do not treat ambiguous access denial as reauthentication."""
    client = MagicMock(spec=NedQuarterClient)
    client.async_read_day = AsyncMock(side_effect=error)
    provider = NedAlphaProvider(client, "synthetic-key", NedRequestBudget())
    with pytest.raises(expected) as raised:
        await provider.async_current()
    assert isinstance(raised.value, ConfigEntryAuthFailed | UpdateFailed)
    assert raised.value.translation_key == translation_key
    if isinstance(error, NedRateLimitError):
        assert isinstance(raised.value, UpdateFailed)
        assert raised.value.retry_after == 300
    expected_attempts = (
        1 if isinstance(error, NedAuthenticationError | NedRateLimitError) else 5
    )
    assert client.async_read_day.await_count == expected_attempts


@pytest.mark.asyncio
async def test_partial_recovery(caplog: pytest.LogCaptureFixture) -> None:
    """Keep successful datasets available and log one failure and one recovery."""
    client = MagicMock(spec=NedQuarterClient)
    provider = NedAlphaProvider(client, "synthetic-key", NedRequestBudget())
    reading = NedPowerReading(_START, _START + QUARTER, 1234)
    client.async_read_day = AsyncMock(
        side_effect=[NedAccessDeniedError("synthetic"), *[(reading,)] * 4] * 2
        + [(reading,)] * 5
    )
    with (
        caplog.at_level("INFO"),
        patch(
            "custom_components.nationaal_energie_dashboard.coordinator.datetime"
        ) as clock,
    ):
        clock.now.return_value = _START + QUARTER
        first = await provider.async_current()
        second = await provider.async_current()
        third = await provider.async_current()
    assert SensorKey.SOLAR not in first
    assert first == second
    assert set(third) == set(POWER_DATASETS)
    assert caplog.text.count("NED dataset solar unavailable") == 1
    assert caplog.text.count("NED dataset solar recovered") == 1


@pytest.mark.asyncio
async def test_future_quarter_not_promoted() -> None:
    """Never publish a quarter that was open when its request started."""
    client = MagicMock(spec=NedQuarterClient)
    provider = NedAlphaProvider(client, "synthetic-key", NedRequestBudget())
    reading = NedPowerReading(_START, _START + QUARTER, 1234)
    client.async_read_day = AsyncMock(return_value=(reading,))
    with patch(
        "custom_components.nationaal_energie_dashboard.coordinator.datetime"
    ) as clock:
        clock.now.return_value = _START
        snapshot = await provider.async_current()
    assert all(not series for series in snapshot.values())
    assert select_reading(
        snapshot[SensorKey.SOLAR], _START + QUARTER, forecast=False
    ) is None


def test_received_at_clock_rollback() -> None:
    """Do not publish a cached reading from a later clock position."""
    reading = NedReading(_START, _START + QUARTER, 1, _START + 2 * QUARTER)
    assert select_reading((reading,), _START + QUARTER, forecast=False) is None
    assert select_reading((reading,), _START + 2 * QUARTER, forecast=False) == reading

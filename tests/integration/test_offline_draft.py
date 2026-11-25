"""Exercise sensor logic and the draft configuration flow without live NED."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.nationaal_energie_dashboard.config_flow import NedConfigFlow
from custom_components.nationaal_energie_dashboard.const import (
    CONTRACT_PENDING,
    DOMAIN,
    QUARTER,
    SENSOR_IDENTIFIERS,
    SensorKey,
)
from custom_components.nationaal_energie_dashboard.coordinator import (
    NedReading,
    estimate_renewable_share,
    select_reading,
)
from custom_components.nationaal_energie_dashboard.sensor import SENSOR_DESCRIPTIONS
from ned_api import (
    NedConnectionError,
    NedResponseError,
    NedTimeoutError,
    TransportResponse,
)

_START = datetime(2026, 11, 22, 12, tzinfo=UTC)


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
    """Show the credential form; the blocked backend cannot create an entry."""
    flow = _flow(hass)
    result = await flow.async_step_user()
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    result = await flow.async_step_user({CONF_API_KEY: "synthetic-key"})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": CONTRACT_PENDING}
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
    response = TransportResponse(
        200,
        b'{"hydra:member":[{"point":"/v1/points/0","type":"/v1/types/2",'
        b'"activity":"/v1/activities/1","classification":"/v1/classifications/2",'
        b'"granularity":"/v1/granularities/4",'
        b'"granularitytimezone":"/v1/granularity_time_zones/0"}]}',
        "application/ld+json",
    )
    with (
        patch(
            "custom_components.nationaal_energie_dashboard.config_flow._ensure_authentication_ready",
        ),
        patch(
            "custom_components.nationaal_energie_dashboard.config_flow.async_get_clientsession",
            return_value=session,
        ) as get_session,
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
    ):
        get.return_value = response
        result = await flow.async_step_user({CONF_API_KEY: "synthetic-key"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_API_KEY: "synthetic-key"}
    get_session.assert_called_once_with(hass)
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
            "custom_components.nationaal_energie_dashboard.config_flow._ensure_authentication_ready",
        ),
        patch(
            "custom_components.nationaal_energie_dashboard.config_flow.async_get_clientsession",
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
    session.close.assert_not_awaited()


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (NedConnectionError("synthetic"), "cannot_connect"),
        (NedTimeoutError("synthetic"), "cannot_connect"),
        (NedResponseError("synthetic"), "cannot_validate"),
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

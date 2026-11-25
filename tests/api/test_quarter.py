"""Verify the alpha quarter contract using only synthetic transport responses."""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession

from ned_api import (
    NedAccessDeniedError,
    NedApiError,
    NedAuthenticationError,
    NedPowerDataset,
    NedQuarterClient,
    NedRequestBudget,
    NedResponseError,
    NedValidationError,
    TransportResponse,
    validate_key_format,
)

_START = datetime(2026, 11, 22, tzinfo=UTC)
_DAY = _START.date()
_QUARTER = timedelta(minutes=15)
_MEDIA = "application/ld+json"


def _record(
    dataset: NedPowerDataset = NedPowerDataset.SOLAR,
    start: datetime = _START,
    capacity: object = 1234,
) -> dict[str, object]:
    """Supply one independently constructed contract-shaped record."""
    type_id, activity = dataset.value
    return {
        "point": "/v1/points/0",
        "type": f"/v1/types/{type_id}",
        "activity": f"/v1/activities/{activity}",
        "classification": "/v1/classifications/2",
        "granularity": "/v1/granularities/4",
        "granularitytimezone": "/v1/granularity_time_zones/0",
        "validfrom": start.isoformat(),
        "validto": (start + _QUARTER).isoformat(),
        "capacity": capacity,
        "volume": 999,
    }


def _response(records: list[object], **extra: object) -> TransportResponse:
    """Build the bounded collection with optional metadata overrides."""
    document = {"hydra:member": records, "hydra:totalItems": len(records)} | extra
    return TransportResponse(200, json.dumps(document).encode(), _MEDIA)


@pytest.mark.parametrize("dataset", list(NedPowerDataset))
@pytest.mark.asyncio
async def test_read_day(dataset: NedPowerDataset) -> None:
    """Use exact query dimensions and native capacity; retain real zero and gaps."""
    client = NedQuarterClient(MagicMock(spec=ClientSession), NedRequestBudget())
    first = _record(dataset, capacity=0)
    first["type"] = f"https://api.ned.nl/v1/types/{dataset.value[0]}"
    second = _record(dataset, _START + 2 * _QUARTER, 1234.5)
    with patch(
        "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
    ) as get:
        get.return_value = _response([second, first])
        readings = await client.async_read_day("synthetic-key", dataset, _DAY)
    assert client.origin == "https://api.ned.nl"
    assert [(item.valid_from, item.capacity_kw) for item in readings] == [
        (_START, 0),
        (_START + 2 * _QUARTER, 1234.5),
    ]
    assert readings[0].valid_to == _START + _QUARTER
    get.assert_awaited_once_with(
        "/v1/utilizations",
        params={
            "point": "0",
            "type": str(dataset.value[0]),
            "activity": str(dataset.value[1]),
            "classification": "2",
            "granularity": "4",
            "granularitytimezone": "0",
            "page": "1",
            "itemsPerPage": "100",
            "order[validfrom]": "asc",
            "validfrom[after]": "2026-11-22",
            "validfrom[strictly_before]": "2026-11-23",
        },
        headers={"Accept": _MEDIA, "X-AUTH-TOKEN": "synthetic-key"},
    )


@pytest.mark.asyncio
async def test_empty_day() -> None:
    """An empty collection is absent data rather than zero power."""
    client = NedQuarterClient(MagicMock(spec=ClientSession), NedRequestBudget())
    with patch(
        "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
    ) as get:
        get.return_value = _response([])
        assert (
            await client.async_read_day("synthetic-key", NedPowerDataset.SOLAR, _DAY)
            == ()
        )


@pytest.mark.parametrize("value", [None, 12, "", " ", "a b", "a\nb", "é", "abc\x7f"])
def test_invalid_key_format(value: object) -> None:
    """Reject absent and unsafe header values without including them in errors."""
    with pytest.raises(NedValidationError, match="printable ASCII"):
        validate_key_format(value)


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (TransportResponse(401, b"synthetic-key", _MEDIA), NedAuthenticationError),
        (
            TransportResponse(403, b"synthetic-key", "application/json"),
            NedAccessDeniedError,
        ),
        (TransportResponse(500, b"synthetic-key", _MEDIA), NedResponseError),
        (TransportResponse(200, b"{}", "text/html"), NedResponseError),
        (TransportResponse(200, b"bad-json", _MEDIA), NedResponseError),
        (TransportResponse(200, b"[]", _MEDIA), NedResponseError),
        (TransportResponse(200, b"{}", _MEDIA), NedResponseError),
        (_response([0]), NedResponseError),
        (_response([{}] * 97), NedResponseError),
        (_response([], **{"hydra:totalItems": True}), NedResponseError),
        (_response([], **{"hydra:totalItems": "0"}), NedResponseError),
        (_response([], **{"hydra:totalItems": 1}), NedResponseError),
        (_response([], **{"hydra:view": []}), NedResponseError),
        (
            _response([], **{"hydra:view": {"hydra:next": "/v1/utilizations?page=2"}}),
            NedResponseError,
        ),
        (_response([_record(), _record()]), NedResponseError),
    ],
)
@pytest.mark.asyncio
async def test_invalid_collection(
    response: TransportResponse, expected: type[NedApiError]
) -> None:
    """Reject invalid collection contracts and never follow an advertised link."""
    client = NedQuarterClient(MagicMock(spec=ClientSession), NedRequestBudget())
    with (
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
        pytest.raises(expected) as raised,
    ):
        get.return_value = response
        await client.async_read_day("synthetic-key", NedPowerDataset.SOLAR, _DAY)
    assert type(raised.value) is expected
    assert "synthetic-key" not in str(raised.value)
    assert raised.value.__cause__ is None
    get.assert_awaited_once()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("point", "/v1/points/1"),
        ("classification", "/v1/classifications/1"),
        ("activity", "/v1/activities/2"),
        ("granularitytimezone", "/v1/granularity_time_zones/1"),
        ("validfrom", None),
        ("validfrom", "invalid"),
        ("validfrom", "2026-11-22T00:00:00"),
        ("validfrom", "2026-11-22T01:00:00+01:00"),
        ("validfrom", "2026-11-21T23:45:00Z"),
        ("validfrom", "2026-11-22T00:01:00Z"),
        ("validfrom", "2026-11-22T00:00:01Z"),
        ("validfrom", "2026-11-22T00:00:00.000001Z"),
        ("validto", "2026-11-23T00:15:00Z"),
        ("validto", "2026-11-22T00:00:00Z"),
        ("validto", "2026-11-22T00:30:00Z"),
        ("capacity", None),
        ("capacity", True),
        ("capacity", "1"),
        ("capacity", -1),
        ("capacity", float("inf")),
        ("capacity", float("nan")),
        ("capacity", 10**400),
    ],
)
@pytest.mark.asyncio
async def test_invalid_record(field: str, value: object) -> None:
    """Reject invalid dimensions, UTC intervals and nonfinite or missing capacity."""
    client = NedQuarterClient(MagicMock(spec=ClientSession), NedRequestBudget())
    record = _record()
    record[field] = value
    with (
        patch(
            "ned_api.transport.NedTransport.async_get", new_callable=AsyncMock
        ) as get,
        pytest.raises(NedResponseError),
    ):
        get.return_value = _response([record])
        await client.async_read_day("synthetic-key", NedPowerDataset.SOLAR, _DAY)
    get.assert_awaited_once()

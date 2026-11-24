"""Observe a fixed national P0 matrix without exposing upstream values."""

import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, DecimalException, InvalidOperation
from urllib.parse import parse_qsl, urlencode, urlsplit
from zoneinfo import ZoneInfo

from scripts.ned_contract_probe import (
    HOST,
    PROBE_ERRORS,
    ProbeError,
    fetch_body,
    report_failure,
    summarize,
)

DATASETS = (1, 2, 51, 27, 59)
METRICS = ("capacity", "volume", "emission", "emissionfactor", "percentage")
MAX_REQUESTS = 18
TIMEZONE_REQUESTS = 6
DAILY_REQUESTS = 2
SEMANTIC_REQUESTS = 6
REQUEST_BUDGETS = {
    "full": MAX_REQUESTS,
    "timezone": TIMEZONE_REQUESTS,
    "daily": DAILY_REQUESTS,
    "semantics": SEMANTIC_REQUESTS,
}
RESOURCE_NAMES = {
    "type": "types",
    "point": "points",
    "activity": "activities",
    "classification": "classifications",
    "granularity": "granularities",
    "granularitytimezone": "granularity_time_zones",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class Query:
    """One fixed national dataset and local or UTC calendar day."""

    type_id: int
    classification: int
    day: date
    timezone_id: int = 0
    granularity: int = 4
    page_size: int = 100
    inspect_semantics: bool = False

    def __post_init__(self) -> None:
        """Reject dimensions outside the approved observation scope."""
        if (
            self.type_id not in DATASETS
            or self.classification not in (1, 2)
            or self.timezone_id not in (0, 1)
            or self.granularity not in (4, 6)
            or self.page_size not in (48, 100)
        ):
            raise ProbeError("Query outside approved scope")

    def dimensions(self) -> dict[str, int]:
        """Return the exact requested dimensions."""
        return {
            "point": 0,
            "type": self.type_id,
            "activity": 2 if self.type_id == 59 else 1,
            "classification": self.classification,
            "granularity": self.granularity,
            "granularitytimezone": self.timezone_id,
        }

    def path(self, page: int) -> str:
        """Build a bounded request without trusting response-provided URLs."""
        if page not in (1, 2) or (page == 2 and self.page_size != 48):
            raise ProbeError("Page outside approved scope")
        parameters = {
            **self.dimensions(),
            "page": page,
            "itemsPerPage": self.page_size,
            "order[validfrom]": "asc",
            "validfrom[after]": self.day.isoformat(),
            "validfrom[strictly_before]": (self.day + timedelta(days=1)).isoformat(),
        }
        return f"/v1/utilizations?{urlencode(parameters)}"

    def intervals(self) -> list[tuple[datetime, datetime]]:
        """Calculate calendar bounds; UTC daily coverage is a test hypothesis."""
        zone = ZoneInfo("Europe/Amsterdam") if self.timezone_id else UTC
        start = datetime.combine(self.day, time.min, zone).astimezone(UTC)
        end = datetime.combine(self.day + timedelta(days=1), time.min, zone).astimezone(
            UTC
        )
        if self.granularity == 6:
            return [(start, end)]
        step = timedelta(minutes=15)
        return [
            (start + i * step, start + (i + 1) * step)
            for i in range((end - start) // step)
        ]


def build_suite(today: date) -> tuple[Query, ...]:
    """Build ten P0 queries, one two-page query and six timezone queries."""
    history = today - timedelta(days=2)
    matrix = tuple(
        Query(type_id=type_id, classification=classification, day=day)
        for type_id in DATASETS
        for classification, day in ((2, history), (1, today + timedelta(days=1)))
    )
    spring = date(2026, 3, 29)
    autumn = date(2026, 10, 25)
    return (
        *matrix,
        Query(type_id=2, classification=2, day=history, page_size=48),
        *(
            Query(type_id=2, classification=2, day=day, timezone_id=1)
            for day in (spring, autumn, history)
        ),
        *(
            Query(type_id=2, classification=2, day=day, timezone_id=1, granularity=6)
            for day in (spring, autumn)
        ),
        Query(type_id=2, classification=2, day=history, granularity=6),
    )


def select_suite(today: date, scope: str) -> tuple[Query, ...]:
    """Select a bounded scope without arbitrary request parameters."""
    if scope == "daily":
        return (
            Query(
                type_id=2,
                classification=2,
                day=date(2026, 10, 25),
                timezone_id=1,
                granularity=6,
            ),
            Query(type_id=2, classification=2, day=date(2026, 11, 22), granularity=6),
        )
    if scope == "semantics":
        return (
            *(
                Query(
                    type_id=type_id,
                    classification=2,
                    day=date(2026, 11, 22),
                    inspect_semantics=True,
                )
                for type_id in DATASETS
            ),
            Query(
                type_id=27,
                classification=1,
                day=today + timedelta(days=1),
                inspect_semantics=True,
            ),
        )
    suite = build_suite(today)
    if scope == "full":
        return suite
    if scope == "timezone":
        return suite[-TIMEZONE_REQUESTS:]
    raise ProbeError("Unsupported contract scope")


def _check_next(value: object, expected_path: str) -> None:
    """Require the exact next query and never follow a supplied URL."""
    if not isinstance(value, str):
        raise ProbeError("Missing or invalid next link")
    actual = urlsplit(value)
    expected = urlsplit(expected_path)
    if (
        (actual.scheme, actual.netloc) not in (("", ""), ("https", HOST))
        or actual.fragment
        or actual.path != expected.path
        or sorted(parse_qsl(actual.query, keep_blank_values=True))
        != sorted(parse_qsl(expected.query, keep_blank_values=True))
    ):
        raise ProbeError("Next link changes host, path or query")


def _timestamp(value: object) -> datetime:
    """Parse a timestamp and require an explicit UTC offset."""
    if not isinstance(value, str):
        raise ProbeError("Timestamp is not a string")
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() != timedelta(0):
        raise ProbeError("Timestamp is not UTC-aware")
    return parsed.astimezone(UTC)


def _number(value: object) -> Decimal:
    """Accept finite numeric representations, never booleans or nonfinite values."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ProbeError("Invalid numeric representation")
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise ProbeError("Invalid numeric representation") from error
    if not number.is_finite():
        raise ProbeError("Nonfinite numeric representation")
    return number


def _response_timezone(value: object) -> int:
    """Identify only known timezone IRIs; never expose arbitrary source values."""
    for identifier in (0, 1):
        iri = f"/v1/{RESOURCE_NAMES['granularitytimezone']}/{identifier}"
        if value in (iri, f"https://{HOST}{iri}"):
            return identifier
    raise ProbeError("Unrecognized response timezone reference")


def _inspect_record(
    record: dict[str, object], query: Query, timezone_ids: set[int]
) -> tuple[datetime, datetime]:
    """Verify the documented IRI dimensions, identity and interval timestamps."""
    for field, identifier in query.dimensions().items():
        if field == "granularitytimezone":
            timezone_ids.add(_response_timezone(record.get(field)))
            continue
        iri = f"/v1/{RESOURCE_NAMES[field]}/{identifier}"
        if record.get(field) not in (iri, f"https://{HOST}{iri}"):
            raise ProbeError(f"Unexpected dataset dimension: {field}")
    identifier_value = record.get("id")
    if isinstance(identifier_value, bool) or not isinstance(
        identifier_value, (int, str)
    ):
        raise ProbeError("Invalid record identifier type")
    _timestamp(record.get("lastupdate"))
    start = _timestamp(record.get("validfrom"))
    end = _timestamp(record.get("validto"))
    if end <= start:
        raise ProbeError("Nonpositive record interval")
    return start, end


def _metric_counts(records: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    """Report only counts of missing, null, zero, negative and above-one values."""
    result: dict[str, dict[str, int]] = {}
    for field in METRICS:
        counts = {"missing": 0, "null": 0, "zero": 0, "negative": 0, "above_one": 0}
        for record in records:
            if field not in record:
                counts["missing"] += 1
            elif record[field] is None:
                counts["null"] += 1
            else:
                number = _number(record[field])
                counts["zero"] += int(number == 0)
                counts["negative"] += int(number < 0)
                counts["above_one"] += int(number > 1)
        result[field] = counts
    return result


def _metric_value(record: dict[str, object], field: str) -> Decimal | None:
    """Read an available finite metric without interpreting null as zero."""
    value = record.get(field)
    return None if value is None else _number(value)


def _capacity_relation(record: dict[str, object]) -> str:
    """Classify the documented quarter-hour relation without assuming rounding."""
    capacity = _metric_value(record, "capacity")
    volume = _metric_value(record, "volume")
    if capacity is None or volume is None:
        return "unavailable"
    difference = abs(capacity - 4 * volume)
    if difference == 0:
        return "exact"
    return "within_3_kw" if difference <= 3 else "outside_3_kw"


def _emission_relation(record: dict[str, object]) -> str:
    """Compare kg and tonne hypotheses, not an authoritative unit decision."""
    volume = _metric_value(record, "volume")
    factor = _metric_value(record, "emissionfactor")
    emission = _metric_value(record, "emission")
    if volume is None or factor is None or emission is None:
        return "unavailable"
    if volume <= 0 or factor <= 0 or emission <= 0:
        return "nonpositive"
    expected_kg = volume * factor
    tolerance = expected_kg * Decimal("0.01")
    if abs(emission - expected_kg) <= tolerance:
        return "kg_within_1_percent"
    if abs(emission * 1000 - expected_kg) <= tolerance:
        return "tonne_within_1_percent"
    return "neither"


def _semantic_counts(
    records: list[dict[str, object]], query: Query
) -> dict[str, dict[str, int]]:
    """Count diagnostic relationships only, without raw values or residuals."""
    capacity = dict.fromkeys(("exact", "within_3_kw", "outside_3_kw", "unavailable"), 0)
    emission = dict.fromkeys(
        (
            "kg_within_1_percent",
            "tonne_within_1_percent",
            "neither",
            "nonpositive",
            "unavailable",
        ),
        0,
    )
    try:
        for record in records:
            capacity[_capacity_relation(record)] += 1
            if query.type_id == 27:
                emission[_emission_relation(record)] += 1
    except DecimalException as error:
        raise ProbeError("Invalid metric arithmetic") from error
    result = {"capacity_relation": capacity}
    if query.type_id == 27:
        result["emission_unit_hypothesis"] = emission
    return result


def _daily_timing(
    expected: tuple[datetime, datetime],
    intervals: list[tuple[datetime, datetime]],
) -> dict[str, float | None]:
    """Report only duration and signed boundary offsets, not raw timestamps."""
    expected_start, expected_end = expected
    result: dict[str, float | None] = {
        "expected_duration_seconds": (expected_end - expected_start).total_seconds(),
        "observed_duration_seconds": None,
        "start_offset_seconds": None,
        "end_offset_seconds": None,
    }
    if len(intervals) == 1:
        actual_start, actual_end = intervals[0]
        result.update(
            observed_duration_seconds=(actual_end - actual_start).total_seconds(),
            start_offset_seconds=(actual_start - expected_start).total_seconds(),
            end_offset_seconds=(actual_end - expected_end).total_seconds(),
        )
    return result


def observe(api_key: str, query: Query) -> bool:
    """Validate one or exactly two pages, printing only sanitized observations."""
    print(json.dumps({"query": query.dimensions(), "day": query.day.isoformat()}))
    expected = query.intervals()
    page_count = 2 if query.page_size == 48 else 1
    intervals: list[tuple[datetime, datetime]] = []
    timezone_ids: set[int] = set()
    total_matches = False
    for page in range(1, page_count + 1):
        body = fetch_body(api_key, query.path(page))
        shape = summarize(body)
        document = json.loads(body)
        if shape["member_key"] != "hydra:member":
            raise ProbeError("Unexpected collection member key")
        records: list[dict[str, object]] = document["hydra:member"]
        if len(records) > query.page_size:
            raise ProbeError("Page exceeds requested record limit")
        intervals.extend(
            _inspect_record(record, query, timezone_ids) for record in records
        )
        view = document.get("hydra:view", {})
        if not isinstance(view, dict):
            raise ProbeError("Invalid pagination metadata")
        if page < page_count:
            _check_next(view.get("hydra:next"), query.path(page + 1))
        elif "hydra:next" in view:
            raise ProbeError("Unexpected extra page")
        total = document.get("hydra:totalItems")
        total_matches = (
            isinstance(total, int)
            and not isinstance(total, bool)
            and total == len(expected)
        )
        print(
            json.dumps(
                {
                    "query": query.dimensions(),
                    "day": query.day.isoformat(),
                    "page": page,
                    **shape,
                    "metric_counts": _metric_counts(records),
                    **(
                        {"semantic_counts": _semantic_counts(records, query)}
                        if query.inspect_semantics
                        else {}
                    ),
                    "total_matches_expected": total_matches,
                    "response_timezone_ids": sorted(timezone_ids),
                },
                sort_keys=True,
            )
        )
        if not isinstance(total, int) or isinstance(total, bool) or total < 0:
            raise ProbeError("Invalid totalItems count or type")
        if page_count == 2 and not total_matches:
            raise ProbeError("Unexpected paginated totalItems count")
    complete = intervals == expected
    print(
        json.dumps(
            {
                "query": query.dimensions(),
                "day": query.day.isoformat(),
                "expected_records": len(expected),
                "coverage_complete": complete,
                **(
                    _daily_timing(expected[0], intervals)
                    if query.granularity == 6
                    else {}
                ),
                "timezone_matches_request": timezone_ids <= {query.timezone_id},
            },
            sort_keys=True,
        )
    )
    return complete and total_matches and timezone_ids <= {query.timezone_id}


def main() -> int:
    """Run the fixed suite only with an explicitly injected key."""
    api_key = os.environ.get("NED_API_KEY", "")
    if not api_key.isascii() or not api_key.isprintable() or not api_key.strip():
        print("Missing or invalid NED_API_KEY", file=sys.stderr)
        return 1
    scope = os.environ.get("NED_CONTRACT_SCOPE", "semantics")
    try:
        suite = select_suite(datetime.now(UTC).date(), scope)
        budget = REQUEST_BUDGETS[scope]
        if sum(2 if query.page_size == 48 else 1 for query in suite) != budget:
            raise ProbeError("Invalid request budget")
        results = [observe(api_key, query) for query in suite]
    except PROBE_ERRORS as error:
        return report_failure(error)
    if not all(results):
        print(
            "Contract mismatch: interval coverage, total count or response timezone",
            file=sys.stderr,
        )
        return 1
    print("Bounded P0 observations completed; semantics still require review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

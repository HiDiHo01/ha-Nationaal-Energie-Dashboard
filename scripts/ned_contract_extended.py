"""Observe a fixed national P0 matrix without exposing upstream values."""

import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qsl, urlencode, urlsplit
from zoneinfo import ZoneInfo

from scripts.ned_contract_probe import (
    HOST,
    TRANSPORT_ERRORS,
    ProbeError,
    fetch_body,
    summarize,
)

DATASETS = (1, 2, 51, 27, 59)
METRICS = ("capacity", "volume", "emission", "emissionfactor", "percentage")
MAX_REQUESTS = 18


@dataclass(frozen=True, slots=True, kw_only=True)
class Query:
    """One fixed national dataset and local or UTC calendar day."""

    type_id: int
    classification: int
    day: date
    timezone_id: int = 0
    granularity: int = 4
    page_size: int = 100

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
        """Calculate expected UTC intervals for the requested calendar day."""
        zone = ZoneInfo("Europe/Amsterdam") if self.timezone_id else UTC
        start = datetime.combine(self.day, time.min, zone).astimezone(UTC)
        end = datetime.combine(self.day + timedelta(days=1), time.min, zone).astimezone(
            UTC
        )
        if self.granularity == 6:
            return [(start, end)] if self.timezone_id else []
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


def _inspect_record(
    record: dict[str, object], query: Query
) -> tuple[datetime, datetime]:
    """Verify the documented IRI dimensions, identity and interval timestamps."""
    resources = {
        "type": "types",
        "point": "points",
        "activity": "activities",
        "classification": "classifications",
        "granularity": "granularities",
        "granularitytimezone": "granularity_time_zones",
    }
    for field, identifier in query.dimensions().items():
        iri = f"/v1/{resources[field]}/{identifier}"
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
        counts = dict(missing=0, null=0, zero=0, negative=0, above_one=0)
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


def observe(api_key: str, query: Query) -> bool:
    """Validate one or exactly two pages, printing only sanitized observations."""
    print(json.dumps({"query": query.dimensions(), "day": query.day.isoformat()}))
    expected = query.intervals()
    page_count = 2 if query.page_size == 48 else 1
    intervals: list[tuple[datetime, datetime]] = []
    for page in range(1, page_count + 1):
        body = fetch_body(api_key, query.path(page))
        shape = summarize(body)
        document = json.loads(body)
        if shape["member_key"] != "hydra:member":
            raise ProbeError("Unexpected collection member key")
        records: list[dict[str, object]] = document["hydra:member"]
        if len(records) > query.page_size:
            raise ProbeError("Page exceeds requested record limit")
        intervals.extend(_inspect_record(record, query) for record in records)
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
                    "total_matches_expected": total_matches,
                },
                sort_keys=True,
            )
        )
        if not total_matches:
            raise ProbeError("Unexpected totalItems count or type")
    complete = intervals == expected
    print(
        json.dumps(
            {
                "query": query.dimensions(),
                "day": query.day.isoformat(),
                "expected_records": len(expected),
                "coverage_complete": complete,
            },
            sort_keys=True,
        )
    )
    return complete


def main() -> int:
    """Run the fixed suite only with an explicitly injected key."""
    api_key = os.environ.get("NED_API_KEY", "")
    if not api_key.isascii() or not api_key.isprintable() or not api_key.strip():
        print("Missing or invalid NED_API_KEY", file=sys.stderr)
        return 1
    suite = build_suite(datetime.now(UTC).date())
    if sum(2 if query.page_size == 48 else 1 for query in suite) != MAX_REQUESTS:
        print("Invalid request budget", file=sys.stderr)
        return 1
    try:
        results = [observe(api_key, query) for query in suite]
    except ProbeError as error:
        print(f"Contract observation failed: {error}", file=sys.stderr)
        return 1
    except TRANSPORT_ERRORS:
        print("Contract observation failed: transport or JSON error", file=sys.stderr)
        return 1
    if not all(results):
        print("Incomplete or unordered interval coverage", file=sys.stderr)
        return 1
    print("Bounded P0 observations completed; semantics still require review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

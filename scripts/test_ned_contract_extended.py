"""Exercise the extended contract matrix using synthetic offline responses."""

import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from unittest.mock import patch

from scripts import ned_contract_extended as extended
from scripts.ned_contract_probe import ProbeError


class ExtendedTests(unittest.TestCase):
    """Verify scope, record coverage, pagination and redacted failures."""

    @staticmethod
    def _response(query: extended.Query, page: int = 1) -> dict[str, object]:
        """Create synthetic records with documented IRIs and known intervals."""
        intervals = query.intervals()
        records = [
            {
                **{
                    field: f"/v1/{extended.RESOURCE_NAMES[field]}/{value}"
                    for field, value in query.dimensions().items()
                },
                "id": index,
                "validfrom": start.isoformat(),
                "validto": end.isoformat(),
                "lastupdate": end.isoformat(),
                "capacity": "12345.67",
                "volume": 0,
                "emission": None,
                "percentage": 0.5,
                "unknown": "synthetic-private",
            }
            for index, (start, end) in enumerate(intervals)
        ]
        return {
            "hydra:member": records[
                (page - 1) * query.page_size : page * query.page_size
            ],
            "hydra:totalItems": len(intervals),
            "hydra:view": {"hydra:next": query.path(2)}
            if page == 1 and query.page_size == 48
            else {},
        }

    def test_suite(self) -> None:
        """Constrain total requests and cover all national P0 combinations."""
        suite = extended.build_suite(date(2026, 11, 24))
        self.assertEqual(len(suite), 17)
        self.assertEqual(sum(2 if q.page_size == 48 else 1 for q in suite), 18)
        self.assertEqual(
            {(q.type_id, q.classification) for q in suite[:10]},
            {(type_id, kind) for type_id in extended.DATASETS for kind in (1, 2)},
        )
        self.assertEqual(
            [len(q.intervals()) for q in suite[11:]], [92, 100, 96, 1, 1, 0]
        )
        self.assertTrue(
            all(q.dimensions()["activity"] == 2 for q in suite if q.type_id == 59)
        )
        with self.assertRaises(ProbeError):
            extended.Query(type_id=999, classification=2, day=date(2026, 11, 22))
        with self.assertRaises(ProbeError):
            suite[0].path(2)

    def test_all_observations(self) -> None:
        """Accept all synthetic valid pages without logging raw source values."""
        suite = extended.build_suite(date(2026, 11, 24))
        responses = [
            json.dumps(self._response(query, page)).encode()
            for query in suite
            for page in range(1, 3 if query.page_size == 48 else 2)
        ]
        with (
            patch.object(extended, "fetch_body", side_effect=responses) as fetch,
            redirect_stdout(io.StringIO()) as output,
        ):
            self.assertTrue(
                all(extended.observe("synthetic", query) for query in suite)
            )
            self.assertEqual(fetch.call_count, 18)
            self.assertNotIn("12345.67", output.getvalue())
            self.assertNotIn("synthetic-private", output.getvalue())
            self.assertIn('"missing": 96', output.getvalue())
            self.assertIn('"null": 96', output.getvalue())

    def test_unsafe_next(self) -> None:
        """Refuse altered filters, hosts and pagination before the next request."""
        query = extended.Query(
            type_id=2, classification=2, day=date(2026, 11, 22), page_size=48
        )
        for link in (
            "https://example.org" + query.path(2),
            query.path(2).replace("type=2", "type=59"),
            query.path(1),
            query.path(2) + "&page=2",
            query.path(2) + "#fragment",
        ):
            document = self._response(query)
            document["hydra:view"] = {"hydra:next": link}
            with (
                self.subTest(link=link),
                patch.object(
                    extended, "fetch_body", return_value=json.dumps(document).encode()
                ) as fetch,
                redirect_stdout(io.StringIO()),
                self.assertRaises(ProbeError),
            ):
                extended.observe("synthetic", query)
            self.assertEqual(fetch.call_count, 1)

    def test_invalid_records(self) -> None:
        """Reject invalid dimensions, timestamps, booleans and nonfinite metrics."""
        query = extended.Query(type_id=2, classification=2, day=date(2026, 11, 22))
        for field, value in (
            ("type", "/v1/types/1"),
            ("granularitytimezone", "https://example.org/synthetic-private"),
            ("validfrom", "2026-11-22T00:00:00"),
            ("validto", "2026-11-21T00:00:00+00:00"),
            ("capacity", True),
            ("capacity", "NaN"),
            ("capacity", "invalid"),
            ("capacity", float("inf")),
        ):
            document = self._response(query)
            records = document["hydra:member"]
            if not isinstance(records, list):
                self.fail("Synthetic records missing")
            records[0][field] = value
            with (
                self.subTest(field=field, value=value),
                patch.object(
                    extended, "fetch_body", return_value=json.dumps(document).encode()
                ),
                redirect_stdout(io.StringIO()),
                self.assertRaises(ProbeError),
            ):
                extended.observe("synthetic", query)

    def test_incomplete_coverage(self) -> None:
        """Do not treat duplicated intervals as complete coverage."""
        query = extended.Query(type_id=2, classification=2, day=date(2026, 11, 22))
        document = self._response(query)
        records = document["hydra:member"]
        if not isinstance(records, list):
            self.fail("Synthetic records missing")
        records[1] = records[0]
        with (
            patch.object(
                extended, "fetch_body", return_value=json.dumps(document).encode()
            ),
            redirect_stdout(io.StringIO()),
        ):
            self.assertFalse(extended.observe("synthetic", query))

    def test_timezone_scope(self) -> None:
        """Select only the six fixed timezone scenarios and reject unknown scopes."""
        today = date(2026, 11, 24)
        self.assertEqual(
            extended.select_suite(today, "timezone"), extended.build_suite(today)[-6:]
        )
        with self.assertRaises(ProbeError):
            extended.select_suite(today, "unapproved")

    def test_timezone_mismatch(self) -> None:
        """Report known response timezone IDs separately from interval coverage."""
        query = extended.Query(
            type_id=2, classification=2, day=date(2026, 3, 29), timezone_id=1
        )
        document = self._response(query)
        records = document["hydra:member"]
        if not isinstance(records, list):
            self.fail("Synthetic records missing")
        for record in records:
            record["granularitytimezone"] = "/v1/granularity_time_zones/0"
        with (
            patch.object(
                extended, "fetch_body", return_value=json.dumps(document).encode()
            ),
            redirect_stdout(io.StringIO()) as output,
        ):
            self.assertFalse(extended.observe("synthetic", query))
            self.assertIn('"coverage_complete": true', output.getvalue())
            self.assertIn('"response_timezone_ids": [0]', output.getvalue())
            self.assertIn('"timezone_matches_request": false', output.getvalue())

    def test_main(self) -> None:
        """Enforce opt-in key injection, request budget and sanitized errors."""
        with (
            patch.dict(os.environ, {"NED_API_KEY": "", "NED_CONTRACT_SCOPE": "full"}),
            patch.object(extended, "observe") as observe,
            redirect_stderr(io.StringIO()) as errors,
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(extended.main(), 1)
            observe.assert_not_called()
            os.environ["NED_API_KEY"] = "synthetic"
            observe.return_value = True
            self.assertEqual(extended.main(), 0)
            self.assertEqual(observe.call_count, 17)
            observe.reset_mock()
            observe.side_effect = OSError("synthetic-private")
            self.assertEqual(extended.main(), 1)
            self.assertEqual(observe.call_count, 1)
            self.assertNotIn("synthetic-private", errors.getvalue())
            observe.reset_mock()
            observe.side_effect = [False, True, True, True, True, True]
            os.environ["NED_CONTRACT_SCOPE"] = "timezone"
            self.assertEqual(extended.main(), 1)
            self.assertEqual(observe.call_count, 6)

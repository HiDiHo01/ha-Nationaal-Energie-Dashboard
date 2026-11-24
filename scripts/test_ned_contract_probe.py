"""Offline tests of the bounded contract probe; no real network or secrets."""

import http.client
import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from scripts import ned_contract_probe as ned


class ProbeTests(unittest.TestCase):
    """Check the request boundary, sanitization and failure paths."""

    def test_query(self) -> None:
        """Constrain the query to a single known dataset and UTC day."""
        parsed = urlsplit(ned.build_path(2, date(2026, 11, 22)))
        self.assertEqual(parsed.path, "/v1/utilizations")
        self.assertEqual(
            parse_qs(parsed.query),
            {
                "page": ["1"],
                "itemsPerPage": ["100"],
                "order[validfrom]": ["asc"],
                "point": ["0"],
                "type": ["2"],
                "activity": ["1"],
                "granularity": ["4"],
                "granularitytimezone": ["0"],
                "classification": ["2"],
                "validfrom[after]": ["2026-11-22"],
                "validfrom[strictly_before]": ["2026-11-23"],
            },
        )
        with self.assertRaises(ned.ProbeError):
            ned.build_path(9, date(2026, 11, 22))

    def test_summary(self) -> None:
        """Report only known keys, types and counts, never raw payload data."""
        body = json.dumps(
            {
                "hydra:member": [{"capacity": 1, "volume": None, "unknown": "private"}],
                "hydra:totalItems": 2,
                "hydra:view": {"hydra:next": "https://example.org/private"},
            }
        ).encode()
        result = ned.summarize(body)
        self.assertEqual(result["record_count"], 1)
        self.assertTrue(result["pagination_metadata_present"])
        self.assertTrue(result["next_link_present"])
        self.assertEqual(result["total_items_type"], "int")
        self.assertNotIn("private", json.dumps(result))
        self.assertIn('"volume": ["NoneType"]', json.dumps(result))
        self.assertEqual(ned.summarize(b'{"member": []}')["record_count"], 0)

    def test_bad_envelope(self) -> None:
        """Reject malformed and unrecognized collections."""
        for body in (b"[]", b"{}", b'{"member": 1}', b'{"member": [1]}'):
            with self.subTest(body=body), self.assertRaises(ned.ProbeError):
                ned.summarize(body)
        with self.assertRaises(ValueError):
            ned.summarize(b"not JSON")

    def test_http_boundaries(self) -> None:
        """Reject redirects, unauthorized responses, media mismatch and oversize."""
        with patch.object(http.client, "HTTPSConnection") as factory:
            connection = factory.return_value
            response = connection.getresponse.return_value
            for status in (302, 401, 403, 429, 500):
                response.status = status
                with self.subTest(status=status), self.assertRaises(ned.ProbeError):
                    ned.probe("synthetic", 2, date(2026, 11, 22))
            self.assertEqual(connection.request.call_count, 5)
            response.read.assert_not_called()
            self.assertEqual(connection.close.call_count, 5)
            response.status = 200
            response.getheader.return_value = "text/html"
            with self.assertRaises(ned.ProbeError):
                ned.probe("synthetic", 2, date(2026, 11, 22))
            response.getheader.return_value = "application/ld+json; charset=utf-8"
            response.read.return_value = b"x" * (ned.MAX_BYTES + 1)
            with self.assertRaises(ned.ProbeError):
                ned.probe("synthetic", 2, date(2026, 11, 22))
            response.read.return_value = b'{"member": [{"volume": 0}]}'
            result = ned.probe("synthetic", 2, date(2026, 11, 22))
            self.assertEqual(result["record_count"], 1)
            factory.assert_called_with("api.ned.nl", timeout=15)
            response.read.assert_called_with(ned.MAX_BYTES + 1)
            self.assertEqual(connection.close.call_count, 8)

    def test_missing_key(self) -> None:
        """Fail before making requests when the key is absent or invalid."""
        for value in ("", " ", "invalid\nvalue"):
            with (
                patch.dict(os.environ, {"NED_API_KEY": value}),
                patch.object(ned, "probe") as observe,
                redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(ned.main(), 1)
                observe.assert_not_called()

    def test_main(self) -> None:
        """Use at most two queries and redact upstream exception text."""
        with (
            patch.dict(os.environ, {"NED_API_KEY": "synthetic"}),
            patch.object(ned, "probe", return_value={"record_count": 1}) as observe,
            redirect_stdout(io.StringIO()) as output,
            redirect_stderr(io.StringIO()) as errors,
        ):
            self.assertEqual(ned.main(), 0)
            self.assertEqual(observe.call_count, 2)
            self.assertNotIn("synthetic", output.getvalue())
            observe.reset_mock()
            observe.side_effect = OSError("synthetic")
            self.assertEqual(ned.main(), 1)
            self.assertEqual(observe.call_count, 1)
            self.assertNotIn("synthetic", errors.getvalue())
            observe.reset_mock()
            observe.side_effect = None
            observe.return_value = {"record_count": 0}
            self.assertEqual(ned.main(), 1)
            self.assertEqual(observe.call_count, 1)

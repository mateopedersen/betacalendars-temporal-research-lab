import sys
import io
from email.message import Message
from datetime import date
from pathlib import Path
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from temporal_lab import api, iso_record, boundary_cases, research, bookmark, markdown_report


class ISOWeekTests(unittest.TestCase):
    def test_reference_cases(self):
        cases = {
            "2018-12-31": "2019-W01-1",
            "2021-01-01": "2020-W53-5",
            "2026-12-28": "2026-W53-1",
            "2026-12-31": "2026-W53-4",
            "2027-01-01": "2026-W53-5",
            "2027-01-03": "2026-W53-7",
            "2027-01-04": "2027-W01-1",
            "2028-02-29": "2028-W09-2",
        }
        for d, week in cases.items():
            with self.subTest(date=d):
                self.assertEqual(iso_record(date.fromisoformat(d))["isoWeekDate"], week)

    def test_full_week(self):
        rec = iso_record(date(2027, 1, 1))
        self.assertEqual((rec["weekStart"], rec["weekEnd"]), ("2026-12-28", "2027-01-03"))
        self.assertTrue(rec["isWeekYearBoundary"])

    def test_window(self):
        records = boundary_cases(2027, days=5)
        self.assertEqual(len(records), 11)
        self.assertEqual(records[5]["date"], "2027-01-01")

    def test_reject_invalid_scan(self):
        with self.assertRaises(ValueError):
            boundary_cases(2027, days=21)

    def test_no_silent_bookmarks(self):
        with self.assertRaisesRegex(RuntimeError, "--confirm-bookmark"):
            bookmark(["existing_id"], "token", confirmed=False)

    def test_search_dedup(self):
        data = {"data": [{"id": "id1", "title": "Temporal API", "url": "https://example.org/one", "source": {"name": "Source"}, "numUpvotes": 11}]}
        with patch("temporal_lab.api", return_value=data) as mocked:
            results = research(["Temporal", "Temporal JavaScript"], 3, "token")
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]["matchedQueries"]), 2)
        self.assertEqual(mocked.call_count, 2)

    def test_zero_results(self):
        with patch("temporal_lab.api", return_value={"data": []}):
            posts = research(["ISO week"], 5, "token")
        self.assertIn("No matching articles", markdown_report([iso_record(date(2027, 1, 1))], posts))

    def test_empty_queries_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            research([" ", ""], 5, "token")


class APIResilienceTests(unittest.TestCase):
    def test_get_retries_transient_server_error(self):
        response = io.BytesIO(b'{"data": []}')
        with patch("temporal_lab._opener.open", side_effect=[HTTPError("url", 503, "unavailable", {}, None), response]) as opened, \
             patch("temporal_lab.time.sleep") as sleep:
            self.assertEqual(api("GET", "/search/posts?q=ISO", "token"), {"data": []})
        self.assertEqual(opened.call_count, 2)
        sleep.assert_called_once_with(0.5)

    def test_write_is_not_retried_on_network_error(self):
        with patch("temporal_lab._opener.open", side_effect=URLError("offline")) as opened:
            with self.assertRaisesRegex(RuntimeError, "URLError"):
                api("POST", "/bookmarks/", "token", {"postIds": ["real-id"]})
        opened.assert_called_once()

    def test_rate_limit_includes_retry_after_without_retry(self):
        headers = Message()
        headers["Retry-After"] = "17"
        error = HTTPError("url", 429, "slow down", headers, None)
        with patch("temporal_lab._opener.open", side_effect=error) as opened:
            with self.assertRaisesRegex(RuntimeError, "Retry-After: 17"):
                api("GET", "/search/posts?q=ISO", "token")
        opened.assert_called_once()


if __name__ == "__main__":
    unittest.main()

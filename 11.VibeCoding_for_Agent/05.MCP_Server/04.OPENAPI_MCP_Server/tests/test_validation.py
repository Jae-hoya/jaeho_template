import unittest
from datetime import date

from seoul_culture_mcp.utils.validation import (
    matches_date_range,
    matches_guname,
    matches_is_free,
    matches_title,
    normalize_limit,
    normalize_page_size,
    parse_event_date_range,
    validate_date_str,
    validate_index_range,
)


class ValidationTests(unittest.TestCase):
    def test_validate_index_range_valid(self) -> None:
        validate_index_range(1, 1)
        validate_index_range(1, 2)

    def test_validate_index_range_invalid(self) -> None:
        with self.assertRaises(ValueError):
            validate_index_range(0, 1)
        with self.assertRaises(ValueError):
            validate_index_range(2, 1)

    def test_validate_date_str(self) -> None:
        self.assertEqual(validate_date_str("2026-05-15"), "2026-05-15")
        self.assertIsNone(validate_date_str("  "))
        with self.assertRaises(ValueError):
            validate_date_str("2026-5-15")
        with self.assertRaises(ValueError):
            validate_date_str("2026-02-30")

    def test_normalize_limit(self) -> None:
        self.assertEqual(normalize_limit(None, 50), 50)
        self.assertEqual(normalize_limit(0, 50), 1)
        self.assertEqual(normalize_limit(1000, 50), 500)
        self.assertEqual(normalize_limit(5, 50), 5)

    def test_normalize_page_size(self) -> None:
        self.assertEqual(normalize_page_size(None, 20), 20)
        self.assertEqual(normalize_page_size(0, 20), 1)
        self.assertEqual(normalize_page_size(1000, 20), 100)
        self.assertEqual(normalize_page_size(5, 20), 5)

    def test_parse_event_date_range_from_epoch(self) -> None:
        event = {"strtdate": 0, "end_date": 86400000}
        start, end = parse_event_date_range(event)
        self.assertEqual(start, date(1970, 1, 1))
        self.assertEqual(end, date(1970, 1, 2))

    def test_parse_event_date_range_from_string(self) -> None:
        event = {"date": "2026-05-15~2026-05-17"}
        start, end = parse_event_date_range(event)
        self.assertEqual(start, date(2026, 5, 15))
        self.assertEqual(end, date(2026, 5, 17))

    def test_matches_title(self) -> None:
        event = {"title": "Seoul Festival"}
        self.assertTrue(matches_title(event, "festival"))
        self.assertFalse(matches_title(event, "opera"))

    def test_matches_guname(self) -> None:
        event = {"guname": "종로구"}
        self.assertTrue(matches_guname(event, "종로구"))
        self.assertFalse(matches_guname(event, "강남구"))

    def test_matches_is_free(self) -> None:
        event = {"is_free": "무료"}
        self.assertTrue(matches_is_free(event, True))
        self.assertFalse(matches_is_free(event, False))

    def test_matches_date_range(self) -> None:
        event = {"date": "2026-05-15~2026-05-17"}
        start = date(2026, 5, 16)
        end = date(2026, 5, 20)
        self.assertTrue(matches_date_range(event, start, end))
        start = date(2026, 5, 18)
        end = date(2026, 5, 20)
        self.assertFalse(matches_date_range(event, start, end))


if __name__ == "__main__":
    unittest.main()

import unittest

from seoul_culture_mcp.clients.seoul_api import extract_description_data


class ExtractDescriptionTests(unittest.TestCase):
    def test_extract_top_level(self) -> None:
        payload = {"DESCRIPTION": {"A": "a"}, "DATA": [{"x": 1}]}
        description, data = extract_description_data(payload)
        self.assertEqual(description, {"A": "a"})
        self.assertEqual(data, [{"x": 1}])

    def test_extract_nested(self) -> None:
        payload = {"culturalEventInfo": {"DESCRIPTION": {"B": "b"}, "DATA": []}}
        description, data = extract_description_data(payload)
        self.assertEqual(description, {"B": "b"})
        self.assertEqual(data, [])

    def test_extract_row_nested(self) -> None:
        payload = {
            "culturalEventInfo": {
                "list_total_count": 2,
                "RESULT": {"CODE": "INFO-000", "MESSAGE": "ok"},
                "row": [{"x": 1}, {"y": 2}],
            }
        }
        description, data = extract_description_data(payload)
        self.assertEqual(description, {})
        self.assertEqual(data, [{"x": 1}, {"y": 2}])

    def test_extract_row_normalizes_keys(self) -> None:
        payload = {
            "culturalEventInfo": {
                "row": [
                    {
                        "TITLE": "Sample Event",
                        "STRTDATE": "2026-05-15 00:00:00.0",
                        "END_DATE": "2026-05-16 00:00:00.0",
                        "IS_FREE": "무료",
                    }
                ]
            }
        }
        _, data = extract_description_data(payload)
        self.assertEqual(data[0]["title"], "Sample Event")
        self.assertEqual(data[0]["is_free"], "무료")
        self.assertEqual(data[0]["strtdate"], 1778770800000)
        self.assertEqual(data[0]["end_date"], 1778857200000)

    def test_extract_missing(self) -> None:
        description, data = extract_description_data({})
        self.assertEqual(description, {})
        self.assertEqual(data, [])


if __name__ == "__main__":
    unittest.main()

import asyncio
import unittest

from seoul_culture_mcp.clients.seoul_api import extract_description_data, fetch_events
from seoul_culture_mcp.settings import get_settings


class IntegrationTests(unittest.TestCase):
    @unittest.skipUnless(get_settings().api_key, "SEOUL_API_KEY not configured")
    def test_fetch_events(self) -> None:
        payload, request_url = asyncio.run(fetch_events(1, 1))
        self.assertIsInstance(payload, dict)
        self.assertTrue(request_url.startswith("http"))
        description, data = extract_description_data(payload)
        self.assertIsInstance(description, dict)
        self.assertIsInstance(data, list)


if __name__ == "__main__":
    unittest.main()

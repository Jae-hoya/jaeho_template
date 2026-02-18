import asyncio

from app.core.config import Settings
from app.schemas.web import LandingAnalyzeResponse
from app.services.web_search_service import WebSearchService


class DummyLandingGraph:
    def __init__(self) -> None:
        self.calls = 0

    async def run_analyze_landing_page(self, url: str, from_tavily: bool = False) -> LandingAnalyzeResponse:
        self.calls += 1
        return LandingAnalyzeResponse(
            url=url,
            title="dummy",
            h1=["h1"],
            h2=["h2"],
            cta_buttons=["cta"],
            body=f"payload-{int(from_tavily)}",
            from_tavily=from_tavily,
        )


def test_analyze_landing_page_uses_url_cache() -> None:
    service = WebSearchService(Settings(force_mock_mode=True, landing_cache_ttl_sec=300))
    dummy_graph = DummyLandingGraph()
    service._graph = dummy_graph  # type: ignore[assignment]

    first = asyncio.run(service.analyze_landing_page("https://Example.com/path/", from_tavily=False))
    second = asyncio.run(service.analyze_landing_page("https://example.com/path", from_tavily=False))
    third = asyncio.run(service.analyze_landing_page("https://example.com/path", from_tavily=True))

    assert first.url == "https://example.com/path"
    assert second.url == "https://example.com/path"
    assert first.body == second.body
    assert dummy_graph.calls == 2
    assert third.from_tavily is True

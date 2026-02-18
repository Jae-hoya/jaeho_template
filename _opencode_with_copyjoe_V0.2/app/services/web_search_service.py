from app.flows.web_graph import WebWorkflowGraph
from app.core.config import Settings
from app.integrations.landing_page_client import LandingPageClient
from app.schemas.web import LandingAnalyzeResponse, WebSearchResult


class WebSearchService:
    def __init__(self, settings: Settings) -> None:
        self._landing_client = LandingPageClient(timeout_sec=settings.landing_request_timeout_sec)
        self._tavily_client = None

        if settings.tavily_api_key:
            try:
                from tavily import TavilyClient

                self._tavily_client = TavilyClient(api_key=settings.tavily_api_key)
            except Exception:
                self._tavily_client = None

        self._graph = WebWorkflowGraph(
            landing_client=self._landing_client,
            tavily_client=self._tavily_client,
        )

    @property
    def graph(self) -> WebWorkflowGraph:
        return self._graph

    def search(self, query: str, max_results: int, strict: bool = True) -> list[WebSearchResult]:
        return self._graph.run_search(query=query, max_results=max_results, strict=strict)

    async def analyze_landing_page(self, url: str, from_tavily: bool = False) -> LandingAnalyzeResponse:
        return await self._graph.run_analyze_landing_page(url=url, from_tavily=from_tavily)

    async def search_then_analyze(self, query: str, max_results: int) -> LandingAnalyzeResponse:
        return await self._graph.run_search_then_analyze(query=query, max_results=max_results)

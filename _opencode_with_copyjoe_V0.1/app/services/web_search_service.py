from app.core.config import Settings
from app.core.errors import AppException, ErrorCode
from app.integrations.landing_page_client import LandingPageClient
from app.schemas.web import LandingAnalyzeResponse, WebSearchResult


class WebSearchService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._landing_client = LandingPageClient(timeout_sec=settings.landing_request_timeout_sec)
        self._tavily_client = None

        if settings.tavily_api_key:
            try:
                from tavily import TavilyClient

                self._tavily_client = TavilyClient(api_key=settings.tavily_api_key)
            except Exception:
                self._tavily_client = None

    def search(self, query: str, max_results: int, strict: bool = True) -> list[WebSearchResult]:
        if self._tavily_client is None:
            if strict:
                raise AppException(
                    status_code=400,
                    code=ErrorCode.web_search_error,
                    message="Tavily API key is missing or Tavily client is unavailable",
                )
            return []

        try:
            response = self._tavily_client.search(query=query, max_results=max_results)
        except Exception as exc:
            raise AppException(
                status_code=502,
                code=ErrorCode.web_search_error,
                message="Tavily search failed",
                details={"reason": str(exc)},
            ) from exc

        items = response.get("results", [])
        results: list[WebSearchResult] = []
        for item in items:
            results.append(
                WebSearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                )
            )
        return results

    async def analyze_landing_page(self, url: str, from_tavily: bool = False) -> LandingAnalyzeResponse:
        try:
            payload = await self._landing_client.analyze(url)
        except Exception as exc:
            raise AppException(
                status_code=502,
                code=ErrorCode.web_search_error,
                message="Landing page analysis failed",
                details={"reason": str(exc)},
            ) from exc

        return LandingAnalyzeResponse(
            url=payload.get("url", url),
            title=payload.get("title", ""),
            h1=payload.get("h1", []),
            h2=payload.get("h2", []),
            cta_buttons=payload.get("cta_buttons", []),
            body=payload.get("body", ""),
            from_tavily=from_tavily,
        )

    async def search_then_analyze(self, query: str, max_results: int) -> LandingAnalyzeResponse:
        results = self.search(query=query, max_results=max_results, strict=True)
        if not results:
            raise AppException(
                status_code=404,
                code=ErrorCode.web_search_error,
                message="No search results found from Tavily",
            )

        return await self.analyze_landing_page(results[0].url, from_tavily=True)

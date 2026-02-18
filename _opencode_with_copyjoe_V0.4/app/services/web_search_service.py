from time import monotonic
from urllib.parse import urlsplit, urlunsplit

from app.flows.web_workflow import WebWorkflowGraph
from app.core.config import Settings
from app.integrations.landing_page_client import LandingPageClient
from app.schemas.web import LandingAnalyzeResponse, WebSearchResult


class WebSearchService:
    def __init__(self, settings: Settings) -> None:
        self._landing_client = LandingPageClient(
            timeout_sec=settings.landing_request_timeout_sec,
            subprocess_timeout_buffer_sec=settings.landing_subprocess_timeout_buffer_sec,
            network_idle_wait_ms=settings.landing_network_idle_wait_ms,
            fallback_timeout_sec=settings.landing_fallback_timeout_sec,
        )
        self._tavily_client = None
        self._landing_cache_ttl_sec = max(10, int(settings.landing_cache_ttl_sec))
        self._landing_cache: dict[str, tuple[float, LandingAnalyzeResponse]] = {}

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
        normalized_url = _normalize_landing_url(url)
        cache_key = f"{int(from_tavily)}:{normalized_url}"
        now = monotonic()

        cached = self._landing_cache.get(cache_key)
        if cached is not None and cached[0] > now:
            return cached[1]

        response = await self._graph.run_analyze_landing_page(url=normalized_url, from_tavily=from_tavily)
        self._landing_cache[cache_key] = (now + self._landing_cache_ttl_sec, response)
        self._prune_landing_cache(now)
        return response

    async def search_then_analyze(self, query: str, max_results: int) -> LandingAnalyzeResponse:
        response = await self._graph.run_search_then_analyze(query=query, max_results=max_results)
        now = monotonic()
        cache_key = f"1:{_normalize_landing_url(response.url)}"
        self._landing_cache[cache_key] = (now + self._landing_cache_ttl_sec, response)
        self._prune_landing_cache(now)
        return response

    def _prune_landing_cache(self, now: float) -> None:
        expired_keys = [key for key, (expires_at, _) in self._landing_cache.items() if expires_at <= now]
        for key in expired_keys:
            self._landing_cache.pop(key, None)

        max_cache_size = 128
        overflow = len(self._landing_cache) - max_cache_size
        if overflow <= 0:
            return

        oldest_keys = sorted(self._landing_cache.items(), key=lambda item: item[1][0])[:overflow]
        for key, _ in oldest_keys:
            self._landing_cache.pop(key, None)


def _normalize_landing_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return raw

    parts = urlsplit(raw)
    if not parts.scheme or not parts.netloc:
        return raw
    path = (parts.path or "/").rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))

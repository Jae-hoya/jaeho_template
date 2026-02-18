from fastapi import APIRouter, Depends

from app.api.deps import web_search_service
from app.schemas.web import (
    LandingAnalyzeRequest,
    LandingAnalyzeResponse,
    WebSearchRequest,
    WebSearchResponse,
)
from app.services.web_search_service import WebSearchService

router = APIRouter()


@router.post("/web/search", response_model=WebSearchResponse)
def web_search(
    payload: WebSearchRequest,
    service: WebSearchService = Depends(web_search_service),
) -> WebSearchResponse:
    results = service.search(query=payload.query, max_results=payload.max_results, strict=True)
    return WebSearchResponse(query=payload.query, results=results)


@router.post("/web/landing/analyze", response_model=LandingAnalyzeResponse)
async def landing_analyze(
    payload: LandingAnalyzeRequest,
    service: WebSearchService = Depends(web_search_service),
) -> LandingAnalyzeResponse:
    if payload.url:
        return await service.analyze_landing_page(payload.url, from_tavily=False)
    return await service.search_then_analyze(payload.query or "", payload.max_results)

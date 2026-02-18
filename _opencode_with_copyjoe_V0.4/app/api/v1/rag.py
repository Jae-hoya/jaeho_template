import asyncio

from fastapi import APIRouter, Depends

from app.api.deps import rag_service
from app.schemas.rag import RagIndexRequest, RagIndexResponse, RagResetResponse, RagSearchRequest, RagSearchResponse
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/rag/index", response_model=RagIndexResponse)
async def rag_index(
    payload: RagIndexRequest,
    service: RagService = Depends(rag_service),
) -> RagIndexResponse:
    return await asyncio.to_thread(
        service.index_documents,
        payload.document_ids,
        payload.chunk_size,
        payload.chunk_overlap,
    )


@router.post("/rag/search", response_model=RagSearchResponse)
async def rag_search(
    payload: RagSearchRequest,
    service: RagService = Depends(rag_service),
) -> RagSearchResponse:
    rows = await asyncio.to_thread(
        service.search,
        payload.query,
        payload.top_k,
        payload.document_ids,
    )
    return RagSearchResponse(query=payload.query, top_k=payload.top_k, results=rows)


@router.post("/rag/reset", response_model=RagResetResponse)
async def rag_reset(service: RagService = Depends(rag_service)) -> RagResetResponse:
    return await asyncio.to_thread(service.reset_index)

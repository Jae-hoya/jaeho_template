from fastapi import APIRouter, Depends

from app.api.deps import rag_service
from app.schemas.rag import RagIndexRequest, RagIndexResponse, RagSearchRequest, RagSearchResponse
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/rag/index", response_model=RagIndexResponse)
def rag_index(
    payload: RagIndexRequest,
    service: RagService = Depends(rag_service),
) -> RagIndexResponse:
    return service.index_documents(
        document_ids=payload.document_ids,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )


@router.post("/rag/search", response_model=RagSearchResponse)
def rag_search(
    payload: RagSearchRequest,
    service: RagService = Depends(rag_service),
) -> RagSearchResponse:
    rows = service.search(query=payload.query, top_k=payload.top_k)
    return RagSearchResponse(query=payload.query, top_k=payload.top_k, results=rows)

from typing import TypedDict

from app.integrations.milvus_client import ScoredDocument
from app.schemas.common import SourceItem
from app.schemas.rag import RagChunk, RagIndexResponse


class RagIndexState(TypedDict):
    document_ids: list[str]
    chunk_size: int
    chunk_overlap: int
    indexed_documents: int
    indexed_chunks: int
    missing_document_ids: list[str]
    response: RagIndexResponse | None


class RagSearchState(TypedDict):
    query: str
    top_k: int
    document_ids: list[str] | None
    scored_rows: list[ScoredDocument]
    results: list[RagChunk]


class RagContextState(TypedDict):
    query: str
    top_k: int
    document_ids: list[str] | None
    results: list[RagChunk]
    context: str
    sources: list[SourceItem]

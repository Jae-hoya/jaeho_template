from pydantic import BaseModel, Field


class RagIndexRequest(BaseModel):
    document_ids: list[str] = Field(default_factory=list)
    chunk_size: int = Field(default=700, ge=200, le=2000)
    chunk_overlap: int = Field(default=120, ge=0, le=500)


class RagIndexResponse(BaseModel):
    indexed_documents: int
    indexed_chunks: int
    missing_document_ids: list[str] = Field(default_factory=list)


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[str] | None = None


class RagChunk(BaseModel):
    content: str
    score: float
    metadata: dict[str, str | int | float] = Field(default_factory=dict)


class RagSearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[RagChunk] = Field(default_factory=list)


class RagResetResponse(BaseModel):
    backend: str
    cleared_documents: int
    cleared_vectors: int

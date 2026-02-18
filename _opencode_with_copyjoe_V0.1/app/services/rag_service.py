from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.errors import AppException, ErrorCode
from app.integrations.milvus_client import MilvusClient
from app.schemas.common import SourceItem
from app.schemas.rag import RagChunk, RagIndexResponse
from app.services.document_store import DocumentStore


class RagService:
    def __init__(self, vector_client: MilvusClient, document_store: DocumentStore) -> None:
        self._vector_client = vector_client
        self._document_store = document_store

    @property
    def backend(self) -> str:
        return self._vector_client.backend

    def index_documents(self, document_ids: list[str], chunk_size: int, chunk_overlap: int) -> RagIndexResponse:
        if chunk_overlap >= chunk_size:
            raise AppException(
                status_code=400,
                code=ErrorCode.validation_error,
                message="chunk_overlap must be smaller than chunk_size",
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        indexed_chunks = 0
        indexed_documents = 0
        missing: list[str] = []

        for document_id in document_ids:
            stored = self._document_store.get(document_id)
            if stored is None:
                missing.append(document_id)
                continue

            chunks = splitter.split_text(stored.converted_text)
            docs = [
                Document(
                    page_content=chunk,
                    metadata={
                        "document_id": stored.document_id,
                        "file_name": stored.file_name,
                        "chunk_index": idx,
                    },
                )
                for idx, chunk in enumerate(chunks)
            ]

            try:
                self._vector_client.add_documents(docs)
            except Exception as exc:
                raise AppException(
                    status_code=500,
                    code=ErrorCode.vector_db_error,
                    message="Vector indexing failed",
                    details={"reason": str(exc)},
                ) from exc

            indexed_chunks += len(docs)
            indexed_documents += 1

        return RagIndexResponse(
            indexed_documents=indexed_documents,
            indexed_chunks=indexed_chunks,
            missing_document_ids=missing,
        )

    def search(self, query: str, top_k: int) -> list[RagChunk]:
        try:
            rows = self._vector_client.similarity_search_with_scores(query, top_k=top_k)
        except Exception as exc:
            raise AppException(
                status_code=500,
                code=ErrorCode.vector_db_error,
                message="RAG search failed",
                details={"reason": str(exc)},
            ) from exc

        return [
            RagChunk(
                content=row.document.page_content,
                score=float(row.score),
                metadata=row.document.metadata,
            )
            for row in rows
        ]

    def build_context(self, query: str, top_k: int) -> tuple[str, list[SourceItem]]:
        results = self.search(query=query, top_k=top_k)
        if not results:
            return "", []

        blocks: list[str] = []
        sources: list[SourceItem] = []

        for item in results:
            blocks.append(item.content)
            sources.append(
                SourceItem(
                    source_type="rag",
                    title=str(item.metadata.get("file_name", "uploaded_document")),
                    snippet=item.content[:500],
                )
            )

        return "\n\n".join(blocks), sources

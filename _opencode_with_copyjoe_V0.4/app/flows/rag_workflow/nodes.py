from typing import Callable, Protocol

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.errors import AppException, ErrorCode
from app.flows.rag_workflow.states import RagContextState, RagIndexState, RagSearchState
from app.integrations.milvus_client import ScoredDocument
from app.schemas.common import SourceItem
from app.schemas.rag import RagChunk, RagIndexResponse

SearchChunksFn = Callable[[str, int, list[str] | None], list[RagChunk]]


class StoredDocument(Protocol):
    document_id: str
    file_name: str
    converted_text: str


class DocumentStoreBackend(Protocol):
    def get(self, document_id: str) -> StoredDocument | None:
        ...


class VectorClientBackend(Protocol):
    def add_documents(self, documents: list[Document]) -> list[str]:
        ...

    def similarity_search_with_scores(
        self,
        query: str,
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[ScoredDocument]:
        ...


class ValidateIndexParamsNode:
    def __call__(self, state: RagIndexState) -> dict[str, object]:
        if state["chunk_overlap"] >= state["chunk_size"]:
            raise AppException(
                status_code=400,
                code=ErrorCode.validation_error,
                message="chunk_overlap must be smaller than chunk_size",
            )
        return {}


class IndexDocumentsNode:
    def __init__(self, vector_client: VectorClientBackend, document_store: DocumentStoreBackend) -> None:
        self._vector_client = vector_client
        self._document_store = document_store

    def __call__(self, state: RagIndexState) -> dict[str, object]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=state["chunk_size"],
            chunk_overlap=state["chunk_overlap"],
        )

        indexed_chunks = 0
        indexed_documents = 0
        missing: list[str] = []
        pending_docs: list[Document] = []
        batch_size = 96

        def flush_pending() -> None:
            nonlocal pending_docs
            if not pending_docs:
                return

            try:
                self._vector_client.add_documents(pending_docs)
            except Exception as exc:
                raise AppException(
                    status_code=500,
                    code=ErrorCode.vector_db_error,
                    message="Vector indexing failed",
                    details={"reason": str(exc)},
                ) from exc

            pending_docs = []

        for document_id in state["document_ids"]:
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

            pending_docs.extend(docs)
            if len(pending_docs) >= batch_size:
                flush_pending()

            indexed_chunks += len(docs)
            indexed_documents += 1

        flush_pending()

        return {
            "indexed_documents": indexed_documents,
            "indexed_chunks": indexed_chunks,
            "missing_document_ids": missing,
        }


class BuildIndexResponseNode:
    def __call__(self, state: RagIndexState) -> dict[str, object]:
        return {
            "response": RagIndexResponse(
                indexed_documents=state.get("indexed_documents", 0),
                indexed_chunks=state.get("indexed_chunks", 0),
                missing_document_ids=list(state.get("missing_document_ids", [])),
            )
        }


class SearchVectorsNode:
    def __init__(self, vector_client: VectorClientBackend) -> None:
        self._vector_client = vector_client

    def __call__(self, state: RagSearchState) -> dict[str, object]:
        try:
            rows = self._vector_client.similarity_search_with_scores(
                state["query"],
                top_k=state["top_k"],
                document_ids=state.get("document_ids"),
            )
        except Exception as exc:
            raise AppException(
                status_code=500,
                code=ErrorCode.vector_db_error,
                message="RAG search failed",
                details={"reason": str(exc)},
            ) from exc

        return {"scored_rows": rows}


class ToChunksNode:
    def __call__(self, state: RagSearchState) -> dict[str, object]:
        rows = list(state.get("scored_rows", []))
        return {
            "results": [
                RagChunk(
                    content=row.document.page_content,
                    score=float(row.score),
                    metadata=row.document.metadata,
                )
                for row in rows
            ]
        }


class CollectChunksForContextNode:
    def __init__(self, search_chunks: SearchChunksFn) -> None:
        self._search_chunks = search_chunks

    def __call__(self, state: RagContextState) -> dict[str, object]:
        return {
            "results": self._search_chunks(state["query"], state["top_k"], state.get("document_ids"))
        }


class BuildContextNode:
    def __call__(self, state: RagContextState) -> dict[str, object]:
        results = list(state.get("results", []))
        if not results:
            return {"context": "", "sources": []}

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

        return {
            "context": "\n\n".join(blocks),
            "sources": sources,
        }

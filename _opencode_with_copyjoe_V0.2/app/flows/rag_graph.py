from typing import TypedDict

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph

from app.core.errors import AppException, ErrorCode
from app.integrations.milvus_client import MilvusClient, ScoredDocument
from app.schemas.common import SourceItem
from app.schemas.rag import RagChunk, RagIndexResponse
from app.services.document_store import DocumentStore


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
    scored_rows: list[ScoredDocument]
    results: list[RagChunk]


class RagContextState(TypedDict):
    query: str
    top_k: int
    results: list[RagChunk]
    context: str
    sources: list[SourceItem]


class RagWorkflowGraph:
    def __init__(self, vector_client: MilvusClient, document_store: DocumentStore) -> None:
        self._vector_client = vector_client
        self._document_store = document_store

        index_builder = StateGraph(RagIndexState)
        index_builder.add_node("validate", self._validate_index_params)
        index_builder.add_node("index", self._index_documents)
        index_builder.add_node("to_response", self._build_index_response)
        index_builder.add_edge(START, "validate")
        index_builder.add_edge("validate", "index")
        index_builder.add_edge("index", "to_response")
        index_builder.add_edge("to_response", END)
        self._index_graph = index_builder.compile()

        search_builder = StateGraph(RagSearchState)
        search_builder.add_node("search", self._search_vectors)
        search_builder.add_node("to_chunks", self._to_chunks)
        search_builder.add_edge(START, "search")
        search_builder.add_edge("search", "to_chunks")
        search_builder.add_edge("to_chunks", END)
        self._search_graph = search_builder.compile()

        context_builder = StateGraph(RagContextState)
        context_builder.add_node("collect_chunks", self._collect_chunks_for_context)
        context_builder.add_node("build_context", self._build_context)
        context_builder.add_edge(START, "collect_chunks")
        context_builder.add_edge("collect_chunks", "build_context")
        context_builder.add_edge("build_context", END)
        self._context_graph = context_builder.compile()

    def run_index(self, document_ids: list[str], chunk_size: int, chunk_overlap: int) -> RagIndexResponse:
        state = self._index_graph.invoke(
            {
                "document_ids": document_ids,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "indexed_documents": 0,
                "indexed_chunks": 0,
                "missing_document_ids": [],
                "response": None,
            }
        )
        response = state.get("response")
        if response is None:
            return RagIndexResponse(indexed_documents=0, indexed_chunks=0, missing_document_ids=[])
        return response

    def run_search(self, query: str, top_k: int) -> list[RagChunk]:
        state = self._search_graph.invoke(
            {
                "query": query,
                "top_k": top_k,
                "scored_rows": [],
                "results": [],
            }
        )
        return list(state.get("results", []))

    def run_build_context(self, query: str, top_k: int) -> tuple[str, list[SourceItem]]:
        state = self._context_graph.invoke(
            {
                "query": query,
                "top_k": top_k,
                "results": [],
                "context": "",
                "sources": [],
            }
        )
        return str(state.get("context", "")), list(state.get("sources", []))

    def _validate_index_params(self, state: RagIndexState) -> dict[str, object]:
        if state["chunk_overlap"] >= state["chunk_size"]:
            raise AppException(
                status_code=400,
                code=ErrorCode.validation_error,
                message="chunk_overlap must be smaller than chunk_size",
            )
        return {}

    def _index_documents(self, state: RagIndexState) -> dict[str, object]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=state["chunk_size"],
            chunk_overlap=state["chunk_overlap"],
        )

        indexed_chunks = 0
        indexed_documents = 0
        missing: list[str] = []

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

        return {
            "indexed_documents": indexed_documents,
            "indexed_chunks": indexed_chunks,
            "missing_document_ids": missing,
        }

    def _build_index_response(self, state: RagIndexState) -> dict[str, object]:
        return {
            "response": RagIndexResponse(
                indexed_documents=state.get("indexed_documents", 0),
                indexed_chunks=state.get("indexed_chunks", 0),
                missing_document_ids=list(state.get("missing_document_ids", [])),
            )
        }

    def _search_vectors(self, state: RagSearchState) -> dict[str, object]:
        try:
            rows = self._vector_client.similarity_search_with_scores(state["query"], top_k=state["top_k"])
        except Exception as exc:
            raise AppException(
                status_code=500,
                code=ErrorCode.vector_db_error,
                message="RAG search failed",
                details={"reason": str(exc)},
            ) from exc

        return {"scored_rows": rows}

    def _to_chunks(self, state: RagSearchState) -> dict[str, object]:
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

    def _collect_chunks_for_context(self, state: RagContextState) -> dict[str, object]:
        return {
            "results": self.run_search(query=state["query"], top_k=state["top_k"]),
        }

    def _build_context(self, state: RagContextState) -> dict[str, object]:
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

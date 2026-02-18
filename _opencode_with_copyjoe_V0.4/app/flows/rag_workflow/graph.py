from langgraph.graph import END, START, StateGraph

from app.flows.rag_workflow.nodes import (
    BuildContextNode,
    BuildIndexResponseNode,
    CollectChunksForContextNode,
    IndexDocumentsNode,
    SearchVectorsNode,
    ToChunksNode,
    ValidateIndexParamsNode,
)
from app.flows.rag_workflow.states import RagContextState, RagIndexState, RagSearchState
from app.integrations.milvus_client import MilvusClient
from app.schemas.common import SourceItem
from app.schemas.rag import RagChunk, RagIndexResponse
from app.services.document_store import DocumentStore


class RagWorkflowGraph:
    def __init__(self, vector_client: MilvusClient, document_store: DocumentStore) -> None:
        index_builder = StateGraph(RagIndexState)
        index_builder.add_node("validate", ValidateIndexParamsNode())
        index_builder.add_node("index", IndexDocumentsNode(vector_client=vector_client, document_store=document_store))
        index_builder.add_node("to_response", BuildIndexResponseNode())
        index_builder.add_edge(START, "validate")
        index_builder.add_edge("validate", "index")
        index_builder.add_edge("index", "to_response")
        index_builder.add_edge("to_response", END)
        self._index_graph = index_builder.compile()

        search_builder = StateGraph(RagSearchState)
        search_builder.add_node("search", SearchVectorsNode(vector_client=vector_client))
        search_builder.add_node("to_chunks", ToChunksNode())
        search_builder.add_edge(START, "search")
        search_builder.add_edge("search", "to_chunks")
        search_builder.add_edge("to_chunks", END)
        self._search_graph = search_builder.compile()

        context_builder = StateGraph(RagContextState)
        context_builder.add_node("collect_chunks", CollectChunksForContextNode(search_chunks=self.run_search))
        context_builder.add_node("build_context", BuildContextNode())
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

    def run_search(self, query: str, top_k: int, document_ids: list[str] | None = None) -> list[RagChunk]:
        state = self._search_graph.invoke(
            {
                "query": query,
                "top_k": top_k,
                "document_ids": list(document_ids) if document_ids else None,
                "scored_rows": [],
                "results": [],
            }
        )
        return list(state.get("results", []))

    def run_build_context(
        self,
        query: str,
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> tuple[str, list[SourceItem]]:
        state = self._context_graph.invoke(
            {
                "query": query,
                "top_k": top_k,
                "document_ids": list(document_ids) if document_ids else None,
                "results": [],
                "context": "",
                "sources": [],
            }
        )
        return str(state.get("context", "")), list(state.get("sources", []))

from dataclasses import dataclass

from app.flows.rag_workflow.nodes import IndexDocumentsNode


@dataclass
class DummyStoredDocument:
    document_id: str
    file_name: str
    converted_text: str


class DummyDocumentStore:
    def __init__(self, rows: dict[str, DummyStoredDocument]) -> None:
        self._rows = rows

    def get(self, document_id: str) -> DummyStoredDocument | None:
        return self._rows.get(document_id)


class DummyVectorClient:
    def __init__(self) -> None:
        self.batch_sizes: list[int] = []

    def add_documents(self, documents):  # type: ignore[no-untyped-def]
        self.batch_sizes.append(len(documents))
        return [f"id-{index}" for index, _ in enumerate(documents)]


def test_index_documents_node_batches_vector_writes() -> None:
    content = "alpha beta gamma " * 4000
    store = DummyDocumentStore(
        {
            "doc-1": DummyStoredDocument("doc-1", "first.txt", content),
            "doc-2": DummyStoredDocument("doc-2", "second.txt", content),
        }
    )
    vector_client = DummyVectorClient()
    node = IndexDocumentsNode(vector_client=vector_client, document_store=store)

    state = {
        "document_ids": ["doc-1", "doc-2"],
        "chunk_size": 80,
        "chunk_overlap": 10,
        "indexed_documents": 0,
        "indexed_chunks": 0,
        "missing_document_ids": [],
        "response": None,
    }

    output = node(state)

    assert output["indexed_documents"] == 2
    assert output["indexed_chunks"] > 96
    assert len(vector_client.batch_sizes) >= 2
    assert sum(vector_client.batch_sizes) == output["indexed_chunks"]

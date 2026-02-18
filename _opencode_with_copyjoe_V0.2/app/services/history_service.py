from typing import Literal, cast

from app.flows.history_graph import HistoryWorkflowGraph
from app.schemas.history import ThreadDetail, ThreadMessageItem, ThreadSummary


class HistoryService:
    def __init__(self) -> None:
        self._graph = HistoryWorkflowGraph()

    @property
    def graph(self) -> HistoryWorkflowGraph:
        return self._graph

    def create_thread(self, title: str) -> ThreadSummary:
        return self._graph.create_thread(title)

    def list_threads(self) -> list[ThreadSummary]:
        return self._graph.list_threads()

    def get_thread(self, thread_id: str) -> ThreadDetail:
        return self._graph.get_thread(thread_id)

    def append_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> ThreadMessageItem:
        return self._graph.append_message(
            thread_id=thread_id,
            role=cast(Literal["user", "assistant", "system"], role),
            content=content,
            metadata=metadata,
        )

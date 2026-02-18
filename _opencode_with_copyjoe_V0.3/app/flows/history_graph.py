from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.core.errors import AppException, ErrorCode
from app.schemas.history import ThreadDetail, ThreadMessageItem, ThreadSummary


@dataclass
class _ThreadMessageRecord:
    message_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: dict[str, Any]
    created_at: datetime


@dataclass
class _ThreadRecord:
    thread_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[_ThreadMessageRecord] = field(default_factory=list)


class CreateThreadState(TypedDict):
    title: str
    record: _ThreadRecord | None
    summary: ThreadSummary | None


class ListThreadsState(TypedDict):
    records: list[_ThreadRecord]
    summaries: list[ThreadSummary]


class GetThreadState(TypedDict):
    thread_id: str
    record: _ThreadRecord | None
    detail: ThreadDetail | None


class AppendMessageState(TypedDict):
    thread_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: dict[str, Any] | None
    record: _ThreadRecord | None
    message_record: _ThreadMessageRecord | None
    message: ThreadMessageItem | None


class HistoryWorkflowGraph:
    def __init__(self) -> None:
        self._threads: dict[str, _ThreadRecord] = {}

        create_builder = StateGraph(CreateThreadState)
        create_builder.add_node("create_record", self._create_record)
        create_builder.add_node("to_summary", self._create_summary)
        create_builder.add_edge(START, "create_record")
        create_builder.add_edge("create_record", "to_summary")
        create_builder.add_edge("to_summary", END)
        self._create_graph = create_builder.compile()

        list_builder = StateGraph(ListThreadsState)
        list_builder.add_node("sort_records", self._sort_records)
        list_builder.add_node("to_summaries", self._map_summaries)
        list_builder.add_edge(START, "sort_records")
        list_builder.add_edge("sort_records", "to_summaries")
        list_builder.add_edge("to_summaries", END)
        self._list_graph = list_builder.compile()

        get_builder = StateGraph(GetThreadState)
        get_builder.add_node("load_record", self._load_thread_record)
        get_builder.add_node("to_detail", self._to_thread_detail)
        get_builder.add_edge(START, "load_record")
        get_builder.add_edge("load_record", "to_detail")
        get_builder.add_edge("to_detail", END)
        self._get_graph = get_builder.compile()

        append_builder = StateGraph(AppendMessageState)
        append_builder.add_node("load_record", self._load_thread_record_for_append)
        append_builder.add_node("append", self._append_message_record)
        append_builder.add_node("to_message", self._to_message_item)
        append_builder.add_edge(START, "load_record")
        append_builder.add_edge("load_record", "append")
        append_builder.add_edge("append", "to_message")
        append_builder.add_edge("to_message", END)
        self._append_graph = append_builder.compile()

    def create_thread(self, title: str) -> ThreadSummary:
        state = self._create_graph.invoke(
            {
                "title": title,
                "record": None,
                "summary": None,
            }
        )
        summary = state.get("summary")
        if summary is None:
            raise RuntimeError("History graph failed to create thread summary")
        return summary

    def list_threads(self) -> list[ThreadSummary]:
        state = self._list_graph.invoke(
            {
                "records": [],
                "summaries": [],
            }
        )
        return list(state.get("summaries", []))

    def get_thread(self, thread_id: str) -> ThreadDetail:
        state = self._get_graph.invoke(
            {
                "thread_id": thread_id,
                "record": None,
                "detail": None,
            }
        )
        detail = state.get("detail")
        if detail is None:
            raise RuntimeError("History graph failed to build thread detail")
        return detail

    def append_message(
        self,
        thread_id: str,
        role: Literal["user", "assistant", "system"],
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ThreadMessageItem:
        state = self._append_graph.invoke(
            {
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "metadata": metadata,
                "record": None,
                "message_record": None,
                "message": None,
            }
        )
        message = state.get("message")
        if message is None:
            raise RuntimeError("History graph failed to append thread message")
        return message

    def _create_record(self, state: CreateThreadState) -> dict[str, object]:
        now = datetime.utcnow()
        record = _ThreadRecord(
            thread_id=str(uuid4()),
            title=state["title"],
            created_at=now,
            updated_at=now,
        )
        self._threads[record.thread_id] = record
        return {"record": record}

    def _create_summary(self, state: CreateThreadState) -> dict[str, object]:
        record = state.get("record")
        if record is None:
            raise RuntimeError("History graph missing thread record")
        return {"summary": self._to_summary(record)}

    def _sort_records(self, _: ListThreadsState) -> dict[str, object]:
        rows = sorted(self._threads.values(), key=lambda item: item.updated_at, reverse=True)
        return {"records": rows}

    def _map_summaries(self, state: ListThreadsState) -> dict[str, object]:
        rows = list(state.get("records", []))
        return {"summaries": [self._to_summary(row) for row in rows]}

    def _load_thread_record(self, state: GetThreadState) -> dict[str, object]:
        thread_id = state["thread_id"]
        record = self._threads.get(thread_id)
        if record is None:
            raise AppException(
                status_code=404,
                code=ErrorCode.not_found,
                message=f"thread not found: {thread_id}",
            )
        return {"record": record}

    def _to_thread_detail(self, state: GetThreadState) -> dict[str, object]:
        record = state.get("record")
        if record is None:
            raise RuntimeError("History graph missing thread record for detail")

        detail = ThreadDetail(
            thread=self._to_summary(record),
            messages=[
                ThreadMessageItem(
                    message_id=message.message_id,
                    role=message.role,
                    content=message.content,
                    metadata=message.metadata,
                    created_at=message.created_at,
                )
                for message in record.messages
            ],
        )
        return {"detail": detail}

    def _load_thread_record_for_append(self, state: AppendMessageState) -> dict[str, object]:
        thread_id = state["thread_id"]
        record = self._threads.get(thread_id)
        if record is None:
            raise AppException(
                status_code=404,
                code=ErrorCode.not_found,
                message=f"thread not found: {thread_id}",
            )
        return {"record": record}

    def _append_message_record(self, state: AppendMessageState) -> dict[str, object]:
        record = state.get("record")
        if record is None:
            raise RuntimeError("History graph missing thread record for append")

        now = datetime.utcnow()
        message_record = _ThreadMessageRecord(
            message_id=str(uuid4()),
            role=state["role"],
            content=state["content"],
            metadata=state.get("metadata") or {},
            created_at=now,
        )
        record.messages.append(message_record)
        record.updated_at = now
        return {"message_record": message_record}

    def _to_message_item(self, state: AppendMessageState) -> dict[str, object]:
        message_record = state.get("message_record")
        if message_record is None:
            raise RuntimeError("History graph missing appended message record")

        return {
            "message": ThreadMessageItem(
                message_id=message_record.message_id,
                role=message_record.role,
                content=message_record.content,
                metadata=message_record.metadata,
                created_at=message_record.created_at,
            )
        }

    def _to_summary(self, record: _ThreadRecord) -> ThreadSummary:
        return ThreadSummary(
            thread_id=record.thread_id,
            title=record.title,
            message_count=len(record.messages),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

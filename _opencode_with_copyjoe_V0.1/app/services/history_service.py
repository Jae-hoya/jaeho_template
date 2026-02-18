from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from app.core.errors import AppException, ErrorCode
from app.schemas.history import ThreadDetail, ThreadMessageItem, ThreadSummary


@dataclass
class _ThreadMessageRecord:
    message_id: str
    role: str
    content: str
    metadata: dict
    created_at: datetime


@dataclass
class _ThreadRecord:
    thread_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[_ThreadMessageRecord] = field(default_factory=list)


class HistoryService:
    def __init__(self) -> None:
        self._threads: dict[str, _ThreadRecord] = {}

    def create_thread(self, title: str) -> ThreadSummary:
        now = datetime.utcnow()
        thread_id = str(uuid4())
        record = _ThreadRecord(
            thread_id=thread_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self._threads[thread_id] = record
        return self._to_summary(record)

    def list_threads(self) -> list[ThreadSummary]:
        rows = sorted(self._threads.values(), key=lambda item: item.updated_at, reverse=True)
        return [self._to_summary(row) for row in rows]

    def get_thread(self, thread_id: str) -> ThreadDetail:
        record = self._threads.get(thread_id)
        if record is None:
            raise AppException(
                status_code=404,
                code=ErrorCode.not_found,
                message=f"thread not found: {thread_id}",
            )

        return ThreadDetail(
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

    def append_message(self, thread_id: str, role: str, content: str, metadata: dict | None = None) -> ThreadMessageItem:
        record = self._threads.get(thread_id)
        if record is None:
            raise AppException(
                status_code=404,
                code=ErrorCode.not_found,
                message=f"thread not found: {thread_id}",
            )

        now = datetime.utcnow()
        message = _ThreadMessageRecord(
            message_id=str(uuid4()),
            role=role,
            content=content,
            metadata=metadata or {},
            created_at=now,
        )
        record.messages.append(message)
        record.updated_at = now

        return ThreadMessageItem(
            message_id=message.message_id,
            role=message.role,
            content=message.content,
            metadata=message.metadata,
            created_at=message.created_at,
        )

    def _to_summary(self, record: _ThreadRecord) -> ThreadSummary:
        return ThreadSummary(
            thread_id=record.thread_id,
            title=record.title,
            message_count=len(record.messages),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

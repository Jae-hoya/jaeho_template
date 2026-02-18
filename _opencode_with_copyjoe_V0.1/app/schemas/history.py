from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ThreadCreateRequest(BaseModel):
    title: str = Field(default="Copy Thread", min_length=1, max_length=120)


class ThreadMessageCreateRequest(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1, max_length=12000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ThreadMessageItem(BaseModel):
    message_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ThreadSummary(BaseModel):
    thread_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class ThreadDetail(BaseModel):
    thread: ThreadSummary
    messages: list[ThreadMessageItem] = Field(default_factory=list)

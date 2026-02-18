from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    source_type: Literal["rag", "web"]
    title: str | None = None
    url: str | None = None
    snippet: str = Field(default="", max_length=3000)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    provider: str
    rag_backend: str

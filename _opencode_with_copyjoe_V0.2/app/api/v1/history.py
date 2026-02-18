from fastapi import APIRouter, Depends

from app.api.deps import history_service
from app.schemas.history import (
    ThreadCreateRequest,
    ThreadDetail,
    ThreadMessageCreateRequest,
    ThreadMessageItem,
    ThreadSummary,
)
from app.services.history_service import HistoryService

router = APIRouter()


@router.post("/history/threads", response_model=ThreadSummary)
def create_thread(
    payload: ThreadCreateRequest,
    service: HistoryService = Depends(history_service),
) -> ThreadSummary:
    return service.create_thread(payload.title)


@router.get("/history/threads", response_model=list[ThreadSummary])
def list_threads(service: HistoryService = Depends(history_service)) -> list[ThreadSummary]:
    return service.list_threads()


@router.get("/history/threads/{thread_id}", response_model=ThreadDetail)
def get_thread(
    thread_id: str,
    service: HistoryService = Depends(history_service),
) -> ThreadDetail:
    return service.get_thread(thread_id)


@router.post("/history/threads/{thread_id}/messages", response_model=ThreadMessageItem)
def append_thread_message(
    thread_id: str,
    payload: ThreadMessageCreateRequest,
    service: HistoryService = Depends(history_service),
) -> ThreadMessageItem:
    return service.append_message(
        thread_id=thread_id,
        role=payload.role,
        content=payload.content,
        metadata=payload.metadata,
    )

from fastapi import APIRouter, Depends

from app.api.deps import copy_lite_service, copy_service
from app.schemas.copy import CopyGenerateRequest, CopyGenerateResponse, CopyLiteRequest, CopyLiteResponse
from app.services.copy_lite_service import CopyLiteService
from app.services.copy_service import CopyService

router = APIRouter()


@router.post("/copy/generate", response_model=CopyGenerateResponse)
async def generate_copy(
    payload: CopyGenerateRequest,
    service: CopyService = Depends(copy_service),
) -> CopyGenerateResponse:
    return await service.generate(payload)


@router.post("/copy/generate-lite", response_model=CopyLiteResponse)
async def generate_copy_lite(
    payload: CopyLiteRequest,
    service: CopyLiteService = Depends(copy_lite_service),
) -> CopyLiteResponse:
    return await service.generate(payload)

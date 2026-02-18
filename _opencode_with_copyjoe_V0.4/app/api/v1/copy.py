from fastapi import APIRouter, Depends

from app.api.deps import copy_service
from app.schemas.copy import CopyGenerateRequest, CopyGenerateResponse, CopyLiteRequest, CopyLiteResponse
from app.services.copy_service import CopyService

router = APIRouter()


@router.post("/copy/generate", response_model=CopyGenerateResponse | CopyLiteResponse)
async def generate_copy(
    payload: CopyGenerateRequest | CopyLiteRequest,
    service: CopyService = Depends(copy_service),
) -> CopyGenerateResponse | CopyLiteResponse:
    if isinstance(payload, CopyLiteRequest):
        return await service.generate_prompt_mode(payload)
    return await service.generate(payload)

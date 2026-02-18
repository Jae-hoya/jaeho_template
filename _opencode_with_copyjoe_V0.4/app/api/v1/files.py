from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import file_service
from app.schemas.file import FileUploadResponse, OcrWarmupResponse
from app.services.file_service import FileService

router = APIRouter()


@router.post("/files/upload", response_model=FileUploadResponse)
async def upload_files(
    files: list[UploadFile] = File(default_factory=list),
    service: FileService = Depends(file_service),
) -> FileUploadResponse:
    return await service.upload_files(files)


@router.post("/files/warmup-ocr", response_model=OcrWarmupResponse)
def warm_up_ocr(service: FileService = Depends(file_service)) -> OcrWarmupResponse:
    return service.warm_up_ocr()

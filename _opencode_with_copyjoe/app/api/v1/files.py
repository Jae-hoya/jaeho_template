from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import file_service
from app.schemas.file import FileUploadResponse
from app.services.file_service import FileService

router = APIRouter()


@router.post("/files/upload", response_model=FileUploadResponse)
async def upload_files(
    files: list[UploadFile] = File(default_factory=list),
    service: FileService = Depends(file_service),
) -> FileUploadResponse:
    return await service.upload_files(files)

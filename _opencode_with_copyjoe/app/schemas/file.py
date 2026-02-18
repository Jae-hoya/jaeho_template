from pydantic import BaseModel, Field


class UploadedFileItem(BaseModel):
    file_name: str
    document_id: str | None = None
    success: bool
    text_length: int = 0
    error_code: str | None = None
    error_message: str | None = None


class FileUploadResponse(BaseModel):
    total_files: int
    success_count: int
    failed_count: int
    files: list[UploadedFileItem] = Field(default_factory=list)

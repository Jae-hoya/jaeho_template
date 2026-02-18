from pydantic import BaseModel, Field


class UploadedFileItem(BaseModel):
    file_name: str
    document_id: str | None = None
    success: bool
    text_length: int = 0
    conversion_engine: str | None = None
    text_preview: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class FileUploadResponse(BaseModel):
    total_files: int
    success_count: int
    failed_count: int
    files: list[UploadedFileItem] = Field(default_factory=list)


class OcrWarmupResponse(BaseModel):
    ok: bool
    image_processing_strategy: str
    image_vlm_preset: str
    image_vlm_device: str
    pdf_ocr_strategy: str
    pdf_layout_model_strategy: str
    pdf_vlm_preset: str
    pdf_vlm_device: str
    warmed_components: list[str] = Field(default_factory=list)
    failed_components: list[str] = Field(default_factory=list)
    duration_ms: int

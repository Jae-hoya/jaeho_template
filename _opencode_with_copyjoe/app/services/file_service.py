from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import Settings
from app.core.errors import AppException, ErrorCode
from app.integrations.docling_client import DoclingClient
from app.schemas.file import FileUploadResponse, UploadedFileItem
from app.services.document_store import DocumentStore, StoredDocument


class FileService:
    def __init__(
        self,
        settings: Settings,
        docling_client: DoclingClient,
        document_store: DocumentStore,
    ) -> None:
        self._settings = settings
        self._docling_client = docling_client
        self._document_store = document_store

        settings.upload_path.mkdir(parents=True, exist_ok=True)
        settings.converted_path.mkdir(parents=True, exist_ok=True)

    async def upload_files(self, files: list[UploadFile]) -> FileUploadResponse:
        if len(files) > self._settings.max_file_count:
            raise AppException(
                status_code=400,
                code=ErrorCode.too_many_files,
                message=f"Maximum {self._settings.max_file_count} files per request",
            )

        items: list[UploadedFileItem] = []

        for file in files:
            file_name = file.filename or "unnamed"
            extension = Path(file_name).suffix.lower()

            if extension not in self._settings.allowed_extensions:
                items.append(
                    UploadedFileItem(
                        file_name=file_name,
                        success=False,
                        error_code=ErrorCode.unsupported_file_type.value,
                        error_message="Allowed: pdf, doc, docx, txt, xls, xlsx, ppt, pptx, png, jpg, jpeg",
                    )
                )
                await file.close()
                continue

            content = await file.read()
            await file.close()

            if len(content) > self._settings.max_file_size_bytes:
                items.append(
                    UploadedFileItem(
                        file_name=file_name,
                        success=False,
                        error_code=ErrorCode.file_too_large.value,
                        error_message=f"File exceeds {self._settings.max_file_size_mb}MB",
                    )
                )
                continue

            token = uuid4().hex
            source_path = self._settings.upload_path / f"{token}_{file_name}"
            source_path.write_bytes(content)

            try:
                text = self._docling_client.convert_to_text(source_path)
            except Exception as exc:
                items.append(
                    UploadedFileItem(
                        file_name=file_name,
                        success=False,
                        error_code=ErrorCode.doc_conversion_failed.value,
                        error_message=str(exc),
                    )
                )
                continue

            text = text.strip()
            if not text:
                items.append(
                    UploadedFileItem(
                        file_name=file_name,
                        success=False,
                        error_code=ErrorCode.doc_conversion_failed.value,
                        error_message="Converted text is empty",
                    )
                )
                continue

            document_id = str(uuid4())
            converted_path = self._settings.converted_path / f"{document_id}.txt"
            converted_path.write_text(text, encoding="utf-8")

            self._document_store.add(
                StoredDocument(
                    document_id=document_id,
                    file_name=file_name,
                    extension=extension,
                    source_path=source_path,
                    converted_path=converted_path,
                    converted_text=text,
                    created_at=datetime.utcnow(),
                )
            )

            items.append(
                UploadedFileItem(
                    file_name=file_name,
                    document_id=document_id,
                    success=True,
                    text_length=len(text),
                )
            )

        success_count = sum(1 for item in items if item.success)
        return FileUploadResponse(
            total_files=len(files),
            success_count=success_count,
            failed_count=len(items) - success_count,
            files=items,
        )

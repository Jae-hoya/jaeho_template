from enum import Enum
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    unsupported_file_type = "UNSUPPORTED_FILE_TYPE"
    file_too_large = "FILE_TOO_LARGE"
    doc_conversion_failed = "DOC_CONVERSION_FAILED"
    embedding_failed = "EMBEDDING_FAILED"
    vector_db_error = "VECTOR_DB_ERROR"
    web_search_error = "WEB_SEARCH_ERROR"
    validation_error = "VALIDATION_ERROR"
    too_many_files = "TOO_MANY_FILES"
    not_found = "NOT_FOUND"
    internal_error = "INTERNAL_ERROR"


class AppException(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


async def app_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppException):
        exc = AppException(
            status_code=500,
            code=ErrorCode.internal_error,
            message="Unhandled server error",
            details={"reason": str(exc)},
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": ErrorCode.internal_error.value,
                "message": "Unhandled server error",
                "details": {"reason": str(exc)},
            }
        },
    )

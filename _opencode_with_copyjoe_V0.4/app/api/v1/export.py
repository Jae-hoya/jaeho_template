from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import export_service
from app.schemas.export import ExportDocRequest, ExportDocxRequest, ExportMarkdownRequest
from app.services.export_service import ExportService

router = APIRouter()


@router.post("/export/docx")
def export_docx(
    payload: ExportDocxRequest,
    service: ExportService = Depends(export_service),
) -> StreamingResponse:
    file_name, content = service.export_docx(payload.file_name, payload.result)
    headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.post("/export/md")
def export_markdown(
    payload: ExportMarkdownRequest,
    service: ExportService = Depends(export_service),
) -> StreamingResponse:
    file_name, content = service.export_markdown(payload.file_name, payload.result)
    headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
    return StreamingResponse(
        iter([content]),
        media_type="text/markdown; charset=utf-8",
        headers=headers,
    )


@router.post("/export/doc")
def export_doc(
    payload: ExportDocRequest,
    service: ExportService = Depends(export_service),
) -> StreamingResponse:
    file_name, content = service.export_doc(payload.file_name, payload.result)
    headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
    return StreamingResponse(
        iter([content]),
        media_type="application/msword",
        headers=headers,
    )

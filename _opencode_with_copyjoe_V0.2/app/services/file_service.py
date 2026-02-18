from fastapi import UploadFile

from app.core.config import Settings
from app.flows.file_upload_graph import FileUploadGraph
from app.integrations.docling_client import DoclingClient
from app.schemas.file import FileUploadResponse
from app.services.document_store import DocumentStore


class FileService:
    def __init__(
        self,
        settings: Settings,
        docling_client: DoclingClient,
        document_store: DocumentStore,
    ) -> None:
        self._graph = FileUploadGraph(
            settings=settings,
            docling_client=docling_client,
            document_store=document_store,
        )

        settings.upload_path.mkdir(parents=True, exist_ok=True)
        settings.converted_path.mkdir(parents=True, exist_ok=True)

    @property
    def graph(self) -> FileUploadGraph:
        return self._graph

    async def upload_files(self, files: list[UploadFile]) -> FileUploadResponse:
        return await self._graph.run(files)

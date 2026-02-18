from app.flows.export_graph import ExportWorkflowGraph
from app.schemas.copy import CopyGenerateResponse


class ExportService:
    def __init__(self) -> None:
        self._graph = ExportWorkflowGraph()

    @property
    def graph(self) -> ExportWorkflowGraph:
        return self._graph

    def export_docx(self, file_name: str, result: CopyGenerateResponse) -> tuple[str, bytes]:
        return self._graph.run_docx(file_name=file_name, result=result)

    def export_markdown(self, file_name: str, result: CopyGenerateResponse) -> tuple[str, bytes]:
        return self._graph.run_markdown(file_name=file_name, result=result)

    def export_doc(self, file_name: str, result: CopyGenerateResponse) -> tuple[str, bytes]:
        return self._graph.run_doc(file_name=file_name, result=result)

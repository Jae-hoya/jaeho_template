from app.flows.meta_graph import MetaCopyFormGuideGraph
from app.schemas.meta import CopyFormGuideResponse


class MetaService:
    def __init__(self) -> None:
        self._graph = MetaCopyFormGuideGraph()

    @property
    def graph(self) -> MetaCopyFormGuideGraph:
        return self._graph

    def copy_form_guide(self) -> CopyFormGuideResponse:
        return self._graph.run()

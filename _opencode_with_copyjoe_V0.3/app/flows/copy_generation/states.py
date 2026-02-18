from typing import TypedDict

from app.schemas.common import SourceItem
from app.schemas.copy import CopyGenerateRequest, CopyStructuredOutput


class CopyGraphState(TypedDict):
    request: CopyGenerateRequest
    query: str
    context_blocks: list[str]
    sources: list[SourceItem]
    output: CopyStructuredOutput | None

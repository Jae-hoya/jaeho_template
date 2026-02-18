from typing import Awaitable, Callable, TypedDict

from app.schemas.common import SourceItem
from app.schemas.copy import (
    CopyGenerateRequest,
    CopyGenerateResponse,
    CopyLiteParsedInput,
    CopyLiteRequest,
    CopyLiteResponse,
    Objective,
)

ParsePromptFn = Callable[[str], tuple[CopyLiteParsedInput, list[str]]]
BuildLandingContextFn = Callable[[CopyLiteRequest], Awaitable[tuple[str | None, SourceItem | None, str | None]]]
InferObjectiveFn = Callable[[str], Objective | None]
InferChannelFn = Callable[[str], str | None]
InferLanguageFn = Callable[[str], str | None]
GenerateCopyFn = Callable[
    [CopyGenerateRequest, list[str] | None, list[SourceItem] | None],
    Awaitable[CopyGenerateResponse],
]


class CopyLiteGraphState(TypedDict):
    payload: CopyLiteRequest
    parsed: CopyLiteParsedInput | None
    assumptions: list[str]
    extra_context_blocks: list[str]
    extra_sources: list[SourceItem]
    landing_source_exists: bool
    objective: Objective | None
    channel: str | None
    language: str
    request: CopyGenerateRequest | None
    result: CopyGenerateResponse | None
    assistant_message: str
    response: CopyLiteResponse | None

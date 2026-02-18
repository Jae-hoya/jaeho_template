from typing import Awaitable, Callable, TypedDict

from langgraph.graph import END, START, StateGraph

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


class CopyLiteGenerationGraph:
    def __init__(
        self,
        parse_prompt: ParsePromptFn,
        build_landing_context: BuildLandingContextFn,
        infer_objective_from_prompt: InferObjectiveFn,
        infer_channel_from_prompt: InferChannelFn,
        infer_language_from_prompt: InferLanguageFn,
        generate_copy: GenerateCopyFn,
    ) -> None:
        self._parse_prompt = parse_prompt
        self._build_landing_context = build_landing_context
        self._infer_objective_from_prompt = infer_objective_from_prompt
        self._infer_channel_from_prompt = infer_channel_from_prompt
        self._infer_language_from_prompt = infer_language_from_prompt
        self._generate_copy = generate_copy

        builder = StateGraph(CopyLiteGraphState)
        builder.add_node("parse_prompt", self._parse_prompt_node)
        builder.add_node("landing_context", self._collect_landing_context_node)
        builder.add_node("infer_objective", self._infer_objective_node)
        builder.add_node("infer_channel", self._infer_channel_node)
        builder.add_node("infer_language", self._infer_language_node)
        builder.add_node("build_request", self._build_request_node)
        builder.add_node("generate_copy", self._generate_copy_node)
        builder.add_node("build_response", self._build_response_node)

        builder.add_edge(START, "parse_prompt")
        builder.add_edge("parse_prompt", "landing_context")
        builder.add_edge("landing_context", "infer_objective")
        builder.add_edge("infer_objective", "infer_channel")
        builder.add_edge("infer_channel", "infer_language")
        builder.add_edge("infer_language", "build_request")
        builder.add_edge("build_request", "generate_copy")
        builder.add_edge("generate_copy", "build_response")
        builder.add_edge("build_response", END)

        self._graph = builder.compile()

    async def run(self, payload: CopyLiteRequest) -> CopyLiteResponse:
        state = await self._graph.ainvoke(
            {
                "payload": payload,
                "parsed": None,
                "assumptions": [],
                "extra_context_blocks": [],
                "extra_sources": [],
                "landing_source_exists": False,
                "objective": None,
                "channel": None,
                "language": payload.language,
                "request": None,
                "result": None,
                "assistant_message": "",
                "response": None,
            }
        )
        response = state.get("response")
        if response is None:
            raise RuntimeError("Copy-lite graph failed to produce a response")
        return response

    def _parse_prompt_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        parsed, assumptions = self._parse_prompt(payload.prompt)
        return {
            "parsed": parsed,
            "assumptions": list(assumptions),
            "extra_context_blocks": list(state.get("extra_context_blocks", [])),
            "extra_sources": list(state.get("extra_sources", [])),
        }

    async def _collect_landing_context_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        assumptions = list(state.get("assumptions", []))
        context_blocks = list(state.get("extra_context_blocks", []))
        sources = list(state.get("extra_sources", []))

        landing_context_block, landing_source, landing_assumption = await self._build_landing_context(payload)

        if landing_context_block:
            context_blocks.append(landing_context_block)
        if landing_source is not None:
            sources.append(landing_source)
        if landing_assumption:
            assumptions.append(landing_assumption)

        return {
            "assumptions": assumptions,
            "extra_context_blocks": context_blocks,
            "extra_sources": sources,
            "landing_source_exists": landing_source is not None,
        }

    def _infer_objective_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        assumptions = list(state.get("assumptions", []))
        inferred_objective = self._infer_objective_from_prompt(payload.prompt)

        objective = payload.objective
        if objective is None:
            if inferred_objective is not None:
                objective = inferred_objective
                assumptions.append(f"objective 미입력: 프롬프트에서 {objective.value}로 추정")
            else:
                objective = Objective.click
                assumptions.append("objective 미입력: click으로 자동 설정")

        return {
            "objective": objective,
            "assumptions": assumptions,
        }

    def _infer_channel_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        assumptions = list(state.get("assumptions", []))
        landing_source_exists = bool(state.get("landing_source_exists", False))

        raw_channel = (payload.channel or "").strip()
        if raw_channel:
            channel = raw_channel
        else:
            if landing_source_exists:
                channel = "랜딩페이지"
                assumptions.append("channel 미입력: 렌더링 랜딩 기반으로 랜딩페이지로 자동 설정")
            else:
                inferred_channel = self._infer_channel_from_prompt(payload.prompt)
                if inferred_channel:
                    channel = inferred_channel
                    assumptions.append(f"channel 미입력: 프롬프트에서 '{channel}'로 추정")
                else:
                    channel = "상세페이지"
                    assumptions.append("channel 미입력: 상세페이지로 자동 설정")

        return {
            "channel": channel,
            "assumptions": assumptions,
        }

    def _infer_language_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        assumptions = list(state.get("assumptions", []))

        language = payload.language
        if "language" not in payload.model_fields_set:
            inferred_language = self._infer_language_from_prompt(payload.prompt)
            if inferred_language:
                language = inferred_language
                assumptions.append(f"language 미입력: 프롬프트에서 '{language}'로 추정")
            else:
                assumptions.append("language 미입력: ko로 자동 설정")

        return {
            "language": language,
            "assumptions": assumptions,
        }

    def _build_request_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        parsed = state.get("parsed")
        objective = state.get("objective")
        channel = state.get("channel")
        language = state.get("language", payload.language)

        if parsed is None:
            parsed, parse_assumptions = self._parse_prompt(payload.prompt)
            assumptions = list(state.get("assumptions", []))
            assumptions.extend(parse_assumptions)
        else:
            assumptions = list(state.get("assumptions", []))

        if objective is None:
            objective = Objective.click
        if channel is None:
            channel = "상세페이지"

        request = CopyGenerateRequest(
            product_name=parsed.product_name,
            target_audience=parsed.target_audience,
            pain_point=parsed.pain_point,
            differentiator=parsed.differentiator,
            tone=parsed.tone,
            objective=objective,
            styles=payload.styles,
            channel=channel,
            language=language,
            web_search_mode=payload.web_search_mode,
            use_rag=payload.use_rag,
            top_k=payload.top_k,
        )
        return {
            "request": request,
            "assumptions": assumptions,
        }

    async def _generate_copy_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        request = state.get("request")
        if request is None:
            raise RuntimeError("Copy-lite graph request was not prepared")

        result = await self._generate_copy(
            request,
            extra_context_blocks=list(state.get("extra_context_blocks", [])),
            extra_sources=list(state.get("extra_sources", [])),
        )
        return {"result": result}

    def _build_response_node(self, state: CopyLiteGraphState) -> dict[str, object]:
        request = state.get("request")
        result = state.get("result")
        if request is None or result is None:
            raise RuntimeError("Copy-lite graph missing request or result")

        if state.get("landing_source_exists"):
            assistant_message = (
                "스타일을 제외한 입력은 프롬프트에서 자동 해석하고, 웹 렌더링 랜딩 컨텍스트를 반영해 카피를 생성했습니다. "
                "아래 assumptions를 확인하고 같은 대화에서 바로 추가 지시를 주세요."
            )
        else:
            assistant_message = (
                "스타일을 제외한 입력은 프롬프트에서 자동 해석해 카피를 생성했습니다. "
                "아래 assumptions를 확인하고, 같은 대화에서 바로 추가 지시를 주세요."
            )

        response = CopyLiteResponse(
            assistant_message=assistant_message,
            assumptions=list(state.get("assumptions", [])),
            normalized_request=request,
            result=result,
        )
        return {
            "assistant_message": assistant_message,
            "response": response,
        }

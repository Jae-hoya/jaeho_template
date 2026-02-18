from abc import ABC, abstractmethod

from app.flows.copy_lite_generation.states import (
    BuildLandingContextFn,
    CopyLiteGraphState,
    GenerateCopyFn,
    InferChannelFn,
    InferLanguageFn,
    InferObjectiveFn,
    ParsePromptFn,
)
from app.schemas.copy import CopyGenerateRequest, CopyLiteResponse, Objective


class BaseNode(ABC):
    @abstractmethod
    def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
        raise NotImplementedError

    def __call__(self, state: CopyLiteGraphState) -> dict[str, object]:
        return self.execute(state)


class AsyncBaseNode(ABC):
    @abstractmethod
    async def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
        raise NotImplementedError

    async def __call__(self, state: CopyLiteGraphState) -> dict[str, object]:
        return await self.execute(state)


class ParsePromptNode(BaseNode):
    def __init__(self, parse_prompt: ParsePromptFn) -> None:
        self._parse_prompt = parse_prompt

    def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        parsed, assumptions = self._parse_prompt(payload.prompt)
        return {
            "parsed": parsed,
            "assumptions": list(assumptions),
            "extra_context_blocks": list(state.get("extra_context_blocks", [])),
            "extra_sources": list(state.get("extra_sources", [])),
        }


class CollectLandingContextNode(AsyncBaseNode):
    def __init__(self, build_landing_context: BuildLandingContextFn) -> None:
        self._build_landing_context = build_landing_context

    async def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
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


class InferObjectiveNode(BaseNode):
    def __init__(self, infer_objective_from_prompt: InferObjectiveFn) -> None:
        self._infer_objective_from_prompt = infer_objective_from_prompt

    def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
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


class InferChannelNode(BaseNode):
    def __init__(self, infer_channel_from_prompt: InferChannelFn) -> None:
        self._infer_channel_from_prompt = infer_channel_from_prompt

    def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
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


class InferLanguageNode(BaseNode):
    def __init__(self, infer_language_from_prompt: InferLanguageFn) -> None:
        self._infer_language_from_prompt = infer_language_from_prompt

    def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
        payload = state["payload"]
        assumptions = list(state.get("assumptions", []))

        language = payload.language
        inferred_language = self._infer_language_from_prompt(payload.prompt)

        if "language" in payload.model_fields_set:
            has_feedback_section = "[사용자 피드백]" in payload.prompt
            if has_feedback_section and inferred_language and inferred_language != language:
                assumptions.append(f"language 변경 요청 감지: '{language}' -> '{inferred_language}'")
                language = inferred_language
                return {
                    "language": language,
                    "assumptions": assumptions,
                }

        if "language" not in payload.model_fields_set:
            if inferred_language:
                language = inferred_language
                assumptions.append(f"language 미입력: 프롬프트에서 '{language}'로 추정")
            else:
                assumptions.append("language 미입력: ko로 자동 설정")

        return {
            "language": language,
            "assumptions": assumptions,
        }


class BuildRequestNode(BaseNode):
    def __init__(self, parse_prompt: ParsePromptFn) -> None:
        self._parse_prompt = parse_prompt

    def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
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
            rag_document_ids=payload.rag_document_ids,
        )

        return {
            "request": request,
            "assumptions": assumptions,
        }


class GenerateCopyNode(AsyncBaseNode):
    def __init__(self, generate_copy: GenerateCopyFn) -> None:
        self._generate_copy = generate_copy

    async def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
        request = state.get("request")
        if request is None:
            raise RuntimeError("Copy-lite graph request was not prepared")

        result = await self._generate_copy(
            request,
            extra_context_blocks=list(state.get("extra_context_blocks", [])),
            extra_sources=list(state.get("extra_sources", [])),
        )
        return {"result": result}


class BuildResponseNode(BaseNode):
    def execute(self, state: CopyLiteGraphState) -> dict[str, object]:
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

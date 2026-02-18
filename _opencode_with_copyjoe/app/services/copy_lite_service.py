import re

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import Settings
from app.integrations.model_factory import create_chat_model
from app.schemas.copy import (
    CopyGenerateRequest,
    CopyLiteParsedInput,
    CopyLiteRequest,
    CopyLiteResponse,
    Objective,
)
from app.services.copy_service import CopyService


class CopyLiteService:
    def __init__(self, settings: Settings, copy_service: CopyService) -> None:
        self._settings = settings
        self._copy_service = copy_service
        self._model = create_chat_model(settings)

    async def generate(self, payload: CopyLiteRequest) -> CopyLiteResponse:
        parsed, assumptions = self._parse_prompt(payload.prompt)

        objective = payload.objective or Objective.click
        if payload.objective is None:
            assumptions.append("objective 미입력: click으로 자동 설정")

        channel = (payload.channel or "상세페이지").strip() or "상세페이지"
        if payload.channel is None or not str(payload.channel).strip():
            assumptions.append("channel 미입력: 상세페이지로 자동 설정")

        request = CopyGenerateRequest(
            product_name=parsed.product_name,
            target_audience=parsed.target_audience,
            pain_point=parsed.pain_point,
            differentiator=parsed.differentiator,
            tone=parsed.tone,
            objective=objective,
            styles=payload.styles,
            channel=channel,
            language=payload.language,
            web_search_mode=payload.web_search_mode,
            use_rag=payload.use_rag,
            top_k=payload.top_k,
        )

        result = await self._copy_service.generate(request)

        assistant_message = (
            "짧은 프롬프트를 바탕으로 기본 입력을 자동 완성해 카피를 생성했습니다. "
            "아래 assumptions를 보고 필요하면 objective/channel만 조정해 다시 생성하세요."
        )

        return CopyLiteResponse(
            assistant_message=assistant_message,
            assumptions=assumptions,
            normalized_request=request,
            result=result,
        )

    def _parse_prompt(self, prompt: str) -> tuple[CopyLiteParsedInput, list[str]]:
        assumptions: list[str] = []

        if self._settings.should_mock or self._model is None:
            parsed = self._heuristic_parse(prompt)
            assumptions.extend(self._build_parse_assumptions(parsed))
            assumptions.append("LLM 파서 미사용: heuristic 파서로 추정")
            return parsed, assumptions

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
너는 마케팅 브리프 정리 도우미다.
사용자 자유 프롬프트에서 아래 필드를 추출한다.
- product_name
- target_audience
- pain_point
- differentiator
- tone

규칙:
1) 모르면 빈 문자열이 아니라 가장 안전한 일반 표현으로 채운다.
2) 한국어로 자연스럽게 요약한다.
3) 과장/환각 금지, 입력 근거 중심으로 정리.
""".strip(),
                ),
                (
                    "human",
                    """
[사용자 프롬프트]
{prompt}
""".strip(),
                ),
            ]
        )

        try:
            structured_model = self._model.with_structured_output(CopyLiteParsedInput)
            parser_bind_kwargs: dict[str, float | int] = {
                "temperature": self._settings.copy_parser_temperature,
                "max_tokens": self._settings.copy_parser_max_tokens,
            }
            try:
                structured_model = structured_model.bind(**parser_bind_kwargs)
            except Exception:
                pass
            chain = prompt_template | structured_model
            result: object = chain.invoke({"prompt": prompt})

            if isinstance(result, CopyLiteParsedInput):
                parsed = result
            elif isinstance(result, dict):
                parsed = CopyLiteParsedInput.model_validate(result)
            elif hasattr(result, "model_dump"):
                parsed = CopyLiteParsedInput.model_validate(result.model_dump())
            else:
                parsed = self._heuristic_parse(prompt)
                assumptions.append("LLM 파싱 결과 해석 실패: heuristic 파서 사용")

            assumptions.extend(self._build_parse_assumptions(parsed))
            return parsed, assumptions
        except Exception:
            parsed = self._heuristic_parse(prompt)
            assumptions.extend(self._build_parse_assumptions(parsed))
            assumptions.append("LLM 파싱 실패: heuristic 파서로 추정")
            return parsed, assumptions

    def _heuristic_parse(self, prompt: str) -> CopyLiteParsedInput:
        text = " ".join(prompt.split())
        candidate_name = self._extract_product_name(text)
        tone = "신뢰형"

        if any(token in text for token in ["친근", "캐주얼", "편안"]):
            tone = "친근형"
        elif any(token in text for token in ["강렬", "도전", "임팩트"]):
            tone = "도전형"

        return CopyLiteParsedInput(
            product_name=candidate_name,
            target_audience="잠재 고객",
            pain_point=text[:500],
            differentiator="핵심 강점을 근거 중심으로 설득한다",
            tone=tone,
        )

    def _extract_product_name(self, text: str) -> str:
        quoted = re.search(r"[\"'“”‘’]([^\"'“”‘’]{2,40})[\"'“”‘’]", text)
        if quoted:
            return quoted.group(1).strip()

        marker_patterns = [
            r"제품명\s*[:：]\s*([^,\.\n]{2,40})",
            r"서비스명\s*[:：]\s*([^,\.\n]{2,40})",
        ]
        for pattern in marker_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()

        if len(text) <= 40:
            return text
        return "제품"

    def _build_parse_assumptions(self, parsed: CopyLiteParsedInput) -> list[str]:
        assumptions: list[str] = []

        if parsed.target_audience.strip() in {"", "잠재 고객"}:
            assumptions.append("target_audience가 모호해 '잠재 고객'으로 설정")
        if parsed.differentiator.strip() in {"", "핵심 강점을 근거 중심으로 설득한다"}:
            assumptions.append("differentiator가 부족해 일반형으로 보정")
        if parsed.product_name.strip() in {"", "제품"}:
            assumptions.append("product_name이 명확하지 않아 '제품'으로 설정")

        return assumptions

import re

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import Settings
from app.integrations.model_factory import create_chat_model
from app.schemas.common import SourceItem
from app.schemas.copy import (
    CopyGenerateRequest,
    CopyLiteParsedInput,
    CopyLiteRequest,
    CopyLiteResponse,
    Objective,
)
from app.schemas.web import LandingAnalyzeResponse
from app.services.copy_service import CopyService
from app.services.web_search_service import WebSearchService


class CopyLiteService:
    def __init__(
        self,
        settings: Settings,
        copy_service: CopyService,
        web_search_service: WebSearchService,
    ) -> None:
        self._settings = settings
        self._copy_service = copy_service
        self._web_search_service = web_search_service
        self._model = create_chat_model(settings)

    async def generate(self, payload: CopyLiteRequest) -> CopyLiteResponse:
        parsed, assumptions = self._parse_prompt(payload.prompt)

        landing_context_block, landing_source, landing_assumption = await self._build_landing_render_context(payload)
        extra_context_blocks: list[str] = []
        extra_sources: list[SourceItem] = []
        if landing_context_block:
            extra_context_blocks.append(landing_context_block)
        if landing_source is not None:
            extra_sources.append(landing_source)
        if landing_assumption:
            assumptions.append(landing_assumption)

        inferred_objective = self._infer_objective_from_prompt(payload.prompt)
        objective = payload.objective
        if objective is None:
            if inferred_objective is not None:
                objective = inferred_objective
                assumptions.append(f"objective 미입력: 프롬프트에서 {objective.value}로 추정")
            else:
                objective = Objective.click
                assumptions.append("objective 미입력: click으로 자동 설정")

        raw_channel = (payload.channel or "").strip()
        if raw_channel:
            channel = raw_channel
        else:
            if landing_source is not None:
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

        language = payload.language
        if "language" not in payload.model_fields_set:
            inferred_language = self._infer_language_from_prompt(payload.prompt)
            if inferred_language:
                language = inferred_language
                assumptions.append(f"language 미입력: 프롬프트에서 '{language}'로 추정")
            else:
                assumptions.append("language 미입력: ko로 자동 설정")

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

        result = await self._copy_service.generate(
            request,
            extra_context_blocks=extra_context_blocks,
            extra_sources=extra_sources,
        )

        if landing_source is not None:
            assistant_message = (
                "스타일을 제외한 입력은 프롬프트에서 자동 해석하고, 웹 렌더링 랜딩 컨텍스트를 반영해 카피를 생성했습니다. "
                "아래 assumptions를 확인하고 같은 대화에서 바로 추가 지시를 주세요."
            )
        else:
            assistant_message = (
                "스타일을 제외한 입력은 프롬프트에서 자동 해석해 카피를 생성했습니다. "
                "아래 assumptions를 확인하고, 같은 대화에서 바로 추가 지시를 주세요."
            )

        return CopyLiteResponse(
            assistant_message=assistant_message,
            assumptions=assumptions,
            normalized_request=request,
            result=result,
        )

    async def _build_landing_render_context(
        self,
        payload: CopyLiteRequest,
    ) -> tuple[str | None, SourceItem | None, str | None]:
        landing_url = (payload.landing_url or "").strip()
        landing_query = (payload.landing_query or "").strip()

        landing: LandingAnalyzeResponse | None = None
        assumption: str | None = None

        try:
            if landing_url:
                landing = await self._web_search_service.analyze_landing_page(landing_url, from_tavily=False)
                assumption = f"landing_url 렌더링 컨텍스트 반영: {landing.url}"
            elif landing_query:
                landing = await self._web_search_service.search_then_analyze(landing_query, max_results=5)
                assumption = f"landing_query 렌더링 컨텍스트 반영: {landing.url}"
        except Exception as exc:
            if landing_url:
                assumption = f"landing_url 렌더링 실패: {landing_url} ({str(exc)[:120]})"
            elif landing_query:
                assumption = f"landing_query 렌더링 실패: {landing_query} ({str(exc)[:120]})"

        if landing is None:
            return None, None, assumption

        context = self._format_landing_render_context(landing)
        source = SourceItem(
            source_type="web",
            title=(landing.title or "Rendered landing page")[:200],
            url=landing.url,
            snippet=landing.body[:1200],
        )
        return context, source, assumption

    def _format_landing_render_context(self, landing: LandingAnalyzeResponse) -> str:
        h1_text = " | ".join(landing.h1[:5]) if landing.h1 else "(없음)"
        h2_text = " | ".join(landing.h2[:8]) if landing.h2 else "(없음)"
        cta_text = " | ".join(landing.cta_buttons[:12]) if landing.cta_buttons else "(없음)"
        body_excerpt = (landing.body or "")[:3500]

        return "\n".join(
            [
                "[렌더링 랜딩 컨텍스트]",
                f"url: {landing.url}",
                f"title: {landing.title}",
                f"h1: {h1_text}",
                f"h2: {h2_text}",
                f"cta_buttons: {cta_text}",
                f"body_excerpt: {body_excerpt}",
            ]
        )

    def _infer_objective_from_prompt(self, prompt: str) -> Objective | None:
        text = prompt.lower()

        if any(token in text for token in ["장바구니", "add to cart", "add_to_cart", "atc"]):
            return Objective.add_to_cart

        if any(token in text for token in ["상담", "문의", "consultation", "demo request", "demo 신청", "데모 신청"]):
            return Objective.consultation

        if any(token in text for token in ["브랜드 인지", "브랜드 기억", "brand memory", "awareness", "광고 회상"]):
            return Objective.brand_memory

        if any(token in text for token in ["클릭", "ctr", "click", "유입", "방문"]):
            return Objective.click

        return None

    def _infer_channel_from_prompt(self, prompt: str) -> str | None:
        text = prompt.lower()

        if any(token in text for token in ["상세페이지", "detail page", "product page"]):
            return "상세페이지"

        if any(token in text for token in ["인스타", "instagram", "insta"]):
            return "인스타 피드"

        if any(token in text for token in ["메타 광고", "meta ad", "facebook ad", "페이스북 광고", "fb ad"]):
            return "메타 광고 랜딩"

        if any(token in text for token in ["유튜브", "youtube", "쇼츠", "shorts"]):
            return "유튜브 쇼츠"

        if any(token in text for token in ["이메일", "email", "newsletter"]):
            return "이메일 캠페인"

        if any(token in text for token in ["카카오", "친구톡", "kakao"]):
            return "카카오 친구톡"

        if any(token in text for token in ["네이버 블로그", "블로그", "blog"]):
            return "네이버 블로그"

        if any(token in text for token in ["랜딩", "landing page", "landing"]):
            return "퍼포먼스 광고 랜딩"

        return None

    def _infer_language_from_prompt(self, prompt: str) -> str | None:
        text = prompt.lower()

        language_markers: list[tuple[str, list[str]]] = [
            ("zh-TW", ["zh-tw", "zh_hant", "traditional chinese", "번체", "繁體"]),
            ("zh-CN", ["zh-cn", "zh_hans", "simplified chinese", "간체", "简体"]),
            ("ja", ["japanese", "ja-jp", "일본어", "일어"]),
            ("en", ["english", "en-us", "en-gb", "영어", "영문"]),
            ("es", ["spanish", "español", "스페인어"]),
            ("fr", ["french", "français", "프랑스어"]),
            ("de", ["german", "deutsch", "독일어"]),
            ("pt-BR", ["portuguese", "português", "pt-br", "브라질 포르투갈어"]),
            ("vi", ["vietnamese", "베트남어"]),
            ("id", ["indonesian", "bahasa indonesia", "인도네시아어"]),
            ("th", ["thai", "태국어", "ภาษาไทย"]),
            ("ko", ["korean", "ko-kr", "한국어", "한글"]),
        ]

        for code, markers in language_markers:
            if any(marker in text for marker in markers):
                return code

        return None

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

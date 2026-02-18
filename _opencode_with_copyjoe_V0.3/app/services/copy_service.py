import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import Settings
from app.flows.copy_generation import CopyGenerationGraph
from app.integrations.model_factory import create_chat_model
from app.schemas.common import SourceItem
from app.schemas.copy import CopyGenerateRequest, CopyGenerateResponse, CopyStructuredOutput
from app.services.rag_service import RagService
from app.services.web_search_service import WebSearchService


class CopyService:
    def __init__(self, settings: Settings, rag_service: RagService, web_search_service: WebSearchService) -> None:
        self._settings = settings
        self._model = create_chat_model(settings)
        self._graph = CopyGenerationGraph(
            rag_service=rag_service,
            web_search_service=web_search_service,
            generator=self._run_chain_or_fallback,
        )

    @property
    def graph(self) -> CopyGenerationGraph:
        return self._graph

    async def generate(
        self,
        request: CopyGenerateRequest,
        extra_context_blocks: list[str] | None = None,
        extra_sources: list[SourceItem] | None = None,
    ) -> CopyGenerateResponse:
        output, sources = self._graph.run(
            request,
            extra_context_blocks=extra_context_blocks,
            extra_sources=extra_sources,
        )
        projected = self._project_styles(output, request.styles)

        rationale = projected.rationale
        rationale += f" | sources={len(sources)}"

        return CopyGenerateResponse(
            head=projected.head,
            body=projected.body,
            cta=projected.cta,
            slogan=projected.slogan,
            sns=projected.sns,
            description=projected.description,
            storyboard_outline=projected.storyboard_outline,
            rationale=rationale,
            sources=sources,
        )

    def _run_chain_or_fallback(self, request: CopyGenerateRequest, context: str) -> CopyStructuredOutput:
        if self._settings.should_mock or self._model is None:
            return self._mock_output(request, context)

        cleaned_context = self._sanitize_context(context, request.language)

        primary = self._invoke_structured_chain(
            request=request,
            context=cleaned_context,
            strict_mode=False,
            temperature=self._settings.copy_generation_temperature,
        )
        if primary is None:
            return self._mock_output(request, cleaned_context)

        if not self._looks_corrupted_output(primary, request.language):
            return primary

        repaired = self._invoke_structured_chain(
            request=request,
            context=cleaned_context,
            strict_mode=True,
            temperature=min(0.35, self._settings.copy_generation_temperature),
        )
        if repaired is not None and not self._looks_corrupted_output(repaired, request.language):
            return repaired

        candidate = repaired if repaired is not None else primary
        return self._stabilize_output_text(candidate, request.language)

    def _invoke_structured_chain(
        self,
        request: CopyGenerateRequest,
        context: str,
        strict_mode: bool,
        temperature: float,
    ) -> CopyStructuredOutput | None:
        model = self._model
        if model is None:
            return None

        prompt = self._build_copy_prompt(strict_mode)

        try:
            structured_model = model.with_structured_output(CopyStructuredOutput)
            bind_kwargs: dict[str, float | int] = {
                "temperature": temperature,
                "max_tokens": self._settings.copy_generation_max_tokens,
            }
            try:
                structured_model = structured_model.bind(**bind_kwargs)
            except Exception:
                pass
            chain = prompt | structured_model
            result: Any = chain.invoke(
                {
                    "product_name": request.product_name,
                    "target_audience": request.target_audience,
                    "pain_point": request.pain_point,
                    "differentiator": request.differentiator,
                    "tone": request.tone,
                    "objective": request.objective.value,
                    "styles": ", ".join(style.value for style in request.styles),
                    "channel": request.channel,
                    "language": request.language,
                    "context": context or "(컨텍스트 없음)",
                }
            )

            if isinstance(result, CopyStructuredOutput):
                return result
            if isinstance(result, dict):
                return CopyStructuredOutput.model_validate(result)
            model_dump = getattr(result, "model_dump", None)
            if callable(model_dump):
                return CopyStructuredOutput.model_validate(model_dump())
            return None
        except Exception:
            return None

    def _build_copy_prompt(self, strict_mode: bool) -> ChatPromptTemplate:
        system_prompt = """
너는 정형 문구를 찍어내는 카피봇이 아니라, 소비자 행동을 실제로 움직이는 성과형 카피라이터다.
목표는 '보기 좋은 문장'이 아니라 '지금 행동하게 만드는 문장'이다.

[절대 규칙]
1) 출력은 스키마를 엄격히 지켜라. 불필요한 키/설명/메타텍스트를 추가하지 마라.
2) 근거 컨텍스트에 없는 수치/사실은 지어내지 마라.
3) 추상어(최고, 혁신, 프리미엄, 완벽) 남발 금지. 구체적인 상황/효익/행동으로 바꿔라.
4) pain_point -> 긴장 증폭 -> differentiator 해소 -> 행동 유도 흐름을 반드시 만든다.

[창의성 규칙]
- 내부적으로 최소 3개 각도(공감형, 반전형, 결과형)를 빠르게 시도한 뒤 가장 설득력이 높은 방향 1개를 선택해 출력하라.
- 상투 문구를 그대로 반복하지 말고, 문장 리듬과 어휘를 새롭게 구성하라.
- 독자가 장면을 떠올릴 수 있도록 최소 1개의 현실 상황 표현을 포함하라.
- 각 필드(head/body/cta/slogan/sns/description)는 서로 다른 역할과 톤으로 분화하라.

[objective별 우선 전략]
- click: 스크롤 스톱 훅 + 즉시 행동 이유
- add_to_cart: 구매 장벽 해소 + 지연 손실 강조
- consultation: 신뢰/전문성 + 부담 없는 첫 행동
- brand_memory: 반복 가능하고 기억되는 한 줄

[채널 최적화]
- 메타/인스타: 첫 문장 강도, 짧은 호흡, 모바일 가독성
- 상세페이지/랜딩: 문제 -> 해결 -> 근거 -> CTA의 설득 구조
- 이메일/메신저: 개인화된 어조 + 다음 행동의 명확성

[출력 품질 기준]
- head: 한 줄에서 차별점이 바로 느껴지는 훅
- body: 3~10문장, 문제 맥락 -> 해결 -> 근거 -> 행동 흐름
- cta: 동사로 시작, 클릭/신청/담기의 즉시 이익 포함
- slogan: 짧고 기억되는 리듬
- sns: 훅 + 근거 + 액션을 압축한 확산형 문장
- description: 운영자가 바로 쓸 수 있는 채널 맞춤 설명
- storyboard_outline: 5~7단계, 각 단계는 '장면:핵심메시지'
- rationale: 적용한 설득 논리(심리 트리거/장벽 해소/근거 연결)를 명확히 기술
        """.strip()

        if strict_mode:
            system_prompt += "\n\n" + """
[텍스트 안정화 규칙]
- 출력 언어({language}) 기준에서 벗어나는 깨진 문자/혼합 스크립트 토큰은 절대 쓰지 마라.
- OCR 잡음처럼 보이는 문자열(예: 서로 다른 문자군이 섞인 이상 토큰, 의미 없는 숫자-기호 연쇄)은 버리고 자연어로 재작성하라.
- 특히 한국어/영어 출력에서는 러시아어/아랍어/기타 외부 스크립트 혼입을 금지한다.
            """.strip()

        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    """
[입력]
상품: {product_name}
타깃: {target_audience}
문제: {pain_point}
차별점: {differentiator}
톤: {tone}
목표: {objective}
스타일: {styles}
채널: {channel}
언어: {language}

[근거 컨텍스트]
{context}

요청:
1) 정형적 표현을 피하고 차별화된 전환형 카피를 작성할 것
2) 소비자가 느끼는 실제 상황과 감정을 문장에 반영할 것
3) 과장 대신 구체성으로 설득하고, 목표 행동을 강하게 유도할 것
4) 언어({language})와 채널({channel}) 특성을 반영할 것
                    """.strip(),
                ),
            ]
        )

    def _sanitize_context(self, context: str, language: str) -> str:
        if not context.strip():
            return context

        lines = context.splitlines()
        cleaned_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if self._is_noise_line(stripped, language):
                continue
            cleaned_lines.append(stripped)

        if not cleaned_lines:
            return ""
        return "\n".join(cleaned_lines)

    def _is_noise_line(self, line: str, language: str) -> bool:
        if "\ufffd" in line:
            return True

        if language.lower().startswith(("ko", "en")):
            if re.search(r"[\u0400-\u052F]", line):
                return True

        token_count = max(1, len(re.findall(r"\S+", line)))
        noisy_token_count = sum(1 for token in re.findall(r"\S+", line) if self._is_mixed_script_token(token))
        if noisy_token_count / token_count >= 0.3:
            return True

        return False

    def _looks_corrupted_output(self, output: CopyStructuredOutput, language: str) -> bool:
        texts = [
            output.head,
            output.body,
            output.cta,
            output.slogan,
            output.sns,
            output.description,
            output.rationale,
            "\n".join(output.storyboard_outline),
        ]
        merged = "\n".join(texts)
        if "\ufffd" in merged:
            return True
        if language.lower().startswith(("ko", "en")) and re.search(r"[\u0400-\u052F]", merged):
            return True

        mixed_tokens = [token for token in re.findall(r"\S+", merged) if self._is_mixed_script_token(token)]
        return len(mixed_tokens) >= 2

    def _is_mixed_script_token(self, token: str) -> bool:
        has_cyrillic = bool(re.search(r"[\u0400-\u052F]", token))
        has_hangul = bool(re.search(r"[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]", token))
        has_latin = bool(re.search(r"[A-Za-z]", token))
        return has_cyrillic and (has_hangul or has_latin)

    def _stabilize_output_text(self, output: CopyStructuredOutput, language: str) -> CopyStructuredOutput:
        def clean_field(text: str) -> str:
            if not text.strip():
                return text
            tokens = re.findall(r"\S+", text)
            filtered = [token for token in tokens if not self._is_mixed_script_token(token)]
            cleaned = " ".join(filtered).strip()
            if language.lower().startswith(("ko", "en")):
                cleaned = re.sub(r"[\u0400-\u052F]+", "", cleaned).strip()
            if len(cleaned) < max(8, len(text) // 4):
                return text
            return cleaned

        cleaned_outline = [clean_field(item) for item in output.storyboard_outline]
        return CopyStructuredOutput(
            head=clean_field(output.head),
            body=clean_field(output.body),
            cta=clean_field(output.cta),
            slogan=clean_field(output.slogan),
            sns=clean_field(output.sns),
            description=clean_field(output.description),
            storyboard_outline=cleaned_outline,
            rationale=clean_field(output.rationale),
        )

    def _project_styles(self, output: CopyStructuredOutput, styles: list) -> CopyStructuredOutput:
        selected = {style.value for style in styles}
        return CopyStructuredOutput(
            head=output.head if "head" in selected else "",
            body=output.body if "body" in selected else "",
            cta=output.cta if "cta" in selected else "",
            slogan=output.slogan if "slogan" in selected else "",
            sns=output.sns if "sns" in selected else "",
            description=output.description if "description" in selected else "",
            storyboard_outline=output.storyboard_outline,
            rationale=output.rationale,
        )

    def _mock_output(self, request: CopyGenerateRequest, context: str) -> CopyStructuredOutput:
        has_context = "있음" if context else "없음"

        cta_by_objective = {
            "click": "지금 핵심 포인트 확인하기",
            "add_to_cart": "혜택 적용하고 장바구니 담기",
            "consultation": "내 상황으로 상담 시작하기",
            "brand_memory": "브랜드 스토리 더 보기",
        }

        cta = cta_by_objective.get(request.objective.value, "지금 바로 확인하기")

        return CopyStructuredOutput(
            head=(
                f"{request.pain_point}를 끝내는 {request.product_name}, "
                f"{request.target_audience}의 선택을 당깁니다"
            ),
            body=(
                f"{request.pain_point}로 성과가 흔들리는 순간, 메시지 전략부터 바꿔야 합니다. "
                f"{request.product_name}는 {request.differentiator} 강점으로 "
                f"{request.channel} 환경에서 실행 가능한 전환형 문장을 빠르게 제시합니다. "
                f"지금 바로 테스트 가능한 카피로 다음 실험 사이클을 앞당기세요."
            ),
            cta=cta,
            slogan=f"{request.product_name}, 성과를 설득으로 연결하다",
            sns=(
                f"성과가 막히는 순간, 카피부터 바꿔야 합니다. "
                f"{request.differentiator} 기반으로 전환형 문구를 빠르게 실행하세요. "
                f"#{request.product_name.replace(' ', '')} #마케팅카피"
            ),
            description=f"{request.channel}에 최적화된 전환형 카피 아이디어 세트",
            storyboard_outline=[
                "문제 장면: 성과 하락을 체감하는 순간",
                "긴장 장면: 기존 방식의 한계가 드러남",
                f"해결 장면: {request.product_name}의 접근 제시",
                "근거 장면: 차별점과 실행 근거 제시",
                "전환 장면: 사용 후 변화 이미지 강화",
                "행동 장면: 즉시 CTA로 마무리",
            ],
            rationale=(
                f"{request.tone} 톤을 유지하면서 pain_point를 선명하게 제시하고, "
                f"differentiator를 행동 이유로 연결했다. objective={request.objective.value}, context={has_context}"
            ),
        )

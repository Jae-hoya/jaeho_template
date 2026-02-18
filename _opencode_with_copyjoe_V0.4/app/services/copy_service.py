import asyncio
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import Settings
from app.flows.copy_generation import CopyGenerationGraph
from app.flows.copy_lite_generation import CopyLiteGenerationGraph
from app.integrations.model_factory import create_chat_model
from app.schemas.common import SourceItem
from app.schemas.copy import (
    CopyGenerateRequest,
    CopyGenerateResponse,
    CopyLiteParsedInput,
    CopyLiteRequest,
    CopyLiteResponse,
    CopyStructuredOutput,
    Objective,
)
from app.schemas.web import LandingAnalyzeResponse
from app.services.rag_service import RagService
from app.services.web_search_service import WebSearchService


class CopyService:
    def __init__(self, settings: Settings, rag_service: RagService, web_search_service: WebSearchService) -> None:
        self._settings = settings
        self._web_search_service = web_search_service
        self._model = create_chat_model(settings)
        self._graph = CopyGenerationGraph(
            rag_service=rag_service,
            web_search_service=web_search_service,
            generator=self._run_chain_or_fallback,
        )
        self._lite_graph = CopyLiteGenerationGraph(
            parse_prompt=self._parse_prompt,
            build_landing_context=self._build_landing_render_context,
            infer_objective_from_prompt=self._infer_objective_from_prompt,
            infer_channel_from_prompt=self._infer_channel_from_prompt,
            infer_language_from_prompt=self._infer_language_from_prompt,
            generate_copy=self.generate,
        )

    @property
    def graph(self) -> CopyGenerationGraph:
        return self._graph

    @property
    def lite_graph(self) -> CopyLiteGenerationGraph:
        return self._lite_graph

    async def generate(
        self,
        request: CopyGenerateRequest,
        extra_context_blocks: list[str] | None = None,
        extra_sources: list[SourceItem] | None = None,
    ) -> CopyGenerateResponse:
        output, sources = await asyncio.to_thread(
            self._graph.run,
            request,
            extra_context_blocks,
            extra_sources,
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

    async def generate_prompt_mode(self, payload: CopyLiteRequest) -> CopyLiteResponse:
        return await self._lite_graph.run(payload)

    def _run_chain_or_fallback(self, request: CopyGenerateRequest, context: str) -> CopyStructuredOutput:
        if self._settings.should_mock or self._model is None:
            return self._mock_output(request, context)

        cleaned_context = self._sanitize_context(context, request.language)
        bounded_context = self._trim_context(cleaned_context, len(request.styles))

        primary = self._invoke_structured_chain(
            request=request,
            context=bounded_context,
            strict_mode=False,
            temperature=self._settings.copy_generation_temperature,
        )
        if primary is None:
            return self._mock_output(request, bounded_context)

        if not self._looks_corrupted_output(primary, request.language):
            return primary

        repaired = self._invoke_structured_chain(
            request=request,
            context=bounded_context,
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
                "max_tokens": self._resolve_generation_max_tokens(request),
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
                    "context": context or "(no context provided)",
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

    def _resolve_generation_max_tokens(self, request: CopyGenerateRequest) -> int:
        style_count = max(1, len(request.styles))
        lower = self._settings.copy_generation_min_tokens
        upper = self._settings.copy_generation_max_tokens
        dynamic = lower + style_count * self._settings.copy_generation_tokens_per_style
        return max(lower, min(upper, dynamic))

    def _trim_context(self, context: str, style_count: int) -> str:
        text = context.strip()
        if not text:
            return ""

        budget = min(
            self._settings.copy_context_max_chars,
            self._settings.copy_context_base_chars
            + max(1, style_count) * self._settings.copy_context_chars_per_style,
        )
        if len(text) <= budget:
            return text

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        kept: list[str] = []
        total = 0
        for line in lines:
            next_size = len(line) + 1
            if total + next_size > budget:
                break
            kept.append(line)
            total += next_size

        if kept:
            return "\n".join(kept)
        return text[:budget]

    def _build_copy_prompt(self, strict_mode: bool) -> ChatPromptTemplate:
        system_prompt = """
You are not a boilerplate copy bot. You are a performance copywriter who drives real user action.
Your goal is not "nice-looking sentences" but "copy that makes people act now".

[Non-Negotiable Rules]
1) Follow the output schema strictly. Do not add extra keys, explanations, or meta text.
2) Never fabricate numbers or facts that are not grounded in the provided evidence context.
3) Avoid vague buzzwords (best, innovative, premium, perfect). Replace them with concrete situations, benefits, and actions.
4) Build a clear persuasion flow: pain_point -> tension escalation -> differentiator relief -> action prompt.

[Creativity Rules]
- Internally test at least three angles (empathy, contrast, outcome), then output only the single most persuasive direction.
- Do not recycle cliches; refresh rhythm, diction, and phrasing.
- Include at least one realistic situation the reader can visualize.
- Differentiate the function and voice of each field (head/body/cta/slogan/sns/description).

[Objective Priorities]
- click: scroll-stopping hook + immediate reason to click
- add_to_cart: remove purchase friction + emphasize cost of delay
- consultation: trust/expertise + low-friction first step
- brand_memory: short, repeatable, memorable line

[Channel Optimization]
- Meta/Instagram: strong first line, short cadence, mobile readability
- Detail/Landing pages: persuasion structure of problem -> solution -> proof -> CTA
- Email/Messenger: personalized tone + explicit next step

[Output Quality Bar]
- head: one-line hook with immediate differentiation
- body: 3-10 sentences, flowing problem context -> solution -> proof -> action
- cta: start with a verb and include immediate gain for click/apply/add-to-cart
- slogan: short and memorable rhythm
- sns: compressed spreadable sentence with hook + proof + action
- description: channel-ready operator-friendly copy
- storyboard_outline: 5-7 steps, each step in format 'scene:key_message'
- rationale: clearly explain the persuasion logic used (psychological trigger / friction removal / evidence linkage)
        """.strip()

        if strict_mode:
            system_prompt += "\n\n" + """
[Text Stabilization Rules]
- Never output broken characters or mixed-script tokens that do not match the target language ({language}).
- Remove OCR-like noise strings (for example, abnormal tokens with mixed character sets or meaningless number-symbol chains) and rewrite them as natural language.
- For Korean/English outputs in particular, do not mix in Russian, Arabic, or other unrelated scripts.
            """.strip()

        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    """
[Input]
Product: {product_name}
Audience: {target_audience}
Problem: {pain_point}
Differentiator: {differentiator}
Tone: {tone}
Objective: {objective}
Styles: {styles}
Channel: {channel}
Language: {language}

[Evidence Context]
{context}

Requirements:
1) Avoid generic wording and write differentiated conversion-oriented copy.
2) Reflect realistic customer situations and emotions in the sentences.
3) Persuade with specificity over hype, and strongly drive the target action.
4) Reflect the characteristics of language ({language}) and channel ({channel}).
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
        h1_text = " | ".join(landing.h1[:5]) if landing.h1 else "(none)"
        h2_text = " | ".join(landing.h2[:8]) if landing.h2 else "(none)"
        cta_text = " | ".join(landing.cta_buttons[:12]) if landing.cta_buttons else "(none)"
        body_budget = max(800, min(3500, self._settings.copy_context_max_chars // 3))
        body_excerpt = (landing.body or "")[:body_budget]

        return "\n".join(
            [
                "[Rendered Landing Context]",
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

    async def _parse_prompt(self, prompt: str) -> tuple[CopyLiteParsedInput, list[str]]:
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
You are a marketing brief extraction assistant.
Extract the following fields from the user's free-form prompt:
- product_name
- target_audience
- pain_point
- differentiator
- tone

Rules:
1) If information is missing, do not return an empty string. Fill it with the safest generic phrasing.
2) Keep outputs concise and natural in the same language as the user's prompt.
3) Do not exaggerate or hallucinate; stay grounded in evidence from the input.
""".strip(),
                ),
                (
                    "human",
                    """
[User Prompt]
{prompt}
""".strip(),
                ),
            ]
        )

        try:
            structured_model = self._model.with_structured_output(CopyLiteParsedInput)
            parser_bind_kwargs: dict[str, float | int] = {
                "temperature": self._settings.copy_parser_temperature,
                "max_tokens": self._resolve_parser_max_tokens(prompt),
            }
            try:
                structured_model = structured_model.bind(**parser_bind_kwargs)
            except Exception:
                pass
            chain = prompt_template | structured_model
            result: object = await asyncio.to_thread(chain.invoke, {"prompt": prompt})

            if isinstance(result, CopyLiteParsedInput):
                parsed = result
            elif isinstance(result, dict):
                parsed = CopyLiteParsedInput.model_validate(result)
            else:
                model_dump = getattr(result, "model_dump", None)
                if callable(model_dump):
                    parsed = CopyLiteParsedInput.model_validate(model_dump())
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

    def _resolve_parser_max_tokens(self, prompt: str) -> int:
        base = 280
        bonus = min(520, max(0, len(prompt) // 12))
        resolved = base + bonus
        return max(280, min(self._settings.copy_parser_max_tokens, resolved))

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

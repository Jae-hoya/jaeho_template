import asyncio

from app.flows.copy_lite_generation_graph import CopyLiteGenerationGraph
from app.schemas.common import SourceItem
from app.schemas.copy import (
    CopyGenerateRequest,
    CopyGenerateResponse,
    CopyLiteParsedInput,
    CopyLiteRequest,
    Objective,
    Style,
)


def test_copy_lite_graph_applies_landing_context_defaults() -> None:
    captured: dict[str, object] = {}

    def parse_prompt(_: str) -> tuple[CopyLiteParsedInput, list[str]]:
        return (
            CopyLiteParsedInput(
                product_name="Copyjoe",
                target_audience="마케터",
                pain_point="클릭률이 낮다",
                differentiator="근거 기반 생성",
                tone="신뢰형",
            ),
            ["parsed by dummy"],
        )

    async def build_landing_context(_: CopyLiteRequest) -> tuple[str | None, SourceItem | None, str | None]:
        return (
            "[렌더링 랜딩 컨텍스트]",
            SourceItem(source_type="web", title="landing", url="https://example.com", snippet="landing snippet"),
            "landing context added",
        )

    def infer_objective(_: str) -> Objective | None:
        return None

    def infer_channel(_: str) -> str | None:
        return None

    def infer_language(_: str) -> str | None:
        return None

    async def generate_copy(
        request: CopyGenerateRequest,
        extra_context_blocks: list[str] | None = None,
        extra_sources: list[SourceItem] | None = None,
    ) -> CopyGenerateResponse:
        captured["request"] = request
        captured["extra_context_blocks"] = list(extra_context_blocks or [])
        captured["extra_sources"] = list(extra_sources or [])
        return CopyGenerateResponse(
            head="h",
            body="b",
            cta="c",
            slogan="s",
            sns="n",
            description="d",
            storyboard_outline=["1", "2", "3", "4"],
            rationale="ok",
            sources=list(extra_sources or []),
        )

    graph = CopyLiteGenerationGraph(
        parse_prompt=parse_prompt,
        build_landing_context=build_landing_context,
        infer_objective_from_prompt=infer_objective,
        infer_channel_from_prompt=infer_channel,
        infer_language_from_prompt=infer_language,
        generate_copy=generate_copy,
    )

    payload = CopyLiteRequest(
        prompt="테스트 프롬프트",
        styles=[Style.head, Style.cta],
        landing_url="https://example.com",
    )

    response = asyncio.run(graph.run(payload))

    assert response.normalized_request.objective == Objective.click
    assert response.normalized_request.channel == "랜딩페이지"
    assert response.normalized_request.language == "ko"
    assert response.result.sources[0].url == "https://example.com"
    assert "렌더링 랜딩 컨텍스트" in response.assistant_message
    assert "objective 미입력: click으로 자동 설정" in response.assumptions
    assert "channel 미입력: 렌더링 랜딩 기반으로 랜딩페이지로 자동 설정" in response.assumptions
    assert "language 미입력: ko로 자동 설정" in response.assumptions

    captured_context = captured.get("extra_context_blocks")
    captured_sources = captured.get("extra_sources")
    assert isinstance(captured_context, list)
    assert isinstance(captured_sources, list)
    assert "[렌더링 랜딩 컨텍스트]" in captured_context
    assert len(captured_sources) == 1


def test_copy_lite_graph_generates_normalized_request() -> None:
    async def run_case() -> None:
        def parse_prompt(_: str) -> tuple[CopyLiteParsedInput, list[str]]:
            return (
                CopyLiteParsedInput(
                    product_name="Copyjoe",
                    target_audience="마케터",
                    pain_point="클릭률이 낮다",
                    differentiator="근거 기반 생성",
                    tone="신뢰형",
                ),
                [],
            )

        async def build_landing_context(_: CopyLiteRequest) -> tuple[str | None, SourceItem | None, str | None]:
            return (None, None, None)

        def infer_objective(_: str) -> Objective | None:
            return Objective.consultation

        def infer_channel(_: str) -> str | None:
            return "메타 광고 랜딩"

        def infer_language(_: str) -> str | None:
            return "en"

        async def generate_copy(
            request: CopyGenerateRequest,
            extra_context_blocks: list[str] | None = None,
            extra_sources: list[SourceItem] | None = None,
        ) -> CopyGenerateResponse:
            _ = (extra_context_blocks, extra_sources)
            return CopyGenerateResponse(
                head=f"{request.objective.value}-{request.channel}-{request.language}",
                body="b",
                cta="c",
                slogan="s",
                sns="n",
                description="d",
                storyboard_outline=["1", "2", "3", "4"],
                rationale="ok",
                sources=[],
            )

        graph = CopyLiteGenerationGraph(
            parse_prompt=parse_prompt,
            build_landing_context=build_landing_context,
            infer_objective_from_prompt=infer_objective,
            infer_channel_from_prompt=infer_channel,
            infer_language_from_prompt=infer_language,
            generate_copy=generate_copy,
        )

        payload = CopyLiteRequest(
            prompt="상담 전환이 필요해",
            styles=[Style.head, Style.body, Style.cta],
        )

        response = await graph.run(payload)
        assert response.normalized_request.objective == Objective.consultation
        assert response.normalized_request.channel == "메타 광고 랜딩"
        assert response.normalized_request.language == "en"
        assert response.result.head == "consultation-메타 광고 랜딩-en"

    asyncio.run(run_case())


def test_copy_lite_graph_refine_feedback_can_override_explicit_language() -> None:
    async def run_case() -> None:
        def parse_prompt(_: str) -> tuple[CopyLiteParsedInput, list[str]]:
            return (
                CopyLiteParsedInput(
                    product_name="Copyjoe",
                    target_audience="마케터",
                    pain_point="클릭률이 낮다",
                    differentiator="근거 기반 생성",
                    tone="신뢰형",
                ),
                [],
            )

        async def build_landing_context(_: CopyLiteRequest) -> tuple[str | None, SourceItem | None, str | None]:
            return (None, None, None)

        def infer_objective(_: str) -> Objective | None:
            return Objective.click

        def infer_channel(_: str) -> str | None:
            return "상세페이지"

        def infer_language(prompt: str) -> str | None:
            return "en" if "[사용자 피드백]" in prompt and "영어" in prompt else None

        async def generate_copy(
            request: CopyGenerateRequest,
            extra_context_blocks: list[str] | None = None,
            extra_sources: list[SourceItem] | None = None,
        ) -> CopyGenerateResponse:
            _ = (extra_context_blocks, extra_sources)
            return CopyGenerateResponse(
                head=request.language,
                body="b",
                cta="c",
                slogan="s",
                sns="n",
                description="d",
                storyboard_outline=["1", "2", "3", "4"],
                rationale="ok",
                sources=[],
            )

        graph = CopyLiteGenerationGraph(
            parse_prompt=parse_prompt,
            build_landing_context=build_landing_context,
            infer_objective_from_prompt=infer_objective,
            infer_channel_from_prompt=infer_channel,
            infer_language_from_prompt=infer_language,
            generate_copy=generate_copy,
        )

        payload = CopyLiteRequest(
            prompt="""아래 기존 카피를 개선해줘\n\n[사용자 피드백]\n영어로 바꿔줘""",
            styles=[Style.head, Style.body, Style.cta],
            language="ko",
        )

        response = await graph.run(payload)
        assert response.normalized_request.language == "en"
        assert "language 변경 요청 감지: 'ko' -> 'en'" in response.assumptions

    asyncio.run(run_case())

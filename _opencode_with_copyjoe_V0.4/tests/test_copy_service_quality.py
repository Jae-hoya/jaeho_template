from typing import Any

from app.core.config import Settings
from app.schemas.copy import CopyGenerateRequest, CopyStructuredOutput, Objective, Style
from app.services.copy_service import CopyService


class DummyRagService:
    def build_context(self, query: str, top_k: int, document_ids: list[str] | None = None) -> tuple[str, list[Any]]:
        _ = (query, top_k, document_ids)
        return "", []


class DummyWebSearchService:
    def search(self, query: str, max_results: int, strict: bool = True) -> list[Any]:
        _ = (query, max_results, strict)
        return []


def _build_service() -> CopyService:
    settings = Settings(force_mock_mode=True)
    return CopyService(settings=settings, rag_service=DummyRagService(), web_search_service=DummyWebSearchService())


def test_mixed_script_token_detection() -> None:
    service = _build_service()
    assert service._is_mixed_script_token("начис흡맞") is True
    assert service._is_mixed_script_token("전환율") is False


def test_context_sanitizer_drops_cyrillic_noise_for_korean() -> None:
    service = _build_service()
    context = "정상 문장\n메일 начис흡맞 등 추 속의 0.8% 클릭 열쇠\n근거 기반 카피"
    cleaned = service._sanitize_context(context, "ko")
    assert "начис" not in cleaned
    assert "정상 문장" in cleaned
    assert "근거 기반 카피" in cleaned


def test_stabilize_output_removes_mixed_script_noise_token() -> None:
    service = _build_service()
    output = CopyStructuredOutput(
        head="메일 начис흡맞 등 추 속의 0.8% 클릭 열쇠",
        body="정상 문장입니다",
        cta="지금 확인",
        slogan="테스트",
        sns="테스트",
        description="테스트",
        storyboard_outline=["장면1: 정상"],
        rationale="근거",
    )

    stabilized = service._stabilize_output_text(output, "ko")
    assert "начис" not in stabilized.head


def test_corrupted_output_detector_flags_cyrillic_mixture() -> None:
    service = _build_service()
    output = CopyStructuredOutput(
        head="메일 начис흡맞 등 추 속의 0.8% 클릭 열쇠",
        body="정상 문장입니다",
        cta="지금 확인",
        slogan="테스트",
        sns="테스트",
        description="테스트",
        storyboard_outline=["장면1: 정상"],
        rationale="근거",
    )

    assert service._looks_corrupted_output(output, "ko") is True


def test_copy_service_still_returns_output_with_mock_mode() -> None:
    service = _build_service()
    request = CopyGenerateRequest(
        product_name="Copyjoe",
        target_audience="마케터",
        pain_point="카피 품질 불안정",
        differentiator="근거 기반 생성",
        tone="신뢰형",
        objective=Objective.click,
        styles=[Style.head, Style.body, Style.cta],
        channel="상세페이지",
        language="ko",
        web_search_mode=False,
        use_rag=False,
        top_k=5,
    )

    generated = service._run_chain_or_fallback(request, "")
    assert isinstance(generated, CopyStructuredOutput)
    assert generated.head != ""


def test_generation_token_budget_scales_with_style_count() -> None:
    service = _build_service()
    base_kwargs = {
        "product_name": "Copyjoe",
        "target_audience": "마케터",
        "pain_point": "카피 품질 불안정",
        "differentiator": "근거 기반 생성",
        "tone": "신뢰형",
        "objective": Objective.click,
        "channel": "상세페이지",
        "language": "ko",
        "web_search_mode": False,
        "use_rag": False,
        "top_k": 5,
    }
    request_small = CopyGenerateRequest(styles=[Style.head, Style.cta], **base_kwargs)
    request_large = CopyGenerateRequest(styles=list(Style), **base_kwargs)

    small_budget = service._resolve_generation_max_tokens(request_small)
    large_budget = service._resolve_generation_max_tokens(request_large)

    assert small_budget < large_budget
    assert large_budget <= service._settings.copy_generation_max_tokens


def test_trim_context_enforces_budget() -> None:
    service = _build_service()
    context = "\n".join([f"line-{index} " + ("x" * 120) for index in range(0, 500)])
    trimmed = service._trim_context(context, style_count=2)
    expected_budget = min(
        service._settings.copy_context_max_chars,
        service._settings.copy_context_base_chars + 2 * service._settings.copy_context_chars_per_style,
    )
    assert len(trimmed) <= expected_budget

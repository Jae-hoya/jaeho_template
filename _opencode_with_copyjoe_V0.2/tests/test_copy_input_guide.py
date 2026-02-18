import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.copy import CopyGenerateRequest, Objective, Style


def _base_request(**overrides):
    payload = {
        "product_name": "Copyjoe",
        "target_audience": "퍼포먼스 마케터",
        "pain_point": "카피 작성 속도가 느리다",
        "differentiator": "RAG 기반 생성",
        "tone": "신뢰형",
        "objective": Objective.click,
        "styles": [Style.head, Style.body, Style.cta],
        "channel": "상세페이지",
        "language": "ko",
        "web_search_mode": False,
        "use_rag": True,
        "top_k": 5,
    }
    payload.update(overrides)
    return payload


def test_language_alias_is_normalized() -> None:
    req = CopyGenerateRequest(**_base_request(language="english"))
    assert req.language == "en"

    req2 = CopyGenerateRequest(**_base_request(language="pt-br"))
    assert req2.language == "pt-BR"

    req3 = CopyGenerateRequest(**_base_request(language="englsh"))
    assert req3.language == "en"


def test_unsupported_language_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        CopyGenerateRequest(**_base_request(language="xx"))


def test_meta_copy_form_guide_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/meta/copy-form-guide")

    assert response.status_code == 200
    body = response.json()
    assert "fields" in body
    assert "objectives" in body
    assert "language_options" in body
    assert any(item["code"] == "ko" for item in body["language_options"])
    field_keys = {item["key"] for item in body["fields"]}
    assert {"pain_point", "differentiator", "objective", "channel", "language", "top_k"}.issubset(field_keys)

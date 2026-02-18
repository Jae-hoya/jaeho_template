from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_docs_and_openapi() -> None:
    docs_res = client.get("/docs")
    openapi_res = client.get("/openapi.json")

    assert docs_res.status_code == 200
    assert openapi_res.status_code == 200
    schema = openapi_res.json()
    assert "/api/v1/copy/generate" in schema["paths"]
    assert "/api/v1/copy/generate-lite" in schema["paths"]
    assert "/api/v1/history/threads" in schema["paths"]
    assert "/api/v1/export/md" in schema["paths"]
    assert "/api/v1/export/doc" in schema["paths"]
    assert "/api/v1/meta/copy-form-guide" in schema["paths"]
    assert "/health" in schema["paths"]


def test_copy_generate() -> None:
    payload = {
        "product_name": "Copyjoe",
        "target_audience": "퍼포먼스 마케터",
        "pain_point": "카피 작성에 시간이 오래 걸린다",
        "differentiator": "RAG와 웹 검색 기반 생성",
        "tone": "신뢰형",
        "objective": "click",
        "styles": ["head", "body", "cta", "slogan", "sns", "description"],
        "channel": "상세페이지",
        "language": "ko",
        "web_search_mode": False,
        "use_rag": False,
        "top_k": 5,
    }

    response = client.post("/api/v1/copy/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    for key in ["head", "body", "cta", "slogan", "sns", "description", "rationale", "storyboard_outline", "sources"]:
        assert key in body


def test_copy_generate_lite() -> None:
    payload = {
        "prompt": "광고 클릭률이 떨어져서 근거 중심 카피를 빠르게 만들고 싶다",
        "styles": ["head", "cta", "sns"],
        "language": "english",
    }

    response = client.post("/api/v1/copy/generate-lite", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "assistant_message" in body
    assert "assumptions" in body
    assert "normalized_request" in body
    assert body["normalized_request"]["language"] == "en"
    assert "result" in body

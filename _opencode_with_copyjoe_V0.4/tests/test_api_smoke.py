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
    assert "/api/v1/rag/reset" in schema["paths"]
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


def test_copy_generate_prompt_mode() -> None:
    payload = {
        "prompt": "광고 클릭률이 떨어져서 근거 중심 카피를 빠르게 만들고 싶다",
        "styles": ["head", "cta", "sns"],
        "language": "english",
    }

    response = client.post("/api/v1/copy/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "assistant_message" in body
    assert "assumptions" in body
    assert "normalized_request" in body
    assert body["normalized_request"]["language"] == "en"
    assert "result" in body


def test_rag_reset() -> None:
    response = client.post("/api/v1/rag/reset")
    assert response.status_code == 200
    body = response.json()
    assert "backend" in body
    assert "cleared_documents" in body
    assert "cleared_vectors" in body


def test_copy_generate_prompt_mode_with_rag_document_ids_filter() -> None:
    reset_response = client.post("/api/v1/rag/reset")
    assert reset_response.status_code == 200

    files = [
        ("files", ("source_a.txt", b"FILTER_TOKEN_ALPHA uploaded source for precise rag grounding", "text/plain")),
        ("files", ("source_b.txt", b"FILTER_TOKEN_BETA unrelated source for exclusion check", "text/plain")),
    ]
    upload_response = client.post("/api/v1/files/upload", files=files)
    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    assert upload_body["success_count"] == 2

    rows = upload_body["files"]
    source_a_row = next(item for item in rows if item["file_name"] == "source_a.txt")
    source_b_row = next(item for item in rows if item["file_name"] == "source_b.txt")

    index_response = client.post(
        "/api/v1/rag/index",
        json={
            "document_ids": [source_a_row["document_id"], source_b_row["document_id"]],
            "chunk_size": 400,
            "chunk_overlap": 40,
        },
    )
    assert index_response.status_code == 200

    generate_response = client.post(
        "/api/v1/copy/generate",
        json={
            "prompt": "FILTER_TOKEN_ALPHA를 근거로 클릭형 카피를 생성해줘",
            "styles": ["head", "body", "cta"],
            "use_rag": True,
            "web_search_mode": False,
            "top_k": 5,
            "rag_document_ids": [source_a_row["document_id"]],
        },
    )
    assert generate_response.status_code == 200

    generate_body = generate_response.json()
    sources = generate_body["result"]["sources"]
    rag_titles = [item.get("title") for item in sources if item.get("source_type") == "rag"]
    assert "source_a.txt" in rag_titles
    assert "source_b.txt" not in rag_titles

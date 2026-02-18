from fastapi.testclient import TestClient

from app.main import app


def _sample_result() -> dict:
    return {
        "head": "h",
        "body": "b",
        "cta": "c",
        "slogan": "s",
        "sns": "n",
        "description": "d",
        "storyboard_outline": ["1", "2", "3", "4"],
        "rationale": "r",
        "sources": [],
    }


def test_history_thread_lifecycle() -> None:
    client = TestClient(app)

    created = client.post("/api/v1/history/threads", json={"title": "test-thread"})
    assert created.status_code == 200
    thread_id = created.json()["thread_id"]

    posted = client.post(
        f"/api/v1/history/threads/{thread_id}/messages",
        json={"role": "user", "content": "hello", "metadata": {"source": "test"}},
    )
    assert posted.status_code == 200

    listed = client.get("/api/v1/history/threads")
    assert listed.status_code == 200
    assert any(item["thread_id"] == thread_id for item in listed.json())

    detail = client.get(f"/api/v1/history/threads/{thread_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["thread"]["thread_id"] == thread_id
    assert len(body["messages"]) == 1


def test_export_markdown_and_doc() -> None:
    client = TestClient(app)

    payload_md = {"file_name": "copyjoe_test.md", "result": _sample_result()}
    response_md = client.post("/api/v1/export/md", json=payload_md)
    assert response_md.status_code == 200
    assert "text/markdown" in response_md.headers.get("content-type", "")
    assert len(response_md.content) > 20

    payload_doc = {"file_name": "copyjoe_test.doc", "result": _sample_result()}
    response_doc = client.post("/api/v1/export/doc", json=payload_doc)
    assert response_doc.status_code == 200
    assert "application/msword" in response_doc.headers.get("content-type", "")
    assert len(response_doc.content) > 20

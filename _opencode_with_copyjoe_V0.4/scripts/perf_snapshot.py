import json
import statistics
import time
from typing import Any

from fastapi.testclient import TestClient

from app.main import app


def _measure(client: TestClient, path: str, payload: dict[str, Any], runs: int = 6, warmups: int = 1) -> dict[str, Any]:
    status_codes: list[int] = []
    durations_ms: list[float] = []

    for _ in range(warmups):
        response = client.post(path, json=payload)
        status_codes.append(response.status_code)

    for _ in range(runs):
        started = time.perf_counter()
        response = client.post(path, json=payload)
        elapsed_ms = (time.perf_counter() - started) * 1000
        status_codes.append(response.status_code)
        durations_ms.append(elapsed_ms)

    return {
        "path": path,
        "runs": runs,
        "status_codes": status_codes,
        "mean_ms": round(statistics.mean(durations_ms), 2),
        "p50_ms": round(statistics.median(durations_ms), 2),
        "p95_ms": round(_percentile(durations_ms, 95), 2),
        "min_ms": round(min(durations_ms), 2),
        "max_ms": round(max(durations_ms), 2),
    }


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * (percentile / 100)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _build_refine_prompt(result_payload: dict[str, Any], feedback: str) -> str:
    body = str(result_payload.get("body", ""))
    if len(body) > 600:
        body = body[:600] + "..."

    return "\n".join(
        [
            "Improve the copy while preserving structure.",
            "Apply feedback with higher persuasion and clarity.",
            "",
            f"[head] {result_payload.get('head', '')}",
            f"[body] {body}",
            f"[cta] {result_payload.get('cta', '')}",
            f"[slogan] {result_payload.get('slogan', '')}",
            f"[sns] {result_payload.get('sns', '')}",
            f"[description] {result_payload.get('description', '')}",
            "",
            "[feedback]",
            feedback,
        ]
    )


def main() -> int:
    client = TestClient(app)

    base_payload: dict[str, Any] = {
        "prompt": "CTR dropped and we need stronger conversion copy for SaaS landing.",
        "styles": ["head", "body", "cta", "slogan", "sns", "description"],
        "web_search_mode": False,
        "use_rag": False,
        "top_k": 5,
    }

    generate_metrics = _measure(client, "/api/v1/copy/generate", base_payload, runs=6, warmups=1)

    first_response = client.post("/api/v1/copy/generate", json=base_payload)
    first_body = first_response.json() if first_response.status_code == 200 else {}
    normalized_request = first_body.get("normalized_request", {})
    result_payload = first_body.get("result", {})
    refine_prompt = _build_refine_prompt(result_payload, "Make CTA more urgent and body more concrete.")

    refine_without_base = {
        "prompt": refine_prompt,
        "styles": normalized_request.get("styles") or base_payload["styles"],
        "language": normalized_request.get("language", "en"),
        "objective": normalized_request.get("objective", "click"),
        "channel": normalized_request.get("channel", "landing page"),
        "web_search_mode": normalized_request.get("web_search_mode", False),
        "use_rag": normalized_request.get("use_rag", False),
        "top_k": normalized_request.get("top_k", 5),
    }
    refine_with_base = {
        **refine_without_base,
        "base_request": normalized_request,
    }

    refine_without_metrics = _measure(client, "/api/v1/copy/generate", refine_without_base, runs=6, warmups=1)
    refine_with_metrics = _measure(client, "/api/v1/copy/generate", refine_with_base, runs=6, warmups=1)

    landing_result: dict[str, Any]
    try:
        landing_payload = {"url": "https://example.com"}

        started = time.perf_counter()
        first_landing = client.post("/api/v1/web/landing/analyze", json=landing_payload)
        first_ms = (time.perf_counter() - started) * 1000

        started = time.perf_counter()
        second_landing = client.post("/api/v1/web/landing/analyze", json=landing_payload)
        second_ms = (time.perf_counter() - started) * 1000

        landing_result = {
            "first_status": first_landing.status_code,
            "second_status": second_landing.status_code,
            "first_ms": round(first_ms, 2),
            "second_ms": round(second_ms, 2),
            "cache_speedup_ratio": round(first_ms / second_ms, 2) if second_ms > 0 else None,
        }
    except Exception as exc:
        landing_result = {"error": str(exc)}

    report = {
        "generate_prompt_mode": generate_metrics,
        "refine_without_base_request": refine_without_metrics,
        "refine_with_base_request": refine_with_metrics,
        "landing_repeat_url": landing_result,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

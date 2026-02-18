import argparse
import json
import shlex
from dataclasses import dataclass, field
from typing import Any

import requests


DEFAULT_PAYLOAD: dict[str, Any] = {
    "product_name": "Copyjoe",
    "target_audience": "퍼포먼스 마케터",
    "pain_point": "카피 작성 속도가 느리다",
    "differentiator": "RAG + Tavily 기반 근거 중심 생성",
    "tone": "신뢰형",
    "objective": "click",
    "styles": ["head", "body", "cta", "slogan", "sns", "description"],
    "channel": "상세페이지",
    "language": "ko",
    "web_search_mode": False,
    "use_rag": True,
    "top_k": 5,
}


@dataclass
class ChatState:
    base_url: str
    payload: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_PAYLOAD))
    turns: list[tuple[str, str]] = field(default_factory=list)


def parse_user_command(raw: str) -> tuple[str, list[str]]:
    text = raw.strip()
    if not text:
        return "", []

    if text.startswith("/"):
        parts = shlex.split(text[1:])
        if not parts:
            return "", []
        return parts[0].lower(), parts[1:]

    return "say", [text]


def apply_local_command(state: ChatState, command: str, args: list[str]) -> str:
    if command == "help":
        return (
            "명령어: /show, /set <field> <value>, /toggle <use_rag|web_search_mode>, "
            "/style <add|remove> <style>, /generate, /landing-url <url>, /landing-query <query>, /health, /quit"
        )

    if command == "show":
        return json.dumps(state.payload, ensure_ascii=False, indent=2)

    if command == "set" and len(args) >= 2:
        key = args[0]
        value = " ".join(args[1:])
        if key in {"top_k"}:
            state.payload[key] = int(value)
        elif key in {"web_search_mode", "use_rag"}:
            state.payload[key] = value.lower() in {"1", "true", "on", "yes"}
        else:
            state.payload[key] = value
        return f"updated: {key}={state.payload[key]}"

    if command == "toggle" and len(args) == 1:
        key = args[0]
        if key not in {"web_search_mode", "use_rag"}:
            return "toggle 대상은 use_rag 또는 web_search_mode만 가능합니다."
        state.payload[key] = not bool(state.payload[key])
        return f"updated: {key}={state.payload[key]}"

    if command == "style" and len(args) == 2:
        action, style = args[0], args[1]
        styles = list(state.payload.get("styles", []))
        if action == "add" and style not in styles:
            styles.append(style)
        if action == "remove" and style in styles:
            styles.remove(style)
        state.payload["styles"] = styles
        return f"updated styles={styles}"

    if command == "say" and args:
        state.payload["pain_point"] = args[0]
        return f"pain_point 업데이트: {args[0]}"

    return "지원하지 않는 명령입니다. /help 를 입력하세요."


def call_copy_generate(state: ChatState) -> str:
    response = requests.post(
        f"{state.base_url}/api/v1/copy/generate",
        json=state.payload,
        timeout=180,
    )
    response.raise_for_status()
    body = response.json()
    return (
        "\n".join(
            [
                f"head: {body.get('head', '')}",
                f"cta: {body.get('cta', '')}",
                f"rationale: {body.get('rationale', '')}",
                f"sources: {len(body.get('sources', []))}",
            ]
        )
        + "\n"
    )


def call_landing_analyze(state: ChatState, payload: dict[str, Any]) -> str:
    response = requests.post(
        f"{state.base_url}/api/v1/web/landing/analyze",
        json=payload,
        timeout=180,
    )
    response.raise_for_status()
    body = response.json()
    summary = {
        "url": body.get("url"),
        "h1": body.get("h1", []),
        "h2_count": len(body.get("h2", [])),
        "cta_count": len(body.get("cta_buttons", [])),
        "body_preview": str(body.get("body", ""))[:300],
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


def run_repl(base_url: str) -> None:
    state = ChatState(base_url=base_url.rstrip("/"))
    print("Copyjoe Interactive Chat 시작. /help 입력으로 명령어 확인")

    while True:
        raw = input("you> ").strip()
        command, args = parse_user_command(raw)
        if not command:
            continue

        if command in {"quit", "exit"}:
            print("종료합니다.")
            break

        try:
            if command == "generate":
                reply = call_copy_generate(state)
            elif command == "landing-url" and args:
                reply = call_landing_analyze(state, {"url": args[0]})
            elif command == "landing-query" and args:
                reply = call_landing_analyze(state, {"query": " ".join(args), "max_results": 5})
            elif command == "health":
                response = requests.get(f"{state.base_url}/health", timeout=20)
                response.raise_for_status()
                reply = json.dumps(response.json(), ensure_ascii=False, indent=2)
            else:
                reply = apply_local_command(state, command, args)
        except Exception as exc:
            reply = f"error: {exc}"

        state.turns.append(("user", raw))
        state.turns.append(("assistant", reply))
        print(f"assistant> {reply}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive Copyjoe CLI")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    run_repl(args.base_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

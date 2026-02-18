import argparse
import os
import subprocess
import sys
import time

import requests


def wait_ready(base_url: str, timeout_sec: int = 45) -> None:
    started = time.time()
    while time.time() - started < timeout_sec:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.7)
    raise RuntimeError("server startup timeout")


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute quality-check Jupyter notebook")
    parser.add_argument("--provider", choices=["openai", "ollama"], default="openai")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ollama-model", default="qwen3:8b")
    parser.add_argument(
        "--output",
        default="notebooks/langchain_quality_checks.executed.ipynb",
        help="Executed notebook output path",
    )
    parser.add_argument(
        "--notebook",
        default="notebooks/langchain_quality_checks.ipynb",
        help="Notebook path to execute",
    )
    args = parser.parse_args()

    env = os.environ.copy()
    env["LLM_PROVIDER"] = args.provider
    env["FORCE_MOCK_MODE"] = "false"
    if args.provider == "ollama":
        env["OLLAMA_CHAT_MODEL"] = args.ollama_model

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(args.port)],
        env=env,
    )

    try:
        base_url = f"http://127.0.0.1:{args.port}"
        wait_ready(base_url)

        runner_env = os.environ.copy()
        runner_env["COPYJOE_BASE_URL"] = base_url

        command = [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--output",
            args.output,
            args.notebook,
        ]

        completed = subprocess.run(command, env=runner_env, check=False)
        return completed.returncode
    finally:
        server.terminate()
        try:
            server.wait(timeout=15)
        except Exception:
            server.kill()


if __name__ == "__main__":
    raise SystemExit(main())

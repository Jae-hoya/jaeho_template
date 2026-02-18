# AGENTS.md

This file defines contributor guidance for work centered on:

- `_opencode_with_copyjoe` (FastAPI + LangChain/LangGraph + Vue)

If your task is outside that folder, treat this document as a baseline and adapt to the target project.

## 1) Project Scope and Layout

- Backend entrypoint: `app/main.py`
- API routes: `app/api/v1/*.py`
- Services/business logic: `app/services/*.py`
- Flow orchestration: `app/flows/copy_generation_graph.py`
- Model/provider integration: `app/integrations/model_factory.py`
- Config single source: `app/core/config.py`
- Frontend app: `frontend/src/**`
- Tests: `tests/**`
- Validation scripts: `scripts/run_full_checks.py`, `scripts/execute_notebook_checks.py`

## 2) Environment and Setup

Use Python virtualenv and npm in `frontend`.

Backend setup:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

Frontend setup:

```bash
cd frontend
npm install
```

## 3) Run Commands

Backend dev server:

```bash
python -m uvicorn app.main:app --reload
```

Frontend dev server:

```bash
cd frontend
npm run dev
```

Runtime validation endpoints:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

## 4) Build, Lint, Test

### Build

Frontend production build (includes TS check via `vue-tsc`):

```bash
cd frontend
npm run build
```

### Lint / Static Checks

There is currently no dedicated repo-wide lint command configured (no ESLint/Ruff config in this project folder).

Use these practical checks instead:

- Frontend type/static gate: `npm run build`
- Backend/API sanity: `python -m pytest -q`

If you introduce a new linter, document command updates in this file.

### Tests

Run full test suite:

```bash
python -m pytest -q
```

Run a single test file:

```bash
python -m pytest -q tests/test_api_smoke.py
```

Run a single test case:

```bash
python -m pytest -q tests/test_api_smoke.py::test_health
```

Run by keyword:

```bash
python -m pytest -q -k history
```

## 5) Full-System Verification

OpenAI mode:

```bash
python scripts/run_full_checks.py --provider openai --port 8012
```

Ollama mode (8b):

```bash
python scripts/run_full_checks.py --provider ollama --ollama-model qwen3:8b --port 8013
```

Notebook execution checks:

```bash
python scripts/execute_notebook_checks.py --provider openai --port 8014 --notebook notebooks/langchain_quality_checks.ipynb --output langchain_quality_checks.executed.ipynb
python scripts/execute_notebook_checks.py --provider ollama --ollama-model qwen3:8b --port 8015 --notebook notebooks/interactive_chat_test.ipynb --output interactive_chat_test.executed.ipynb
```

## 6) Coding Guidelines

### Python (FastAPI/LangChain)

- Keep route handlers thin; put business logic in `app/services`.
- Keep model/provider creation centralized; avoid scattered hardcoded model settings.
- Preserve `app/core/config.py` as the single source for generation/parser tuning constants.
- Favor explicit Pydantic schemas for API I/O.
- Add or update tests for behavioral/API changes.

### Frontend (Vue)

- Keep components focused; avoid mixing prompt-input and generation-render logic unnecessarily.
- Follow existing section/component split under `frontend/src/copyjoe`.
- Ensure loading/disabled states prevent duplicate submissions.
- Keep field-level validation feedback clear, especially for 422 responses.

### General

- Prefer minimal, targeted changes over wide refactors.
- Avoid adding comments unless a block is non-obvious.
- Keep naming consistent with existing modules and API terms.

## 7) API and Data Contract Rules

- Maintain backward compatibility for existing endpoints unless the task explicitly requires a breaking change.
- If request/response schema changes, update:
  - `app/schemas/*`
  - relevant service/route
  - tests
  - README docs where applicable
- Keep language normalization and validation behavior aligned across backend and frontend messaging.

## 8) Git and Change Hygiene

- Do not revert unrelated local changes.
- Keep commits scoped and descriptive when asked to commit.
- Do not use destructive git commands unless explicitly requested.
- Do not commit secrets or credentials.

## 9) Cursor/Copilot Rules Check

Within `_opencode_with_copyjoe`:

- No `.cursor/rules` files found.
- No `.github/copilot-instructions.md` found.

If these files are later added, mirror key constraints in this document.

## 10) Quick PR/Review Checklist

- App boots and `/health` returns OK.
- OpenAPI docs load at `/docs` and `/openapi.json`.
- `python -m pytest -q` passes.
- `cd frontend && npm run build` passes.
- Changed behavior is documented in README if user-facing.

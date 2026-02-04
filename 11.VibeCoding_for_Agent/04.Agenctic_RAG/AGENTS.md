# AGENTS.md

## Purpose
This repository implements a hybrid search CLI for loan products using ParadeDB (BM25) and pgvector. This file guides agentic tools for safe edits, consistent style, and correct commands.

## Quick Context
- Language: Python 3.10+
- DB: ParadeDB (PostgreSQL + pg_search + pgvector)
- Embeddings: OpenAI `text-embedding-3-small`
- Entry point: `python -m search_app.main "<query>"`
- DB setup: `python -m search_app.setup`
- Env file: `C:\Users\skyop\jaeho_template\.env`
- BM25 mode switch: `BM25_MODE=paradedb` (default) or `BM25_MODE=fts`

## Build / Install
There is no separate build step. Install dependencies with pip.

```bash
# From this folder
pip install psycopg python-dotenv openai numpy
```

If using the provided Windows venv:

```bash
C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m pip install psycopg python-dotenv openai numpy
```

## Run Commands
```bash
# Run CLI search
python -m search_app.main "의사 전용 대출"

# Initialize DB and load data
python -m search_app.setup
```

## Test Commands
- Pytest is the expected runner, but there are currently no test files.

```bash
# Run all tests (if any exist)
python -m pytest

# Run a single test by name
python -m pytest -k "test_name"

# Run a single test file
python -m pytest tests/test_some_module.py
```

## Lint / Format
- No lint or formatter is configured in this repo.
- Do not assume ruff/black/isort unless added explicitly.
- Keep formatting consistent with existing files (4-space indents, PEP8-ish).

## Project Layout
- `search_app/config.py`: env/config loading, constants
- `search_app/database.py`: connection, extensions, indexes
- `search_app/data_loader.py`: JSON loading, text cleaning, embeddings
- `search_app/hybrid_search.py`: BM25 + vector + RRF logic
- `search_app/setup.py`: database initialization and data load
- `search_app/main.py`: CLI entry

## Code Style Guidelines

### Imports
- Order: standard library, third-party, local imports.
- Use explicit imports rather than star imports.

### Formatting
- 4 spaces per indent, no tabs.
- Use double quotes for strings (existing code uses them consistently).
- Keep line length reasonable (~88-100 chars).

### Types
- Use type hints for public functions when practical (existing code uses typing in core modules).
- Prefer `List`, `Dict`, `Tuple` from `typing` for Python 3.10 compatibility with existing style.

### Naming
- snake_case for functions and variables.
- PascalCase for classes.
- UPPER_SNAKE_CASE for constants in `Config`.

### Error Handling
- Use try/except around DB connection and setup (see `Database.connect`, `setup.py`).
- When exceptions occur, log a clear message and re-raise or `sys.exit(1)` in CLI.
- Avoid silent failures; if you must fall back, log the reason (see BM25 index fallback).

### SQL Usage
- Always parameterize SQL with `%s` placeholders.
- Avoid string concatenation for user input.
- Keep queries formatted with triple-quoted strings for readability.

### Search Logic
- BM25 is selected via `Config.BM25_MODE`.
- Vector search uses cosine distance on `searchable_text_embedding`.
- Hybrid uses RRF with `Config.RRF_K`.

### Data Loading
- `DataLoader.clean_text_for_bm25` removes special characters; preserve this behavior unless needed.
- Embeddings are generated with OpenAI API; ensure `OPENAI_API_KEY` is set.

### Output / Logging
- Console output uses `print` (no structured logger configured).
- Windows UTF-8 handling is done in `search_app/main.py`.

## Environment / Secrets
- Do not commit `.env` or API keys.
- Read env vars from `C:\Users\skyop\jaeho_template\.env`.

## Single-Test Guidance
There are no tests now. If you add tests:
- Put them under `tests/` with `test_*.py` names.
- Run a single test with `python -m pytest -k "test_name"`.

## Notes for Agents
- Use the existing venv if provided (`dotenv_windows`).
- Avoid changing DB schemas unless required.
- Keep SQL and config changes minimal and reversible.
- If you add new commands, update this file.

## DB / Data Safety
- Index creation may fail if `pg_search` is missing; fall back to standard FTS where needed.
- Keep destructive operations behind explicit flags (see `setup.py` reset logic).
- Use transactions and rollback on index creation errors.

## Performance / Querying
- Favor LIMITed queries with `search_limit` to avoid heavy DB scans.
- When comparing search modes, keep query strings identical and vary only `BM25_MODE`.

## CLI Behavior
- Exit with non-zero code on failure (`sys.exit(1)` in CLI).
- Preserve Windows UTF-8 output fix in `search_app/main.py`.

## Tokenization (BM25)
- BM25 text uses `Config.tokenize_for_bm25` for both indexing and query time.
- `BM25_TOKENIZER` controls tokenization: `simple` (default) or `kiwi`.
- `KIWI_POS_FILTER` defines Kiwi POS tags to keep (comma-separated list).
- After changing tokenization, rebuild `cleaned_searchable_text` and BM25 index.

## Tooling Rules
- No Cursor or Copilot rules were found in this repo.

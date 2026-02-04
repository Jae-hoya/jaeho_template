# AGENTS.md

This repository is a minimal Python MCP server implementing arithmetic tools.
Use these notes when editing or extending the code.

## Repository layout
- `server.py`: MCP server definition and tool implementations.
- `requirements.txt`: Python dependencies.
- `README_PLAY.md`: prompt notes (not executable).

## Environment assumptions
- Platform: Windows (paths use backslashes in examples).
- Python 3.11+ recommended (asyncio + typing).
- Uses the `mcp` package for MCP protocol support.

## Setup
- Create/activate a virtualenv in the repo root.
- Install dependencies: `pip install -r requirements.txt`.
- No additional build step is required.

## Run commands (manual)
- Start the server (stdio): `python server.py`.
- The server communicates via stdio; it does not bind a TCP port.
- Debug logs go to stderr with a `[debug]` prefix.

## Build commands
- No build system is configured.
- If you add packaging later, keep scripts in `pyproject.toml` or `setup.cfg`.

## Lint/format commands
- No linter/formatter is configured in this repo.
- If adding one, prefer `ruff` + `black` and document the commands here.
- Example (only if added): `python -m ruff .` and `python -m black .`.

## Test commands
- No test runner or test files are present.
- If tests are added with pytest, use `python -m pytest`.
- Single test (pytest only): `python -m pytest path\to\test_file.py::test_name`.

## MCP-specific behavior
- Server name constant: `calculate-mcp-server`.
- Tools are registered via `@server.list_tools()` and `@server.call_tool()`.
- Tool responses are `TextContent` containing plain text.
- Input validation uses `Decimal` conversion with `ValueError` on failure.

## Tool contract guidelines
- Each tool must define `inputSchema` with `type`, `properties`, and `required`.
- Use `number` schema types for numeric inputs.
- Keep tool `description` short and imperative.
- Keep tool names lowercase verbs (e.g., `add`, `multiply`).

## Logging guidelines
- Use `log_debug()` for all operational debug output.
- Always log input arguments before computation.
- Always log formatted output after computation.
- Log error conditions before raising exceptions.
- Logs must go to stderr with `flush=True`.

## Numeric handling
- Use `Decimal` for arithmetic to avoid floating-point surprises.
- Convert inputs with `Decimal(str(value))` for deterministic parsing.
- Keep global precision set via `getcontext().prec`.
- Return decimal output using `format(value, "f")` (no exponent).

## Error handling
- Raise `ValueError` for invalid tools or invalid numeric inputs.
- For divide-by-zero, log first and then raise `ValueError`.
- Do not swallow exceptions; let MCP framework surface errors.

## Async patterns
- Use `async def` for MCP handlers and `main()`.
- Run the server via `asyncio.run(main())`.
- Keep `stdio_server()` context manager at top-level in `main()`.

## Imports
- Order imports: standard library, third-party, local.
- Keep each import on its own line unless multiple names from one module.
- Avoid unused imports; keep `sys` for stderr logging.

## Formatting
- Follow PEP 8 line length (88 or 100 is acceptable).
- Use 4 spaces for indentation; no tabs.
- Use double quotes for strings (matches existing code).
- Keep blank lines between top-level definitions.

## Typing
- Prefer explicit type hints on public functions and handlers.
- Use `list[Tool]` and `list[TextContent]` style typing (Py 3.9+).
- Use `object` for unknown incoming types, then validate.

## Naming conventions
- Constants: `UPPER_SNAKE_CASE`.
- Functions: `lower_snake_case`.
- Variables: `lower_snake_case`.
- Keep tool names short, verb-based, lowercase.

## Data flow
- Read tool arguments from the `arguments` dict.
- Validate inputs early; fail fast on missing or invalid values.
- Keep computation pure and side-effect free (except logging).

## File organization
- Keep MCP server entrypoint in `server.py`.
- If adding modules, create a `src/` package and update imports.
- Keep new files ASCII-only unless required by domain data.

## Adding new tools
- Update `list_tools()` to include new `Tool` entries.
- Extend `call_tool()` dispatch logic.
- Add input validation and logging for each new tool.
- Include any new output formatting in `format_decimal()` if needed.

## Security and safety
- Do not log secrets or user-provided tokens.
- Treat all tool inputs as untrusted.
- Avoid executing shell commands from tool input.

## Documentation
- Keep `README_PLAY.md` as a note file; do not use for config.
- Add usage examples to a new `README.md` if needed.

## Git hygiene
- Only commit when explicitly requested by the user.
- Avoid touching unrelated files.

## Cursor/Copilot rules
- No `.cursor/rules`, `.cursorrules`, or `.github/copilot-instructions.md` found.
- If such files are added later, update this section.

## Common pitfalls
- Forgetting to log both input and output for a tool.
- Returning scientific notation (use `format(..., "f")`).
- Parsing floats directly instead of using `Decimal`.
- Creating tools without `inputSchema` definitions.

## Suggested future improvements (optional)
- Add pytest tests for each tool and error case.
- Add ruff/black config for consistent formatting.
- Add type checking (mypy or pyright) if project grows.

## Example single-test command (pytest)
- `python -m pytest tests\test_math.py::test_divide_by_zero`

## Example run with stdio
- `python server.py`
- Communicate via MCP-compatible client over stdio.

## Contact points
- Main entry: `server.py`.
- Dependencies: `requirements.txt`.

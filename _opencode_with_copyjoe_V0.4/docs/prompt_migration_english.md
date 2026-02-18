# Prompt Migration Notes (Korean to English)

Date: 2026-02-18

## Goal

This change set migrates LLM-facing prompt templates to English so smaller models (for example `qwen3:8b`) can follow instructions more consistently.

## Changed Python Files

### `app/services/copy_service.py`

- Updated fallback context placeholder to English: line `125`
  - Uses `(no context provided)` when no context exists.
- Rewrote the copy generation system prompt in English: lines `174-211`
  - Includes non-negotiable rules, creativity rules, objective priorities, channel optimization, and output quality bar.
- Rewrote strict-mode text stabilization block in English: lines `213-219`.
- Rewrote the human prompt input block labels and requirements in English: lines `227-246`.

### `app/services/copy_service.py` (copy-lite section)

- Rewrote landing context labels to English in `_format_landing_render_context`
  - Header is now `[Rendered Landing Context]`.
  - Empty section placeholders use `(none)`.
- Rewrote parser system prompt in English in `_parse_prompt`.
- Rewrote parser human prompt label to English (`[User Prompt]`).

Note: This logic was previously in `app/services/copy_lite_service.py` and is now consolidated into `CopyService`.

### `app/flows/copy_lite_generation/nodes.py`

- Updated refinement context block in `_build_refinement_context_block`: lines `37-49`
  - Adds an English header: `[Refinement Request from User Feedback]`.
  - Keeps the existing Korean header for compatibility with current flows.
- Expanded feedback section detection in `InferLanguageNode`: lines `200-201`
  - Supports both the existing Korean feedback marker and the new English marker (`[User Feedback]`).

## Intentionally Unchanged

- Heuristic inference logic for objective/channel/language remains as-is to avoid behavior regressions.
- Existing response schema and output field keys remain unchanged.
- Existing assumption-generation behavior remains unchanged.

## Verification

- Command run:

```bash
python -m pytest -q tests/test_copy_lite_generation_graph.py tests/test_copy_service_quality.py
```

- Result: `11 passed`

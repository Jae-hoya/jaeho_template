# 프롬프트 영어 전환 변경 요약

날짜: 2026-02-18

## 목적

LLM이 직접 읽는 프롬프트 템플릿을 한국어에서 영어로 전환해, 상대적으로 작은 모델(예: `qwen3:8b`)에서도 지시 추종성과 출력 일관성을 높이기 위한 변경입니다.

## 변경된 Python 파일

### `app/services/copy_service.py`

- 컨텍스트가 비어 있을 때의 기본 문구를 영어로 변경: `125`행
  - `(컨텍스트 없음)` -> `(no context provided)`
- 카피 생성 system 프롬프트 전체를 영어로 재작성: `174-211`행
  - Non-Negotiable Rules, Creativity Rules, Objective Priorities, Channel Optimization, Output Quality Bar 포함
- strict 모드 텍스트 안정화 규칙을 영어로 재작성: `213-219`행
- human 프롬프트의 입력 라벨/요구사항을 영어로 재작성: `227-246`행

### `app/services/copy_service.py` (copy-lite 영역)

- `_format_landing_render_context`의 랜딩 컨텍스트 라벨을 영어로 변경
  - 헤더: `[Rendered Landing Context]`
  - 비어있는 값 표기: `(none)`
- `_parse_prompt`의 parser system 프롬프트를 영어로 재작성
- parser human 프롬프트 라벨을 영어로 변경
  - `[User Prompt]`

참고: 위 로직은 기존 `app/services/copy_lite_service.py`에 있었고, 현재는 `CopyService`로 통합되었습니다.

### `app/flows/copy_lite_generation/nodes.py`

- `_build_refinement_context_block` 개선 컨텍스트 블록에 영어 헤더 추가: `37-49`행
  - `[Refinement Request from User Feedback]`
  - 기존 한국어 헤더도 호환성을 위해 유지
- `InferLanguageNode`의 피드백 섹션 감지를 확장: `200-201`행
  - 기존 한국어 마커 + 영어 마커(`[User Feedback]`) 모두 지원

## 의도적으로 유지한 부분

- objective/channel/language 추론 휴리스틱 로직은 회귀 방지를 위해 유지
- 응답 스키마 및 출력 필드 키는 변경 없음
- assumption 생성 동작은 변경 없음

## 검증

- 실행 커맨드:

```bash
python -m pytest -q tests/test_copy_lite_generation_graph.py tests/test_copy_service_quality.py
```

- 결과: `11 passed`

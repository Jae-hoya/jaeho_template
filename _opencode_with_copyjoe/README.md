# Copyjoe (FastAPI + LangChain + LangGraph + Vue)

`copyjoe_prd_v1.0.md` 기준 구현입니다.

## 핵심 포인트

- 백엔드: FastAPI
- 생성 엔진: LangChain (`with_structured_output`)
- 오케스트레이션: LangGraph (`app/flows/copy_generation_graph.py`)
- 랜딩 UI: Vue 3 SFC (`frontend/src/pages/IndexPage.vue`)
- 간편 생성 API: `POST /api/v1/copy/generate-lite` (prompt + style 중심)
- 출력 포맷: JSON 응답 + `md/doc/docx` 파일 내보내기
- 사용 이력: 쓰레드 기반 히스토리 API (`/api/v1/history/*`)
- 대화형 예시: `scripts/interactive_copy_chat.py`, `notebooks/interactive_chat_test.ipynb`

## 1) 백엔드 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

확인 URL:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/docs`

## 2) Vue 랜딩 페이지 실행 (`.vue` 파일 기반)

```bash
cd frontend
npm install
npm run dev
```

접속: `http://127.0.0.1:5173`

빌드 후 FastAPI `/`로도 보려면:

```bash
cd frontend
npm run build
```

Vue 주요 파일:

- `frontend/src/pages/IndexPage.vue`
- `frontend/src/copyjoe/sections/PromptSection.vue`
- `frontend/src/copyjoe/sections/GenerationSection.vue`
- `frontend/src/copyjoe/components/GenerateResult.vue`
- `frontend/src/copyjoe/components/ExportDialog.vue`

참고:

- `PromptSection.vue`는 `간편 대화형`/`상세 입력` 모드를 모두 지원합니다.
- `간편 대화형`은 질문-응답 대화로 objective/channel을 수집하고, language는 버튼으로 선택합니다.
- `간편 대화형`에서 language는 하단 버튼 클릭으로 별도 선택할 수 있습니다.
- 사이드바에서 파일 업로드 후 자동 인덱싱으로 RAG 근거를 즉시 쌓을 수 있습니다.
- 업로드 지원: `pdf, doc, docx, txt, xls, xlsx, ppt, pptx, png, jpg`
- 처리 중에는 새 카피 생성/랜딩 분석 버튼이 잠겨 중복 실행을 막습니다.
- 레이아웃은 `프롬프트 사이드바 + 제너레이션 메인` 구조입니다.
- 생성 후 메인 화면의 "대화 기반 개선" 입력으로 피드백을 주면 더 풍부한 문체로 연속 개선 버전을 생성합니다.
- 상세 입력 필드의 `?` 아이콘에 마우스를 올리면 pain_point/differentiator/objective/channel/tone/language/top_k 설명이 표시됩니다.
- language 입력은 별칭/경미한 오타를 자동 보정합니다. 예: `englsh` -> `en`
- 검증 오류(422) 시 프론트에서 어떤 필드를 이해하지 못했는지 항목별로 표시합니다.

## 3) 어디서 LangChain/LangGraph가 실행되나?

요약:

- LangGraph: `app/flows/copy_generation_graph.py`
- LangChain: `app/services/copy_service.py`
- API 진입: `app/api/v1/copy.py`

자세한 맵: `docs/runtime_map.md`

## 4) 모델 설정

`.env` 예시:

- OpenAI
  - `LLM_PROVIDER=openai`
  - `OPENAI_API_KEY=...`
- Ollama (8b)
  - `LLM_PROVIDER=ollama`
  - `OLLAMA_CHAT_MODEL=qwen3:8b`
  - `OLLAMA_EMBEDDING_MODEL=qwen3-embedding:4b`

## 4-1) 입력 필드 상세 가이드

온도/토큰 설정 원칙:

- 설정의 단일 소스는 `app/core/config.py` 입니다.
- 생성/파서 온도와 토큰 상한은 `.env`가 아니라 `app/core/config.py` 상수에서만 수정합니다.
- `app/integrations/model_factory.py`는 모델 객체만 만들고, 온도는 고정하지 않습니다.
- `app/services/copy_service.py`는 생성용 설정(`COPY_GENERATION_*`)을 읽어 바인딩합니다.
- `app/services/copy_lite_service.py`는 파싱용 설정(`COPY_PARSER_*`)을 읽어 바인딩합니다.

`POST /api/v1/copy/generate`의 핵심 입력값을 아래처럼 이해하면 쉽습니다.

- `pain_point`
  - 의미: 고객이 지금 겪는 핵심 문제
  - 작성법: 문제 상황 + 손실(시간/비용/성과) + 감정을 1~2문장
  - 예시: `랜딩 전환률이 낮아 광고비가 새고, 개선 포인트를 빠르게 찾기 어렵다`

- `differentiator`
  - 의미: 경쟁 대비 우리 솔루션 차별점
  - 작성법: 기능 + 근거 + 기대 결과를 한 문장
  - 예시: `LangGraph 기반 RAG+Tavily 결합으로 근거 있는 카피를 빠르게 생성한다`

- `objective`
  - 의미: 카피의 최종 행동 목표
  - 값:
    - `brand_memory`: 브랜드 인지/기억
    - `click`: 클릭 유도
    - `add_to_cart`: 장바구니 담기 유도
    - `consultation`: 상담/문의 유도

- `channel`
  - 의미: 문구가 쓰일 실제 매체/지면
  - 예시: `상세페이지`, `메타 광고 랜딩`, `인스타 피드`, `유튜브 쇼츠`, `이메일 캠페인`

- `language`
  - 의미: 출력 언어 코드 (BCP-47 스타일)
  - 지원 코드: `ko`, `en`, `ja`, `zh-CN`, `zh-TW`, `es`, `fr`, `de`, `pt-BR`, `vi`, `id`, `th`
  - 별칭도 자동 인식: `english -> en`, `korean -> ko`, `ja-jp -> ja`, `pt-br -> pt-BR`

- `top_k`
  - 의미: RAG/웹 검색에서 참고할 근거 개수
  - 권장: 보통 `3~8`, 기본 `5`
  - 값이 너무 작으면 근거가 빈약해지고, 너무 크면 문맥이 퍼질 수 있음

필드 가이드를 API로도 확인할 수 있습니다:

- `GET /api/v1/meta/copy-form-guide`

간편 생성 API:

- `POST /api/v1/copy/generate-lite`
- 입력: `prompt`, `styles` 중심
- 출력: `result` + `assumptions` + 자동 완성된 `normalized_request`

입력 제한:

- 자연어 prompt 최대 `8000`자

내보내기 API:

- `POST /api/v1/export/docx`
- `POST /api/v1/export/doc`
- `POST /api/v1/export/md`

사용 이력(쓰레드) API:

- `POST /api/v1/history/threads`
- `GET /api/v1/history/threads`
- `GET /api/v1/history/threads/{thread_id}`
- `POST /api/v1/history/threads/{thread_id}/messages`

## 5) 대화형 시스템 예시 (py / ipynb)

### CLI (py)

```bash
python scripts/interactive_copy_chat.py --base-url http://127.0.0.1:8000
```

예시 명령:

- `/set product_name Copyjoe Pro`
- `/toggle web_search_mode`
- `/generate`
- `/landing-url https://example.com`
- `/landing-query copywriting saas landing page`

### Notebook (ipynb)

- `notebooks/interactive_chat_test.ipynb`
- `chat_turn("generate")` 처럼 셀에서 대화형 호출

## 6) 품질 검사 노트북

- `notebooks/langchain_quality_checks.ipynb`
- 항목: RAG 검색, structured output, 생성 품질, `/health`/`/docs`/`/openapi.json`

실행(자동):

```bash
python scripts/execute_notebook_checks.py --provider openai --port 8014 --notebook notebooks/langchain_quality_checks.ipynb --output langchain_quality_checks.executed.ipynb
python scripts/execute_notebook_checks.py --provider ollama --ollama-model qwen3:8b --port 8015 --notebook notebooks/interactive_chat_test.ipynb --output interactive_chat_test.executed.ipynb
```

## 7) 전체 기능 한번에 점검

```bash
python scripts/run_full_checks.py --provider openai --port 8012
python scripts/run_full_checks.py --provider ollama --ollama-model qwen3:8b --port 8013
```

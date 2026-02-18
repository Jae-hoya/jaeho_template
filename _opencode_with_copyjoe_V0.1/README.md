# Copyjoe (FastAPI + LangChain + LangGraph + Vue)

`copyjoe_prd_v1.0.md` 기준 구현입니다.

## 핵심 포인트

- 백엔드: FastAPI
- 생성 엔진: LangChain (`with_structured_output`)
- 오케스트레이션: LangGraph (`app/flows/copy_generation_graph.py`)
- 랜딩 UI: Vue 3 SFC (`frontend/src/pages/IndexPage.vue`)
- 간편 생성 API: `POST /api/v1/copy/generate-lite` (prompt + style 중심)
- 랜딩 렌더링 기반 생성: `landing_url`/`landing_query` 입력 시 렌더링 텍스트를 생성 컨텍스트에 반영
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

현재 UX 흐름:

- 좌측 `PromptSection.vue`: 스타일 선택 + RAG 업로드 + 랜딩 분석
- 우측 `GenerationSection.vue`: 대화형 브리프 입력 + 생성 결과/로그/개선
- 스타일 상세(`head/body/cta/slogan/sns/description`)는 `?` 아이콘 툴팁(hover/focus)으로 확인
- `landing_url`(선택)을 입력하면 Playwright 렌더링 텍스트를 카피 근거로 반영
- 랜딩 분석 완료 후 `이 랜딩으로 콘티 작성` 버튼으로 storyboard 중심 카피 즉시 생성
- objective/channel/language는 프롬프트 문맥에서 자동 추론 (미입력 시 `click`/`상세페이지`/`ko`)
- 생성 후 "대화 기반 개선" 입력으로 연속 개선 버전 생성
- 처리 중에는 새 카피 생성/랜딩 분석/업로드 버튼이 잠겨 중복 실행 방지
- 검증 오류(422) 시 프론트에서 이해하지 못한 필드를 항목별 표시

빠른 사용 시나리오 (3-step):

- 시나리오 A - 기본 카피 생성: 1) 좌측에서 스타일 선택 2) 우측 대화형 브리프 입력 후 생성 3) 결과에서 개선 피드백 입력
- 시나리오 B - 랜딩 기반 카피 생성: 1) 우측 입력에 `landing_url` + 브리프 입력 2) 카피 생성 3) assumptions에서 자동 추론/렌더링 반영 여부 확인
- 시나리오 C - 랜딩 분석 후 콘티 생성: 1) 좌측 랜딩 분석 실행 2) 결과 카드의 `이 랜딩으로 콘티 작성` 클릭 3) `storyboard_outline` 중심으로 콘티 확인

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
- 입력: `prompt`, `styles` 중심 (`landing_url` 또는 `landing_query` 선택 입력 가능)
- 출력: `result` + `assumptions` + 자동 완성된 `normalized_request`

렌더링 기반 랜딩 분석 API:

- `POST /api/v1/web/landing/analyze`
- 입력: `url` 또는 `query`
- 동작: Playwright 렌더링 분석 우선, 실패 시 requests 파서 폴백

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

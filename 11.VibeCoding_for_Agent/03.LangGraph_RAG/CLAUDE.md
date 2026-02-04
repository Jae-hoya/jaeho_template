# CLAUDE_KR.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드 작업 시 참고할 가이드를 제공합니다.

## 프로젝트 개요

대출 상품 하이브리드 검색 시스템으로, BM25 전문 검색과 벡터 의미 검색을 RRF(Reciprocal Rank Fusion)로 결합한 Python 기반 시스템입니다. ParadeDB (PostgreSQL + pgvector + pg_search)에서 실행되며 OpenAI 임베딩을 사용합니다.




## 필수 명령어

### 데이터베이스 설정
```bash
# 데이터베이스 초기화, 테이블 생성, 데이터 로드, 임베딩 생성
python -m search_app.setup
```

이 명령어 실행 시:
- pgvector와 pg_search 확장 설치
- loan_products 테이블 생성
- loan_products.json에서 67개 대출 상품 로드
- 1536차원 OpenAI 임베딩 배치 생성 (67개 상품 → 1번 API 호출로 최적화)
- BM25 및 벡터 검색 인덱스 생성

### 검색 실행
```bash
# 하이브리드 검색 수행 (CLI)
python -m search_app.main "의사 전용 대출"

# Streamlit 웹 UI 실행 (권장)
streamlit run streamlit_app.py
```

### 의존성 설치
```bash
pip install psycopg python-dotenv openai numpy kiwipiepy
```

### 테스트
```bash
# 모든 테스트 실행 (pytest 예상, 현재 테스트 파일 없음)
python -m pytest

# 특정 테스트 실행
python -m pytest -k "test_name"
```

## 환경 설정

환경 변수는 `C:\Users\skyop\jaeho_template\dotenv_windows`에서 로드됩니다:

**필수:**
- `OPENAI_API_KEY`: 임베딩 생성용 OpenAI API 키
- `DATABASE_URL`: PostgreSQL 연결 문자열 (기본값: `postgresql://postgres:postgres@localhost:5433/postgres`)

**선택:**
- `BM25_MODE`: `paradedb` (기본값) 또는 `fts` (PostgreSQL 전문 검색)
- `BM25_TOKENIZER`: `simple` (기본값) 또는 `kiwi` (한국어 토크나이저)
- `KIWI_POS_FILTER`: Kiwi 토크나이저용 품사 태그 (기본값: `NNG,NNP,NNB,NR,NP,VV,VA,XR,SL,SN`)

### ParadeDB Docker
```bash
docker run -d \
  --name hybrid-search-paradedb \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -p 5433:5432 \
  paradedb/paradedb:latest
```

## 아키텍처

### 핵심 모듈

**`search_app/config.py`**: 설정 및 환경 변수 로드
- `Config.get_connection_string()`: PostgreSQL 연결 문자열 반환
- `Config.tokenize_for_bm25()`: BM25 검색용 텍스트 토큰화 (simple 또는 Kiwi 토크나이저 지원)
- `C:\Users\skyop\jaeho_template\.env`에서 환경 변수 로드

**`search_app/database.py`**: 데이터베이스 연결 및 스키마 관리
- `Database.setup_extensions()`: pgvector와 pg_search 확장 설치
- `Database.create_table()`: 벡터 컬럼이 포함된 loan_products 테이블 생성
- `Database.create_bm25_index()`: BM25 인덱스 생성 (pg_search 없으면 GIN으로 대체)
- `Database.create_vector_index()`: IVFFlat 벡터 인덱스 생성

**`search_app/data_loader.py`**: 데이터 수집 및 임베딩 생성
- `DataLoader.load_json()`: loan_products.json 로드
- `DataLoader.generate_embeddings_batch()`: 배치 처리로 OpenAI 임베딩 생성 (67개 상품 → 1번 API 호출)
- `DataLoader.clean_text_for_bm25()`: BM25 인덱싱을 위한 특수문자 제거
- `DataLoader.load_data()`: 배치 임베딩 생성 후 DB 삽입

**`search_app/hybrid_search.py`**: 검색 구현
- `HybridSearch.bm25_search()`: `cleaned_searchable_text`에서 BM25 전문 검색
- `HybridSearch.vector_search()`: `searchable_text_embedding`에서 코사인 유사도 검색
- `HybridSearch.reciprocal_rank_fusion()`: RRF 공식으로 결과 통합: `RRF_score(d) = Σ(1 / (k + rank(d)))`
- `HybridSearch.search()`: BM25, 벡터, RRF를 조율하는 메인 검색 메서드

**`search_app/setup.py`**: 데이터베이스 초기화 스크립트
**`search_app/main.py`**: Windows UTF-8 처리가 포함된 CLI 진입점

**`streamlit_app.py`**: Streamlit 웹 UI
- `process_question()`: 질문 처리 및 RAG 실행 (에러 처리 포함)
- `initialize_rag()`: RAG 시스템 초기화
- `pending_question` 상태: 예제 질문 클릭 시 중복 방지
- 홈 버튼: 대화 초기화 기능

### 검색 흐름

1. **BM25 검색**: 쿼리가 토큰화되어 ParadeDB의 BM25 인덱스(`@@@` 연산자) 또는 PostgreSQL의 `ts_rank`를 사용하여 `cleaned_searchable_text`와 매칭
2. **벡터 검색**: 쿼리 임베딩이 생성되고 코사인 거리(`<=>` 연산자)를 사용하여 `searchable_text_embedding`과 비교
3. **RRF 융합**: k=60 (Config.RRF_K로 설정 가능)으로 Reciprocal Rank Fusion을 사용하여 결과 통합
4. **결과 검색**: 상위 순위 문서의 전체 상품 상세 정보 가져오기

### 데이터베이스 스키마

테이블: `loan_products`

주요 컬럼:
- `id` (VARCHAR, PRIMARY KEY): 고유 상품 식별자
- `searchable_text` (TEXT): 원본 연결된 검색 가능 콘텐츠
- `cleaned_searchable_text` (TEXT): BM25용 특수문자 제거 전처리 텍스트
- `searchable_text_embedding` (vector(1536)): 의미 검색용 OpenAI 임베딩
- 다양한 대출 상품 필드 (product_name, product_code, 금리 등)

## 코드 스타일

- **들여쓰기**: 공백 4칸, 탭 사용 금지
- **따옴표**: 문자열에 큰따옴표 사용
- **임포트**: 표준 라이브러리, 서드파티, 로컬 순서 (스타 임포트 금지)
- **타입 힌트**: Python 3.10 호환성을 위해 `typing.List`, `Dict`, `Tuple` 사용
- **네이밍**: snake_case (함수/변수), PascalCase (클래스), UPPER_SNAKE_CASE (상수)
- **SQL**: 항상 `%s` 플레이스홀더로 파라미터화된 쿼리 사용
- **에러 처리**: DB 작업을 try/except로 감싸고, 명확하게 로그 작성, 실패 시 명시적으로 처리

## BM25 모드

시스템은 `BM25_MODE`로 제어되는 두 가지 BM25 구현을 지원합니다:

1. **ParadeDB** (기본값): `pg_search` 확장과 `@@@` 연산자 및 `paradedb.score()` 사용
2. **PostgreSQL FTS**: pg_search를 사용할 수 없을 때 `to_tsvector`/`ts_rank`로 대체

모드나 토크나이저를 변경할 때는 `python -m search_app.setup`을 재실행하여 인덱스를 다시 빌드해야 합니다.

## 토큰화

BM25용 두 가지 토큰화 전략:

1. **Simple** (기본값): 정규표현식 기반 특수문자 제거
2. **Kiwi**: 품사 필터링이 있는 한국어 형태소 분석기

토큰화는 인덱싱 시점(`cleaned_searchable_text` 생성)과 쿼리 시점(`Config.tokenize_for_bm25()`)에 일관되게 적용됩니다.

## 중요 사항

- Windows UTF-8 출력 처리는 `search_app/main.py`에 구현됨
- 확장 생성(pgvector, pg_search)은 일부 PostgreSQL 인스턴스에서 실패할 수 있으며, 대체 방법이 구현됨
- BM25 인덱스 생성은 pg_search를 사용할 수 없으면 GIN 인덱스로 대체
- OpenAI API 호출은 배치 처리로 최적화됨 (67개 상품 → 1번 API 호출)
- 린터/포매터 미설정; 기존 코드와 일관성 유지
- 데이터베이스 작업은 오류 시 롤백이 있는 트랜잭션 사용

## 성능 최적화

### 임베딩 생성 배치 처리
- **개선 전**: 각 상품마다 개별 API 호출 (67번)
- **개선 후**: `generate_embeddings_batch()`로 한 번에 처리 (1번)
- **효과**: API 호출 98.5% 감소, 초기화 시간 대폭 단축

### Streamlit UI 최적화
- **즉시 응답**: 스트리밍 효과 제거로 답변 즉시 표시
- **예제 질문**: 클릭 시 바로 처리, `pending_question` 상태 관리로 중복 표시 방지
- **홈 버튼**: 왼쪽 상단 "🏠 홈" 버튼으로 대화 초기화 및 초기 화면 복귀
- **에러 처리**: `process_question()` 함수에 상세 에러 메시지 및 traceback 포함
- **RAG 초기화 체크**: 처리 전 RAG 시스템 초기화 상태 확인

## 코드 레벨 구현 상세

### 1. 배치 임베딩 생성 (`search_app/data_loader.py`)

#### 개선 전 구조
```python
def insert_product(self, product):
    # 각 상품마다 개별 호출
    embedding = self.generate_embedding(searchable_text)  # API 호출 1회
    # DB 삽입

def load_data(self, json_file):
    for product in products:
        self.insert_product(product)  # 67번 반복 = 67번 API 호출
```

#### 개선 후 구조
```python
def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100):
    """배치로 임베딩 생성"""
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = self.client.embeddings.create(
            model=Config.EMBEDDING_MODEL,
            input=batch,  # 리스트 전체 전송
            encoding_format="float"
        )
        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)
    return embeddings

def load_data(self, json_file):
    # 1단계: 모든 검색 가능 텍스트 생성
    searchable_texts = []
    for product in products:
        searchable_texts.append(self.create_searchable_text(product))

    # 2단계: 배치로 한번에 임베딩 생성 (1번 API 호출)
    embeddings = self.generate_embeddings_batch(searchable_texts)

    # 3단계: 생성된 임베딩으로 DB 삽입
    for product, searchable_text, embedding in zip(products, searchable_texts, embeddings):
        # DB INSERT (임베딩 이미 생성됨)
```

**핵심 변경점:**
- `generate_embedding()` (단일) 제거 → `generate_embeddings_batch()` (배치) 사용
- `insert_product()` 제거 → `load_data()` 내부에서 직접 처리
- 텍스트 생성 → 임베딩 생성 → DB 삽입을 순차적으로 분리

---

### 2. Streamlit 예제 질문 중복 방지 (`streamlit_app.py`)

#### 문제 상황
```
사용자가 예제 질문 클릭
  ↓
st.rerun() 호출
  ↓
화면 재렌더링 시작
  ↓
예제 질문 섹션 다시 표시 (중복!)
  ↓
RAG 처리 시작
  ↓
처리 완료 후 다시 rerun
  ↓
예제 질문 사라짐
```

#### 해결 방법: `pending_question` 상태 관리

**세션 상태 초기화:**
```python
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
```

**예제 질문 버튼 클릭:**
```python
# 버튼 클릭 시 질문 저장만 하고 바로 rerun
if st.button(f"📝 {example}"):
    st.session_state.pending_question = example  # 질문 저장
    st.rerun()  # 즉시 rerun
```

**pending_question 처리 (main 함수 초반):**
```python
# RAG 초기화 후, 채팅 인터페이스 표시 전에 처리
if st.session_state.pending_question is not None:
    question = st.session_state.pending_question
    st.session_state.pending_question = None  # 즉시 초기화
    with st.spinner("답변 생성 중..."):
        process_question(question)  # RAG 처리
    st.rerun()  # 처리 완료 후 화면 갱신
```

**예제 질문 표시 조건:**
```python
# 두 조건 모두 충족해야 표시
if len(st.session_state.messages) == 0 and st.session_state.pending_question is None:
    # 예제 질문 표시
```

**실행 흐름:**
```
1. 버튼 클릭
   - pending_question = "질문"
   - rerun()

2. Rerun (1차)
   - pending_question != None → 예제 질문 숨김 ✓
   - RAG 처리 시작
   - pending_question = None
   - messages에 추가
   - rerun()

3. Rerun (2차)
   - pending_question == None
   - messages > 0 → 예제 질문 조건 불충족 ✓
   - 대화 표시
```

---

### 3. 질문 처리 함수 (`streamlit_app.py`)

#### process_question() 함수 구조
```python
def process_question(prompt: str):
    """질문 처리 및 RAG 실행"""
    try:
        # 1. RAG 초기화 체크
        if st.session_state.rag is None:
            raise RuntimeError("RAG 시스템이 초기화되지 않았습니다.")

        # 2. 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })

        # 3. RAG 상태 생성
        initial_state: RAGState = {
            "question": prompt,
            "route_decision": "",
            "search_results": [],
            "answer": "",
            "debug": st.session_state.debug_mode
        }

        # 4. LangGraph 실행
        final_state = st.session_state.rag.graph.invoke(initial_state)

        # 5. 결과 추출
        answer = final_state["answer"]
        route = final_state.get("route_decision", "unknown")
        search_results = final_state.get("search_results", [])

        # 6. 응답 메시지 추가
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "route": route,
            "search_results": search_results,
            "timestamp": datetime.now().isoformat()
        })

        return True

    except Exception as e:
        # 7. 에러 처리 (traceback 포함)
        import traceback
        error_msg = f"오류가 발생했습니다: {str(e)}\n\n{traceback.format_exc()}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg,
            "route": "error",
            "search_results": [],
            "timestamp": datetime.now().isoformat()
        })
        return False
```

**주요 특징:**
- **사전 체크**: RAG 초기화 상태 확인
- **에러 처리**: try-except로 모든 에러 포착, traceback 포함
- **상태 저장**: route와 search_results를 메시지에 포함하여 UI에서 활용
- **타임스탬프**: 모든 메시지에 시간 기록

---

### 4. 홈 버튼 구현 (`streamlit_app.py`)

#### 레이아웃 구조
```python
def main():
    # 3열 레이아웃: [홈 버튼 | 제목 | 빈칸]
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button("🏠 홈", use_container_width=True):
            # 세션 상태 초기화
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()

    with col2:
        st.markdown("<div class='main-header'>🔍 LangGraph RAG</div>",
                    unsafe_allow_html=True)
```

**초기화 동작:**
1. `messages = []`: 모든 대화 내역 삭제
2. `pending_question = None`: 대기 중인 질문 초기화
3. `st.rerun()`: 화면 새로고침
4. 예제 질문 조건 충족 (`messages == 0` and `pending_question == None`) → 예제 질문 표시

---

### 5. 스트리밍 효과 제거

#### 개선 전 (한 글자씩 출력)
```python
import time
displayed_text = ""
for char in answer:
    displayed_text += char
    message_placeholder.markdown(displayed_text + "▌")  # 커서 표시
    time.sleep(st.session_state.streaming_speed)  # 속도 조절

message_placeholder.markdown(answer)  # 최종 출력
```

#### 개선 후 (즉시 출력)
```python
message_placeholder.markdown(answer)  # 바로 전체 출력
```

**제거된 것들:**
- `streaming_speed` 세션 상태
- 스트리밍 속도 선택 UI (사이드바)
- `time.sleep()` 반복문
- 속도 관련 모든 코드

---

### 6. 메시지 표시 로직

#### 대화 표시
```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # 메시지 내용
        st.markdown(message["content"])

        # 라우팅 뱃지 (assistant만)
        if message["role"] == "assistant" and "route" in message:
            route = message["route"]
            badge_class = "route-search" if route == "search" else "route-direct"
            st.markdown(
                f"<span class='route-badge {badge_class}'>{route.upper()}</span>",
                unsafe_allow_html=True
            )

        # 검색 결과 (있는 경우만)
        if message["role"] == "assistant" and "search_results" in message:
            if message["search_results"]:
                with st.expander("🔍 검색 결과 보기"):
                    st.markdown(
                        format_search_results(message["search_results"]),
                        unsafe_allow_html=True
                    )
```

**데이터 구조:**
```python
# 사용자 메시지
{
    "role": "user",
    "content": "질문 내용",
    "timestamp": "2024-01-21T10:00:00"
}

# 응답 메시지
{
    "role": "assistant",
    "content": "답변 내용",
    "route": "search" or "direct",
    "search_results": [...],
    "timestamp": "2024-01-21T10:00:05"
}
```

---

### 7. 채팅 입력 처리

```python
# Chat input
if prompt := st.chat_input("질문을 입력하세요..."):
    with st.spinner("답변 생성 중..."):
        process_question(prompt)
    st.rerun()  # 처리 후 화면 갱신
```

**흐름:**
1. 사용자가 채팅 입력창에 질문 입력
2. `process_question()` 호출로 RAG 처리
3. 처리 중 스피너 표시
4. 완료 후 `rerun()`으로 화면 갱신
5. 새로운 메시지가 대화 목록에 표시됨

---

### 8. 세션 상태 관리

```python
# 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag" not in st.session_state:
    st.session_state.rag = None

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
```

**세션 상태 변수:**
- `messages`: 전체 대화 내역 (리스트)
- `rag`: LangGraphRAG 인스턴스 (한 번만 초기화)
- `debug_mode`: 디버그 모드 on/off (불린)
- `pending_question`: 대기 중인 예제 질문 (문자열 또는 None)

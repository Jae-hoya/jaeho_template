입력: (테스트)
rag 사용해서 "의료인 대출 상품 추천해줘" 실행 

만약 어떠한 문제가 발생한다면,
입력: 
어떠한 문제가 반복되니까,
1. 테스트 파일을 만들고,
2. CLAUDE.md 파일을 업데이트해서 테스트 하라고 하면 반드시 ~이 설정이 되어있는지 테스트 하게해
3. langgraph_rag.py  를 사용하는 방법을 CLAUDE.md 에 추가해줘 (나이브한 명령어를 내렸을떄 추가하지 못하는 오류가 발생했음)

---------------------------------------------------------------------------------------------------------------------
입력:
rag 시스템 프롬프트를 개선할 방안을 고민해줘.
(방안이 나오면)
1번, 2번, 4번을 반영해서 업데이트 해줘 
(langgraph_rag.py 를 업데이트한다.)

조금 더 자세히, 상세하게 적어줘야 할거같아.

---------------------------------------------------------------------------------------------------------------------
입력:
(thinking 키고)
@PRD.md 를 바탕으로 계획을 세우고 구현해줘.

--
입력:
(thinking 끄고)
gpt-5-mini 모델을 정말로 사용했는지 검토해줘.
- 여기서 버전이 잘 안맞는 경우가 있다. 그래서 4o 모델까지 사용하는 경우가 있기 때문에, 버전체크도 잘해줘야 한다.

혹시 langchain 버전이 낮아서 gpt -5-mini모델을 모르는것 아닌지 검토해줘

---------------------------------------------------------------------------------------------------------------------
입력:
배포를 위한 Streamlit 구현해줘.

출력 형식을 한글자씩 나오는 스트리밍 형식으로 구현해줘.

---------------------------------------------------------------------------------------------------------------------
입력:
구현한 내용을 코드레벨에서 더 디테일하게 설명해줘.



# RAG PRD.md 작성
스펙:
- Langgraph, LangChain, langchain-openai
- GPT-5-mini

목표:
Routing 기반 Langgraph RAG CLI 구현

워크플로우:
1. Route: 질문 분석 → search/direct 판단
2. Retrieve: Hybrid Search로 top-3 검색
3. Generate: 답변 생성

핵심 구현:
- StateGraph로 노드 정의 (route, retrieve, generate)
- conditional_edges로 routing

CLI:
uv run python langgraph_rag.py "질문" [--debug]

참고:
- langgraph 구현할 때에는 context7으로 최신 개발 문서 확인
- langgraph 도구 확인

---

CLAUDE.md에
다음을 추가

마지막 부분에,
---
## NOTES
- 데이터베이스 관련 정보
- OpenAI GPT-5-mini 모델을 사용해야해.
   - (2025년 8월 출시)
- 프로젝트 목표를 RAG 개발로 수정
---------------------------------------------------------------------------------------------------------------------

입력
❯ @CLAUDE_KR.md 파일 업데이트:

프로젝트 목표를 하이브리드 서치를 포함해서 RAG를 만드는것으로 수정해줘


---------------------------------------------------------------------------------------------------------------------
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
- 1536차원 OpenAI 임베딩 생성
- BM25 및 벡터 검색 인덱스 생성

### 검색 실행
```bash
# 하이브리드 검색 수행
python -m search_app.main "의사 전용 대출"
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
- `DataLoader.generate_embeddings()`: 속도 제한 처리와 함께 OpenAI 임베딩 배치 생성
- `DataLoader.clean_text_for_bm25()`: BM25 인덱싱을 위한 특수문자 제거

**`search_app/hybrid_search.py`**: 검색 구현
- `HybridSearch.bm25_search()`: `cleaned_searchable_text`에서 BM25 전문 검색
- `HybridSearch.vector_search()`: `searchable_text_embedding`에서 코사인 유사도 검색
- `HybridSearch.reciprocal_rank_fusion()`: RRF 공식으로 결과 통합: `RRF_score(d) = Σ(1 / (k + rank(d)))`
- `HybridSearch.search()`: BM25, 벡터, RRF를 조율하는 메인 검색 메서드

**`search_app/setup.py`**: 데이터베이스 초기화 스크립트
**`search_app/main.py`**: Windows UTF-8 처리가 포함된 CLI 진입점

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
- OpenAI API 호출에는 재시도 로직과 속도 제한 처리 포함
- 린터/포매터 미설정; 기존 코드와 일관성 유지
- 데이터베이스 작업은 오류 시 롤백이 있는 트랜잭션 사용

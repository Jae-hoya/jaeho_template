# Hybrid Search for Loan Products

Python 기반 하이브리드 검색 시스템으로 BM25와 벡터 검색을 결합하여 대출 상품 데이터를 검색합니다.

## 기술 스택

- **Language**: Python 3.10+
- **Database**: ParadeDB (PostgreSQL with pgvector and BM25 support)
- **Embedding Model**: OpenAI text-embedding-3-small
- **Database Driver**: psycopg (psycopg3)

## 프로젝트 구조

```
hybrid_search/
├── search_app/
│   ├── __init__.py
│   ├── config.py           # 환경 설정
│   ├── database.py         # 데이터베이스 연결 및 테이블 관리
│   ├── data_loader.py      # 데이터 로딩 및 임베딩 생성
│   ├── hybrid_search.py    # 하이브리드 검색 구현
│   ├── setup.py            # 데이터베이스 초기화 스크립트
│   └── main.py             # CLI 실행 파일
├── loan_products.json      # 대출 상품 데이터 (67개)
├── pyproject.toml          # 프로젝트 의존성
└── README.md
```

## 설치 및 설정

### 1. ParadeDB Docker 컨테이너 실행

```bash
docker run -d \
  --name hybrid-search-paradedb \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -p 5433:5432 \
  paradedb/paradedb:latest
```

### 2. 환경 변수 설정

`C:\Users\skyop\jaeho_template\.env` 파일에 다음 내용 추가:

```bash
# ParadeDB connection (port 5433)
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/postgres

# OpenAI API Key (필수)
OPENAI_API_KEY=your-openai-api-key
```

### 3. 의존성 설치

```bash
cd C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\hybrid_search
pip install psycopg python-dotenv openai numpy kiwipiepy
```

### 4. 데이터베이스 초기화 및 데이터 로드

```bash
python -m search_app.setup
```

**처리 과정:**
- ✅ pgvector와 pg_search 확장 설치
- ✅ loan_products 테이블 생성
- ✅ 67개 대출 상품 데이터 로드
- ✅ OpenAI를 사용한 1536차원 벡터 임베딩 생성
- ✅ 검색 인덱스 생성

## 사용법

### 기본 검색

```bash
python -m search_app.main "의사 전용 대출"
```

### 검색 결과 예시

```
================================================================================
Found 10 results
================================================================================

1. NH메디프로론
   Code: 40000523
   Score: 0.0309
   Interest Rate: 3.64% ~ 4.94%
   Summary: 의료인 전용 우대 신용대출...

2. NH전세대출(서울보증보험)
   Code: 40000528
   Score: 0.0164
   Interest Rate: 2.9% ~ 5.3%
   Summary: 서울보증보험을 담보로 최대 5억원까지 든든한 전세 대출 상품...
```

### 다양한 검색어 테스트

```bash
# 직업별 대출
python -m search_app.main "의사 전용 대출"
python -m search_app.main "소상공인 대출"

# 목적별 대출
python -m search_app.main "저금리 주택담보대출"
python -m search_app.main "전세자금대출"

# 영어 검색
python -m search_app.main "small business loan"
```

## 하이브리드 검색 동작 방식

### 1. BM25 전문 검색 (Full-Text Search)
- PostgreSQL의 `ts_rank` 함수 사용
- `cleaned_searchable_text` 필드에서 키워드 매칭
- 특수문자가 제거된 텍스트로 정확한 매칭 수행

### 2. 벡터 유사도 검색 (Semantic Search)
- OpenAI text-embedding-3-small 모델 사용 (1536 차원)
- `searchable_text_embedding` 벡터와 쿼리 임베딩 간 코사인 유사도 계산
- 의미적으로 유사한 대출 상품 검색

### 3. RRF (Reciprocal Rank Fusion)
두 검색 결과를 통합하여 최종 순위 결정:

```
RRF_score(d) = Σ(1 / (k + rank(d)))
```

- `k`: 상수 (기본값: 60)
- `rank(d)`: 각 검색 방법에서의 문서 순위

## BM25 토크나이저 (Kiwi 지원)

한국어 토큰화를 위해 Kiwi 토크나이저를 선택할 수 있습니다.

### 1) 설치
```bash
pip install kiwipiepy
```

### 2) 환경 변수 설정
```bash
# 기본값: simple
BM25_TOKENIZER=kiwi

# Kiwi 품사 필터(기본값)
KIWI_POS_FILTER=NNG,NNP,NNB,NR,NP,VV,VA,XR,SL,SN
```

### 3) 재색인
토크나이저를 변경하면 `cleaned_searchable_text`와 BM25 인덱스를 다시 생성해야 합니다.

```bash
python -m search_app.setup
```

## BM25 모드 설정

```bash
# ParadeDB BM25 (기본값)
BM25_MODE=paradedb

# PostgreSQL FTS
BM25_MODE=fts
```

## 데이터 스키마

### loan_products 테이블

| 컬럼명                      | 타입         | 설명                          |
| --------------------------- | ------------ | ----------------------------- |
| id                          | VARCHAR(255) | 상품 ID (Primary Key)         |
| product_code                | VARCHAR(100) | 상품 코드                     |
| product_name                | VARCHAR(500) | 상품명                        |
| product_summary             | TEXT         | 상품 요약                     |
| product_description         | TEXT         | 상품 설명                     |
| target_description          | TEXT         | 대상 설명                     |
| loan_limit_description      | TEXT         | 대출 한도 설명                |
| loan_period_guide           | TEXT         | 대출 기간 안내                |
| repayment_method            | VARCHAR(200) | 상환 방법                     |
| min_interest_rate           | DECIMAL(5,2) | 최저 금리                     |
| max_interest_rate           | DECIMAL(5,2) | 최고 금리                     |
| required_documents          | TEXT         | 필요 서류                     |
| searchable_text             | TEXT         | 검색 가능 텍스트 (원본)       |
| cleaned_searchable_text     | TEXT         | 전처리된 텍스트 (BM25용)      |
| searchable_text_embedding   | vector(1536) | 벡터 임베딩 (의미 검색용)     |

## 성능 특징

- **데이터셋**: 67개 농협 대출 상품
- **임베딩 차원**: 1536 (OpenAI text-embedding-3-small)
- **검색 속도**: < 1초 (벡터 검색 + BM25 통합)
- **정확도**: 의미 기반 검색으로 높은 재현율(Recall) 달성

## 주요 기능

### ✅ 완료된 기능
- [x] ParadeDB (PostgreSQL + pgvector) 연동
- [x] 대출 상품 데이터 로드 및 전처리
- [x] OpenAI 임베딩 생성 및 저장
- [x] BM25 전문 검색
- [x] 벡터 유사도 검색
- [x] RRF를 통한 하이브리드 검색
- [x] CLI 인터페이스
- [x] Windows 한글 출력 지원

### 🚀 향후 개선 가능 사항
- [ ] BM25 인덱스 최적화 (ParadeDB pg_search)
- [ ] 벡터 인덱스 생성 (IVFFlat/HNSW)
- [ ] 검색 결과 하이라이팅
- [ ] 필터링 기능 (금리, 대출 유형 등)
- [ ] REST API 추가

## 참고 자료

- [ParadeDB Documentation](https://docs.paradedb.com)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Reciprocal Rank Fusion Paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

## 문제 해결

### Docker 컨테이너 관리

```bash
# 컨테이너 상태 확인
docker ps -a | grep paradedb

# 컨테이너 중지
docker stop hybrid-search-paradedb

# 컨테이너 재시작
docker start hybrid-search-paradedb

# 로그 확인
docker logs hybrid-search-paradedb
```

### 한글 출력 오류

Windows 콘솔에서 한글이 깨지는 경우:
- 이미 `main.py`에서 UTF-8 인코딩 처리됨
- 문제 발생 시 환경 변수 설정: `set PYTHONIOENCODING=utf-8`

### 임베딩 생성 오류

1. OPENAI_API_KEY 확인
2. OpenAI API 할당량 확인
3. 인터넷 연결 확인

### 데이터베이스 연결 오류

1. ParadeDB 컨테이너 실행 상태 확인
2. .env 파일의 DATABASE_URL 확인 (포트 5433)
3. 방화벽 설정 확인

# LangGraph RAG - 설치 및 설정 가이드

## 1. 사전 요구사항

- Python 3.11+
- PostgreSQL with ParadeDB extensions
- OpenAI API Key

## 2. 환경 설정

### 2.1 .env 파일 생성

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/postgres
```

또는 `C:\Users\skyop\jaeho_template\dotenv_windows`에 환경 변수를 설정할 수 있습니다.

### 2.2 데이터베이스 설정

#### ParadeDB Docker 실행

```bash
docker run -d \
  --name hybrid-search-paradedb \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -p 5433:5432 \
  paradedb/paradedb:latest
```

#### 데이터베이스 초기화

```bash
cd ../hybrid_search
python -m search_app.setup
```

이 명령어는:
- pgvector와 pg_search 확장 설치
- loan_products 테이블 생성
- 대출 상품 데이터 로드 (67개)
- OpenAI 임베딩 생성 (1536차원)
- BM25 및 벡터 검색 인덱스 생성

## 3. 패키지 설치

### 3.1 pip 사용

```bash
pip install -r requirements.txt
```

### 3.2 uv 사용 (권장)

```bash
uv pip install -r requirements.txt
```

필요한 패키지:
- langgraph>=1.0.0
- langchain>=0.3.0
- langchain-openai>=0.2.0
- openai>=1.0.0
- psycopg>=3.0.0
- python-dotenv>=1.0.0
- numpy>=1.24.0
- kiwipiepy>=0.17.0
- typing-extensions>=4.0.0

## 4. 설치 확인

### 4.1 Import 테스트

```bash
python -c "from langgraph_rag import LangGraphRAG; print('Import successful')"
```

### 4.2 데이터베이스 연결 테스트

```bash
cd ../hybrid_search
python -c "from search_app.database import Database; db = Database(); db.connect(); print('DB connected'); db.close()"
```

## 5. 사용법

### 5.1 기본 실행

```bash
python langgraph_rag.py "의사 전용 대출 상품 추천해줘"
```

### 5.2 디버그 모드

```bash
python langgraph_rag.py "저금리 대출 찾고 있어요" --debug
```

### 5.3 uv 사용

```bash
uv run python langgraph_rag.py "질문"
```

## 6. 테스트

```bash
python test_langgraph_rag.py
```

테스트 항목:
1. Direct Question (검색 불필요)
2. Search Question (검색 필요)
3. Low Interest Rate Search (구체적 검색)

## 7. 문제 해결

### 7.1 OPENAI_API_KEY not found

`.env` 파일에 OpenAI API 키가 설정되어 있는지 확인하세요.

```bash
# .env 파일 확인
cat .env

# 또는 환경 변수 확인
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows CMD
```

### 7.2 Database connection error

1. ParadeDB Docker가 실행 중인지 확인:
   ```bash
   docker ps | grep paradedb
   ```

2. 데이터베이스 URL이 올바른지 확인:
   ```bash
   python -c "from search_app.config import Config; print(Config.get_connection_string())"
   ```

3. 데이터베이스 초기화가 완료되었는지 확인:
   ```bash
   cd ../hybrid_search
   python -m search_app.setup
   ```

### 7.3 Import errors

필요한 패키지가 모두 설치되었는지 확인:

```bash
python -m pip list | grep -E "(langgraph|langchain|openai)"
```

## 8. 디렉토리 구조

```
11.VibeCoding_for_Agent/
├── LangGraph_RAG/              # 이 프로젝트
│   ├── langgraph_rag.py        # 메인 스크립트
│   ├── test_langgraph_rag.py   # 테스트 스크립트
│   ├── requirements.txt        # 의존성
│   ├── .env.example            # 환경 변수 예제
│   ├── README.md               # 사용 가이드
│   ├── SETUP.md                # 이 파일
│   └── PRD.md                  # 프로젝트 요구사항
│
└── hybrid_search/              # 하이브리드 검색 시스템
    ├── search_app/
    │   ├── hybrid_search.py    # 검색 로직
    │   ├── database.py         # DB 연결
    │   ├── config.py           # 설정
    │   └── ...
    └── loan_products.json      # 대출 상품 데이터
```

## 9. 추가 정보

- **LangGraph 문서**: https://github.com/langchain-ai/langgraph
- **Hybrid Search 시스템**: `../hybrid_search/README.md`
- **프로젝트 요구사항**: `PRD.md`
- **사용 가이드**: `README.md`

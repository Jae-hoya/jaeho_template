# 의존성 가이드

## 독립 실행 구조

✓ **이 프로젝트는 이제 독립적으로 실행됩니다!**

`search_app` 모듈이 프로젝트 내부에 포함되어 있어 외부 의존성 없이 실행할 수 있습니다.

### 프로젝트 구조

```
LangGraph_RAG/                  # 이 프로젝트 (독립 실행)
├── search_app/                 # 하이브리드 검색 모듈 (포함됨)
│   ├── __init__.py
│   ├── hybrid_search.py        # HybridSearch 클래스
│   ├── database.py             # Database 클래스
│   ├── config.py               # Config 클래스
│   ├── data_loader.py
│   ├── main.py
│   └── setup.py
├── langgraph_rag.py            # 메인 CLI
├── loan_products.json          # 대출 상품 데이터
└── ...
```

### 포함된 모듈

langgraph_rag.py는 다음 모듈을 직접 import합니다:

```python
from search_app.hybrid_search import HybridSearch
from search_app.database import Database
from search_app.config import Config
```

## 변경 이력

### 이전 구조 (의존성 있음)

```
11.VibeCoding_for_Agent/
├── hybrid_search/              # 외부 의존성
│   └── search_app/
└── LangGraph_RAG/              # 이 프로젝트
    └── langgraph_rag.py        # ../hybrid_search에서 import
```

**문제점**:
- 외부 디렉토리에 의존
- 프로젝트 이동 시 경로 문제
- 배포 복잡도 증가

### 현재 구조 (독립 실행)

```
LangGraph_RAG/                  # 모든 것이 포함됨
├── search_app/                 # 내부 모듈
└── langgraph_rag.py            # search_app에서 직접 import
```

**장점**:
- ✓ 외부 의존성 없음
- ✓ 프로젝트 이동 용이
- ✓ 배포 간단
- ✓ 독립적인 버전 관리

## 실행 전 확인사항

### 1. search_app 디렉토리 확인

```bash
ls -la search_app/
```

다음 파일들이 있어야 합니다:
- `__init__.py`
- `hybrid_search.py`
- `database.py`
- `config.py`
- `data_loader.py`
- `main.py`
- `setup.py`

### 2. 데이터 파일 확인

```bash
ls -la loan_products.json
```

loan_products.json 파일이 있어야 합니다. 없다면:

```bash
cp ../hybrid_search/loan_products.json ./
```

### 3. 환경 변수 설정

`.env` 파일 생성:

```bash
cp .env.example .env
# OPENAI_API_KEY 설정
```

### 4. 데이터베이스 초기화

```bash
python -m search_app.setup
```

## Import 테스트

```bash
python -c "from langgraph_rag import LangGraphRAG; print('Import successful')"
```

성공하면 모든 준비가 완료된 것입니다!

## 문제 해결

### ModuleNotFoundError: No module named 'search_app'

**원인**: search_app 디렉토리가 없거나 손상됨

**해결**:
```bash
# search_app 디렉토리 확인
ls -la search_app/

# 없다면 원본에서 복사
cp -r ../hybrid_search/search_app ./
```

### 환경 변수 에러

```
ValueError: OPENAI_API_KEY not found in environment variables
```

**해결**:
1. `.env` 파일 생성
2. `OPENAI_API_KEY=your_key_here` 추가

### 데이터베이스 연결 에러

**해결**:
1. ParadeDB Docker 실행 확인
2. DATABASE_URL 확인
3. 데이터베이스 초기화 실행

## 원본 프로젝트와의 관계

이 프로젝트의 `search_app` 모듈은 `../hybrid_search/search_app`에서 복사되었습니다.

### 업데이트 방법

원본 hybrid_search가 업데이트되었다면:

```bash
# 백업
mv search_app search_app.backup

# 최신 버전 복사
cp -r ../hybrid_search/search_app ./

# 테스트
python -c "from langgraph_rag import LangGraphRAG; print('OK')"
```

### 독립적인 수정

`search_app` 모듈을 이 프로젝트에 맞게 수정할 수 있습니다:
- 원본 hybrid_search에 영향 없음
- 독립적인 버전 관리
- 프로젝트별 최적화 가능

## 요약

✓ **search_app 포함**: 외부 의존성 없이 독립 실행
✓ **간단한 배포**: 프로젝트 디렉토리만 복사하면 됨
✓ **독립적 관리**: 원본과 독립적으로 수정 가능
✓ **이동 용이**: 어디든 이동 가능

이제 이 프로젝트는 완전히 독립적으로 실행됩니다!

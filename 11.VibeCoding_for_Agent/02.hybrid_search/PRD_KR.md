PRD 문서를 만들고 그 문서를 바탕으로 구현하는것. 이때, thinking mode 키기기

# 대출 상품 하이브리드 검색 시스템 - PRD

## 개요
Neon PostgreSQL을 사용하여 BM25와 벡터 검색을 결합한 Python 기반 하이브리드 검색 시스템

## 기술 스택
- **언어**: Python
- **패키지 매니저**: uv
- **데이터베이스**: Neon PostgreSQL (pgvector, pg_search 확장)
- **임베딩 모델**: OpenAI text-embedding-3-small
- **데이터베이스 드라이버**: psycopg2
- **환경**: `C:\Users\skyop\jaeho_template` 경로의 dotenv 가상환경

## 데이터베이스 설정
- **MCP**: Neon MCP
- **프로젝트**: nonghyup-loan
- **테이블**: loan_products

## 데이터 스키마
`loan_products` 테이블 구성:
- `loan_products.json` 원본 대출 상품 데이터
- `searchable_text`: 원본 검색 가능 텍스트
- `cleaned_searchable_text`: 특수문자 제거된 전처리 텍스트 (BM25용)
- `searchable_text_embedding`: 벡터 임베딩 (의미 검색용)

## 핵심 기능

### 1. 데이터 적재
`loan_products.json` 파일의 대출 상품 데이터를 `loan_products` 테이블에 저장

### 2. 텍스트 전처리
BM25 검색 최적화를 위해 `searchable_text`에서 특수문자를 제거하여 `cleaned_searchable_text` 생성

### 3. 임베딩 생성
`searchable_text`에 대한 임베딩을 생성하여 `searchable_text_embedding` 컬럼에 저장

### 4. 하이브리드 검색
`hybrid_search()` 함수 구현:
- `cleaned_searchable_text`로 BM25 검색 수행
- `searchable_text_embedding`으로 벡터 검색 수행
- RRF(Reciprocal Rank Fusion)로 결과 결합
- 참고: https://docs.paradedb.com/documentation/guides/hybrid
- 두 검색 모두 테이블 전체를 대상으로 수행

## CLI 사용법
```bash
uv run python ... "의사 전용 대출"
```

## 구현 참고사항
- 구현 세부사항은 AI 판단에 유연하게 맡김
- 핵심 기능과 아키텍처에 집중
- SQL 최적화 및 세부 구현은 개발 단계에서 결정

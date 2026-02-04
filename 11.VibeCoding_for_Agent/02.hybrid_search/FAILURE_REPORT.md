# 실패 가능성 리포트 (코드베이스 점검)

## 개요
코드베이스를 정적 점검한 결과, 실행/설정 환경에 따라 실패하거나 불안정해질 수 있는 **잠재적** 이슈가 몇 가지 확인되었습니다. 아래는 재현 조건과 영향 범위를 포함한 요약입니다.

## 1) 의존성 불일치 (psycopg vs psycopg2)
- **위치**: `pyproject.toml` / `search_app/database.py`
- **내용**: `pyproject.toml`은 `psycopg2-binary`를 설치하도록 되어 있으나, 코드에서는 `import psycopg`(psycopg3)를 사용합니다.
- **영향**: `pip install -e .` 또는 `pip install`만 수행한 환경에서 `ModuleNotFoundError: No module named 'psycopg'` 발생 가능.
- **재현**: `pip install -e .` 후 `python -m search_app.main "의사 전용 대출"` 실행

## 2) OPENAI_API_KEY 미설정 시 전면 실패
- **위치**: `search_app/config.py`
- **내용**: 모듈 import 시점에 `Config.validate()`가 호출되어 OPENAI_API_KEY가 없으면 예외 발생.
- **영향**: DB 연결 확인, BM25-only 테스트 등 임베딩이 필요 없는 작업도 실행 불가.
- **재현**: `.env`에 OPENAI_API_KEY 미설정 상태에서 `python -m search_app.main "쿼리"`

## 3) ParadeDB BM25 인덱스 미존재 시 쿼리 실패
- **위치**: `search_app/hybrid_search.py` (`bm25_search`)
- **내용**: `BM25_MODE=paradedb`인 경우 `@@@` 쿼리를 실행하지만, 인덱스가 없으면 에러가 발생.
- **영향**: `search_app.setup`을 수행하지 않았거나 인덱스 생성 실패 시 검색이 즉시 실패.
- **재현**: 인덱스 생성 실패 상태에서 `BM25_MODE=paradedb`로 검색 실행

## 4) 데이터 로딩 중 실패 시 트랜잭션 롤백 누락
- **위치**: `search_app/data_loader.py` (`load_data`)
- **내용**: `insert_product` 실패 시 예외를 출력하고 continue하지만, 트랜잭션 rollback이 없음.
- **영향**: 한 번이라도 INSERT가 실패하면 커넥션이 오류 상태로 남아 이후 INSERT/COMMIT이 연쇄 실패할 수 있음.
- **재현**: 데이터 한 건의 스키마 불일치/타입 오류 등으로 INSERT 실패 유도

## 5) 벡터 인덱스 생성 실패 후 롤백 없음
- **위치**: `search_app/database.py` (`create_vector_index`)
- **내용**: 인덱스 생성 실패 시 rollback이 없어 이후 트랜잭션 상태가 불안정할 수 있음.
- **영향**: 설정/로드 과정에서 벡터 인덱스 생성 실패 후 커밋/추가 쿼리 실패 가능.
- **재현**: pgvector 미설치 환경에서 `search_app.setup` 실행

## 결론
- **즉시 실패 가능성이 높은 항목**: (1) psycopg 의존성 불일치, (2) OPENAI_API_KEY 미설정 시 전면 실패, (3) BM25 인덱스 미존재 시 쿼리 오류.
- **데이터 정합성/안정성 이슈**: (4), (5) 트랜잭션 롤백 누락.
- 모든 항목은 **실제 환경/설정에 따라 발생할 수 있는 실패 가능성**으로, 현재 환경에서 반드시 재현된 문제는 아닙니다.



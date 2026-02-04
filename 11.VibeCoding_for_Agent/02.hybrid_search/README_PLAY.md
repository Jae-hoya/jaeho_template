# 왜 PRD 프롬프트가 중요한가?
AI 에이전트는 사람이 아니기 때문에 필요한 모든 맥락을 명확하게 제공해야 한다

나쁜 예시:
하이브리드 검색을 만들어줘

좋은 예시:
Neon PostgreSQL의 loan_products 테이블에서
pgvector(코사인 유사도)와 pg_search(paradedb)를
RRF 알고리즘으로 결합한 Python CLI 구현.
text-embedding-3-small 사용

## Neon MCP 서버 연결하기
Hybrid Search 구현을 위해 Neon PostgreSQL을 Claude Code와 연결.

claude mcp add --transport http neon https://mcp.neon.tech/mcp -s project

claude mcp add --transport http neon https://mcp.neon.tech/mcp (전역역)

출처: https://neon.com/guides/claude-code-mcp-neon

## ParadeDB Hybrid Search 가이드
### Hybrid Search란?
ParadeDB의 Hybrid Search는 Full-text Search(BM25)와 Similarity Search(Vector)를 결합한 검색 방식입니다.

### RRF (Reciprocal Rank Fusion) 알고리즘
Hybrid Search의 핵심은 두 검색 결과를 어떻게 결합하는가입니다. ParadeDB는 RRF 알고리즘을 사용합니다.

RRF 동작 방식:
1. BM25 점수와 Similarity 점수로 각각 문서의 상위 결과 계산
2. 각 검색 방식별로 문서 순위 매기기
3. Reciprocal Rank 계산: 1/(k + r)
   - k: 일반적으로 60 (조정 가능)
   - r: 해당 문서의 순위
4. 두 Reciprocal Rank를 합산하여 최종 Hybrid Search 점수 생성


---
### PRD 작성 시 체크리스트
AI가 좋아하는 PRD
✅ 정확한 기술 스택 (pgvector, OpenAI 모델명, PostgreSQL 확장) 
✅ 명확한 입출력 정의 (CLI 명령어 예시)
✅ 구체적인 알고리즘 (RRF 공식, 코사인 거리) 
✅ 실제 데이터 정보 (테이블명, 컬럼명, 데이터 개수)

AI가 싫어하는 PRD
❌ "좋은 검색 시스템 만들어줘" 
❌ "적당히 하이브리드 검색해줘" 
❌ 버전 정보 없음 
❌ 모호한 요구사항

-----------------------------------------------------------------------

#  PRD 프롬프트
스펙:
- Python, uv 패키지 매니저
- Neon PostgreSQL (pgvector, pg_search 확장)
- OpenAI text-embedding-3-small
- psycopg2
- C:\Users\skyop\jaeho_template경로에서 dotenv_windows 가상환경 사용

데이터베이스:
- Neon MCP 사용
- 프로젝트: nonghyup-loan
- 테이블: loan_products

핵심 기능:
- 대출 상품 데이터 파일(loan_products.json)을 loan_products 테이블에 저장
- 대출 상품이 searchable_text 를 bm25로 검색하기 좋게 특수문자 제거하여 cleaned_searchable_text 생성 -> bm25 search
- searchable_text 를 embedding해서 searchable_text_embedding에 저장 -> vector search
- hybrid_search(): RRF로 vector, bm25 search 결합
  - https://docs.paradedb.com/documentation/guides/hybrid 참고 구현
  - bm25, vector search 할 때는 테이블 전체를 대상으로 계산

CLI 동작:
uv run python ... "의사 전용 대출"

주의:
- PRD는 핵심만 간략하게
- 구체적인 SQL 코드 작성하지 않기
- 구현 세부사항은 AI에게 맡기기


---
@PRD.md 를 바탕으로 구현해줘 
                                                                                                                                                          
작업순서                                                                                                                                                 
1. @loan_productions.json 를 데이터베이스에 NEON MCP를 사용해서 저장해                                                                                   
2. Hybrid search 구현해. search_app/ 디렉토리를 만들어서 아래에 파이썬 파일을 저장해줘   


  ---
@search_app/.env 파일 만들어줘. 


---
이제 검색 실행해볼래? 

가상환경은 C:\Users\skyop\jaeho_template경로에서 dotenv_windows 가상환경 사용하면 돼돼

(postgtres 비밀번호: postgres)
(-> docker를 이용해 postgres sql을 사용했다.)
(인증문제가 발생하여, ParadeDB사용. 근데 애초에 ParadeDB 써달랬는데, env떄문에 postgres를 한거같다.)

---
잘 안되는거 같은데, ParadeDB 를 사용해보는건 어떄? 


(paradedb : https://docs.paradedb.com/documentation/guides/hybrid)

---
(한글이 깨져서)
한글이 깨지면 안돼

---

(BM25 검색이 0이다.)
bm25 검색이 제대로 되는건지 검토해.
https://paradedb-dev.mintlify.app/documentation/guides/hybrid
이것과 코드가 다른가?

---

(만약 여전히 안된다면)
문제 상황을 정리해서 실패 리포트를 작성해줘.
동작이나 테스트에도 문제가 있다면 포함해도 좋아.

---

햇살론이 bm25 서치하는 필드에 있는지 검토 해줄래?

----
ngram 또는 kiwi토크나이저 토큰을 자르는게 성능에 더 도움이 될 수 있지 않을까?

---
(결과적으로 정확도가 올랐다)
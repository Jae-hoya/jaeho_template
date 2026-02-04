/mcp 로 neon 연결 되어있는지 확인

입력:
Neon에 "Recruit-service-demo"라는 이름의 프로젝트 만들어줘
----------------------------------------------------------------------------------------------------
입력:
"Recruit-service-demo" 프로젝트에 candidates 테이블을 만들어줘
컬럼은 id, name, position, skills(배열), company, created_at


### 생성된것

- 적용 위치: square-dew-10756324 / main / neondb
- 테이블: public.candidates

public.candidates 컬럼은 아래와 같아요.
- id (bigint, not null, 기본값: 시퀀스)
- name (text, not null)
- position (text, not null)
- skills (text[] 배열, not null, 기본값: 빈 배열)
- company (text, not null)
- created_at (timestamptz, not null, 기본값: now())
----------------------------------------------------------------------------------------------------
# Mock Data 생성

## 직군별 스킬 예시

### Developer
Backend: Python/Django, Java/Spring Boot, Go/Kubernetes, Node.js

Frontend: React, Vue.js, TypeScript, Next.js

Mobile: Swift/iOS, Kotlin/Android, Flutter

특수: Machine Learning, Blockchain, Game Development

### Designer
UI/UX: Figma, Sketch, Adobe XD, Prototyping

Visual: Branding, Illustration, Motion Graphics

System: Design System, Component Library, Tokens

Specialized: 3D Design, Game UI, Data Visualization

### PM
Method: Agile, Scrum, OKR, Lean Startup

Analytics: SQL, Data Analysis, A/B Testing

Domain: E-commerce, Fintech, Healthcare, Gaming

### Marketer
Digital: SEO, Google Analytics, Performance Marketing

Content: Copywriting, Content Strategy, Brand Storytelling

Growth: Growth Hacking, Viral Marketing, Community Management

Channel: Social Media, Influencer, Email Marketing

----
위 데이터를 참고해서 넣어줄래? insert_candidates.sql 이름으로 넣어주면 돼.
----------------------------------------------------------------------------------------------------
입력:
neon mcp를 통해서.
recruit-service-demo 프로젝트에 insert_candidates.sql 파일의 내용을 실행해줘.
insert_candidates.sql 파일을 읽어서 recruit-service-demo 프로젝트의 candidates 테이블에 데이터를 삽입해줘

올바르게 들어갔는지 테스트도 해줘
----------------------------------------------------------------------------------------------------
입력:
recruit-service-demo 프로젝트의 connection string을 알려줘
postgresql://neondb_owner:npg_Rg60QLPdmVDG@ep-wild-recipe-afcbq7r1-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require
----------------------------------------------------------------------------------------------------
입력:

recursive_mcp_server를 구현해줘

Python으로 PostgreSQL MCP 서버를 구현해줘.

기본 요구사항:
1. https://github.com/modelcontextprotocol/servers-archived/tree/main/src/postgres
   참고해서 읽기 전용 query tool 구현
2. 안전한 update_candidate tool 추가 구현

update_candidate tool 설계:
- position, skills, company 필드만 변경 가능
- name과 id는 변경 불가 (보안상 중요)
- SQL Injection 방지를 위한 파라미터화된 쿼리 사용
- 명시적 파라미터만 허용 (임의의 SQL 실행 금지)

프로젝트 구조:
- server.py: 메인 서버 코드
- pyproject.toml: 패키지 설정 (mcp, asyncpg 의존성)
- README.md: 사용 가이드

이후 잘돌아가는지 확인해달라 하기
인코딩 문제가 발생해서, 인코딩 해달라고 함
----------------------------------------------------------------------------------------------------
@server.py 의 구현내용을 자세히 설명해줘
이 내용을 readme.md 에도 추가해줘

---
구성 개요
- stdio 기반 MCP 서버를 띄우고, PostgreSQL에 asyncpg로 연결하는 최소한의 런타임이야.
- 도구는 두 개:
  - query: 읽기 전용 SQL만 허용
  - update_candidate: position, skills, company만 업데이트 허용
주요 흐름
- SERVER_NAME, SERVER_VERSION 같은 상수로 서버 식별.
- 전역 _pool에 커넥션 풀을 잡아두고, ensure_pool()로 안전하게 접근.
연결 URL 처리
- get_connection_url()는
  - CLI 첫 번째 인자 우선
  - 없으면 환경 변수(DATABASE_URL, POSTGRES_URL, PG_URL) 순회
  - 둘 다 없으면 에러 발생
SQL 안전 장치
- normalize_sql():
  - 문자열인지 확인
  - 공백/빈 문자열 차단
  - 세미콜론 제거 후에도 세미콜론이 남으면 “다중 statement”로 차단
- is_read_only_sql():
  - 첫 토큰이 SELECT, WITH, SHOW, EXPLAIN, VALUES인지 확인
입력 검증 헬퍼
- coerce_int() → 숫자 문자열/정수만 허용, bool 금지
- coerce_str() → 공백 없는 문자열만 허용
- coerce_skills() → 문자열 배열만 허용
도구 등록 (list_tools)
- query:
  - 입력: { "sql": "..." }
  - additionalProperties: false
- update_candidate:
  - 입력: { "id": 1, "position": "...", "skills": [...], "company": "..." }
  - id 필수, 나머지는 선택
  - additionalProperties: false
도구 실행 (call_tool)
- query:
  - SQL 타입 검사 → 단일/읽기 전용 검사
  - READ ONLY 트랜잭션으로 실행
  - 결과를 JSON으로 반환 (default=str로 datetime 처리)
- update_candidate:
  - 허용 필드 화이트리스트로 unknown 필드 차단
  - id 강제 검증
  - 바꿀 값 하나도 없으면 에러
  - 파라미터 바인딩으로 UPDATE (SQL injection 방지)
  - 변경된 row를 반환, 없으면 updated: false
실행 루프
- main()에서 asyncpg.create_pool()로 풀 생성
- stdio_server() 컨텍스트에서 MCP 서버 실행
- 종료 시 풀 안전하게 close
----------------------------------------------------------------------------------------------------


김민준 님의 회사를 제일기획으로 옮겨줘
insert_candidates.sql도 바꿔줘야해

ex)
다양한 업데이트 시나리오
시나리오 1: 회사 변경
"김민준 님의 회사를 카카오로 변경해줘"


시나리오 2: 스킬 추가
"ID 3번 후보자에게 Docker 스킬 추가해줘"


시나리오 3: 직군 변경
"강수빈빈 님이 PM으로 직군을 변경했어"

"배수아 님이 네이버로 이직하고 TypeScript, Go 스킬을 추가했어"
----------------------------------------------------------------------------------------------------
입력:

opencode와 claude desktop에 연결할 수 있게 db table의 주소를 찾아서 @opencode.json 와 .mcp.json.example에 수정해.
mcp.json.example은, https://modelcontextprotocol.io/legacy/tools/debugging 를 기반으로 작성해 줘야해.
---
입력:
recursive_mcp를 이용해서 python mcp 개발자 조회해줘

노서윤씨 네이버로 이직했어

노서윤씨 데이터 조회해줘
----------------------------------------------------------------------------------------------------
입력:
풀스텍 개발자를 찾아줘. 프론트엔드와 백엔드를 둘 다 할수 있는 사람말야.

남예은 씨를 풀스텍 개발자가 되도록 업데이트 해줘.
풀스텍 개발자 조회해줘
# MCP 분석 리포트

## 범위
- 대상: `mcp/` 모노레포와 `amazon-bedrock-agentcore-mcp-server`
- 목적: 하위 MCP 서버 관리 방식 파악, AgentCore 서버 구조/핵심기능/데이터 흐름 정리

## 1. 하위 MCP 서버 관리 방식
- 모노레포 구조: 서버별 패키지를 `mcp/src/<server>-mcp-server/`에 독립적으로 배치하고, 서버마다 `README.md`, `pyproject.toml`, `tests/`를 포함함. `mcp/DEVELOPER_GUIDE.md`
- 설계 표준화: 패키지 네이밍/엔트리포인트/모듈 분리를 `mcp/DESIGN_GUIDELINES.md`로 고정해 일관성을 보장함.
- 신규 서버 생성 절차: cookiecutter 템플릿으로 생성 후 문서/사이드바/서버 카드 업데이트를 요구함. `mcp/DEVELOPER_GUIDE.md`
- 카탈로그 운영: 루트 `mcp/README.md`에서 모든 서버 목록과 클라이언트별 설치 예시를 유지함.
- 품질 검증 스크립트: README 패키지명 일치 검사 `mcp/scripts/verify_package_name.py`, `awslabs` 네임스페이스 검증 `mcp/scripts/verify_awslabs_init.py`
- 테스트 정책: 서버별 단위/통합 테스트를 `tests/`에 배치하고 공통 테스트 프레임워크를 제공함. `mcp/testing/README.md`
- 릴리스/배포: 변경 디렉터리를 감지해 PyPI/컨테이너 배포를 자동화함. `mcp/.github/workflows/release.yml`

## 2. AgentCore MCP Server 핵심기능
- 문서 검색: `llms.txt` 기반 큐레이션 URL을 인덱싱하고 TF-IDF + Markdown 가중치로 랭킹 제공. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/indexer.py`
- 스니펫 하이드레이션: 상위 결과만 온디맨드로 본문을 가져와 스니펫 생성(기본 최대 5개). `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/cache.py`
- 문서 원문 조회: URL 검증 → fetch/정제 → 전체 본문 반환. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/docs.py`
- 운영 가이드 툴: Runtime/Memory/Gateway 운영 절차를 문서 형태로 제공. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/runtime.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/memory.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/gateway.py`
- 안전한 문서 접근: allowlist 도메인 검증과 상대 경로 보정으로 접근 범위를 제한. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/url_validator.py`
- 성능 최적화: 초기에는 링크/타이틀만 로드하고 본문은 필요 시 로딩. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/cache.py`

## 3. AgentCore MCP Server 구성요소

### 3.1 패키지/엔트리
- 메타/의존성: `mcp/src/amazon-bedrock-agentcore-mcp-server/pyproject.toml`
- 버전 정보: `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/__init__.py`
- 서버 엔트리: `FastMCP` 생성 후 툴 등록, `main()`에서 캐시 준비 후 실행. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/server.py`

### 3.2 Tools (MCP 표면)
- `search_agentcore_docs`: 인덱스 검색 + 스니펫 생성. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/docs.py`
- `fetch_agentcore_doc`: 특정 URL의 전체 본문 반환. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/docs.py`
- `manage_agentcore_runtime`: 배포/운영 CLI 가이드 반환. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/runtime.py`
- `manage_agentcore_memory`: 메모리 리소스 CLI 가이드 반환. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/memory.py`
- `manage_agentcore_gateway`: 게이트웨이 배포/운영 가이드 반환. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/gateway.py`

### 3.3 Config / Utils
- 설정 값: `llm_texts_url` 기본값은 `https://aws.github.io/bedrock-agentcore-starter-toolkit/llms.txt`. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/config.py`
- 설정 값: `timeout` 30s, `user_agent`는 `agentcore-mcp-docs/1.0`. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/config.py`
- 캐시 상태: `_INDEX`, `_URL_CACHE`, `_URL_TITLES`, `_LINKS_LOADED`로 상태를 관리. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/cache.py`
- 캐시 로딩: `load_links_only()`로 링크만 인덱싱, `ensure_page()`로 본문을 필요 시 로딩. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/cache.py`
- 인덱서: Markdown 헤더/코드/링크 가중치와 제목 부스트를 적용하는 TF-IDF 검색. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/indexer.py`
- 문서 수집: `urllib.request`로 fetch, HTML 정제/타이틀 추출 후 `Page`로 반환. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/doc_fetcher.py`
- 텍스트 처리: 타이틀 결정 규칙과 스니펫 생성 로직 제공. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/text_processor.py`
- URL 검증: 허용 도메인 allowlist와 상대 경로 보정 처리. `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/url_validator.py`

### 3.4 테스트
- 문서 검색/원문 조회 툴: `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_server.py`
- Runtime/Memory/Gateway 가이드 툴: `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_tools.py`
- 캐시/인덱스/텍스트 처리/URL 검증: `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_cache.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_indexer.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_text_processor.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_url_validator.py`
- 설정/버전: `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_config.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/tests/test_init.py`

## 4. AgentCore 데이터 흐름 다이어그램 요약

```mermaid
flowchart TD
  A[Server Start] --> B[cache.ensure_ready()]
  B --> C[load_links_only()]
  C --> D[Index: titles + urls only]

  E[search_agentcore_docs] --> F[IndexSearch.search()]
  F --> G{Top N results}
  G --> H[cache.ensure_page()]
  H --> I[doc_fetcher.fetch_and_clean]
  I --> J[text_processor.make_snippet]
  J --> K[Search Response]

  L[fetch_agentcore_doc] --> H
  H --> M[Full Document Response]
```

- 서버 시작 시 `llms.txt` 링크만 로드해 인덱스를 구성하고 본문은 로딩하지 않음.
- 검색 요청은 인덱스에서 랭킹 후 상위 결과만 하이드레이션하여 스니펫을 생성함.
- 원문 조회는 URL 검증 → fetch/정제 → 캐시 저장 → 전체 본문 반환 흐름을 따름.

## 5. 주요 코드 경로
- 서버 엔트리/등록: `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/server.py`
- 문서 검색/원문 조회: `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/tools/docs.py`
- 캐시/인덱스: `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/cache.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/indexer.py`
- 문서 수집/정제: `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/doc_fetcher.py`, `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/text_processor.py`
- URL 검증: `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/utils/url_validator.py`
- 설정: `mcp/src/amazon-bedrock-agentcore-mcp-server/awslabs/amazon_bedrock_agentcore_mcp_server/config.py`

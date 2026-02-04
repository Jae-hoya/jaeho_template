---
description: Generate an MCP server with cookiecutter, then implement tools from an XLS API spec and sample data.
---

You are creating a new MCP server.

Inputs
- Template path: $1 (default: ./cookiecutter_template)
- Output directory: $2 (default: .)
- API spec: XLS file provided by the user
- Example data files: provided by the user

Workflow
1. Resolve the template path and output directory. If the target output already exists, ask for a new output directory before continuing.
2. Run cookiecutter first to generate the project.
   - Use `cookiecutter <template> --no-input` when no custom metadata is provided.
   - If the user provides `project_domain`, `author_name`, `author_email`, `description`, or `instructions`, pass them via `--extra-context` and still use `--no-input`.
3. Locate the generated project directory and confirm the path before editing files.
4. Read the XLS spec and example data.
   - If XLS parsing is not possible with available tooling, ask the user for a CSV export or a text summary of endpoints and fields.
5. Implement the MCP server based on the spec and sample data.
   - Update tool definitions in `awslabs/.../tools/` to match endpoints, names, and parameters.
   - Implement API calls in `utils/api_client.py` with proper request/response handling.
   - Register tools in `server.py`.
   - Update `config.py` for required env vars and defaults.
6. Tests and quality.
   - Follow TDD: write a failing test first, implement, then refactor.
   - Add/update tests in `tests/` to cover the new tools.
7. Documentation.
   - Update `README.md` when tools or env vars change.
8. Report results and any gaps.

Rules
- Follow TDD (failing test -> implementation -> refactor).
- Keep commits atomic; stage only files related to the change.
- Never run `git push`.
- Avoid logging secrets or API keys.

Output format
- Explain what was generated and modified with file paths.
- List tests run or state they were not run.
- Call out any missing inputs required to proceed.

---

한국어 안내

입력값
- 템플릿 경로: $1 (기본값: ./cookiecutter_template)
- 출력 디렉터리: $2 (기본값: .)
- API 명세서: 사용자 제공 XLS
- 예시 데이터: 사용자 제공 파일

작업 흐름
1. 템플릿 경로와 출력 디렉터리를 확인합니다. 출력 경로가 이미 존재하면 새 경로를 요청합니다.
2. cookiecutter로 프로젝트를 먼저 생성합니다.
   - 커스텀 메타데이터가 없으면 `cookiecutter <template> --no-input`을 사용합니다.
   - `project_domain`, `author_name`, `author_email`, `description`, `instructions`가 제공되면 `--extra-context`로 전달하고 `--no-input`을 유지합니다.
3. 생성된 프로젝트 경로를 확인한 뒤 파일을 수정합니다.
4. XLS 명세서와 예시 데이터를 읽습니다.
   - XLS 파싱이 불가능하면 CSV 내보내기 또는 엔드포인트/필드 요약을 요청합니다.
5. 명세와 예시 데이터에 맞게 MCP 서버를 구현합니다.
   - `awslabs/.../tools/`의 도구 정의를 엔드포인트/파라미터에 맞게 갱신합니다.
   - `utils/api_client.py`에 실제 API 호출 로직을 구현합니다.
   - `server.py`에 도구 등록을 추가합니다.
   - 필요한 환경 변수/기본값은 `config.py`에 반영합니다.
6. 테스트 및 품질.
   - TDD: 실패하는 테스트 작성 -> 구현 -> 리팩터링 순서.
   - `tests/`에 새 도구 테스트를 추가/수정합니다.
7. 문서.
   - 도구나 환경 변수가 바뀌면 `README.md`를 갱신합니다.
8. 결과 요약 및 부족한 입력값을 보고합니다.

규칙
- TDD 기반으로 진행합니다.
- 커밋은 atomic 단위로 유지하고 관련 파일만 스테이징합니다.
- `git push`는 실행하지 않습니다.
- 비밀값/API 키는 로그에 남기지 않습니다.

출력 형식
- 생성/수정된 파일 경로와 변경 요약을 제공합니다.
- 실행한 테스트 또는 미실행 여부를 명시합니다.
- 진행에 필요한 누락 입력을 알립니다.

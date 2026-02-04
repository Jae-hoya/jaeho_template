# Linear Issues Creation Command

Linear MCP를 사용하여 fastcampus-seminar-02 팀에 구조화된 이슈를 생성합니다.
메인 이슈를 생성하고, 모든 서브 이슈를 메인 이슈 하위에 연결합니다.

## 실행 흐름

### 1단계: 팀 정보 조회
`mcp__linear__search-teams` 도구로 "fastcampus-seminar-02" 팀을 검색하여 팀 ID를 획득합니다.

### 2단계: 사용자 입력 수집
AskUserQuestion 도구를 사용하여 다음 정보를 수집합니다:

**메인 이슈 정보:**
- 제목 (title): 프로젝트/에픽의 전체 목표
- 설명 (description): 상세 내용

**서브 이슈 목록:**
각 서브 이슈에 대해:
- 제목
- 설명 (선택)
- 우선순위: urgent(0), high(1), medium(2), low(3)

### 3단계: 메인 이슈 생성
`mcp__linear__create-issue` 도구로 메인 이슈를 먼저 생성합니다.

```
mcp__linear__create-issue:
  - teamId: (1단계에서 조회한 팀 ID)
  - title: (메인 이슈 제목)
  - description: (메인 이슈 설명)
  - priority: 1 (High)
```

생성된 메인 이슈의 ID를 저장합니다.

### 4단계: 서브 이슈 생성 (메인 이슈에 연결)
각 서브 이슈를 생성할 때 `parentId`에 메인 이슈 ID를 설정하여 모두 메인 이슈 하위에 연결합니다.

```
mcp__linear__create-issue:
  - teamId: (팀 ID)
  - title: (서브 이슈 제목)
  - description: (서브 이슈 설명)
  - parentId: (메인 이슈 ID)  <-- 핵심: 모든 서브 이슈가 메인에 연결
  - priority: (우선순위)
```

### 5단계: 결과 리포트
생성된 모든 이슈 정보를 정리하여 출력합니다:

```
## 생성 완료

**메인 이슈:**
- [TEAM-123] 메인 이슈 제목
  URL: https://linear.app/team/issue/TEAM-123

**서브 이슈:**
- [TEAM-124] 서브 이슈 1 (Parent: TEAM-123)
- [TEAM-125] 서브 이슈 2 (Parent: TEAM-123)
- [TEAM-126] 서브 이슈 3 (Parent: TEAM-123)
```

## 이슈 구조 예시

```
[메인 이슈] MCP 서버 개발 프로젝트
    ├── [서브 이슈 1] 요구사항 분석
    ├── [서브 이슈 2] API 설계
    ├── [서브 이슈 3] 코어 기능 구현
    ├── [서브 이슈 4] 테스트 작성
    └── [서브 이슈 5] 문서화
```

## 우선순위 가이드

| 값 | 레벨 | 설명 |
|---|------|------|
| 0 | Urgent | 긴급하고 중요한 작업 |
| 1 | High | 높은 우선순위 |
| 2 | Medium | 중간 우선순위 (기본값) |
| 3 | Low | 낮은 우선순위 |

## 지금 실행

위 단계에 따라 fastcampus-seminar-02 팀에 이슈를 생성합니다.
먼저 팀 정보를 조회하고, 사용자에게 이슈 정보를 물어본 후 생성을 진행합니다.

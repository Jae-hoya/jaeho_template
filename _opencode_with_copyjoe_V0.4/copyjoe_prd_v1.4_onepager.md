# Copyjoe PRD v1.4 One Pager

기준 문서: `copyjoe_prd_v1.4.md`  
작성일: 2026-02-18

## 제품 한 줄

Copyjoe는 RAG와 웹 컨텍스트를 결합해 **전환형 카피를 빠르게 생성하고 반복 개선**할 수 있게 하는 마케팅 카피 플랫폼이다.

## 왜 필요한가

- 카피 제작 속도가 느려 실험 사이클이 지연된다.
- 작성자별 품질 편차가 크다.
- 내부 문서/랜딩/웹 근거가 반영되지 않으면 설득력이 떨어진다.

## v1.4 핵심 결정

1. 생성 API 단일화: `POST /api/v1/copy/generate`
2. 서비스 단일화: `CopyService`에서 structured/prompt mode 통합 처리
3. 프롬프트 품질 안정화: 영어 중심 지시문 정비(특히 `qwen3:8b` 대응)
4. 근거 유지: 업로드 문서 RAG + 랜딩/웹 컨텍스트 결합

## 사용자와 기대 가치

- 퍼포먼스 마케터: CTR/전환 개선 문구를 빠르게 A/B 실험
- 콘텐츠 마케터: 채널별 카피 변형을 일관된 품질로 생성
- AE/기획자: 고객 근거 기반 설득 문안 신속 제시

## 핵심 기능

- 카피 생성(`head/body/cta/slogan/sns/description`)
- storyboard 초안 생성(`storyboard_outline`)
- 자유형 prompt 기반 생성 + assumptions 제공
- 파일 업로드/변환/인덱싱 기반 RAG
- 웹 검색/랜딩 분석 기반 컨텍스트 주입
- 결과 내보내기(`.docx`, `.doc`, `.md`)
- 쓰레드 기반 이력 관리

## 단일 엔드포인트 계약

`POST /api/v1/copy/generate`는 두 입력 모드를 지원한다.

- Structured mode
  - 입력: `CopyGenerateRequest`
  - 출력: `CopyGenerateResponse`
- Prompt mode
  - 입력: `CopyLiteRequest`
  - 출력: `CopyLiteResponse` (`assistant_message`, `assumptions`, `normalized_request`, `result`)

## 운영 정책 요약

- 업로드 제한: 최대 30MB, 최대 10개/요청
- 확장자: pdf/doc/docx/txt/xls/xlsx/ppt/pptx/png/jpg/jpeg/webp
- RAG 백엔드: Milvus 우선, 미설정 시 memory fallback
- 헬스/계약 가시성: `/health`, `/docs`, `/openapi.json`

## 성공 기준 (DoD)

- 단일 생성 endpoint로 structured/prompt 모두 정상 동작
- 프론트 생성/개선 플로우가 단일 endpoint로 안정 동작
- RAG/웹 근거가 결과 `sources`에 반영
- export/history/meta API 정상 동작
- `python -m pytest -q`, `cd frontend && npm run build` 통과

## v1.4 변경 포인트

- `/api/v1/copy/generate-lite` 제거, `/api/v1/copy/generate`로 통합
- `CopyLiteService` 제거, `CopyService`로 통합
- 프론트/스크립트/테스트의 레거시 경로 참조 제거
- 용어를 `prompt mode` 중심으로 정리

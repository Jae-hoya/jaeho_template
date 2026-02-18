# Golden Datasets

이 디렉토리는 Copyjoe 서비스용 한국어 골든 데이터셋을 담고 있습니다.

## 파일

- `golden_qa_v1_ko.jsonl`
  - 형식: JSON Lines (한 줄에 한 샘플)
  - 샘플 수: 36
  - 도메인: 입력 필드 설명, objective 선택, language/alias, 간편 대화형 동작, 개선 재생성, 랜딩 분석 해석, API 사용법

- `golden_marketer_copy_ideas_v1_ko.jsonl`
  - 형식: JSON Lines (한 줄에 한 샘플)
  - 샘플 수: 12
  - 도메인: 실제 마케터 질문(성과 지표/채널 맥락) + 기대 카피 아이디어 세트
  - 추천 용도: 생성 품질 평가(질문 -> 카피 아이디어 정합성)

## 스키마

각 라인은 아래 키를 가집니다.

- `id`: 샘플 ID
- `category`: 분류
- `question`: 사용자 질문
- `expected_answer`: 기대 답변
- `must_include`: 정답 판정 시 포함 권장 키워드

## 사용 예시

평가 시 다음처럼 쓸 수 있습니다.

1. `question`을 모델에 입력
2. 모델 응답 생성
3. `expected_answer` 의미 일치 여부 확인
4. `must_include` 키워드 포함률로 자동 점수 보조

## Marketer Copy Ideas 스키마

`golden_marketer_copy_ideas_v1_ko.jsonl` 각 라인은 아래 키를 가집니다.

- `id`: 샘플 ID
- `marketer_question`: 실제 마케터 질문
- `brief`: 구조화된 캠페인 맥락
  - `product_name`, `target_audience`, `pain_point`, `differentiator`, `objective`, `channel`, `tone`, `language`
- `expected_copy_ideas`: 기대 카피 아이디어 배열
  - 각 아이디어는 `head`, `body`, `cta`, `slogan`, `sns`, `description`
- `expected_storyboard_outline`: 기대 스토리보드 흐름
- `expected_rationale`: 기대 설득 논리
- `must_include_keywords`: 정합성 점검 키워드

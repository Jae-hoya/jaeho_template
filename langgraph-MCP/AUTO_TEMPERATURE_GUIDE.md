# 🌡️ Auto Temperature 기능 가이드

## 개요

V2의 새로운 자동화 기능으로 MCP가 알아서 최적의 temperature를 찾고 비교해줍니다!

더 이상 temperature를 직접 설정하느라 고민할 필요가 없습니다. 🎉

## 🆕 새로운 Tools

### 1. `retrieve_with_temperature_comparison` 🌡️

여러 temperature 값으로 검색하고 결과를 자동으로 비교 분석합니다.

#### 기능
- ✅ 여러 temperature로 동시에 쿼리 확장
- ✅ 각 temperature별 검색 수행
- ✅ 결과를 시각적으로 비교
- ✅ 자동 분석 및 추천

#### 사용법
```python
# 기본 사용 (0.3, 0.7, 0.9 비교)
await retrieve_with_temperature_comparison(
    query="인공지능 윤리"
)

# 커스텀 temperature 지정
await retrieve_with_temperature_comparison(
    query="딥러닝",
    temperatures=[0.2, 0.5, 0.8],
    retriever_mode="compression",
    fetch_k=20,
    top_n=5
)
```

#### 출력 예시
```
================================================================================
🌡️  Temperature 비교 검색
================================================================================

원본 쿼리: 인공지능 윤리
비교할 Temperature: [0.3, 0.7, 0.9]
검색 모드: compression

================================================================================

🌡️  Temperature 0.3 (보수적)
------------------------------------------------------------
  원본: 인공지능 윤리
  확장1: AI 윤리 원칙
  확장2: 인공지능 책임과 규제
  확장3: AI 개발의 윤리적 고려사항

🌡️  Temperature 0.7 (균형잡힌)
------------------------------------------------------------
  원본: 인공지능 윤리
  확장1: AI 기술의 도덕적 영향
  확장2: 인공지능 시대의 가치와 책임
  확장3: 머신러닝 알고리즘의 공정성

🌡️  Temperature 0.9 (매우 창의적)
------------------------------------------------------------
  원본: 인공지능 윤리
  확장1: AI가 인류에게 미치는 철학적 문제
  확장2: 로봇과 인간의 공존을 위한 윤리 체계
  확장3: 디지털 지능의 도덕적 딜레마

================================================================================
📊 각 Temperature별 검색 결과
================================================================================

🌡️  Temperature 0.3 (보수적)
   검색 결과: 8개 문서
------------------------------------------------------------
   [Document 1] ...
   [Document 2] ...
   [Document 3] ...

🌡️  Temperature 0.7 (균형잡힌)
   검색 결과: 12개 문서
   ...

🌡️  Temperature 0.9 (매우 창의적)
   검색 결과: 15개 문서
   ...

================================================================================
🎯 분석 및 추천
================================================================================

📈 문서 개수:
   0.3 (보수적         ):  8개 ████
   0.7 (균형잡힌       ): 12개 ██████
   0.9 (매우 창의적    ): 15개 ███████

💡 추천:
   • 가장 많은 결과: Temperature 0.9 (15개)
   • 가장 집중된 결과: Temperature 0.3 (8개)

   • 전체 고유 문서 수: 18개
   • 평균 문서 수: 11.7개

   ⚠️  Temperature에 따라 결과가 크게 달라집니다!
      다양한 관점이 필요하면 높은 temperature를 추천합니다.
================================================================================
```

---

### 2. `retrieve_auto_optimized` 🤖

MCP가 자동으로 최적의 temperature를 선택해서 검색합니다.

#### 기능
- ✅ 3가지 temperature(0.3, 0.7, 0.9) 자동 테스트
- ✅ 최적의 temperature 자동 선택
- ✅ 선택 이유 설명
- ✅ 바로 사용 가능한 검색 결과 반환

#### 사용법
```python
# 쿼리만 입력하면 끝!
await retrieve_auto_optimized(
    query="생성형 AI의 미래"
)

# 고급 설정
await retrieve_auto_optimized(
    query="트랜스포머 아키텍처",
    retriever_mode="compression",
    fetch_k=30,
    top_n=10
)
```

#### 출력 예시
```
================================================================================
🤖 자동 최적화 검색
================================================================================

원본 쿼리: 생성형 AI의 미래
테스트 중인 Temperature: [0.3, 0.7, 0.9]

⏳ 최적의 temperature를 찾는 중...

   Temperature 0.3: 7개 문서 발견
   Temperature 0.7: 11개 문서 발견
   Temperature 0.9: 14개 문서 발견

✅ 선택된 최적 Temperature: 0.7
   (너무 적지도(7개), 많지도(14개) 않은 11개 문서)

================================================================================
🎯 최적화된 검색 결과
================================================================================

=== Document 1 ===
[문서 내용...]

=== Document 2 ===
[문서 내용...]

...
```

---

## 🎯 언제 어떤 Tool을 사용할까?

### Temperature 비교 (`retrieve_with_temperature_comparison`)

#### 이럴 때 사용하세요:
- ✅ Temperature를 어떻게 설정할지 모를 때
- ✅ 각 temperature의 효과를 보고 싶을 때
- ✅ 다양한 관점을 모두 확인하고 싶을 때
- ✅ 실험적으로 검색 전략을 탐색할 때
- ✅ 보고서나 분석 자료가 필요할 때

#### 장점:
- 📊 상세한 비교 분석
- 📈 시각적 차트
- 💡 구체적인 추천
- 🔍 모든 결과를 한눈에

#### 단점:
- ⏱️ 시간이 조금 더 걸림 (여러 번 검색)
- 💰 API 비용이 더 많이 듦

---

### 자동 최적화 (`retrieve_auto_optimized`)

#### 이럴 때 사용하세요:
- ✅ 빠르게 최고 품질의 결과를 원할 때
- ✅ Temperature 설정을 MCP에게 맡기고 싶을 때
- ✅ 균형잡힌 검색 결과가 필요할 때
- ✅ 초보자이거나 추천이 필요할 때

#### 장점:
- 🚀 간단한 사용법 (쿼리만 입력)
- 🎯 바로 사용 가능한 결과
- 🤖 MCP의 똑똑한 선택
- 💼 프로덕션에 바로 적용

#### 단점:
- 📊 상세 비교는 없음
- 🎛️ 사용자 선택권 적음

---

## 🔥 실전 예제

### 예제 1: 기술 문서 검색
```python
# Temperature 비교로 최적 값 찾기
result = await retrieve_with_temperature_comparison(
    query="Transformer 아키텍처 구조",
    temperatures=[0.2, 0.4, 0.6],  # 기술 문서는 보수적으로
    retriever_mode="compression"
)
```

### 예제 2: 트렌드 조사
```python
# 자동 최적화로 빠르게
result = await retrieve_auto_optimized(
    query="2024년 AI 산업 전망",
    fetch_k=30,
    top_n=10
)
```

### 예제 3: 창의적 탐색
```python
# 높은 temperature들로 비교
result = await retrieve_with_temperature_comparison(
    query="메타버스와 AI의 융합",
    temperatures=[0.7, 0.8, 0.9, 1.0],  # 창의적 범위
    retriever_mode="compression"
)
```

### 예제 4: 프로덕션 환경
```python
# 자동 최적화 - 안정적이고 빠름
result = await retrieve_auto_optimized(
    query=user_input_query,  # 사용자 입력
    retriever_mode="compression"
)
```

---

## 📊 Temperature 선택 로직

### `retrieve_auto_optimized`의 선택 기준:

1. **3가지 temperature 테스트**: 0.3, 0.7, 0.9
2. **평균 계산**: 각 temperature의 문서 개수 평균
3. **최적 선택**: 평균에 가장 가까운 temperature
4. **이유**: 너무 적지도, 많지도 않은 균형잡힌 결과

#### 예시:
```
Temperature 0.3: 5개 문서
Temperature 0.7: 10개 문서  ← 선택! (평균 10개에 가장 가까움)
Temperature 0.9: 15개 문서

평균: 10개
```

---

## 🎨 출력 형식 비교

| 특징 | Temperature 비교 | 자동 최적화 |
|------|------------------|-------------|
| 쿼리 확장 표시 | ✅ 모든 temperature | ❌ |
| 검색 결과 | 📊 요약 (상위 3개) | ✅ 전체 |
| 분석 차트 | ✅ | ❌ |
| 추천 사항 | ✅ 상세 | ✅ 간단 |
| 최종 결과 | ❌ | ✅ |

---

## 💡 Pro Tips

### Tip 1: 탐색 단계
```python
# 먼저 비교로 탐색
comparison = await retrieve_with_temperature_comparison(query="...")
# 결과를 보고 최적 temperature 파악

# 이후 해당 temperature로 본격 검색
result = await retrieve(query="...", temperature=optimal_temp)
```

### Tip 2: 빠른 프로토타입
```python
# 자동 최적화로 빠르게 시작
result = await retrieve_auto_optimized(query="...")
# 만족스러우면 그대로 사용!
```

### Tip 3: A/B 테스트
```python
# 사용자 그룹 A: 보수적
# 사용자 그룹 B: 창의적
comparison = await retrieve_with_temperature_comparison(
    query="...",
    temperatures=[0.3, 0.9]
)
```

---

## 🚀 빠른 실행

### 데모 실행
```bash
python demo_auto_temperature.py
```

이 데모는:
1. Temperature 비교 검색 시연
2. 자동 최적화 검색 시연
3. 결과 분석 및 추천

---

## 📚 관련 문서

- [ENHANCED_RETRIEVER_GUIDE.md](./ENHANCED_RETRIEVER_GUIDE.md) - 전체 가이드
- [QUICK_START_V2.md](./QUICK_START_V2.md) - 빠른 시작
- [demo_comparison_v2.py](./demo_comparison_v2.py) - 종합 데모
- [demo_auto_temperature.py](./demo_auto_temperature.py) - Temperature 데모

---

**MCP가 알아서 최적의 temperature를 찾아드립니다! 🌡️✨**















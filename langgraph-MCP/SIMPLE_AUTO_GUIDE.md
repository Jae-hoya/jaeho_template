# 🎯 간단 자동 최적화 가이드

## 핵심 개념

**MCP가 내부적으로 여러 temperature를 테스트하고, 가장 좋은 결과만 반환합니다.**

비교 과정은 보여주지 않고, **최종 답변만 깔끔하게** 제공합니다.

---

## 🚀 사용법

### 방법 1: `retrieve_auto_optimized` (추천)

가장 간단합니다. 쿼리만 입력하면 끝!

```python
# 이게 전부입니다!
result = await retrieve_auto_optimized(query="인공지능 윤리")
```

**동작:**
1. 내부에서 0.3, 0.7, 0.9 세 가지 temperature로 테스트
2. 가장 균형잡힌 결과를 선택
3. **최종 문서만 반환** (비교 과정 없음)

**출력:**
```
=== Document 1 ===
[문서 내용...]

=== Document 2 ===
[문서 내용...]

...
```

---

### 방법 2: `retrieve` + `auto_optimize_temperature=True`

기존 retrieve 함수에 자동 최적화 옵션 추가

```python
result = await retrieve(
    query="딥러닝 활용 사례",
    use_expansion=True,
    auto_optimize_temperature=True,  # 🔥 이것만 추가!
    retriever_mode="compression"
)
```

**장점:**
- 기존 retrieve의 모든 옵션 사용 가능
- auto_optimize_temperature만 True로 설정하면 됨

---

## 📊 비교: Before vs After

### ❌ Before (수동)
```python
# Temperature를 직접 설정해야 함
result1 = await retrieve(query="...", temperature=0.3)  # 이게 좋을까?
result2 = await retrieve(query="...", temperature=0.7)  # 이게 더 나을까?
result3 = await retrieve(query="...", temperature=0.9)  # 다시 해보자...

# 결과를 직접 비교하고 선택해야 함 😰
```

### ✅ After (자동)
```python
# MCP가 알아서 최적값을 찾아서 결과만 반환
result = await retrieve_auto_optimized(query="...")  # 끝! 😎
```

---

## 🎯 콘솔 로그 (디버깅용)

사용자에게는 결과만 보이지만, 콘솔(서버 로그)에는 과정이 기록됩니다:

```
[V2 Auto] 쿼리: 인공지능 윤리
[V2 Auto] Temperature 자동 최적화 중... ([0.3, 0.7, 0.9])
[V2 Auto] Temperature 0.3: 8개
[V2 Auto] Temperature 0.7: 12개
[V2 Auto] Temperature 0.9: 15개
[V2 Auto] 최적 Temperature 선택: 0.7 (12개 문서)
```

**사용자 응답:**
```
=== Document 1 ===
[문서 내용...]

=== Document 2 ===
[문서 내용...]
...
```

깔끔하죠? 🎉

---

## 💡 옵션: 과정도 보고 싶다면?

```python
# show_process=True로 설정
result = await retrieve_auto_optimized(
    query="AI 트렌드",
    show_process=True  # 과정 표시
)
```

**출력:**
```
[Enhanced Retriever V2 - Auto Optimized]
최적 Temperature: 0.7 (자동 선택)
검색 결과: 12개 문서

============================================================

=== Document 1 ===
[문서 내용...]
...
```

---

## 🎨 실전 예제

### 예제 1: 가장 간단한 사용
```python
# 이게 전부!
result = await retrieve_auto_optimized(query="생성형 AI")
```

### 예제 2: 고급 설정
```python
result = await retrieve_auto_optimized(
    query="트랜스포머 아키텍처",
    retriever_mode="compression",  # Reranking 사용
    fetch_k=30,
    top_n=10
)
```

### 예제 3: retrieve 함수 사용
```python
result = await retrieve(
    query="메타버스",
    use_expansion=True,
    auto_optimize_temperature=True,  # 자동 최적화
    retriever_mode="compression",
    fetch_k=20,
    top_n=5
)
```

---

## 🆚 Tool 선택 가이드

| 상황 | 추천 Tool |
|------|-----------|
| 가장 쉽게 사용하고 싶다 | `retrieve_auto_optimized()` |
| 세밀한 제어도 필요하다 | `retrieve(..., auto_optimize_temperature=True)` |
| 비교 과정도 보고 싶다 | `retrieve_with_temperature_comparison()` |
| 직접 temperature 설정 | `retrieve(..., temperature=0.7)` |

---

## ⚙️ 최적화 알고리즘

**어떻게 선택하나요?**

1. **3가지 temperature 테스트**: 0.3 (보수적), 0.7 (균형), 0.9 (창의적)
2. **문서 개수 확인**: 각 temperature마다 검색된 문서 수
3. **평균 계산**: 세 개의 평균
4. **최적 선택**: 평균에 가장 가까운 값

**예시:**
```
Temperature 0.3: 5개  ← 너무 적음
Temperature 0.7: 10개 ← 선택! (평균 10개)
Temperature 0.9: 15개 ← 너무 많음

평균: 10개
최적: 0.7 (평균에 가장 가까움)
```

**이유:** 너무 적으면 정보가 부족하고, 너무 많으면 노이즈가 있을 수 있음. 균형잡힌 중간값을 선호!

---

## 🎁 보너스 팁

### Tip 1: 빠른 프로토타입
```python
# 프로토타입 개발 시 이것만 사용
result = await retrieve_auto_optimized(query=user_query)
# temperature 고민 없이 바로 사용 가능!
```

### Tip 2: 프로덕션 환경
```python
# 안정적이고 균형잡힌 결과
result = await retrieve_auto_optimized(
    query=user_query,
    retriever_mode="compression"  # 품질 향상
)
```

### Tip 3: 디버깅
```python
# 콘솔 로그를 확인하면 어떤 temperature가 선택됐는지 알 수 있음
result = await retrieve_auto_optimized(query="...")
# 서버 로그: [V2 Auto] 최적 Temperature 선택: 0.7 (12개 문서)
```

---

## 📚 더 알아보기

- **상세 가이드**: [AUTO_TEMPERATURE_GUIDE.md](./AUTO_TEMPERATURE_GUIDE.md)
- **빠른 시작**: [QUICK_START_V2.md](./QUICK_START_V2.md)
- **전체 문서**: [ENHANCED_RETRIEVER_GUIDE.md](./ENHANCED_RETRIEVER_GUIDE.md)

---

## 요약

```python
# 이전: Temperature 직접 고민
result = await retrieve(query="...", temperature=???)  # 뭘 써야 하지? 🤔

# 지금: MCP가 알아서 해줌
result = await retrieve_auto_optimized(query="...")  # 끝! 😎
```

**MCP가 내부적으로 테스트하고, 최적 결과만 반환합니다!** 🎯✨















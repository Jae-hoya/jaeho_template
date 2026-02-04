# 평가 코드 및 동작 설명

## 평가 코드(요약)
아래 코드는 실제 실행에 사용한 로직을 정리한 요약본입니다. 하이브리드/단독 비교와 Recall/MAP/MRR 계산을 모두 포함합니다.

## 실행 코드 참고
- 실제 실행은 `SEARCH_EVAL_RUN.py`를 참고했습니다.

```python
# 1) 쿼리셋과 키워드 정의
cases = [
    {"query": "의사 전용 대출", "keywords": ["의료", "의사", "전문직", "메디", "프로"]},
    # ... (40개 쿼리)
]

# 2) 휴리스틱 라벨링
# - 각 문서의 텍스트 필드에 키워드가 포함되면 관련 문서로 판정
# - 관련 문서 집합은 전체 데이터셋에서 키워드가 포함된 문서 ID로 구성

def is_relevant(product, keywords):
    fields = [
        product["product_name"],
        product["product_summary"],
        product["product_description"],
        product["target_description"],
        product["loan_limit_description"],
        product["loan_period_guide"],
        product["repayment_method"],
        product["required_documents"],
    ]
    haystack = " ".join([f for f in fields if f])
    return any(k in haystack for k in keywords)

# 3) 하이브리드 검색 실행
# - BM25(paradedb/fts) + vector + RRF
results = search.search(query, limit=10, search_limit=20)

# 4) 단독 검색 실행
# - bm25_only: bm25_search만 실행 후 결과 상세 조회
# - vector_only: vector_search만 실행 후 결과 상세 조회

# 5) 메트릭 계산
# Precision@K
precision_k = relevant_in_top_k / K

# Recall@K
recall_k = relevant_in_top_k / total_relevant

# MAP@K (Average Precision)
# AP@K = Σ(P@i * rel_i) / total_relevant

# MRR@K
# MRR@K = 1 / (첫 관련 문서 순위)

# NDCG@K
# DCG@K = Σ(rel_i / log2(i + 1))
# NDCG@K = DCG@K / IDCG@K

# Overlap@K
# Overlap@K = |A_K ∩ B_K| / K
```

## 실제 실행 흐름
1. **쿼리셋 정의**: 12개/40개 쿼리와 해당 키워드 리스트를 준비합니다.
2. **휴리스틱 라벨 생성**: 전체 상품 데이터에서 키워드가 포함된 문서를 관련 문서로 정의합니다.
3. **검색 실행**:
   - 하이브리드: `search.search()`로 BM25+벡터+RRF 결합 결과를 가져옵니다.
   - 단독: `bm25_search()` 또는 `vector_search()`로 상위 결과만 가져옵니다.
4. **메트릭 계산**: Precision, Recall, MAP, MRR, NDCG를 각 쿼리별로 계산 후 평균을 냅니다.
5. **요약 정리**: 결과를 `SEARCH_EVAL_SUMMARY.md`에 반영합니다.

## 참고
- 실제 실행 스크립트는 임시 파일로 생성/실행 후 정리했습니다.
- 현재 결과는 휴리스틱 라벨 기반이므로 참고용입니다.

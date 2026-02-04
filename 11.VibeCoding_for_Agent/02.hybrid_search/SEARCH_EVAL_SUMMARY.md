# Hybrid Search 변경 및 평가 통합 요약

## 변경 요약
- 기존 BM25는 ParadeDB가 아니라 PostgreSQL FTS(tsvector + ts_rank)였음.
- ParadeDB BM25 쿼리로 전환: `@@@` + `paradedb.score(id)` 사용.
- `BM25_MODE` 환경변수로 `paradedb`/`fts` 전환 가능.
- BM25 인덱스 생성 옵션을 ParadeDB 가이드 방식으로 수정.
- 인덱스 생성 실패 시 rollback 추가.

## 정확도 평가 1 (12쿼리, 자동 라벨)
- 방식: 쿼리 12개, 상위 10개 결과, 키워드 포함 여부로 관련성 판정

| Metric | ParadeDB BM25 | FTS (tsvector/ts_rank) | Diff |
| --- | ---: | ---: | ---: |
| Precision@5 | 0.700 | 0.700 | 0.000 |
| Precision@10 | 0.625 | 0.625 | 0.000 |
| NDCG@10 | 0.953 | 0.953 | 0.000 |
| Overlap@10 | 1.000 | 1.000 | 0.000 |

## 정확도 평가 2 (40쿼리, 자동 라벨)
- 방식: 쿼리 40개, 상위 10개 결과, 키워드 포함 여부로 관련성 판정

| Metric | ParadeDB BM25 | FTS (tsvector/ts_rank) | Diff |
| --- | ---: | ---: | ---: |
| Precision@5 | 0.675 | 0.675 | 0.000 |
| Precision@10 | 0.613 | 0.615 | -0.002 |
| NDCG@10 | 0.875 | 0.875 | -0.000 |
| Overlap@10 | 0.997 | 0.997 | 0.000 |

## 하이브리드 vs 단독 비교 (40쿼리, 자동 라벨)
- 방식: 쿼리 40개, 상위 10개 결과, 키워드 포함 여부로 관련성 판정
- Hybrid는 BM25(paradedb) + vector + RRF 조합

| Metric | Hybrid | BM25 only | Vector only |
| --- | ---: | ---: | ---: |
| Precision@5 | 0.675 | 0.665 | 0.640 |
| Precision@10 | 0.613 | 0.515 | 0.570 |
| NDCG@10 | 0.875 | 0.918 | 0.831 |

## 메트릭 설명
- Precision@K: 상위 K개 결과 중 관련 문서 비율. `Precision@K = (관련 문서 수@K) / K`
- Recall@K: 전체 관련 문서 중 상위 K개에서 찾은 비율. `Recall@K = (관련 문서 수@K) / (전체 관련 문서 수)`
- MAP@K: 쿼리별 Average Precision의 평균. `AP@K = Σ(P@i * rel_i) / (전체 관련 문서 수)`
- MRR@K: 첫 관련 문서 순위의 역수 평균. `MRR@K = 평균(1 / 첫 관련 문서 순위)`
- NDCG@K: 상위 K개에서 관련 문서가 앞쪽에 올수록 높은 점수(순위 품질 반영).
  - `DCG@K = Σ(rel_i / log2(i + 1))`
  - `NDCG@K = DCG@K / IDCG@K`
- Overlap@K: 두 검색 모드의 상위 K개 결과 집합이 얼마나 겹치는지 비율로 측정.
  - `Overlap@K = |A_K ∩ B_K| / K`

예시: 상위 5개 중 3개가 관련이면 `Precision@5 = 3/5 = 0.6`.

### 휴리스틱 라벨 기준
- 각 쿼리에 키워드 리스트를 정의하고, 결과 문서의 텍스트 필드에 해당 키워드가 포함되면 관련으로 판정
- 관련 문서 집합은 전체 데이터셋에서 키워드가 포함된 문서를 모두 모아서 구성

### 이번 평가 값 요약
- 12쿼리 평균 (하이브리드, ParadeDB/FTS 동일): Recall@10 0.444, MAP@10 0.405, MRR@10 0.958
- 40쿼리 평균 (하이브리드, ParadeDB): Recall@10 0.386, MAP@10 0.345, MRR@10 0.858
- 40쿼리 평균 (하이브리드, FTS): Recall@10 0.385, MAP@10 0.344, MRR@10 0.858
- Hybrid vs 단독(40쿼리 평균):
  - Hybrid Recall@10 0.386 / MAP@10 0.345 / MRR@10 0.858
  - BM25 only Recall@10 0.329 / MAP@10 0.306 / MRR@10 0.950
  - Vector only Recall@10 0.369 / MAP@10 0.286 / MRR@10 0.815
- 12쿼리 평균: Precision@5 0.700, Precision@10 0.625, NDCG@10 0.953, Overlap@10 1.000
- 40쿼리 평균: Precision@5 0.675, Precision@10 0.613, NDCG@10 0.875, Overlap@10 0.997
- Hybrid vs 단독(40쿼리 평균): Hybrid P@5 0.675 / P@10 0.613 / NDCG@10 0.875
- Kiwi vs Simple (40쿼리, 휴리스틱 라벨):
  - Hybrid simple: P@10 0.610, NDCG@10 0.877, Recall@10 0.384, MAP@10 0.343, MRR@10 0.871
  - Hybrid kiwi:   P@10 0.670, NDCG@10 0.923, Recall@10 0.434, MAP@10 0.403, MRR@10 0.938
  - BM25 simple:   P@10 0.515, NDCG@10 0.918, Recall@10 0.329, MAP@10 0.306, MRR@10 0.950
  - BM25 kiwi:     P@10 0.715, NDCG@10 0.936, Recall@10 0.455, MAP@10 0.446, MRR@10 0.938

## 해석 요약
- BM25 모드 비교에서는 결과가 거의 동일했고, Overlap@10이 매우 높음.
- 하이브리드는 Precision@10에서 단독 방식보다 높았음.
- 자동 라벨(키워드 포함) 기반이라 정답 라벨 평가보다 거칠 수 있음.
- 실행 참고 코드: `SEARCH_EVAL_RUN.py`

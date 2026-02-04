import os
import math
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
from search_app.database import Database
from search_app.hybrid_search import HybridSearch


@dataclass
class QueryCase:
    query: str
    keywords: List[str]


CASES_12 = [
    QueryCase("의사 전용 대출", ["의료", "의사", "전문직", "메디", "프로"]),
    QueryCase("소상공인 대출", ["소상공인", "개인사업자", "자영업", "사업자"]),
    QueryCase("전세자금대출", ["전세", "전세자금", "보증"]),
    QueryCase("주택담보대출", ["주택", "담보", "주거"]),
    QueryCase("개인택시 대출", ["개인택시", "택시"]),
    QueryCase("공무원 대출", ["공무원", "소방", "경찰", "해양경찰", "히어로"]),
    QueryCase("국가유공자 대출", ["국가유공", "나라사랑", "보훈"]),
    QueryCase("오피스텔 담보대출", ["오피스텔", "담보"]),
    QueryCase("사업자 신용대출", ["사업자", "기업", "신용", "자영업"]),
    QueryCase("전세 보증보험", ["보증", "서울보증", "전세"]),
    QueryCase("저금리 대출", ["저금리", "우대", "특별", "금리"]),
    QueryCase("신용대출", ["신용", "신용대출"]),
]

CASES_40 = [
    QueryCase("의사 전용 대출", ["의료", "의사", "전문직", "메디", "프로"]),
    QueryCase("치과의사 대출", ["치과", "의료", "전문직"]),
    QueryCase("전문직 신용대출", ["전문직", "의사", "변호", "회계", "신용"]),
    QueryCase("공무원 대출", ["공무원", "소방", "경찰", "해양경찰", "히어로"]),
    QueryCase("군인 대출", ["군인", "장병", "군"]),
    QueryCase("국가유공자 대출", ["국가유공", "나라사랑", "보훈"]),
    QueryCase("교직원 대출", ["교직", "교사", "교원"]),
    QueryCase("직장인 신용대출", ["직장", "샐러리", "신용", "회사"]),
    QueryCase("개인사업자 대출", ["개인사업자", "사업자", "자영업"]),
    QueryCase("소상공인 대출", ["소상공인", "개인사업자", "자영업", "사업자"]),
    QueryCase("법인 대출", ["법인", "기업", "회사"]),
    QueryCase("스타트업 대출", ["스타트업", "창업", "벤처"]),
    QueryCase("프랜차이즈 대출", ["프랜차이즈", "가맹"]),
    QueryCase("수출기업 대출", ["수출", "무역", "기업"]),
    QueryCase("중소기업 대출", ["중소", "기업", "SME"]),
    QueryCase("매출 연동 대출", ["매출", "사업", "기업"]),
    QueryCase("운전자금 대출", ["운전자금", "운영", "자금"]),
    QueryCase("시설자금 대출", ["시설", "설비", "자금"]),
    QueryCase("전세자금대출", ["전세", "전세자금", "보증"]),
    QueryCase("전세 보증보험", ["보증", "서울보증", "전세"]),
    QueryCase("전세대출 갈아타기", ["전세", "갈아타", "대환"]),
    QueryCase("월세 보증금 대출", ["월세", "보증금"]),
    QueryCase("주택담보대출", ["주택", "담보", "주거"]),
    QueryCase("아파트 담보대출", ["아파트", "담보", "주택"]),
    QueryCase("오피스텔 담보대출", ["오피스텔", "담보"]),
    QueryCase("주거용 오피스텔 대출", ["오피스텔", "주거", "담보"]),
    QueryCase("전세 사잇돌대출", ["사잇돌", "전세", "중금리"]),
    QueryCase("저금리 대출", ["저금리", "우대", "특별", "금리"]),
    QueryCase("중금리 대출", ["중금리", "사잇돌", "금리"]),
    QueryCase("고금리 대출", ["고금리", "금리"]),
    QueryCase("모바일 대출", ["모바일", "비대면", "온라인"]),
    QueryCase("비대면 대출", ["비대면", "모바일", "온라인"]),
    QueryCase("신용대출", ["신용", "신용대출"]),
    QueryCase("마이너스통장", ["한도", "마이너스", "통장"]),
    QueryCase("대환대출", ["대환", "갈아타", "전환"]),
    QueryCase("보증서 담보대출", ["보증서", "신용보증", "기금"]),
    QueryCase("서울보증보험 대출", ["서울보증", "보증", "보험"]),
    QueryCase("개인택시 대출", ["개인택시", "택시"]),
    QueryCase("의료인 우대대출", ["의료", "의사", "우대", "전문직"]),
    QueryCase("소방 경찰 대출", ["소방", "경찰", "해양경찰", "히어로"]),
]

K = 10


def normalize(text: str) -> str:
    return (text or "").lower()


def is_relevant(product: Dict[str, str], keywords: List[str]) -> bool:
    fields = [
        product.get("product_name"),
        product.get("product_summary"),
        product.get("product_description"),
        product.get("target_description"),
        product.get("loan_limit_description"),
        product.get("loan_period_guide"),
        product.get("repayment_method"),
        product.get("required_documents"),
    ]
    haystack = " ".join([normalize(f) for f in fields if f])
    return any(k.lower() in haystack for k in keywords)


def dcg_at_k(rels: List[int], k: int) -> float:
    dcg = 0.0
    for i, rel in enumerate(rels[:k], start=1):
        if rel:
            dcg += 1.0 / math.log2(i + 1)
    return dcg


def ndcg_at_k(rels: List[int], k: int) -> float:
    dcg = dcg_at_k(rels, k)
    ideal = sorted(rels, reverse=True)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0:
        return 0.0
    return dcg / idcg


def precision_at_k(rels: List[int], k: int) -> float:
    return sum(rels[:k]) / k if rels else 0.0


def recall_at_k(rels: List[int], total_relevant: int, k: int) -> float:
    if total_relevant == 0:
        return 0.0
    return sum(rels[:k]) / total_relevant


def average_precision_at_k(rels: List[int], total_relevant: int, k: int) -> float:
    if total_relevant == 0:
        return 0.0
    ap = 0.0
    hits = 0
    for i, rel in enumerate(rels[:k], start=1):
        if rel:
            hits += 1
            ap += hits / i
    return ap / total_relevant


def mrr_at_k(rels: List[int], k: int) -> float:
    for i, rel in enumerate(rels[:k], start=1):
        if rel:
            return 1.0 / i
    return 0.0


def fetch_products(db: Database, ids: List[str]) -> List[Dict[str, str]]:
    if not ids:
        return []
    placeholders = ",".join(["%s"] * len(ids))
    fetch_query = f"""
    SELECT id, product_code, product_name, product_summary,
           product_description, target_description, loan_limit_description,
           loan_period_guide, repayment_method, min_interest_rate,
           max_interest_rate, required_documents
    FROM loan_products
    WHERE id IN ({placeholders})
    """
    db.execute(fetch_query, tuple(ids))
    rows = db.cur.fetchall()
    products = []
    for row in rows:
        products.append(
            {
                "id": row[0],
                "product_code": row[1],
                "product_name": row[2],
                "product_summary": row[3],
                "product_description": row[4],
                "target_description": row[5],
                "loan_limit_description": row[6],
                "loan_period_guide": row[7],
                "repayment_method": row[8],
                "min_interest_rate": float(row[9]) if row[9] else None,
                "max_interest_rate": float(row[10]) if row[10] else None,
                "required_documents": row[11],
            }
        )
    products.sort(key=lambda x: ids.index(x["id"]))
    return products


def get_all_products(db: Database) -> List[Dict[str, str]]:
    db.execute(
        """
        SELECT id, product_code, product_name, product_summary,
               product_description, target_description, loan_limit_description,
               loan_period_guide, repayment_method, min_interest_rate,
               max_interest_rate, required_documents
        FROM loan_products
        """
    )
    rows = db.cur.fetchall()
    products = []
    for row in rows:
        products.append(
            {
                "id": row[0],
                "product_code": row[1],
                "product_name": row[2],
                "product_summary": row[3],
                "product_description": row[4],
                "target_description": row[5],
                "loan_limit_description": row[6],
                "loan_period_guide": row[7],
                "repayment_method": row[8],
                "min_interest_rate": float(row[9]) if row[9] else None,
                "max_interest_rate": float(row[10]) if row[10] else None,
                "required_documents": row[11],
            }
        )
    return products


def relevant_set(all_products: List[Dict[str, str]], keywords: List[str]):
    return {p["id"] for p in all_products if is_relevant(p, keywords)}


def eval_case(results: List[Dict[str, str]], rel_ids: set) -> Dict[str, float]:
    rels = [1 if r["id"] in rel_ids else 0 for r in results]
    total_rel = len(rel_ids)
    return {
        "p10": precision_at_k(rels, K),
        "ndcg10": ndcg_at_k(rels, K),
        "recall10": recall_at_k(rels, total_rel, K),
        "map10": average_precision_at_k(rels, total_rel, K),
        "mrr10": mrr_at_k(rels, K),
    }


def avg(values):
    return sum(values) / len(values) if values else 0.0


def run_hybrid_mode(cases: List[QueryCase], mode: str):
    os.environ["BM25_MODE"] = mode
    with Database() as db:
        search = HybridSearch(db)
        all_products = get_all_products(db)
        per_case = []
        for case in cases:
            rel_ids = relevant_set(all_products, case.keywords)
            results = search.search(case.query, limit=10, search_limit=20)
            per_case.append(eval_case(results, rel_ids))
        return {
            "recall10": avg([c["recall10"] for c in per_case]),
            "map10": avg([c["map10"] for c in per_case]),
            "mrr10": avg([c["mrr10"] for c in per_case]),
        }


def run_modes_single(cases: List[QueryCase]):
    os.environ["BM25_MODE"] = "paradedb"
    with Database() as db:
        search = HybridSearch(db)
        all_products = get_all_products(db)
        metrics = {
            "hybrid": [],
            "bm25": [],
            "vector": [],
        }
        for case in cases:
            rel_ids = relevant_set(all_products, case.keywords)

            hybrid_results = search.search(case.query, limit=10, search_limit=20)
            metrics["hybrid"].append(eval_case(hybrid_results, rel_ids))

            bm25 = search.bm25_search(case.query, limit=10)
            bm25_ids = [doc_id for doc_id, _ in bm25]
            bm25_results = fetch_products(db, bm25_ids)
            metrics["bm25"].append(eval_case(bm25_results, rel_ids))

            embedding = search.generate_query_embedding(case.query)
            vec = search.vector_search(embedding, limit=10)
            vec_ids = [doc_id for doc_id, _ in vec]
            vec_results = fetch_products(db, vec_ids)
            metrics["vector"].append(eval_case(vec_results, rel_ids))

        def avg_metrics(items: List[Dict[str, float]]):
            return {
                "recall10": avg([c["recall10"] for c in items]),
                "map10": avg([c["map10"] for c in items]),
                "mrr10": avg([c["mrr10"] for c in items]),
            }

        return {
            "hybrid": avg_metrics(metrics["hybrid"]),
            "bm25": avg_metrics(metrics["bm25"]),
            "vector": avg_metrics(metrics["vector"]),
        }


def main():
    metrics_12_paradedb = run_hybrid_mode(CASES_12, "paradedb")
    metrics_12_fts = run_hybrid_mode(CASES_12, "fts")
    metrics_40_paradedb = run_hybrid_mode(CASES_40, "paradedb")
    metrics_40_fts = run_hybrid_mode(CASES_40, "fts")
    metrics_modes_40 = run_modes_single(CASES_40)

    print("METRICS_12_PARADEDB", metrics_12_paradedb)
    print("METRICS_12_FTS", metrics_12_fts)
    print("METRICS_40_PARADEDB", metrics_40_paradedb)
    print("METRICS_40_FTS", metrics_40_fts)
    print("METRICS_MODES_40", metrics_modes_40)


if __name__ == "__main__":
    main()

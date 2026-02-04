"""Hybrid search implementation using BM25 and vector search"""

from typing import List, Dict, Any, Tuple
from openai import OpenAI
from .config import Config
from .database import Database


class HybridSearch:
    """Hybrid search combining BM25 and vector similarity"""

    def __init__(self, db: Database):
        self.db = db
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        response = self.client.embeddings.create(
            model=Config.EMBEDDING_MODEL, input=query, encoding_format="float"
        )
        return response.data[0].embedding

    def bm25_search(self, query: str, limit: int = 20) -> List[Tuple[str, float]]:
        """Perform BM25 full-text search"""
        tokenized_query = Config.tokenize_for_bm25(query) or query
        if Config.BM25_MODE == "paradedb":
            search_query = f"""
            SELECT id, paradedb.score(id) AS score
            FROM {Config.TABLE_NAME}
            WHERE cleaned_searchable_text @@@ %s
            ORDER BY paradedb.score(id) DESC
            LIMIT %s
            """
            self.db.execute(search_query, (tokenized_query, limit))
        else:
            search_query = f"""
            SELECT id, ts_rank(
                to_tsvector('english', cleaned_searchable_text),
                plainto_tsquery('english', %s)
            ) AS score
            FROM {Config.TABLE_NAME}
            WHERE to_tsvector('english', cleaned_searchable_text) @@ plainto_tsquery('english', %s)
            ORDER BY score DESC
            LIMIT %s
            """
            self.db.execute(search_query, (tokenized_query, tokenized_query, limit))

        results = self.db.cur.fetchall()
        return [(row[0], float(row[1])) for row in results]

    def vector_search(
        self, query_embedding: List[float], limit: int = 20
    ) -> List[Tuple[str, float]]:
        """Perform vector similarity search"""
        search_query = f"""
        SELECT id, 1 - (searchable_text_embedding <=> %s::vector) as score
        FROM {Config.TABLE_NAME}
        ORDER BY searchable_text_embedding <=> %s::vector
        LIMIT %s
        """

        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        self.db.execute(search_query, (embedding_str, embedding_str, limit))

        results = self.db.cur.fetchall()
        return [(row[0], float(row[1])) for row in results]

    def reciprocal_rank_fusion(
        self,
        bm25_results: List[Tuple[str, float]],
        vector_results: List[Tuple[str, float]],
        k: int = None,
    ) -> List[Tuple[str, float]]:
        """
        Combine BM25 and vector search results using Reciprocal Rank Fusion (RRF)

        RRF formula: RRF_score(d) = sum(1 / (k + rank(d)))
        where k is a constant (typically 60) and rank is the position in the result list
        """
        if k is None:
            k = Config.RRF_K

        # Calculate RRF scores
        rrf_scores: Dict[str, float] = {}

        # Process BM25 results
        for rank, (doc_id, _) in enumerate(bm25_results, start=1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank)

        # Process vector results
        for rank, (doc_id, _) in enumerate(vector_results, start=1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank)

        # Sort by RRF score
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_results

    def search(
        self, query: str, limit: int = 10, search_limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining BM25 and vector search

        Args:
            query: Search query string
            limit: Number of final results to return
            search_limit: Number of results to retrieve from each search method

        Returns:
            List of loan products ranked by hybrid score
        """
        print(f"Searching for: '{query}'")

        # 1. BM25 Search
        print("Performing BM25 search...")
        bm25_results = self.bm25_search(query, limit=search_limit)
        print(f"BM25 found {len(bm25_results)} results")

        # 2. Vector Search
        print("Generating query embedding...")
        query_embedding = self.generate_query_embedding(query)
        print("Performing vector similarity search...")
        vector_results = self.vector_search(query_embedding, limit=search_limit)
        print(f"Vector search found {len(vector_results)} results")

        # 3. Reciprocal Rank Fusion
        print("Combining results with RRF...")
        combined_results = self.reciprocal_rank_fusion(bm25_results, vector_results)

        # 4. Retrieve full product details
        top_results = combined_results[:limit]
        product_ids = [doc_id for doc_id, _ in top_results]

        if not product_ids:
            print("No results found")
            return []

        # Fetch full product data
        placeholders = ",".join(["%s"] * len(product_ids))
        fetch_query = f"""
        SELECT id, product_code, product_name, product_summary,
               product_description, target_description, loan_limit_description,
               loan_period_guide, repayment_method, min_interest_rate,
               max_interest_rate, required_documents
        FROM {Config.TABLE_NAME}
        WHERE id IN ({placeholders})
        """

        self.db.execute(fetch_query, tuple(product_ids))
        rows = self.db.cur.fetchall()

        # Map results with scores
        score_map = {doc_id: score for doc_id, score in top_results}
        products = []

        for row in rows:
            product = {
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
                "rrf_score": score_map.get(row[0], 0.0),
            }
            products.append(product)

        # Sort by score (maintain RRF order)
        products.sort(key=lambda x: x["rrf_score"], reverse=True)

        print(f"[OK] Found {len(products)} results")
        return products

    def print_results(self, products: List[Dict[str, Any]]):
        """Pretty print search results"""
        if not products:
            print("\nNo results found")
            return

        print(f"\n{'=' * 80}")
        print(f"Found {len(products)} results")
        print(f"{'=' * 80}\n")

        for i, product in enumerate(products, 1):
            print(f"{i}. {product['product_name']}")
            print(f"   Code: {product['product_code']}")
            print(f"   Score: {product['rrf_score']:.4f}")
            print(
                f"   Interest Rate: {product['min_interest_rate']}% ~ {product['max_interest_rate']}%"
            )
            print(f"   Summary: {product['product_summary'][:100]}...")
            print()

"""Data loading and embedding generation"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from openai import OpenAI
from .config import Config
from .database import Database


class DataLoader:
    """Load and process loan product data"""

    def __init__(self, db: Database):
        self.db = db
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def load_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Load loan products from JSON file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Loading data from {file_path}...")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"[OK] Loaded {len(data)} loan products")
        return data

    def create_searchable_text(self, product: Dict[str, Any]) -> str:
        """Create searchable text from product fields"""
        fields = [
            "product_name",
            "product_summary",
            "product_description",
            "target_description",
            "loan_limit_description",
            "loan_period_guide",
            "repayment_method",
            "required_documents",
            "early_repayment_info",
            "important_notices",
        ]

        text_parts = []
        for field in fields:
            value = product.get(field, "")
            if value:
                text_parts.append(str(value))

        return " ".join(text_parts)

    def clean_text_for_bm25(self, text: str) -> str:
        """Normalize text for BM25 search"""
        return Config.tokenize_for_bm25(text)

    def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings in batches"""
        embeddings = []
        total = len(texts)

        for i in range(0, total, batch_size):
            batch = texts[i : i + batch_size]
            print(
                f"Generating embeddings: {i + 1}-{min(i + batch_size, total)}/{total}"
            )

            response = self.client.embeddings.create(
                model=Config.EMBEDDING_MODEL, input=batch, encoding_format="float"
            )

            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)

        return embeddings

    def load_data(self, json_file_path: str, batch_commit: int = 50):
        """Load all data from JSON file into database"""
        products = self.load_json(json_file_path)
        total = len(products)

        print(f"\nProcessing {total} products...")

        # Prepare all searchable texts
        print("Creating searchable texts...")
        searchable_texts = []
        for product in products:
            searchable_text = self.create_searchable_text(product)
            searchable_texts.append(searchable_text)

        # Generate all embeddings in batch
        print("\nGenerating embeddings in batch...")
        embeddings = self.generate_embeddings_batch(searchable_texts)
        print(f"[OK] Generated {len(embeddings)} embeddings")

        # Insert products with pre-generated embeddings
        print("\nInserting products into database...")
        for i, (product, searchable_text, embedding) in enumerate(
            zip(products, searchable_texts, embeddings), 1
        ):
            try:
                cleaned_text = self.clean_text_for_bm25(searchable_text)

                insert_query = f"""
                INSERT INTO {Config.TABLE_NAME} (
                    id, product_code, product_name, product_summary, product_description,
                    target_description, loan_limit_description, loan_period_guide,
                    repayment_method, min_interest_rate, max_interest_rate,
                    required_documents, customer_cost_info, early_repayment_info,
                    overdue_interest_info, important_notices,
                    searchable_text, cleaned_searchable_text, searchable_text_embedding
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    product_code = EXCLUDED.product_code,
                    product_name = EXCLUDED.product_name,
                    product_summary = EXCLUDED.product_summary,
                    product_description = EXCLUDED.product_description,
                    target_description = EXCLUDED.target_description,
                    loan_limit_description = EXCLUDED.loan_limit_description,
                    loan_period_guide = EXCLUDED.loan_period_guide,
                    repayment_method = EXCLUDED.repayment_method,
                    min_interest_rate = EXCLUDED.min_interest_rate,
                    max_interest_rate = EXCLUDED.max_interest_rate,
                    required_documents = EXCLUDED.required_documents,
                    customer_cost_info = EXCLUDED.customer_cost_info,
                    early_repayment_info = EXCLUDED.early_repayment_info,
                    overdue_interest_info = EXCLUDED.overdue_interest_info,
                    important_notices = EXCLUDED.important_notices,
                    searchable_text = EXCLUDED.searchable_text,
                    cleaned_searchable_text = EXCLUDED.cleaned_searchable_text,
                    searchable_text_embedding = EXCLUDED.searchable_text_embedding
                """

                self.db.execute(
                    insert_query,
                    (
                        product.get("id"),
                        product.get("product_code"),
                        product.get("product_name"),
                        product.get("product_summary"),
                        product.get("product_description"),
                        product.get("target_description"),
                        product.get("loan_limit_description"),
                        product.get("loan_period_guide"),
                        product.get("repayment_method"),
                        product.get("min_interest_rate"),
                        product.get("max_interest_rate"),
                        product.get("required_documents"),
                        product.get("customer_cost_info"),
                        product.get("early_repayment_info"),
                        product.get("overdue_interest_info"),
                        product.get("important_notices"),
                        searchable_text,
                        cleaned_text,
                        embedding,
                    ),
                )

                if i % batch_commit == 0:
                    self.db.commit()
                    print(f"Progress: {i}/{total} products inserted")

            except Exception as e:
                print(f"Error inserting product {product.get('id')}: {e}")
                continue

        # Commit remaining
        self.db.commit()
        print(f"\n[OK] Successfully inserted {total} products")

        # Create indexes after data insertion
        print("\nCreating indexes...")
        self.db.create_bm25_index()
        self.db.create_vector_index()
        print("[OK] Data loading complete!")

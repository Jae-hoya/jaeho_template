"""Database connection and table management"""

import psycopg
from typing import Optional
from .config import Config


class Database:
    """Database connection and management"""

    def __init__(self):
        self.conn_string = Config.get_connection_string()
        self.conn: Optional[psycopg.Connection] = None
        self.cur: Optional[psycopg.Cursor] = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg.connect(self.conn_string)
            self.cur = self.conn.cursor()
            print("Database connection established")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def close(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def execute(self, query: str, params: tuple = None):
        """Execute a query"""
        if not self.cur:
            raise RuntimeError("Database not connected")
        self.cur.execute(query, params)

    def commit(self):
        """Commit transaction"""
        if self.conn:
            self.conn.commit()

    def setup_extensions(self):
        """Install required PostgreSQL extensions"""
        print("Setting up extensions...")

        # Set autocommit for extension creation
        old_autocommit = self.conn.autocommit
        self.conn.autocommit = True

        try:
            # Install pgvector extension
            self.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("[OK] pgvector extension enabled")
        except Exception as e:
            print(f"Warning: Could not enable pgvector: {e}")

        try:
            # Install pg_search extension (ParadeDB)
            self.execute("CREATE EXTENSION IF NOT EXISTS pg_search")
            print("[OK] pg_search extension enabled")
        except Exception as e:
            print(f"Warning: Could not enable pg_search: {e}")
            print("Note: pg_search may not be available on all Neon projects")

        # Reset autocommit
        self.conn.autocommit = old_autocommit

    def create_table(self):
        """Create loan_products table with required columns"""
        print(f"Creating table '{Config.TABLE_NAME}'...")

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {Config.TABLE_NAME} (
            id VARCHAR(255) PRIMARY KEY,
            product_code VARCHAR(100),
            product_name VARCHAR(500),
            product_summary TEXT,
            product_description TEXT,
            target_description TEXT,
            loan_limit_description TEXT,
            loan_period_guide TEXT,
            repayment_method VARCHAR(200),
            min_interest_rate DECIMAL(5,2),
            max_interest_rate DECIMAL(5,2),
            required_documents TEXT,
            customer_cost_info TEXT,
            early_repayment_info TEXT,
            overdue_interest_info TEXT,
            important_notices TEXT,
            searchable_text TEXT,
            cleaned_searchable_text TEXT,
            searchable_text_embedding vector({Config.EMBEDDING_DIMENSIONS})
        )
        """

        self.execute(create_table_query)
        self.commit()
        print(f"[OK] Table '{Config.TABLE_NAME}' created successfully")

    def create_bm25_index(self):
        """Create BM25 index for full-text search using pg_search"""
        print("Creating BM25 index...")

        try:
            # Drop existing index if exists
            drop_index_query = f"""
            DROP INDEX IF EXISTS idx_{Config.TABLE_NAME}_bm25
            """
            self.execute(drop_index_query)

            # Create BM25 index using pg_search
            # Note: This requires pg_search extension
            create_index_query = f"""
            CREATE INDEX idx_{Config.TABLE_NAME}_bm25
            ON {Config.TABLE_NAME}
            USING bm25 (id, cleaned_searchable_text)
            WITH (key_field='id')
            """
            self.execute(create_index_query)
            self.commit()
            print("[OK] BM25 index created successfully")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Warning: Could not create BM25 index: {e}")
            print("Note: BM25 indexing requires pg_search extension")
            print("Falling back to standard full-text search capabilities")

            # Create standard GIN index as fallback
            try:
                create_gin_query = f"""
                CREATE INDEX IF NOT EXISTS idx_{Config.TABLE_NAME}_gin
                ON {Config.TABLE_NAME}
                USING gin(to_tsvector('english', cleaned_searchable_text))
                """
                self.execute(create_gin_query)
                self.commit()
                print("[OK] GIN full-text search index created as fallback")
            except Exception as gin_error:
                if self.conn:
                    self.conn.rollback()
                print(f"Warning: Could not create GIN index: {gin_error}")

    def create_vector_index(self):
        """Create vector index for similarity search"""
        print("Creating vector index...")

        create_index_query = f"""
        CREATE INDEX IF NOT EXISTS idx_{Config.TABLE_NAME}_embedding
        ON {Config.TABLE_NAME}
        USING ivfflat (searchable_text_embedding vector_cosine_ops)
        WITH (lists = 100)
        """

        try:
            self.execute(create_index_query)
            self.commit()
            print("[OK] Vector index created successfully")
        except Exception as e:
            print(f"Warning: Could not create vector index: {e}")

    def drop_table(self):
        """Drop loan_products table"""
        print(f"Dropping table '{Config.TABLE_NAME}'...")

        drop_table_query = f"DROP TABLE IF EXISTS {Config.TABLE_NAME} CASCADE"
        self.execute(drop_table_query)
        self.commit()
        print(f"[OK] Table '{Config.TABLE_NAME}' dropped")

    def initialize_database(self, reset: bool = False):
        """Initialize database with extensions and tables"""
        if reset:
            self.drop_table()

        self.setup_extensions()
        self.create_table()
        # Indexes will be created after data insertion for better performance

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based hybrid search system for loan products that combines BM25 full-text search with vector semantic search using Reciprocal Rank Fusion (RRF). The system runs on ParadeDB (PostgreSQL with pgvector and pg_search extensions) and uses OpenAI embeddings.

## Essential Commands

### Database Setup
```bash
# Initialize database, create tables, load data, and generate embeddings
python -m search_app.setup
```

This command:
- Installs pgvector and pg_search extensions
- Creates the loan_products table
- Loads 67 loan products from loan_products.json
- Generates 1536-dimensional OpenAI embeddings
- Creates BM25 and vector search indexes

### Search
```bash
# Perform hybrid search
python -m search_app.main "의사 전용 대출"
```

### Dependency Installation
```bash
pip install psycopg python-dotenv openai numpy kiwipiepy
```

### Testing
```bash
# Run all tests (pytest is expected but no tests exist yet)
python -m pytest

# Run specific test
python -m pytest -k "test_name"
```

## Environment Configuration

Environment variables are loaded from `C:\Users\skyop\jaeho_template\dotenv_windows`:

**Required:**
- `OPENAI_API_KEY`: OpenAI API key for embeddings
- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5433/postgres`)

**Optional:**
- `BM25_MODE`: `paradedb` (default) or `fts` (PostgreSQL full-text search)
- `BM25_TOKENIZER`: `simple` (default) or `kiwi` (Korean tokenizer)
- `KIWI_POS_FILTER`: Comma-separated POS tags for Kiwi tokenizer (default: `NNG,NNP,NNB,NR,NP,VV,VA,XR,SL,SN`)

### ParadeDB Docker
```bash
docker run -d \
  --name hybrid-search-paradedb \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -p 5433:5432 \
  paradedb/paradedb:latest
```

## Architecture

### Core Modules

**`search_app/config.py`**: Configuration and environment variable loading
- `Config.get_connection_string()`: Returns PostgreSQL connection string
- `Config.tokenize_for_bm25()`: Tokenizes text for BM25 search (supports simple or Kiwi tokenizer)
- Loads `.env` from `C:\Users\skyop\jaeho_template\.env`

**`search_app/database.py`**: Database connection and schema management
- `Database.setup_extensions()`: Installs pgvector and pg_search extensions
- `Database.create_table()`: Creates loan_products table with vector column
- `Database.create_bm25_index()`: Creates BM25 index (falls back to GIN if pg_search unavailable)
- `Database.create_vector_index()`: Creates IVFFlat vector index

**`search_app/data_loader.py`**: Data ingestion and embedding generation
- `DataLoader.load_json()`: Loads loan_products.json
- `DataLoader.generate_embeddings()`: Batch generates OpenAI embeddings with rate limit handling
- `DataLoader.clean_text_for_bm25()`: Removes special characters for BM25 indexing

**`search_app/hybrid_search.py`**: Search implementation
- `HybridSearch.bm25_search()`: BM25 full-text search on `cleaned_searchable_text`
- `HybridSearch.vector_search()`: Cosine similarity search on `searchable_text_embedding`
- `HybridSearch.reciprocal_rank_fusion()`: Combines results using RRF formula: `RRF_score(d) = Σ(1 / (k + rank(d)))`
- `HybridSearch.search()`: Main search method orchestrating BM25, vector, and RRF

**`search_app/setup.py`**: Database initialization script
**`search_app/main.py`**: CLI entry point with Windows UTF-8 handling

### Search Flow

1. **BM25 Search**: Query is tokenized and matched against `cleaned_searchable_text` using either ParadeDB's BM25 index (`@@@` operator) or PostgreSQL's `ts_rank`
2. **Vector Search**: Query embedding is generated and compared against `searchable_text_embedding` using cosine distance (`<=>` operator)
3. **RRF Fusion**: Results are combined using Reciprocal Rank Fusion with k=60 (configurable via `Config.RRF_K`)
4. **Result Retrieval**: Full product details are fetched for top-ranked documents

### Database Schema

Table: `loan_products`

Key columns:
- `id` (VARCHAR, PRIMARY KEY): Unique product identifier
- `searchable_text` (TEXT): Raw concatenated searchable content
- `cleaned_searchable_text` (TEXT): Preprocessed text with special characters removed for BM25
- `searchable_text_embedding` (vector(1536)): OpenAI embedding for semantic search
- Various loan product fields (product_name, product_code, interest rates, etc.)

## Code Style

- **Indentation**: 4 spaces, no tabs
- **Quotes**: Double quotes for strings
- **Imports**: Standard library, third-party, local (no star imports)
- **Type hints**: Use `typing.List`, `Dict`, `Tuple` for Python 3.10 compatibility
- **Naming**: snake_case (functions/vars), PascalCase (classes), UPPER_SNAKE_CASE (constants)
- **SQL**: Always use parameterized queries with `%s` placeholders
- **Error handling**: Wrap DB operations in try/except, log clearly, fail loudly

## BM25 Modes

The system supports two BM25 implementations controlled by `BM25_MODE`:

1. **ParadeDB** (default): Uses `pg_search` extension with `@@@` operator and `paradedb.score()`
2. **PostgreSQL FTS**: Falls back to `to_tsvector`/`ts_rank` if pg_search unavailable

When switching modes or tokenizers, re-run `python -m search_app.setup` to rebuild indexes.

## Tokenization

Two tokenization strategies for BM25:

1. **Simple** (default): Regex-based removal of special characters
2. **Kiwi**: Korean morphological analyzer with POS filtering

Tokenization is applied consistently at both indexing time (`cleaned_searchable_text` generation) and query time (`Config.tokenize_for_bm25()`).

## Important Notes

- Windows UTF-8 output handling is implemented in `search_app/main.py`
- Extension creation (pgvector, pg_search) may fail on some PostgreSQL instances; fallbacks are implemented
- BM25 index creation falls back to GIN index if pg_search is unavailable
- OpenAI API calls include retry logic and rate limit handling
- No linter/formatter configured; maintain consistency with existing code
- Database operations use transactions with rollback on errors

## NOTES
- 데이터베이스 관련 정보
- OpenAI GPT-5-mini 모델을 사용해야해.
   - (2025년 8월 출시)
- 프로젝트 목표를 RAG 개발로 수정
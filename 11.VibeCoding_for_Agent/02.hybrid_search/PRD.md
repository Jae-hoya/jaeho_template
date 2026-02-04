# Hybrid Search for Loan Products - PRD

## Overview
Python-based hybrid search system combining BM25 and vector search for loan product data using Neon PostgreSQL.

## Tech Stack
- **Language**: Python
- **Package Manager**: uv
- **Database**: Neon PostgreSQL (pgvector, pg_search extensions)
- **Embedding Model**: OpenAI text-embedding-3-small
- **Database Driver**: psycopg2
- **Environment**: dotenv from `C:\Users\skyop\jaeho_template`

## Database Configuration
- **MCP**: Neon MCP
- **Project**: nonghyup-loan
- **Table**: loan_products

## Data Schema
The `loan_products` table stores:
- Original loan product data from `loan_products.json`
- `searchable_text`: raw searchable content
- `cleaned_searchable_text`: preprocessed text with special characters removed (for BM25)
- `searchable_text_embedding`: vector embeddings (for semantic search)

## Core Features

### 1. Data Ingestion
Load loan product data from `loan_products.json` into `loan_products` table.

### 2. Text Preprocessing
Generate `cleaned_searchable_text` by removing special characters from `searchable_text` to optimize BM25 search.

### 3. Embedding Generation
Generate and store embeddings for `searchable_text` in `searchable_text_embedding` column.

### 4. Hybrid Search
Implement `hybrid_search()` function that:
- Performs BM25 search on `cleaned_searchable_text`
- Performs vector search on `searchable_text_embedding`
- Combines results using Reciprocal Rank Fusion (RRF)
- Reference: https://docs.paradedb.com/documentation/guides/hybrid
- Both searches operate on the full table

## CLI Usage
```bash
uv run python ... "의사 전용 대출"
```

## Implementation Notes
- Keep implementation details flexible for AI decision-making
- Focus on core functionality and architecture
- SQL optimization and detailed implementation left to development phase

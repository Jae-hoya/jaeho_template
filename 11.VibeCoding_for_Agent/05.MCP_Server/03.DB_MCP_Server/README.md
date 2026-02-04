# recursive-mcp-server

Python MCP server for PostgreSQL with a read-only query tool and a safe `update_candidate` tool.

## Requirements
- Python 3.11+
- PostgreSQL connection URL

## Install
```sh
pip install -e .
```

## Run
Provide the database URL as the first argument or via environment variables.

```sh
python server.py "postgresql://user:pass@host:5432/db"
```

Or set one of these env vars: `DATABASE_URL`, `POSTGRES_URL`, `PG_URL`.

```sh
set DATABASE_URL=postgresql://user:pass@host:5432/db
python server.py
```

## Tools

### query
Execute a single read-only SQL statement. The server runs the query inside a read-only transaction and
rejects multiple statements.

Input:
```json
{ "sql": "SELECT * FROM public.candidates LIMIT 5" }
```

### update_candidate
Safely update candidate fields by id. Only `position`, `skills`, and `company` are allowed.
`id` is required and `name` cannot be changed. When `position` is updated, `category` is inferred
automatically.

Input:
```json
{
  "id": 1,
  "position": "Backend Developer",
  "skills": ["Python", "Django"],
  "company": "Hoya Company"
}
```

The update uses parameterized SQL and rejects unknown fields.

## Implementation Notes (server.py)
- Connection URL: first CLI arg or env vars `DATABASE_URL`, `POSTGRES_URL`, `PG_URL`.
- Read-only SQL guard: single statement only, must start with `SELECT`, `WITH`, `SHOW`, `EXPLAIN`, `VALUES`, or `TABLE`.
- Query execution: runs inside a read-only transaction and returns JSON output.
- update_candidate: only `position`, `skills`, `company` are allowed; `id` is required. `category` auto-updates from `position`.
- Safety: strict field whitelist, input validation, and parameterized SQL.
- Resources: exposes public table schemas via MCP resources.

import asyncio
import json
import os
import sys
from urllib.parse import urlparse, urlunparse
from typing import Any, cast

import asyncpg
from pydantic import AnyUrl
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.types import Resource, TextContent, Tool

SERVER_NAME = "recursive-mcp-server"
SERVER_VERSION = "0.1.0"
DEFAULT_POOL_SIZE = 5
ENV_URL_KEYS = ("DATABASE_URL", "POSTGRES_URL", "PG_URL")
RESOURCE_SCHEMA_PATH = "schema"
READ_ONLY_TOKENS = {"SELECT", "WITH", "SHOW", "EXPLAIN", "VALUES", "TABLE"}

server = Server(SERVER_NAME, version=SERVER_VERSION)
_pool: asyncpg.Pool | None = None
_resource_base_url: str | None = None


def log_debug(message: str) -> None:
    print(f"[debug] {message}", file=sys.stderr, flush=True)


def get_connection_url(argv: list[str]) -> str:
    if argv:
        return argv[0]
    for key in ENV_URL_KEYS:
        value = os.getenv(key)
        if value:
            return value
    raise ValueError(
        "Missing PostgreSQL URL. Provide it as the first argument or set DATABASE_URL/POSTGRES_URL/PG_URL."
    )


def normalize_sql(sql: str) -> str:
    if not isinstance(sql, str):
        raise ValueError("sql must be a string")
    cleaned = sql.strip()
    if not cleaned:
        raise ValueError("sql must not be empty")
    while cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()
    if ";" in cleaned:
        raise ValueError("Only a single SQL statement is allowed")
    return cleaned


def is_read_only_sql(sql: str) -> bool:
    token = sql.lstrip().split(None, 1)[0].upper()
    return token in READ_ONLY_TOKENS


def coerce_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    raise ValueError(f"{field_name} must be an integer")


def coerce_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def coerce_skills(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("skills must be a list of strings")
    skills: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("skills must contain non-empty strings")
        skills.append(item.strip())
    return skills


def infer_category_from_position(position: str) -> str | None:
    value = position.lower()
    if "designer" in value:
        return "Designer"
    if "marketer" in value:
        return "Marketer"
    if "product" in value:
        return "PM"
    if value == "pm" or value.endswith(" pm") or " pm " in value:
        return "PM"
    if "developer" in value or "engineer" in value:
        return "Developer"
    return None


def ensure_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool


def ensure_resource_base_url() -> str:
    if _resource_base_url is None:
        raise RuntimeError("Resource base URL is not initialized")
    return _resource_base_url


def build_resource_base_url(connection_url: str) -> str:
    parsed = urlparse(connection_url)
    if not parsed.hostname:
        raise ValueError("Invalid PostgreSQL URL: missing host")

    netloc = parsed.hostname
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    if parsed.username:
        netloc = f"{parsed.username}@{netloc}"

    path = parsed.path or "/"
    if not path.endswith("/"):
        path += "/"

    return urlunparse(("postgres", netloc, path, "", "", ""))


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query",
            description="Execute a read-only SQL query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "Read-only SQL query"}
                },
                "required": ["sql"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="update_candidate",
            description="Update candidate fields by id (position, skills, company only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Candidate id"},
                    "position": {"type": "string", "description": "New position"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New skills list",
                    },
                    "company": {"type": "string", "description": "New company"},
                },
                "required": ["id"],
                "additionalProperties": False,
            },
        ),
    ]


@server.list_resources()
async def list_resources() -> list[Resource]:
    pool = ensure_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )

    base_url = ensure_resource_base_url()
    resources: list[Resource] = []
    for row in rows:
        table_name = row["table_name"]
        uri = cast(AnyUrl, f"{base_url}{table_name}/{RESOURCE_SCHEMA_PATH}")
        resources.append(
            Resource(
                name=f"{table_name}_schema",
                title=f"\"{table_name}\" database schema",
                uri=uri,
                mimeType="application/json",
                description=f"Schema for public.{table_name}",
            )
        )
    return resources


@server.read_resource()
async def read_resource(uri: AnyUrl) -> list[ReadResourceContents]:
    parsed = urlparse(str(uri))
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        raise ValueError("Invalid resource URI")

    schema_part = path_parts[-1]
    table_name = path_parts[-2]
    if schema_part != RESOURCE_SCHEMA_PATH:
        raise ValueError("Invalid resource URI")

    pool = ensure_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1",
            table_name,
        )

    payload = json.dumps([dict(row) for row in rows], indent=2, ensure_ascii=False)
    return [ReadResourceContents(content=payload, mime_type="application/json")]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "query":
        sql_value = arguments.get("sql")
        if not isinstance(sql_value, str):
            raise ValueError("sql must be a string")
        sql = normalize_sql(sql_value)
        if not is_read_only_sql(sql):
            raise ValueError("Only read-only queries are allowed")
        log_debug("query requested")
        pool = ensure_pool()
        async with pool.acquire() as conn:
            async with conn.transaction(readonly=True):
                rows = await conn.fetch(sql)
        payload = [dict(row) for row in rows]
        return [
            TextContent(
                type="text",
                text=json.dumps(payload, ensure_ascii=False, default=str),
            )
        ]

    if name == "update_candidate":
        allowed_fields = {"position", "skills", "company", "id"}
        unknown_fields = set(arguments.keys()) - allowed_fields
        if unknown_fields:
            raise ValueError(f"Unknown fields: {', '.join(sorted(unknown_fields))}")

        candidate_id = coerce_int(arguments.get("id"), "id")
        updates: list[str] = []
        values: list[Any] = []

        if "position" in arguments:
            position = coerce_str(arguments.get("position"), "position")
            updates.append("position")
            values.append(position)
            category = infer_category_from_position(position)
            if category is not None:
                updates.append("category")
                values.append(category)
        if "skills" in arguments:
            updates.append("skills")
            values.append(coerce_skills(arguments.get("skills")))
        if "company" in arguments:
            updates.append("company")
            values.append(coerce_str(arguments.get("company"), "company"))

        if not updates:
            raise ValueError("At least one of position, skills, or company must be provided")

        set_clauses = [f"{field} = ${idx}" for idx, field in enumerate(updates, start=1)]
        values.append(candidate_id)
        sql = (
            "UPDATE public.candidates "
            f"SET {', '.join(set_clauses)} "
            f"WHERE id = ${len(values)} "
            "RETURNING id, name, position, skills, company, category, created_at"
        )

        log_debug(f"update_candidate id={candidate_id} fields={updates}")
        pool = ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(sql, *values)

        if row is None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"updated": False, "reason": "not_found"}),
                )
            ]

        payload = {"updated": True, "candidate": dict(row)}
        return [
            TextContent(
                type="text",
                text=json.dumps(payload, ensure_ascii=False, default=str),
            )
        ]

    raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    global _pool
    global _resource_base_url
    url = get_connection_url(sys.argv[1:])
    _resource_base_url = build_resource_base_url(url)
    _pool = await asyncpg.create_pool(url, min_size=1, max_size=DEFAULT_POOL_SIZE)
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    finally:
        pool = _pool
        if pool is not None:
            await pool.close()


if __name__ == "__main__":
    asyncio.run(main())

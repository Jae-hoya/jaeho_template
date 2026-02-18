#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

NOTION_VERSION = "2022-06-28"
SEARCH_URL = "https://api.notion.com/v1/search"


def fetch_pages(token):
    results = []
    start_cursor = None
    while True:
        payload = {
            "page_size": 100,
            "filter": {"property": "object", "value": "page"},
        }
        if start_cursor:
            payload["start_cursor"] = start_cursor
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(SEARCH_URL, data=data, method="POST")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Notion-Version", NOTION_VERSION)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            raise RuntimeError(f"Notion API error {exc.code}: {err_body}")
        results.extend(body.get("results", []))
        if not body.get("has_more"):
            break
        start_cursor = body.get("next_cursor")
        if not start_cursor:
            break
    return results


def get_page_title(page):
    props = page.get("properties") or {}
    for prop in props.values():
        if prop.get("type") == "title":
            title_parts = [t.get("plain_text", "") for t in prop.get("title", [])]
            title = "".join(title_parts).strip()
            if title:
                return title
    return "(untitled)"


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("NOTION_TOKEN 환경변수가 필요합니다.", file=sys.stderr)
        sys.exit(1)

    pages = fetch_pages(token)
    for page in pages:
        title = get_page_title(page)
        url = page.get("url", "")
        page_id = page.get("id", "")
        parent = page.get("parent", {})
        parent_str = f"{parent.get('type', '')}:{parent.get(parent.get('type', ''), '')}" if parent else ""
        print(f"{title}\t{url}\t{page_id}\t{parent_str}")


if __name__ == "__main__":
    main()

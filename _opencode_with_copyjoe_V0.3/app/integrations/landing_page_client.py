import asyncio
import json
import subprocess
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup


class LandingPageClient:
    def __init__(self, timeout_sec: int = 35) -> None:
        self.timeout_sec = timeout_sec

    async def analyze(self, url: str) -> dict[str, Any]:
        try:
            if self._should_use_playwright_subprocess():
                return await asyncio.to_thread(self._analyze_with_playwright_subprocess, url)
            return await asyncio.to_thread(self._analyze_with_playwright_sync, url)
        except Exception:
            return await asyncio.to_thread(self._analyze_with_requests, url)

    def _should_use_playwright_subprocess(self) -> bool:
        policy_name = asyncio.get_event_loop_policy().__class__.__name__
        return policy_name == "WindowsSelectorEventLoopPolicy"

    def _analyze_with_playwright_subprocess(self, url: str) -> dict[str, Any]:
        timeout_ms = self.timeout_sec * 1000
        script = r'''
import json
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
timeout_ms = int(sys.argv[2])

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=timeout_ms)
    page.wait_for_timeout(1500)
    data = page.evaluate(
        """
        () => {
          const clean = (v) => (v || '').replace(/\s+/g, ' ').trim();
          const uniq = (arr) => [...new Set(arr.filter(Boolean))];

          const h1 = uniq(Array.from(document.querySelectorAll('h1')).map(el => clean(el.textContent))).slice(0, 8);
          const h2 = uniq(Array.from(document.querySelectorAll('h2')).map(el => clean(el.textContent))).slice(0, 12);
          const ctas = uniq(
            Array.from(document.querySelectorAll('a, button, [role="button"], input[type="submit"]'))
              .map(el => clean(el.innerText || el.value || el.getAttribute('aria-label')))
              .filter(text => text.length >= 2 && text.length <= 80)
          ).slice(0, 20);

          const body = clean(document.body ? document.body.innerText : '').slice(0, 8000);
          const title = clean(document.title);

          return { title, h1, h2, cta_buttons: ctas, body };
        }
        """
    )
    browser.close()

print(json.dumps({"url": url, **data}, ensure_ascii=False))
'''

        completed = subprocess.run(
            [sys.executable, "-c", script, url, str(timeout_ms)],
            capture_output=True,
            text=True,
            timeout=self.timeout_sec + 20,
            check=False,
        )

        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            stdout = (completed.stdout or "").strip()
            raise RuntimeError(stderr or stdout or "Playwright subprocess failed")

        output = (completed.stdout or "").strip()
        if not output:
            raise RuntimeError("Playwright subprocess returned empty output")

        return json.loads(output)

    def _analyze_with_playwright_sync(self, url: str) -> dict[str, Any]:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_sec * 1000)
            page.wait_for_timeout(1500)

            data = page.evaluate(
                """
                () => {
                  const clean = (v) => (v || '').replace(/\s+/g, ' ').trim();
                  const uniq = (arr) => [...new Set(arr.filter(Boolean))];

                  const h1 = uniq(Array.from(document.querySelectorAll('h1')).map(el => clean(el.textContent))).slice(0, 8);
                  const h2 = uniq(Array.from(document.querySelectorAll('h2')).map(el => clean(el.textContent))).slice(0, 12);
                  const ctas = uniq(
                    Array.from(document.querySelectorAll('a, button, [role="button"], input[type="submit"]'))
                      .map(el => clean(el.innerText || el.value || el.getAttribute('aria-label')))
                      .filter(text => text.length >= 2 && text.length <= 80)
                  ).slice(0, 20);

                  const body = clean(document.body ? document.body.innerText : '').slice(0, 8000);
                  const title = clean(document.title);

                  return { title, h1, h2, cta_buttons: ctas, body };
                }
                """
            )
            browser.close()
            return {"url": url, **data}

    def _analyze_with_requests(self, url: str) -> dict[str, Any]:
        response = requests.get(
            url,
            timeout=self.timeout_sec,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = _normalize(soup.title.text if soup.title else "")
        h1 = _unique([_normalize(node.get_text(" ", strip=True)) for node in soup.select("h1")])[:8]
        h2 = _unique([_normalize(node.get_text(" ", strip=True)) for node in soup.select("h2")])[:12]

        cta_candidates = []
        for node in soup.select("a, button, [role='button'], input[type='submit']"):
            value_attr = node.get("value", "")
            if isinstance(value_attr, list):
                value_text = " ".join(str(item) for item in value_attr)
            else:
                value_text = str(value_attr)
            text = _normalize(node.get_text(" ", strip=True) or value_text)
            if 2 <= len(text) <= 80:
                cta_candidates.append(text)

        paragraphs = [_normalize(node.get_text(" ", strip=True)) for node in soup.select("p")]
        body = " ".join([text for text in paragraphs if text])
        if not body:
            body = _normalize(soup.get_text(" ", strip=True))

        return {
            "url": url,
            "title": title,
            "h1": h1,
            "h2": h2,
            "cta_buttons": _unique(cta_candidates)[:20],
            "body": body[:8000],
        }


def _normalize(text: object | None) -> str:
    return " ".join(str(text or "").split()).strip()


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output

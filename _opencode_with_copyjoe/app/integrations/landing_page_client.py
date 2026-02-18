import asyncio
from typing import Any

import requests
from bs4 import BeautifulSoup


class LandingPageClient:
    def __init__(self, timeout_sec: int = 35) -> None:
        self.timeout_sec = timeout_sec

    async def analyze(self, url: str) -> dict[str, Any]:
        try:
            return await self._analyze_with_playwright(url)
        except Exception:
            return await asyncio.to_thread(self._analyze_with_requests, url)

    async def _analyze_with_playwright(self, url: str) -> dict[str, Any]:
        from playwright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_sec * 1000)
            await page.wait_for_timeout(1500)

            data = await page.evaluate(
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
            await browser.close()
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
            text = _normalize(node.get_text(" ", strip=True) or node.get("value", ""))
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


def _normalize(text: str) -> str:
    return " ".join(text.split()).strip()


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output

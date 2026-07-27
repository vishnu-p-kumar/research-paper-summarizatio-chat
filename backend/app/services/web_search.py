from __future__ import annotations

import html
import re
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from app.config import WEB_MAX_RESULTS, WEB_TIMEOUT_S


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def web_search(query: str, max_results: int | None = None) -> List[Dict[str, str]]:
    """
    Very lightweight web search via DuckDuckGo HTML endpoint (no API key).
    Returns a list of {title, url, snippet}.
    """
    max_results = int(max_results or WEB_MAX_RESULTS)
    max_results = max(1, min(max_results, 8))

    url = "https://duckduckgo.com/html/"
    headers = {"User-Agent": USER_AGENT}
    resp = requests.post(url, data={"q": query}, headers=headers, timeout=WEB_TIMEOUT_S)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results: List[Dict[str, str]] = []

    for r in soup.select(".result"):
        a = r.select_one("a.result__a")
        if not a:
            continue
        title = a.get_text(" ", strip=True)
        href = a.get("href") or ""
        snippet_el = r.select_one(".result__snippet")
        snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""

        title = html.unescape(title)
        snippet = html.unescape(snippet)
        snippet = re.sub(r"\s+", " ", snippet).strip()

        if href.startswith("//"):
            href = "https:" + href

        results.append({"title": title, "url": href, "snippet": snippet})
        if len(results) >= max_results:
            break

    return results


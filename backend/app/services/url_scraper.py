from __future__ import annotations

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.utils.text_cleaner import clean_text


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def _extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def scrape_text_from_url(url: str, timeout_s: int = 20) -> str:
    if not url:
        return ""

    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout_s)
    resp.raise_for_status()

    content_type: Optional[str] = resp.headers.get("content-type")
    if content_type and "application/pdf" in content_type.lower():
        # Caller should use PDF upload for best results; still attempt parse via bytes.
        from app.services.pdf_parser import extract_text_from_pdf_bytes

        return extract_text_from_pdf_bytes(resp.content)

    return clean_text(_extract_visible_text(resp.text))


from __future__ import annotations

import requests
from bs4 import BeautifulSoup
import trafilatura


def _scrape_bs4(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)
    return text if len(text) > 100 else None


def _scrape_trafilatura(html: str) -> str | None:
    return trafilatura.extract(html, include_comments=False, include_tables=False)


def scrape_article(url: str, timeout: int = 15) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    text = _scrape_bs4(html)
    method = "beautifulsoup"

    if not text:
        text = _scrape_trafilatura(html)
        method = "trafilatura"

    if not text:
        raise ValueError("Gagal mengekstrak teks artikel dari URL yang diberikan.")

    return {"title": title, "text": text, "method": method, "url": url}

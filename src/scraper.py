"""Modul scraper: mengambil dan mengekstrak teks artikel berita dari URL."""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup
import trafilatura


def _scrape_bs4(html: str) -> str | None:
    """Ekstrak teks artikel menggunakan BeautifulSoup.

    Parameter:
        html: string HTML mentah dari halaman web.
    Return:
        Teks gabungan paragraf, atau None jika hasilnya terlalu pendek (<100 karakter).
    """
    soup = BeautifulSoup(html, "html.parser")
    # Hapus elemen non-konten agar hanya paragraf artikel yang tersisa
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)
    return text if len(text) > 100 else None


def _scrape_trafilatura(html: str) -> str | None:
    """Ekstrak teks artikel menggunakan library trafilatura sebagai fallback.

    Parameter:
        html: string HTML mentah dari halaman web.
    Return:
        Teks artikel hasil ekstraksi, atau None jika gagal.
    """
    return trafilatura.extract(html, include_comments=False, include_tables=False)


def scrape_article(url: str, timeout: int = 15) -> dict:
    """Mengambil halaman web dan mengekstrak judul serta teks artikel.

    Mencoba BeautifulSoup terlebih dahulu; jika gagal, gunakan trafilatura.

    Parameter:
        url: URL artikel berita.
        timeout: batas waktu request HTTP dalam detik.
    Return:
        Dict berisi 'title', 'text', 'method' (metode scraping), dan 'url'.
    """
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

"""Modul summarizer: pipeline utama peringkasan teks dan artikel dari URL."""

from __future__ import annotations

from .scraper import scrape_article
from .cleaner import clean_text, filter_boilerplate_sentences
from .preprocessor import preprocess, detect_language, tokenize_sentences
from .tfidf_extractor import extract_keywords
from .textrank import textrank_summarize


def summarize_text(
    text: str,
    lang: str | None = None,
    top_n: int = 5,
    num_keywords: int = 10,
) -> dict:
    """Ringkas teks artikel melalui pipeline: cleaning → preprocessing → TextRank.

    Parameter:
        text: teks artikel mentah.
        lang: kode bahasa ('id'/'en'), atau None untuk deteksi otomatis.
        top_n: jumlah kalimat ringkasan.
        num_keywords: jumlah kata kunci TF-IDF yang diekstrak.
    Return:
        Dict berisi teks asli, teks bersih, bahasa, kalimat ringkasan, kata kunci, dsb.
    """
    cleaned = clean_text(text)
    if lang is None:
        lang = detect_language(cleaned)

    prep = preprocess(cleaned, lang=lang)
    sentences = filter_boilerplate_sentences(prep["sentences"])

    keywords = extract_keywords(sentences, lang=lang, top_n=num_keywords)
    summary_sentences = textrank_summarize(sentences, lang=lang, top_n=top_n)
    summary = " ".join(summary_sentences)

    return {
        "original_text": text,
        "cleaned_text": cleaned,
        "lang": lang,
        "num_sentences_original": len(sentences),
        "num_sentences_summary": len(summary_sentences),
        "keywords": keywords,
        "summary_sentences": summary_sentences,
        "summary": summary,
    }


def summarize_url(
    url: str,
    lang: str | None = None,
    top_n: int = 5,
    num_keywords: int = 10,
) -> dict:
    """Ringkas artikel dari URL: scraping → cleaning → preprocessing → TextRank.

    Parameter:
        url: URL artikel berita.
        lang: kode bahasa ('id'/'en'), atau None untuk deteksi otomatis.
        top_n: jumlah kalimat ringkasan.
        num_keywords: jumlah kata kunci TF-IDF yang diekstrak.
    Return:
        Dict berisi judul, URL, metode scraping, dan hasil ringkasan.
    """
    article = scrape_article(url)
    result = summarize_text(
        article["text"], lang=lang, top_n=top_n, num_keywords=num_keywords
    )
    result["title"] = article["title"]
    result["url"] = article["url"]
    result["scrape_method"] = article["method"]
    return result

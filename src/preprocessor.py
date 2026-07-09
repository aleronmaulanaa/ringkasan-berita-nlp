"""Modul preprocessor: tokenisasi, stopword removal, stemming, dan deteksi bahasa."""

from __future__ import annotations

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Pastikan resource NLTK yang dibutuhkan sudah terunduh
for resource in ["punkt_tab", "stopwords"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

_sastrawi_factory = StemmerFactory()
_stemmer_id = _sastrawi_factory.create_stemmer()
_stemmer_en = PorterStemmer()

STOPWORDS_EN = set(stopwords.words("english"))
STOPWORDS_ID = set(stopwords.words("indonesian"))


def detect_language(text: str) -> str:
    """Deteksi bahasa teks (Indonesia atau Inggris) berdasarkan kata penanda.

    Parameter:
        text: teks yang akan dideteksi bahasanya.
    Return:
        'id' untuk Bahasa Indonesia, 'en' untuk Bahasa Inggris.
    """
    id_markers = {
        "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "pada",
        "adalah", "dari", "ke", "tidak", "akan", "juga", "sudah",
        "saya", "kami", "mereka", "telah", "atau", "bahwa", "oleh",
        "seperti", "ada", "bisa", "hanya", "lebih", "antara", "kata",
    }
    words = text.lower().split()[:200]
    id_count = sum(1 for w in words if w in id_markers)
    ratio = id_count / max(len(words), 1)
    # Threshold 8% kata penanda Indonesia sudah cukup untuk membedakan kedua bahasa
    return "id" if ratio > 0.08 else "en"


def tokenize_sentences(text: str) -> list[str]:
    """Pecah teks menjadi daftar kalimat menggunakan NLTK sent_tokenize.

    Parameter:
        text: teks yang akan dipecah.
    Return:
        Daftar kalimat.
    """
    return sent_tokenize(text)


def tokenize_words(text: str) -> list[str]:
    """Pecah teks menjadi daftar kata (lowercase) menggunakan NLTK word_tokenize.

    Parameter:
        text: teks yang akan dipecah.
    Return:
        Daftar kata dalam huruf kecil.
    """
    return word_tokenize(text.lower())


def remove_stopwords(words: list[str], lang: str) -> list[str]:
    """Hapus stopwords dan kata non-alfabet dari daftar kata.

    Parameter:
        words: daftar kata.
        lang: kode bahasa ('id' atau 'en').
    Return:
        Daftar kata tanpa stopwords.
    """
    sw = STOPWORDS_ID if lang == "id" else STOPWORDS_EN
    return [w for w in words if w.isalpha() and w not in sw]


def stem_words(words: list[str], lang: str) -> list[str]:
    """Lakukan stemming pada daftar kata sesuai bahasa.

    Menggunakan Sastrawi untuk Bahasa Indonesia, PorterStemmer untuk Inggris.

    Parameter:
        words: daftar kata.
        lang: kode bahasa ('id' atau 'en').
    Return:
        Daftar kata yang sudah di-stem.
    """
    if lang == "id":
        return [_stemmer_id.stem(w) for w in words]
    return [_stemmer_en.stem(w) for w in words]


def preprocess(text: str, lang: str | None = None) -> dict:
    """Pipeline preprocessing lengkap: tokenisasi, stopword removal, dan stemming.

    Parameter:
        text: teks yang akan diproses.
        lang: kode bahasa ('id'/'en'), atau None untuk deteksi otomatis.
    Return:
        Dict berisi 'lang', 'sentences', 'words', 'filtered_words', 'stemmed_words'.
    """
    if lang is None:
        lang = detect_language(text)
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)
    filtered = remove_stopwords(words, lang)
    stemmed = stem_words(filtered, lang)
    return {
        "lang": lang,
        "sentences": sentences,
        "words": words,
        "filtered_words": filtered,
        "stemmed_words": stemmed,
    }

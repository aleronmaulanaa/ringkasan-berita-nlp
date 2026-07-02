from __future__ import annotations

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

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
    id_markers = {
        "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "pada",
        "adalah", "dari", "ke", "tidak", "akan", "juga", "sudah",
        "saya", "kami", "mereka", "telah", "atau", "bahwa", "oleh",
        "seperti", "ada", "bisa", "hanya", "lebih", "antara", "kata",
    }
    words = text.lower().split()[:200]
    id_count = sum(1 for w in words if w in id_markers)
    ratio = id_count / max(len(words), 1)
    return "id" if ratio > 0.08 else "en"


def tokenize_sentences(text: str) -> list[str]:
    return sent_tokenize(text)


def tokenize_words(text: str) -> list[str]:
    return word_tokenize(text.lower())


def remove_stopwords(words: list[str], lang: str) -> list[str]:
    sw = STOPWORDS_ID if lang == "id" else STOPWORDS_EN
    return [w for w in words if w.isalpha() and w not in sw]


def stem_words(words: list[str], lang: str) -> list[str]:
    if lang == "id":
        return [_stemmer_id.stem(w) for w in words]
    return [_stemmer_en.stem(w) for w in words]


def preprocess(text: str, lang: str | None = None) -> dict:
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

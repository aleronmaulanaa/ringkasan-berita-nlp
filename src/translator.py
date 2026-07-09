"""Modul translator: terjemahkan kalimat ringkasan dan kata kunci menggunakan Google Translate."""

from __future__ import annotations

from deep_translator import GoogleTranslator


def translate_sentences(
    sentences: list[str],
    target_lang: str,
    source_lang: str = "auto",
) -> list[str]:
    """Terjemahkan daftar kalimat ke bahasa target satu per satu.

    Jika terjemahan gagal untuk suatu kalimat, kalimat asli tetap dipertahankan.

    Parameter:
        sentences: daftar kalimat yang akan diterjemahkan.
        target_lang: kode bahasa target (misal 'id', 'en').
        source_lang: kode bahasa sumber, default 'auto' (deteksi otomatis).
    Return:
        Daftar kalimat hasil terjemahan.
    """
    if not sentences or not target_lang:
        return sentences

    translator = GoogleTranslator(source=source_lang, target=target_lang)
    translated = []
    for sent in sentences:
        try:
            result = translator.translate(sent)
            translated.append(result if result else sent)
        except Exception:
            translated.append(sent)
    return translated


def translate_keywords(
    keywords: list[tuple[str, float]],
    target_lang: str,
    source_lang: str = "auto",
) -> list[tuple[str, float]]:
    """Terjemahkan daftar kata kunci ke bahasa target, pertahankan skor TF-IDF.

    Kata kunci digabung dengan koma lalu diterjemahkan sekaligus untuk efisiensi.
    Jika jumlah hasil terjemahan tidak cocok, kembalikan kata kunci asli.

    Parameter:
        keywords: daftar tuple (kata_kunci, skor_tfidf).
        target_lang: kode bahasa target.
        source_lang: kode bahasa sumber, default 'auto'.
    Return:
        Daftar tuple (kata_kunci_terjemahan, skor_tfidf).
    """
    if not keywords or not target_lang:
        return keywords

    words = [kw for kw, _ in keywords]
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    try:
        # Gabung semua kata kunci dengan koma, terjemahkan sekali untuk efisiensi API
        joined = ", ".join(words)
        result = translator.translate(joined)
        translated_words = [w.strip() for w in result.split(",")]
        if len(translated_words) == len(keywords):
            return [(tw, score) for tw, (_, score) in zip(translated_words, keywords)]
    except Exception:
        pass
    return keywords

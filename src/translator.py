from __future__ import annotations

from deep_translator import GoogleTranslator


def translate_sentences(
    sentences: list[str],
    target_lang: str,
    source_lang: str = "auto",
) -> list[str]:
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
    if not keywords or not target_lang:
        return keywords

    words = [kw for kw, _ in keywords]
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    try:
        joined = ", ".join(words)
        result = translator.translate(joined)
        translated_words = [w.strip() for w in result.split(",")]
        if len(translated_words) == len(keywords):
            return [(tw, score) for tw, (_, score) in zip(translated_words, keywords)]
    except Exception:
        pass
    return keywords

import re
import unicodedata

BOILERPLATE_EXACT = [
    "scroll to continue with content",
    "scroll to continue",
    "advertisement",
    "baca juga",
    "baca juga:",
    "baca selengkapnya",
    "baca artikel selengkapnya",
    "simak video",
    "simak juga video",
    "simak juga:",
    "tonton juga:",
    "tonton video",
    "saksikan video",
    "lihat juga:",
    "lihat foto:",
    "foto:",
    "video:",
    "infografis:",
    "klik di sini",
    "klik untuk baca",
    "klik banner",
    "selengkapnya di sini",
    "unduh di sini",
    "download di sini",
    "share this article",
    "share this story",
    "read more",
    "read more:",
    "read also:",
    "also read:",
    "see also:",
    "related articles",
    "related stories",
    "recommended for you",
    "you may also like",
    "don't miss",
    "subscribe to our newsletter",
    "sign up for our newsletter",
    "follow us on",
    "click here",
    "click to expand",
    "tap to expand",
    "continue reading",
    "artikel ini telah tayang di",
    "artikel ini ditulis oleh",
    "sumber:",
    "editor:",
    "reporter:",
    "pewarta:",
    "kontributor:",
    "penulis:",
    "cek berita dan artikel",
    "cek berita lainnya",
    "pilihan editor",
    "pilihan editor:",
    "editor's picks",
    "editor's choice",
    "breaking news",
    "sponsored content",
    "konten bersponsor",
    "iklan",
    "promoted content",
    "dapatkan update berita",
    "gabung di channel",
    "gabung grup telegram",
    "ikuti kami di",
    "follow kami di",
    "jangan lewatkan video",
    "jangan lewatkan:",
]

BOILERPLATE_PATTERNS = [
    re.compile(r"^baca juga\s*:", re.IGNORECASE),
    re.compile(r"^simak (?:juga )?video\b", re.IGNORECASE),
    re.compile(r"^tonton (?:juga )?video\b", re.IGNORECASE),
    re.compile(r"^saksikan (?:juga )?video\b", re.IGNORECASE),
    re.compile(r"^lihat (?:juga|foto)\s*:", re.IGNORECASE),
    re.compile(r"^(?:foto|video|infografis)\s*:", re.IGNORECASE),
    re.compile(r"^(?:editor|reporter|pewarta|penulis|kontributor|sumber)\s*:", re.IGNORECASE),
    re.compile(r"^read (?:more|also)\s*:", re.IGNORECASE),
    re.compile(r"^(?:also read|see also|related)\s*:", re.IGNORECASE),
    re.compile(r"^\(.*(?:baca|read|see)\s.*\)$", re.IGNORECASE),
    re.compile(r"^advertisement\s*$", re.IGNORECASE),
    re.compile(r"^iklan\s*$", re.IGNORECASE),
    re.compile(r"^sponsored\b", re.IGNORECASE),
    re.compile(r"^halaman\s+\d+\s*(?:dari\s+\d+)?$", re.IGNORECASE),
    re.compile(r"^page\s+\d+\s*(?:of\s+\d+)?$", re.IGNORECASE),
    re.compile(r"^(?:share|bagikan)\s*:", re.IGNORECASE),
    re.compile(r"^tag\s*:", re.IGNORECASE),
    re.compile(r"^(?:cek|simak) berita\b", re.IGNORECASE),
    re.compile(r"^(?:dapatkan|gabung|ikuti|follow)\b.*(?:update|channel|telegram|whatsapp|newsletter|twitter|instagram|facebook|tiktok|youtube|x\.com)", re.IGNORECASE),
    re.compile(r"^(?:ikuti|follow)\s+kami\b", re.IGNORECASE),
]

_SHORT_NOISE_WORDS = {
    "scroll", "advertisement", "iklan", "klik", "click",
    "baca", "read", "share", "bagikan", "subscribe",
    "download", "unduh", "sponsored", "lanjutkan", "continue",
    "selengkapnya", "selanjutnya", "tonton", "simak", "saksikan",
}


_INLINE_PHRASES = [p for p in BOILERPLATE_EXACT if len(p.split()) >= 2]

_INLINE_BOILERPLATE_RE = re.compile(
    "|".join(re.escape(phrase) for phrase in sorted(_INLINE_PHRASES, key=len, reverse=True)),
    re.IGNORECASE,
)


def strip_inline_boilerplate(text: str) -> str:
    text = _INLINE_BOILERPLATE_RE.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = strip_inline_boilerplate(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_boilerplate(sentence: str) -> bool:
    stripped = sentence.strip()
    lowered = stripped.lower()

    if lowered in BOILERPLATE_EXACT:
        return True

    for pattern in BOILERPLATE_PATTERNS:
        if pattern.search(stripped):
            return True

    words = lowered.split()
    if len(words) < 4 and any(w in _SHORT_NOISE_WORDS for w in words):
        return True

    return False


def filter_boilerplate_sentences(sentences: list) -> list:
    return [s for s in sentences if not _is_boilerplate(s)]

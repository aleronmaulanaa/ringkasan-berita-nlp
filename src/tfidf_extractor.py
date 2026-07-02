from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import numpy as np

_STOPWORDS_ID = list(stopwords.words("indonesian"))


def extract_keywords(
    sentences: list[str],
    lang: str = "id",
    top_n: int = 10,
) -> list[tuple[str, float]]:
    if not sentences:
        return []

    stop = _STOPWORDS_ID if lang == "id" else "english"
    vectorizer = TfidfVectorizer(stop_words=stop, max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(sentences)

    feature_names = vectorizer.get_feature_names_out()
    scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()

    ranked_indices = scores.argsort()[::-1][:top_n]
    return [(feature_names[i], float(scores[i])) for i in ranked_indices]

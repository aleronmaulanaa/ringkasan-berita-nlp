import math
import numpy as np
from .preprocessor import tokenize_words, remove_stopwords


def _sentence_words(sentence: str, lang: str) -> set[str]:
    words = tokenize_words(sentence)
    return set(remove_stopwords(words, lang))


def _similarity(words_i: set[str], words_j: set[str]) -> float:
    """Mihalcea & Tarau (2004) sentence similarity:
    overlap(Si, Sj) / (log(|Si|) + log(|Sj|))"""
    if len(words_i) <= 1 or len(words_j) <= 1:
        return 0.0
    overlap = len(words_i & words_j)
    if overlap == 0:
        return 0.0
    denom = math.log(len(words_i)) + math.log(len(words_j))
    if denom == 0:
        return 0.0
    return overlap / denom


def build_similarity_matrix(sentences: list[str], lang: str) -> np.ndarray:
    n = len(sentences)
    word_sets = [_sentence_words(s, lang) for s in sentences]
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            sim = _similarity(word_sets[i], word_sets[j])
            matrix[i][j] = sim
            matrix[j][i] = sim
    return matrix


def _power_iteration(matrix: np.ndarray, d: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> np.ndarray:
    n = matrix.shape[0]
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    transition = matrix / row_sums

    scores = np.ones(n) / n
    for _ in range(max_iter):
        prev = scores.copy()
        scores = (1 - d) / n + d * transition.T @ scores
        if np.abs(scores - prev).sum() < tol:
            break
    return scores


def textrank_summarize(
    sentences: list[str],
    lang: str = "id",
    top_n: int = 5,
    damping: float = 0.85,
) -> list[str]:
    if len(sentences) <= top_n:
        return sentences

    sim_matrix = build_similarity_matrix(sentences, lang)
    scores = _power_iteration(sim_matrix, d=damping)

    ranked_indices = scores.argsort()[::-1][:top_n]
    selected = sorted(ranked_indices)
    return [sentences[i] for i in selected]

"""Modul TextRank: peringkasan ekstraktif berbasis graf kemiripan antar-kalimat.

Implementasi mengacu pada jurnal Mihalcea & Tarau (2004),
"TextRank: Bringing Order into Texts".
"""

import math
import numpy as np
from .preprocessor import tokenize_words, remove_stopwords


def _sentence_words(sentence: str, lang: str) -> set[str]:
    """Konversi kalimat menjadi himpunan kata bermakna (tanpa stopwords).

    Parameter:
        sentence: kalimat yang akan diproses.
        lang: kode bahasa ('id' atau 'en').
    Return:
        Himpunan (set) kata-kata bermakna dari kalimat.
    """
    words = tokenize_words(sentence)
    return set(remove_stopwords(words, lang))


def _similarity(words_i: set[str], words_j: set[str]) -> float:
    """Hitung kemiripan dua kalimat menggunakan formula Mihalcea & Tarau (2004):
    similarity(Si, Sj) = |Si ∩ Sj| / (log|Si| + log|Sj|)

    Formula ini menghitung jumlah kata yang overlap (irisan) antara dua kalimat,
    dinormalisasi dengan jumlah logaritma panjang masing-masing kalimat.

    Parameter:
        words_i: himpunan kata kalimat pertama.
        words_j: himpunan kata kalimat kedua.
    Return:
        Skor kemiripan (float), 0.0 jika tidak ada overlap atau kalimat terlalu pendek.
    """
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
    """Bangun matriks kemiripan simetris antar semua pasangan kalimat.

    Parameter:
        sentences: daftar kalimat.
        lang: kode bahasa ('id' atau 'en').
    Return:
        Matriks numpy berukuran n×n berisi skor kemiripan antar-kalimat.
    """
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
    """Hitung skor peringkat kalimat menggunakan algoritma iteratif mirip PageRank.

    Menggunakan damping factor d untuk menyeimbangkan antara skor dari
    tetangga (kalimat yang mirip) dan distribusi seragam.
    Formula iterasi: scores = (1-d)/n + d * M^T * scores

    Parameter:
        matrix: matriks kemiripan antar-kalimat.
        d: damping factor (default 0.85, sesuai PageRank standar).
        max_iter: jumlah iterasi maksimum.
        tol: threshold konvergensi.
    Return:
        Array skor peringkat untuk setiap kalimat.
    """
    n = matrix.shape[0]
    # Normalisasi baris agar menjadi matriks transisi (stochastic matrix)
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
    """Ringkas teks dengan memilih kalimat terpenting menggunakan TextRank.

    Parameter:
        sentences: daftar kalimat dari teks asli.
        lang: kode bahasa ('id' atau 'en').
        top_n: jumlah kalimat yang dipilih untuk ringkasan.
        damping: damping factor untuk algoritma PageRank.
    Return:
        Daftar kalimat terpilih, diurutkan sesuai posisi aslinya dalam teks.
    """
    if len(sentences) <= top_n:
        return sentences

    sim_matrix = build_similarity_matrix(sentences, lang)
    scores = _power_iteration(sim_matrix, d=damping)

    ranked_indices = scores.argsort()[::-1][:top_n]
    # Urutkan kembali berdasarkan posisi asli agar ringkasan tetap koheren
    selected = sorted(ranked_indices)
    return [sentences[i] for i in selected]

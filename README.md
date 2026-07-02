# 📰 Ringkasan Berita NLP

Aplikasi web *extractive text summarization* untuk artikel berita berbahasa Indonesia dan Inggris, menggunakan metode **TF-IDF** dan **TextRank** (algoritma *graph-based ranking* yang diadaptasi dari PageRank).

🔗 **Live Demo:** [news-summarize-ai.streamlit.app](https://news-summarize-ai.streamlit.app/)

---

## 📋 Daftar Isi

- [Tentang Aplikasi](#tentang-aplikasi)
- [Fitur](#fitur)
- [Arsitektur Pipeline](#arsitektur-pipeline)
- [Tech Stack](#tech-stack)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi & Menjalankan Lokal](#instalasi--menjalankan-lokal)
- [Cara Penggunaan](#cara-penggunaan)
- [Hasil Evaluasi](#hasil-evaluasi)
- [Referensi](#referensi)
- [Lisensi](#lisensi)

---

## Tentang Aplikasi

Di tengah banjir informasi digital, membaca artikel berita secara utuh satu per satu memakan banyak waktu. **Ringkasan Berita NLP** membantu memadatkan sebuah artikel menjadi beberapa kalimat inti secara otomatis, tanpa perlu membaca keseluruhan teks.

Aplikasi ini menggunakan pendekatan **extractive summarization** — memilih kalimat-kalimat paling representatif langsung dari teks asli, bukan menghasilkan kalimat baru (*abstractive*). Pendekatan ini dipilih karena hasilnya selalu dapat ditelusuri kembali ke sumber aslinya, sehingga tidak berisiko menghasilkan informasi yang menyimpang dari artikel.

Dua metode inti yang digunakan:
- **TF-IDF (Term Frequency–Inverse Document Frequency)** untuk mengekstraksi kata kunci dominan dari artikel.
- **TextRank** untuk menentukan kalimat mana yang paling penting, berdasarkan seberapa besar kemiripannya dengan kalimat-kalimat lain dalam artikel.

## Fitur

- ✅ Ringkas artikel langsung dari **URL** atau dari **teks yang ditempel manual**
- ✅ Mendukung **Bahasa Indonesia dan Inggris**, dengan deteksi bahasa otomatis
- ✅ Filter *boilerplate* otomatis — menghapus noise seperti "Baca juga:", "Advertisement", "Scroll to continue", dll. (dua lapis: substring inline & filter kalimat penuh)
- ✅ Ekstraksi **kata kunci dominan** berbasis TF-IDF
- ✅ Pengaturan jumlah kalimat ringkasan & jumlah kata kunci (slider di sidebar)
- ✅ Dua mode tampilan ringkasan: **List Bernomor** atau **Paragraf mengalir**
- ✅ **Fitur terjemahan** hasil ringkasan (Asli / Bahasa Indonesia / English), terpisah dari pipeline inti sehingga tidak memengaruhi hasil ringkasan itu sendiri
- ✅ Statistik teks (jumlah kalimat asli vs ringkasan, rasio kompresi, bahasa terdeteksi)

## Arsitektur Pipeline

```
URL / Teks Input
      │
      ▼
┌─────────────────┐
│  1. Scraping     │  requests + BeautifulSoup4 (fallback: trafilatura)
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  2. Cleaning     │  Hapus URL, email, tag HTML, boilerplate inline & per-kalimat
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  3. Preprocessing│  Deteksi bahasa, tokenisasi, stopword removal,
│                  │  stemming (Sastrawi untuk ID, Porter Stemmer untuk EN)
└─────────────────┘
      │
      ├──────────────────────┐
      ▼                      ▼
┌─────────────────┐   ┌──────────────────────┐
│ 4. TF-IDF        │   │ 5. TextRank           │
│ Keyword          │   │ - Similarity matrix:  │
│ Extraction       │   │   overlap(Si,Sj) /    │
│ (scikit-learn)   │   │   (log|Si|+log|Sj|)   │
│                  │   │ - Power iteration      │
│                  │   │   (damping d=0.85)     │
└─────────────────┘   └──────────────────────┘
                              │
                              ▼
                     ┌──────────────────────┐
                     │ 6. Seleksi Top-N      │
                     │    Kembalikan ke      │
                     │    urutan asli teks   │
                     └──────────────────────┘
                              │
                              ▼
                     ┌──────────────────────┐
                     │ 7. (Opsional)         │
                     │    Terjemahan tampilan │
                     └──────────────────────┘
                              │
                              ▼
                     Ringkasan + Keyword + Statistik
```

Formula *sentence similarity* pada tahap TextRank:

$$Similarity(S_i, S_j) = \frac{|\{w_k \mid w_k \in S_i \ \& \ w_k \in S_j\}|}{\log|S_i| + \log|S_j|}$$

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Bahasa Pemrograman | Python 3.9+ |
| Web Framework | Streamlit |
| Web Scraping | requests, BeautifulSoup4, trafilatura |
| Text Preprocessing | NLTK (Inggris), Sastrawi (Indonesia) |
| Feature Extraction | scikit-learn (TfidfVectorizer) |
| Ranking Algorithm | Custom TextRank (NumPy, power iteration) |
| Evaluasi | rouge-score |
| Terjemahan | deep-translator |
| Deployment | Streamlit Community Cloud |

## Struktur Proyek

```
ringkasan-berita-nlp/
├── app.py                      # Entry point aplikasi Streamlit (UI)
├── requirements.txt            # Daftar dependency
├── README.md
├── data/
│   └── sample_articles.json    # Artikel uji + reference summary (untuk evaluasi ROUGE)
├── src/
│   ├── __init__.py             # Re-export seluruh fungsi publik
│   ├── scraper.py              # Web scraping (BeautifulSoup, fallback trafilatura)
│   ├── cleaner.py               # Text cleaning & filter boilerplate (2 lapis)
│   ├── preprocessor.py          # Tokenisasi, stopword removal, stemming, deteksi bahasa
│   ├── tfidf_extractor.py       # Ekstraksi kata kunci berbasis TF-IDF
│   ├── textrank.py              # Similarity function & power iteration TextRank
│   ├── summarizer.py            # Orchestrator pipeline (summarize_url, summarize_text)
│   └── translator.py            # Terjemahan hasil ringkasan (post-processing tampilan)
└── tests/
    ├── __init__.py
    └── evaluate_rouge.py         # Evaluasi ROUGE-1/2/L terhadap reference summary
```

## Instalasi & Menjalankan Lokal

```bash
# 1. Clone repository
git clone https://github.com/aleronmaulanaa/ringkasan-berita-nlp.git
cd ringkasan-berita-nlp

# 2. Buat & aktifkan virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependency
pip install -r requirements.txt

# 4. Download resource NLTK yang dibutuhkan
python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

# 5. Jalankan aplikasi
python3 -m streamlit run app.py
```

Aplikasi akan terbuka otomatis di `http://localhost:8501`.

## Cara Penggunaan

1. Buka aplikasi (lokal atau [live demo](https://news-summarize-ai.streamlit.app/)).
2. Pilih tab **"Dari URL"** untuk meringkas artikel dari tautan, atau **"Dari Teks"** untuk menempelkan teks secara manual.
3. Atur **jumlah kalimat ringkasan** dan **jumlah kata kunci** melalui slider di sidebar.
4. (Opsional) Pilih bahasa tampilan hasil di bagian **Terjemahan** pada sidebar.
5. Klik tombol **Ringkas**, dan hasil akan ditampilkan lengkap dengan statistik teks, kata kunci TF-IDF, serta teks asli yang sudah dibersihkan.

## Hasil Evaluasi

Evaluasi dilakukan terhadap 5 artikel berita nyata (3 Bahasa Indonesia, 2 Bahasa Inggris) menggunakan *reference summary* yang ditulis ulang secara manual (paraphrase independen, bukan kutipan langsung dari artikel).

| Metrik | F1-Score (rata-rata) |
|---|---|
| ROUGE-1 | 0.4550 |
| ROUGE-2 | 0.2221 |
| ROUGE-L | 0.3153 |

Rentang skor ini konsisten dengan karakteristik metode *extractive summarization* berbasis graph-ranking tanpa *supervised learning*.

## Referensi

Metode inti aplikasi ini merujuk pada algoritma TextRank yang diperkenalkan oleh:

> Mihalcea, R., & Tarau, P. (2004). *TextRank: Bringing Order into Texts.* Proceedings of EMNLP 2004.

## Lisensi

Proyek ini dibuat untuk keperluan pembelajaran dan dapat digunakan secara bebas untuk tujuan non-komersial. Silakan sesuaikan lisensi sesuai kebutuhan Anda.
import streamlit as st
from src.summarizer import summarize_url, summarize_text

st.set_page_config(page_title="Peringkas Berita Otomatis", layout="wide")
st.title("Peringkas Artikel Berita Otomatis")
st.caption("Ekstraktif · TextRank + TF-IDF · Bahasa Indonesia & Inggris")

tab_url, tab_text = st.tabs(["Dari URL", "Dari Teks"])

with st.sidebar:
    st.header("Pengaturan")
    lang_option = st.selectbox("Bahasa", ["Deteksi Otomatis", "Indonesia", "English"])
    lang_map = {"Deteksi Otomatis": None, "Indonesia": "id", "English": "en"}
    lang = lang_map[lang_option]
    top_n = st.slider("Jumlah kalimat ringkasan", 1, 15, 5)
    num_keywords = st.slider("Jumlah kata kunci", 5, 30, 10)

with tab_url:
    url = st.text_input("Masukkan URL artikel berita:")
    if st.button("Ringkas dari URL", type="primary"):
        if not url.strip():
            st.warning("Masukkan URL terlebih dahulu.")
        else:
            with st.spinner("Mengambil dan meringkas artikel..."):
                try:
                    result = summarize_url(url, lang=lang, top_n=top_n, num_keywords=num_keywords)
                    st.session_state["result"] = result
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

with tab_text:
    text_input = st.text_area("Tempel teks artikel di sini:", height=250)
    if st.button("Ringkas dari Teks", type="primary"):
        if not text_input.strip():
            st.warning("Masukkan teks terlebih dahulu.")
        else:
            with st.spinner("Meringkas teks..."):
                try:
                    result = summarize_text(text_input, lang=lang, top_n=top_n, num_keywords=num_keywords)
                    st.session_state["result"] = result
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()

    if "title" in result:
        st.subheader(result["title"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Kalimat Asli", result["num_sentences_original"])
    col2.metric("Kalimat Ringkasan", result["num_sentences_summary"])
    col3.metric("Bahasa", "Indonesia" if result["lang"] == "id" else "English")

    st.subheader("Ringkasan")
    display_mode = st.radio(
        "Tampilan:",
        ["List Bernomor", "Paragraf"],
        horizontal=True,
    )
    if display_mode == "List Bernomor":
        for i, sent in enumerate(result["summary_sentences"], 1):
            st.write(f"{i}. {sent}")
    else:
        st.write(" ".join(result["summary_sentences"]))

    st.subheader("Kata Kunci (TF-IDF)")
    kw_cols = st.columns(min(len(result["keywords"]), 5))
    for i, (word, score) in enumerate(result["keywords"]):
        kw_cols[i % len(kw_cols)].code(f"{word}: {score:.4f}")

    with st.expander("Lihat teks asli (sudah dibersihkan)"):
        st.write(result["cleaned_text"])

    if "scrape_method" in result:
        st.caption(f"Metode scraping: {result['scrape_method']}")

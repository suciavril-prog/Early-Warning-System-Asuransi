"""Aplikasi web Early Warning System perusahaan asuransi (prototipe LPS–SBM ITB).

Jalankan:  streamlit run app.py
"""
import streamlit as st

from ews.ui import inisialisasi

inisialisasi()

halaman = {
    "Mulai di sini": [
        st.Page("halaman/beranda.py", title="Beranda", icon=":material/home:", default=True),
        st.Page("halaman/tentang.py", title="Tentang EWS", icon=":material/school:"),
    ],
    "Hasil penelitian": [
        st.Page("halaman/ringkasan.py", title="Ringkasan temuan", icon=":material/dashboard:"),
        st.Page("halaman/indikator.py", title="Indikator", icon=":material/insights:"),
        st.Page("halaman/model.py", title="Model dan validasi", icon=":material/fact_check:"),
        st.Page("halaman/kegagalan.py", title="Kasus kegagalan", icon=":material/warning:"),
        st.Page("halaman/skor2026.py", title="Skor 2026", icon=":material/leaderboard:"),
    ],
    "Alat skor": [
        st.Page("halaman/simulator.py", title="Simulator entitas", icon=":material/tune:"),
        st.Page("halaman/pantauan.py", title="Daftar pantauan", icon=":material/table_view:"),
    ],
    "Bantuan": [
        st.Page("halaman/panduan.py", title="Panduan dan batasan", icon=":material/menu_book:"),
    ],
}
st.navigation(halaman).run()

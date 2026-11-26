"""Early Warning System perusahaan asuransi: pusat belajar, penilaian, dan perbandingan
(prototipe penelitian LPS–SBM ITB).

Jalankan:  streamlit run app.py
"""
import streamlit as st

from ews.ui import inisialisasi

inisialisasi()

halaman = {
    "": [st.Page("halaman/beranda.py", title="Beranda", icon=":material/home:", default=True)],
    "Belajar": [
        st.Page("halaman/tentang.py", title="Mengenal EWS", icon=":material/school:"),
        st.Page("halaman/glosarium.py", title="Glosarium", icon=":material/dictionary:"),
    ],
    "Metode penilaian": [
        st.Page("halaman/metode_penilaian.py", title="Profil metode", icon=":material/category:"),
    ],
    "Coba dan bandingkan": [
        st.Page("halaman/bandingkan.py", title="Bandingkan metode", icon=":material/compare_arrows:"),
        st.Page("halaman/simulator.py", title="Simulator model EWS", icon=":material/tune:"),
        st.Page("halaman/pantauan.py", title="Nilai dari Excel", icon=":material/table_view:"),
    ],
    "Model penelitian kami": [
        st.Page("halaman/ringkasan.py", title="Ringkasan temuan", icon=":material/dashboard:"),
        st.Page("halaman/indikator.py", title="Indikator", icon=":material/insights:"),
        st.Page("halaman/model.py", title="Model dan validasi", icon=":material/fact_check:"),
        st.Page("halaman/kegagalan.py", title="Kasus kegagalan", icon=":material/warning:"),
        st.Page("halaman/skor2026.py", title="Skor 2026", icon=":material/leaderboard:"),
    ],
    "Bantuan": [
        st.Page("halaman/panduan.py", title="Panduan dan batasan", icon=":material/menu_book:"),
    ],
}
st.navigation(halaman, expanded=True).run()

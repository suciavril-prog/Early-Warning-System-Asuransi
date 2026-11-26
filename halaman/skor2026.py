import streamlit as st

from ews import charts
from ews.data import muat_hasil
from ews.ui import fmt, kaki, kartu_angka, kepala, sumber

dist = muat_hasil("skor2026_dist")
seg = muat_hasil("skor2026_segmen")
kunci = muat_hasil("angka_kunci").set_index("kode")["nilai"]
tot = seg.set_index("segmen").loc["Total"]

kepala("Skor risiko 2026", label="Hasil penelitian")
st.markdown("Model B2 diterapkan pada laporan tahun buku 2025. Realisasi dibandingkan dengan data YTD September 2026, "
            "sehingga hasil ini masih sementara.")
kartu_angka([
    dict(label="Entitas beralarm", nilai=fmt(tot["alarm"], 0), nada="kritis", konteks="seluruhnya asuransi jiwa"),
    dict(label="Sudah D2 (YTD Sep 2026)", nilai=fmt(tot["d2_ytd_sep"], 0), nada="waspada",
         konteks="realisasi sementara"),
    dict(label="Presisi alarm", nilai=fmt(kunci["presisi_alarm"], 0) + "%", nada="utama",
         konteks="alarm yang terbukti D2; sekitar lima kali tingkat dasar"),
    dict(label="Sensitivitas alarm", nilai=fmt(kunci["sensitivitas_alarm"], 0) + "%", nada="utama",
         konteks="kejadian D2 yang sudah beralarm"),
])

kiri, kanan = st.columns(2)
with kiri:
    st.subheader("Distribusi probabilitas")
    st.plotly_chart(charts.distribusi(dist), width="stretch")
    sumber("Tabel 6.18")
with kanan:
    st.subheader("Ringkasan per segmen")
    st.dataframe(seg.rename(columns={"segmen": "Segmen", "perusahaan": "Perusahaan", "median_p": "Median prob. (%)",
                                     "rata_p": "Rata-rata prob. (%)", "alarm": "Alarm", "d2_ytd_sep": "D2 YTD Sep"}),
                 hide_index=True, width="stretch")
    sumber("Tabel 6.19")
    st.warning("Daftar bernama hanya disampaikan kepada LPS (Bagian 5.9). Untuk menilai entitas nyata, gunakan "
               "halaman Daftar pantauan dengan data Anda sendiri.")
kaki()

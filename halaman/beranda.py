import streamlit as st

from ews import charts
from ews.data import muat_hasil
from ews.ui import fmt, kaki, kartu_angka, kepala, kotak, sumber

kunci = muat_hasil("angka_kunci").set_index("kode")["nilai"]
kin = muat_hasil("kinerja").set_index("model")
seg26 = muat_hasil("skor2026_segmen").set_index("segmen")
b2, b0 = kin.loc["B2 EWS keuangan · hazard"], kin.loc["B0 modal saja · hazard"]

kepala("Kenali perusahaan asuransi berisiko sebelum terlambat",
       "Sistem peringatan dini ini memperkirakan peluang sebuah perusahaan asuransi <b>mulai mengalami financial "
       "distress tahun depan</b>, hanya dari laporan keuangan yang dipublikasikan. Hasilnya berupa peluang, "
       "bukan vonis.", label="Early Warning System · prototipe penelitian LPS–SBM ITB", hero=True)

a, b, c, _ = st.columns([1, 1, 1, 1.2])
a.page_link("halaman/tentang.py", label="Apa itu EWS?", icon=":material/school:")
b.page_link("halaman/simulator.py", label="Coba simulator", icon=":material/tune:")
c.page_link("halaman/skor2026.py", label="Lihat skor 2026", icon=":material/leaderboard:")

st.subheader("Empat angka terpenting")
kartu_angka([
    dict(label="Perusahaan beralarm 2026", nilai=fmt(seg26.loc["Total", "alarm"], 0), nada="kritis",
         konteks=f"dari {fmt(seg26.loc['Total', 'perusahaan'], 0)} perusahaan; seluruhnya asuransi jiwa. "
                 "Hasil sementara."),
    dict(label="Ketepatan model EWS (AUC)", nilai=fmt(b2["auc"], 3), nada="utama",
         konteks=f"dibanding {fmt(b0['auc'], 3)} untuk model modal saja, pada data uji 2023–2025"),
    dict(label="Awal financial distress", nilai=fmt(kunci["onset"], 0), nada="waspada",
         konteks=f"kejadian dari {fmt(kunci['risk_set'], 0)} firm-year berisiko, 2016–2025"),
    dict(label="Kegagalan terkait keuangan", nilai=fmt(kunci["gagal"], 0), nada="netral",
         konteks="pencabutan izin usaha dalam periode observasi"),
])

st.subheader("Apa yang bisa Anda lakukan di sini")
k = st.columns(3)
kartu = [
    ("Memahami EWS", "Pengertian, analogi sederhana, definisi distress, dan cara membaca hasil model.",
     "halaman/tentang.py", "Buka Tentang EWS", ":material/school:"),
    ("Menilai satu perusahaan", "Isi enam rasio dari Laporan Publikasi, lalu lihat peluang, status, dan "
     "faktor pendorongnya.", "halaman/simulator.py", "Buka Simulator", ":material/tune:"),
    ("Menilai banyak perusahaan", "Unggah berkas CSV atau Excel dan dapatkan daftar pantauan yang bisa diunduh.",
     "halaman/pantauan.py", "Buka Daftar pantauan", ":material/table_view:"),
]
for kol, (judul, teks, hal, lab, ik) in zip(k, kartu):
    with kol.container(border=True):
        st.markdown(f"**{judul}**")
        st.caption(teks)
        st.page_link(hal, label=lab, icon=ik)

kiri, kanan = st.columns([1.5, 1])
with kiri:
    with st.container(border=True):
        st.markdown("**Tingkat financial distress (D2) per tahun**")
        st.plotly_chart(charts.tren(muat_hasil("tren"), "d2"), width="stretch")
        sumber("Tabel 6.3, proporsi firm-year berstatus distress")
with kanan:
    st.markdown("**Temuan utama**")
    kotak(f"<b>RBC saja tidak cukup.</b> Seluruh {fmt(kunci['onset_rbc'], 0)} awal distress yang memiliki data RBC "
          f"tercatat ber-RBC di atas 120% satu tahun sebelumnya.")
    kotak("<b>Rasio klaim adalah sinyal dini terkuat.</b> ROA dan rasio klaim memburuk sekitar tiga tahun sebelum "
          "tindakan OJK, setahun lebih awal dari runtuhnya ekuitas.")
    kotak("<b>Batas penggunaan.</b> Skor adalah alat penyaring untuk memprioritaskan pemeriksaan, bukan dasar "
          "sanksi. Definisi distress D2 adalah usulan tim dan belum divalidasi terhadap status pengawasan OJK.",
          "awas")
kaki()

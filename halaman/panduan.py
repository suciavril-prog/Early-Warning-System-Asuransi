import streamlit as st

from ews.model import muat_konfigurasi
from ews.ui import fmt, kaki, kepala

cfg = muat_konfigurasi()

kepala("Panduan dan batasan", label="Bantuan")

st.subheader("Cara kerja")
st.markdown(
    "**Tingkat 1, skor kuantitatif.** Model B2 memperkirakan probabilitas perusahaan yang belum distress akan "
    "memasuki distress D2 pada tahun t, dari indikator tahun t−1: rasio klaim, ROA, ekuitas/aset, pertumbuhan premi "
    "bruto, ukuran perusahaan (ln aset), dan lini usaha.\n\n"
    "**Tingkat 2, penanda kegagalan.** Untuk entitas yang sudah atau hampir distress: ekuitas negatif, ROA negatif, "
    "rugi dua tahun berturut-turut, label D2 pada tahun berjalan, dan ekuitas di bawah ekuitas minimum tahap pertama "
    "POJK 23/2023. Penanda ini sensitif tetapi tidak spesifik, dan belum dikalibrasi menjadi skor karena hanya ada "
    "tujuh kegagalan."
)
st.subheader("Model yang sedang dipakai")
st.json({k: v for k, v in cfg.meta.items() if k != "median_referensi"}, expanded=False)
st.caption(f"Ambang alarm bawaan {fmt(cfg.ambang * 100, 1)}%. Koefisien dibaca dari config/koefisien.json; "
           "lihat docs/PANDUAN_PEMUTAKHIRAN.md untuk memperbaruinya.")

st.subheader("Batas penggunaan")
st.markdown(
    "1. Alat penyaring, bukan bukti sebab-akibat dan bukan dasar pengenaan sanksi.\n"
    "2. Tidak mendeteksi kegagalan akibat pelanggaran tata kelola yang tidak tampak pada rasio keuangan publik.\n"
    "3. Penerapan pada entitas spin-off baru adalah ekstrapolasi: kohor pasca-POJK 11/2023 hanya tiga firm-year "
    "dalam sampel estimasi.\n"
    "4. Tidak berlaku untuk reasuransi.\n"
    "5. Definisi D2 adalah usulan tim dan belum divalidasi terhadap status pengawasan OJK.\n"
    "6. Rasio klaim asuransi jiwa mencakup manfaat jatuh tempo dan penebusan, sehingga sebagian efek lini jiwa bisa "
    "merupakan artefak pengukuran.\n"
    "7. Model diestimasi pada data winsorize P1/P99; input ekstrem menghasilkan probabilitas jenuh."
)
st.warning(f"**Asumsi satuan aset.** {cfg.meta.get('satuan_aset_ln', '')}. Satuan yang keliru menggeser skor secara "
           "besar; konfirmasi dengan berkas data panel sebelum dipakai untuk keputusan.")
st.subheader("Kerahasiaan")
st.markdown("Skor per entitas bernama hanya untuk LPS sebagai pemberi mandat (Bagian 5.9 proposal). Jalankan "
            "aplikasi di server dengan login aktif bila memuat data bernama.")
kaki()

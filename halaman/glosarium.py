import pandas as pd
import streamlit as st

from ews.ui import kaki, kepala

kepala("Glosarium", "Istilah yang sering muncul di aplikasi ini, dijelaskan dengan bahasa sederhana.", label="Belajar")

ISTILAH = [
    ("Early Warning System (EWS)", "Sistem indikator dan model yang memberi sinyal ketika risiko perusahaan mulai memburuk."),
    ("Financial distress", "Kondisi keuangan memburuk tetapi perusahaan masih dapat pulih. Di penelitian ini diukur dengan D2."),
    ("D2", "Definisi distress penelitian ini: ekuitas negatif, atau RBC di bawah 100%, atau rugi bersih bersamaan dengan rugi underwriting."),
    ("Kegagalan", "Izin usaha dicabut OJK karena kesehatan keuangan atau pelanggaran yang merugikan pemegang polis."),
    ("RBC (risk-based capital)", "Tingkat solvabilitas: modal yang tersedia dibanding modal minimum berbasis risiko. Minimum 100%."),
    ("Ekuitas", "Aset dikurangi liabilitas; modal sendiri perusahaan."),
    ("Rasio klaim", "Beban klaim dibagi pendapatan premi neto. Di atas 100% berarti klaim melebihi premi."),
    ("ROA", "Laba bersih dibagi total aset. Negatif berarti rugi."),
    ("Hasil underwriting", "Hasil dari kegiatan inti asuransi (premi dikurangi klaim dan beban terkait), di luar hasil investasi."),
    ("Premi bruto dan neto", "Bruto: seluruh premi yang ditulis. Neto: setelah dikurangi bagian yang direasuransikan."),
    ("Firm-year", "Satu perusahaan pada satu tahun. Sepuluh perusahaan selama lima tahun = 50 firm-year."),
    ("Onset (awal distress)", "Tahun pertama perusahaan masuk kondisi distress setelah sebelumnya tidak distress."),
    ("Model hazard waktu diskret", "Model yang memperkirakan peluang suatu kejadian terjadi tahun ini, bila belum terjadi sebelumnya, memakai seluruh riwayat tahunan."),
    ("Koreksi Firth", "Penyesuaian statistik agar regresi logistik tetap stabil ketika kejadiannya jarang."),
    ("Peluang (probabilitas)", "Angka 0–100% yang menunjukkan seberapa mungkin perusahaan mulai distress tahun depan."),
    ("Ambang alarm", "Batas peluang yang memicu status Alarm. Bawaan 17,3%; ambang kebijakan ditetapkan LPS."),
    ("AUC", "Ukuran daya pembeda model. 0,5 = tebakan acak, 1 = sempurna."),
    ("Brier score", "Rata-rata kuadrat selisih peluang prediksi dan kejadian nyata. Makin kecil makin baik."),
    ("Data uji (out-of-sample)", "Data yang tidak dipakai saat membuat model, untuk menguji kinerja secara jujur."),
    ("IRIS", "Insurance Regulatory Information System dari NAIC (Amerika Serikat): rasio peringatan dengan rentang wajar."),
    ("Spin-off syariah", "Pemisahan unit usaha syariah menjadi perusahaan asuransi syariah tersendiri (POJK 11/2023)."),
    ("Program Penjaminan Polis (PPP)", "Mandat LPS dari UU 4/2023 (P2SK) untuk menjamin polis asuransi."),
]
cari = st.text_input("Cari istilah", placeholder="misalnya: RBC")
df = pd.DataFrame(ISTILAH, columns=["Istilah", "Arti"])
if cari:
    df = df[df.apply(lambda r: cari.lower() in (r["Istilah"] + r["Arti"]).lower(), axis=1)]
st.dataframe(df, hide_index=True, width="stretch", height=min(40 + 36 * len(df), 820))
if df.empty:
    st.caption("Istilah tidak ditemukan. Coba kata lain.")
kaki()

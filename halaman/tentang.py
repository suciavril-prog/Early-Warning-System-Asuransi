import pandas as pd
import streamlit as st

from ews.data import muat_hasil
from ews.ui import fmt, kaki, kartu_angka, kepala, kotak, langkah

lb = muat_hasil("latar_belakang").set_index("kode")["nilai"]
kin = muat_hasil("kinerja").set_index("model")
kunci = muat_hasil("angka_kunci").set_index("kode")["nilai"]
b2 = kin.loc["B2 EWS keuangan · hazard"]

kepala("Apa itu Early Warning System?",
       "Early Warning System (EWS) atau sistem peringatan dini adalah seperangkat indikator dan model statistik "
       "yang memantau kondisi keuangan perusahaan secara berkala, lalu memberi sinyal ketika risikonya mulai "
       "memburuk. Tujuannya agar masalah terlihat <b>sebelum</b> menjadi kegagalan, sehingga masih ada waktu "
       "untuk bertindak.", label="Mulai di sini")

st.subheader("Tiga cara sederhana memahaminya")
a, b, c = st.columns(3)
with a:
    kotak("<b>Seperti lampu indikator mobil.</b><br>Lampu oli menyala sebelum mesin rusak. Pengemudi belum tahu "
          "kerusakannya, tetapi tahu harus segera memeriksa. EWS memberi \"lampu kuning\" serupa bagi pengawas.",
          "analogi")
with b:
    kotak("<b>Seperti pemeriksaan kesehatan rutin.</b><br>Tekanan darah naik bertahun-tahun sebelum serangan "
          "jantung. EWS memantau rasio klaim dan laba yang memburuk sebelum modal habis.", "analogi")
with c:
    kotak("<b>Seperti prakiraan cuaca.</b><br>\"Peluang hujan 30%\" bukan berarti pasti hujan. Skor EWS juga "
          "berupa peluang, bukan vonis bahwa perusahaan pasti bermasalah.", "analogi")

st.subheader("Mengapa EWS dibutuhkan untuk asuransi di Indonesia")
kartu_angka([
    dict(label="Izin asuransi dicabut OJK, 2011–2025", nilai=fmt(lb["izin_dicabut"], 0), nada="kritis",
         konteks=f"{fmt(lb['gagal_total'], 0)} di antaranya tergolong gagal total"),
    dict(label="Asuransi syariah mandiri", nilai=f"{fmt(lb['syariah_awal_min'], 0)}–{fmt(lb['syariah_awal_max'], 0)}"
         f" → {fmt(lb['syariah_akhir_min'], 0)}–{fmt(lb['syariah_akhir_max'], 0)}", nada="waspada",
         konteks="proyeksi akhir 2026 akibat kewajiban spin-off POJK 11/2023"),
    dict(label="Rencana pemisahan unit syariah", nilai=fmt(lb["rencana_spinoff"], 0), nada="utama",
         konteks="perusahaan yang sudah menyampaikan rencana (per 7 Juli 2026)"),
])
st.markdown(
    "- **Mandat baru LPS.** UU No. 4 Tahun 2023 (P2SK) memberi LPS mandat Program Penjaminan Polis (PPP), yang "
    "disiapkan aktif bertahap mulai 2027. LPS perlu alat untuk mengenali calon peserta yang berisiko sejak awal.\n"
    "- **Banyak entitas baru tanpa rekam jejak.** Gelombang spin-off syariah melahirkan perusahaan yang belum "
    "memiliki riwayat keuangan sendiri.\n"
    "- **RBC saja tidak cukup.** RBC adalah tolok ukur utama kesehatan perusahaan asuransi, tetapi penelitian ini "
    "menemukan RBC tidak membedakan perusahaan yang akan mengalami distress.")
st.caption("Angka latar belakang diambil dari proposal penelitian (Bagian 2.1) dan perlu dicek ulang terhadap "
           "publikasi OJK terbaru sebelum dikutip.")

st.subheader("Tangga masalah perusahaan asuransi")
st.markdown("Istilah-istilah ini sering tertukar. Penelitian ini membedakannya dengan tegas. "
            "**EWS memprediksi anak tangga kedua** (kotak bergaris tebal).")
langkah([
    ("Sehat", "Modal cukup, kinerja usaha positif, kewajiban kepada pemegang polis terpenuhi."),
    ("Financial distress", "Keuangan memburuk tetapi masih dapat pulih. Diukur dengan definisi D2."),
    ("Masalah regulasi", "OJK bertindak, misalnya pengawasan khusus atau pembatasan kegiatan usaha (PKU)."),
    ("Kegagalan", "Izin usaha dicabut karena kesehatan keuangan atau pelanggaran yang merugikan pemegang polis."),
    ("Keluar pasar biasa", "Merger, single presence, atau pengembalian izin sukarela. Tidak dihitung kegagalan."),
], sorot=2)
st.caption("Gagal bayar klaim (default) tidak dimodelkan tersendiri karena tanggal gagal bayar per perusahaan "
           "tidak tersedia di data publik.")

kiri, kanan = st.columns(2)
with kiri:
    with st.container(border=True):
        st.markdown("**Definisi financial distress (D2)**")
        st.markdown("Perusahaan dihitung distress pada suatu tahun bila **salah satu** kondisi berikut terpenuhi:\n"
                    "1. Ekuitas negatif: utang lebih besar dari aset.\n"
                    "2. RBC dilaporkan di bawah batas minimum tingkat solvabilitas 100% (POJK 71/2016, dipertahankan "
                    "POJK 26/2025).\n"
                    "3. Rugi bersih (ROA negatif) **dan** rugi underwriting pada tahun yang sama.")
        st.caption("D2 adalah usulan tim dan belum divalidasi terhadap status pengawasan OJK.")
with kanan:
    with st.container(border=True):
        st.markdown("**Mengapa RBC terbatas sebagai peringatan dini**")
        st.markdown("- **Potret satu waktu:** mengukur modal hari ini, bukan laju kerugian yang menggerusnya.\n"
                    "- **Terlambat:** pada kasus gagal, RBC baru runtuh sekitar dua tahun sebelum tindakan OJK.\n"
                    "- **Jarang tersedia:** hanya dilaporkan pada sebagian kecil data publik.")
        kotak("RBC ibarat isi tangki bahan bakar; rasio klaim dan ROA ibarat laju konsumsinya. Tangki yang masih "
              "penuh tidak memberi tahu bahwa kendaraan sedang bocor.", "analogi")

st.subheader("Kamus indikator")
st.dataframe(pd.DataFrame([
    ("Rasio klaim", "Beban klaim ÷ pendapatan premi neto", "Naik = risiko naik", "Sinyal dini terkuat"),
    ("ROA", "Laba bersih ÷ total aset", "Naik = risiko turun", "Memburuk jelas menjelang kegagalan"),
    ("Ekuitas/aset", "Ekuitas ÷ total aset", "Naik = risiko turun", "Efek kecil sebagai sinyal dini"),
    ("Pertumbuhan premi bruto", "Perubahan premi bruto dari tahun sebelumnya", "Naik = risiko turun",
     "Efek kecil, tidak signifikan"),
    ("Ukuran perusahaan", "ln total aset (juta rupiah)", "Naik = risiko turun", "Perusahaan besar lebih tahan"),
    ("Lini usaha jiwa", "Asuransi jiwa = 1, umum = 0", "Jiwa = risiko lebih tinggi", "Risiko struktural lini jiwa"),
    ("Margin underwriting", "Hasil underwriting ÷ premi neto", "Tidak masuk skor", "Bagian dari definisi D2"),
    ("RBC", "Modal tersedia ÷ modal minimum berbasis risiko", "Tidak masuk skor", "Pemicu D2, bukan sinyal dini"),
], columns=["Indikator", "Cara menghitung", "Arah dalam model", "Catatan"]), hide_index=True, width="stretch")

st.subheader("Cara kerja model, dalam lima langkah")
langkah([
    ("Ambil data", "Enam indikator dari laporan tahun lalu (t−1)."),
    ("Beri bobot", "Kalikan tiap indikator dengan koefisiennya, lalu jumlahkan menjadi skor z."),
    ("Ubah jadi peluang", "Fungsi logistik mengubah z menjadi peluang 0–100%."),
    ("Bandingkan ambang", "Peluang di atas ambang memicu alarm. Ambang kebijakan ditetapkan LPS."),
    ("Periksa Tingkat 2", "Untuk perusahaan yang sudah distress, periksa penanda kegagalan."),
])
st.caption("Model memakai pendekatan discrete-time hazard (Shumway, 2001) yang memanfaatkan seluruh riwayat "
           "tahunan setiap perusahaan, dengan koreksi Firth untuk kejadian yang jarang.")

st.subheader("Cara membaca ukuran kinerja model")
langkah([
    ("AUC", f"Peluang model memberi skor lebih tinggi kepada perusahaan yang kemudian distress. 0,5 = tebakan "
            f"acak, 1 = sempurna. Model EWS: <b>{fmt(b2['auc'], 3)}</b>."),
    ("Brier score", f"Rata-rata kuadrat selisih peluang prediksi dan kejadian nyata. Makin kecil makin baik. "
                    f"Model EWS: <b>{fmt(b2['brier'], 3)}</b>."),
    ("Kalibrasi", f"Apakah rata-rata peluang sesuai kenyataan. Prediksi rata-rata <b>{fmt(b2['rata_prediksi'])}%</b>, "
                  f"kejadian nyata <b>{fmt(kunci['laju_aktual_uji'])}%</b>."),
], bernomor=False)

a, b, _ = st.columns([1, 1, 2])
a.page_link("halaman/ringkasan.py", label="Lanjut ke Ringkasan temuan", icon=":material/arrow_forward:")
b.page_link("halaman/simulator.py", label="Coba sendiri di Simulator", icon=":material/tune:")
kaki()

import streamlit as st

from ews.ui import kaki, kepala, kotak, langkah

kepala("Metode penilaian financial distress",
       "Ada banyak cara menilai apakah perusahaan asuransi mulai bermasalah. Pilih satu metode untuk melihat "
       "konsepnya, indikator yang dipakai, cara kerjanya, serta kelebihan dan keterbatasannya.",
       label="Metode penilaian")

M = {
    "Aturan regulasi (RBC)": dict(
        jenis="Berbasis ketentuan regulator",
        tentang="Regulator menetapkan batas minimum yang wajib dipenuhi. Di Indonesia, tolok ukur utamanya adalah "
                "tingkat solvabilitas berbasis risiko (RBC) dan ekuitas minimum. Perusahaan yang berada di bawah "
                "batas menjadi perhatian pengawas.",
        indikator=["RBC: modal yang tersedia dibanding modal minimum berbasis risiko. Minimum 100%, target "
                   "internal minimal 120% (POJK 71/2016).",
                   "Ekuitas minimum: Rp250 miliar untuk konvensional dan Rp100 miliar untuk syariah pada tahap "
                   "pertama (POJK 23/2023)."],
        alur=[("Data laporan", "RBC dan ekuitas dari laporan berkala."),
              ("Bandingkan batas", "Apakah di atas batas minimum?"),
              ("Hasil", "Memenuhi atau tidak memenuhi.")],
        plus=["Dasar hukum jelas dan berlaku untuk semua perusahaan.", "Mudah dipahami dan diperiksa."],
        minus=["Potret satu waktu; tidak menangkap laju kerugian.",
               "Cenderung terlambat: pada kasus gagal dalam penelitian ini, RBC baru runtuh sekitar dua tahun "
               "sebelum tindakan OJK.",
               "Dalam data penelitian, seluruh 11 awal distress yang memiliki data RBC masih ber-RBC di atas 120% "
               "setahun sebelumnya.",
               "Data RBC jarang tersedia lengkap di laporan publik."],
        coba="bandingkan"),
    "Penanda sederhana": dict(
        jenis="Berbasis aturan praktis (rule of thumb)",
        tentang="Beberapa kondisi keuangan yang jelas buruk dicek satu per satu. Makin banyak penanda yang menyala, "
                "makin perlu perusahaan diperiksa.",
        indikator=["Ekuitas negatif", "Rugi bersih", "Rugi dua tahun berturut-turut", "Rasio klaim di atas 100%",
                   "Rugi underwriting"],
        alur=[("Data laporan", "Laba, ekuitas, klaim, hasil underwriting."),
              ("Cek tiap kondisi", "Ya atau tidak."),
              ("Hasil", "Jumlah penanda yang menyala.")],
        plus=["Sangat mudah dan transparan.", "Berguna untuk perusahaan yang sudah bermasalah (dipakai sebagai "
                                             "Tingkat 2 dalam penelitian ini)."],
        minus=["Tidak memberi peluang; hanya ya atau tidak.", "Banyak alarm palsu: perusahaan sehat pun bisa rugi "
                                                               "sesekali.",
               "Tidak ada bobot; semua penanda dianggap sama penting.", "Sering baru menyala ketika masalah sudah "
                                                                         "terjadi."],
        coba="bandingkan"),
    "Rasio peringatan IRIS (NAIC)": dict(
        jenis="Rasio khusus industri asuransi",
        tentang="Insurance Regulatory Information System (IRIS) dikembangkan oleh National Association of "
                "Insurance Commissioners (NAIC) di Amerika Serikat sebagai alat penyaring. Setiap rasio punya "
                "\"rentang wajar\"; hasil di luar rentang mendorong analisis lebih lanjut, tetapi tidak otomatis "
                "berarti perusahaan bermasalah.",
        indikator=["Asuransi umum: 13 rasio, misalnya premi neto terhadap surplus, perubahan premi, rasio operasi "
                   "dua tahun, imbal hasil investasi, liabilitas terhadap aset likuid, dan perkembangan cadangan.",
                   "Asuransi jiwa: 12 rasio, misalnya perubahan modal dan surplus, laba terhadap total pendapatan, "
                   "kecukupan hasil investasi, dan perubahan premi."],
        alur=[("Data laporan", "Pos laporan keuangan statutori."),
              ("Hitung rasio", "Bandingkan dengan rentang wajar."),
              ("Hasil", "Jumlah rasio di luar rentang.")],
        plus=["Dirancang khusus untuk asuransi.", "Mencakup banyak sisi: modal, profitabilitas, likuiditas, "
                                                  "cadangan.", "Rentang dan rumusnya dipublikasikan."],
        minus=["Rentang wajar dibuat untuk pasar Amerika Serikat, belum dikalibrasi untuk Indonesia.",
               "Banyak rasio butuh pos rinci yang tidak ada di laporan publik Indonesia, sehingga di aplikasi ini "
               "hanya sebagian rasio yang diadaptasi.", "Tidak memberi peluang dan tidak memberi bobot."],
        coba="bandingkan"),
    "Model statistik (EWS penelitian ini)": dict(
        jenis="Model prediksi statistik",
        tentang="Model statistik memberi bobot pada beberapa indikator berdasarkan data historis, lalu menghitung "
                "peluang suatu kejadian. Literatur klasiknya antara lain analisis diskriminan (Altman, 1968), "
                "regresi logistik (Ohlson, 1980), dan model hazard waktu diskret (Shumway, 2001). Model EWS "
                "penelitian ini (B2) memakai model hazard waktu diskret dengan koreksi Firth.",
        indikator=["Rasio klaim", "ROA", "Ekuitas/aset", "Pertumbuhan premi bruto", "Ukuran perusahaan (ln aset)",
                   "Lini usaha (jiwa atau umum)"],
        alur=[("Data laporan t−1", "Enam indikator."), ("Bobot dari data", "Koefisien hasil estimasi."),
              ("Peluang", "Fungsi logistik, 0–100%."), ("Status", "Dibandingkan dengan ambang alarm.")],
        plus=["Menghasilkan peluang, bukan hanya ya atau tidak.", "Bobot indikator ditentukan data, bukan "
                                                                  "ditebak.",
              "Kinerjanya bisa diuji: AUC 0,777 pada data uji 2023–2025."],
        minus=["Butuh data panel dan cukup banyak kejadian distress.", "Bergantung pada definisi distress (D2 "
                                                                       "adalah usulan tim).",
               "Perlu diestimasi ulang secara berkala.", "Tidak menangkap masalah tata kelola yang tidak tampak "
                                                         "di rasio keuangan."],
        coba="simulator"),
    "Model umum (Altman Z-score)": dict(
        jenis="Model distress untuk perusahaan nonkeuangan",
        tentang="Z-score Altman (1968) adalah model distress paling terkenal. Model ini disusun dari sampel "
                "perusahaan manufaktur dengan analisis diskriminan. Karena itu, model ini <b>tidak cocok</b> "
                "untuk perusahaan asuransi dan sengaja tidak disediakan untuk dicoba.",
        indikator=["Modal kerja / total aset", "Laba ditahan / total aset", "EBIT / total aset",
                   "Nilai pasar ekuitas / total liabilitas", "Penjualan / total aset"],
        alur=[("Rasio umum", "Lima rasio."), ("Bobot tetap", "Dari sampel manufaktur."),
              ("Skor Z", "Zona aman, abu-abu, atau distress.")],
        plus=["Sederhana dan sangat dikenal.", "Bagus sebagai contoh sejarah model prediksi distress."],
        minus=["Asuransi tidak punya \"modal kerja\" dan \"penjualan\" dalam arti yang sama dengan manufaktur.",
               "Liabilitas asuransi sebagian besar adalah cadangan teknis untuk pemegang polis, sehingga rasio "
               "utang memiliki arti berbeda.", "Bobotnya berasal dari sampel yang sangat berbeda dari industri "
                                                 "asuransi Indonesia."],
        coba=None),
    "Machine learning": dict(
        jenis="Model prediksi berbasis algoritma",
        tentang="Metode seperti decision tree, random forest, gradient boosting, support vector machine, dan "
                "jaringan saraf tiruan mencari pola dari data tanpa menetapkan bentuk hubungan sejak awal. Metode "
                "ini <b>belum bisa dicoba</b> di aplikasi karena harus dilatih dulu dengan data panel, dan "
                "penelitian ini belum melatih model machine learning.",
        indikator=["Bisa memakai indikator yang sama dengan model statistik, ditambah indikator lain bila data "
                   "tersedia."],
        alur=[("Data latih", "Riwayat banyak perusahaan."), ("Pelatihan", "Algoritma mencari pola."),
              ("Validasi", "Diuji pada data yang belum pernah dilihat."), ("Prediksi", "Skor atau kelas.")],
        plus=["Dapat menangkap hubungan nonlinier dan interaksi antarindikator.",
              "Berpotensi lebih akurat bila data cukup besar."],
        minus=["Butuh banyak kejadian; data ini hanya punya 63 awal distress dan 7 kegagalan, sehingga risiko "
               "overfitting tinggi.", "Lebih sulit dijelaskan kepada pengawas dan perusahaan.",
               "Perlu divalidasi dengan cara yang sama agar adil dibandingkan dengan model statistik."],
        coba=None),
}

pilih = st.pills("Pilih metode", list(M), default=list(M)[0], key="metode_pilih")
pilih = pilih or list(M)[0]
m = M[pilih]

st.markdown(f"### {pilih}")
st.caption(m["jenis"])

st.markdown("**A. Tentang metode ini**")
kotak(m["tentang"])

st.markdown("**B. Indikator yang dipakai**")
st.markdown("\n".join(f"- {i}" for i in m["indikator"]))
st.markdown("**C. Cara kerjanya**")
langkah(m["alur"])

st.markdown("**D. Kelebihan dan keterbatasan**")
a, b = st.columns(2)
with a.container(border=True):
    st.markdown("**Kelebihan**")
    st.markdown("\n".join(f"- {i}" for i in m["plus"]))
with b.container(border=True):
    st.markdown("**Keterbatasan**")
    st.markdown("\n".join(f"- {i}" for i in m["minus"]))

st.markdown("**E. Coba metode ini**")
if m["coba"] == "bandingkan":
    st.page_link("halaman/bandingkan.py", label="Coba di halaman Bandingkan metode", icon=":material/compare_arrows:")
elif m["coba"] == "simulator":
    c1, c2 = st.columns(2)
    c1.page_link("halaman/simulator.py", label="Coba di Simulator model EWS", icon=":material/tune:")
    c2.page_link("halaman/bandingkan.py", label="Bandingkan dengan metode lain", icon=":material/compare_arrows:")
else:
    st.info("Metode ini tidak disediakan untuk dicoba. Alasannya ada di bagian A dan D.")

st.caption("Pustaka: Altman, E. I. (1968). Journal of Finance, 23(4). Ohlson, J. A. (1980). Journal of Accounting "
           "Research, 18(1). Shumway, T. (2001). Journal of Business, 74(1). NAIC (2024). IRIS Ratios Manual. "
           "POJK 71/2016 dan POJK 23/2023.")
kaki()

import streamlit as st

from ews.data import muat_hasil
from ews.ui import fmt, kaki, kepala, kotak

kin = muat_hasil("kinerja").set_index("model")
kunci = muat_hasil("angka_kunci").set_index("kode")["nilai"]
b2, b0 = kin.loc["B2 EWS keuangan · hazard"], kin.loc["B0 modal saja · hazard"]

kepala("Kenali risiko keuangan sebelum menjadi distress",
       "Pusat belajar interaktif tentang Early Warning System (EWS) untuk perusahaan asuransi. Pelajari konsepnya, "
       "kenali berbagai metode penilaian, coba menilai perusahaan, lalu bandingkan hasilnya.",
       label="Pelajari · Nilai · Bandingkan · Pahami", hero=True)

PINTU = [
    ("1", "Mengenal EWS", "Apa itu EWS, apa itu financial distress, dan mengapa asuransi di Indonesia "
                          "membutuhkannya.", "halaman/tentang.py", "Mulai belajar", ":material/school:"),
    ("2", "Kenali metode penilaian", "Dari aturan RBC, penanda sederhana, rasio IRIS, model statistik, sampai "
                                     "machine learning: kelebihan dan keterbatasannya.",
     "halaman/metode_penilaian.py", "Lihat metode", ":material/category:"),
    ("3", "Coba menilai", "Masukkan data satu perusahaan, atau unggah Excel berisi banyak perusahaan, lalu lihat "
                          "peluang distress-nya.", "halaman/simulator.py", "Coba simulator", ":material/tune:"),
    ("4", "Bandingkan metode", "Nilai perusahaan yang sama dengan empat metode sekaligus dan lihat mengapa "
                               "hasilnya bisa berbeda.", "halaman/bandingkan.py", "Bandingkan",
     ":material/compare_arrows:"),
]
kol = st.columns(4)
for k, (n, judul, teks, hal, lab, ik) in zip(kol, PINTU):
    with k.container(border=True, height="stretch"):
        st.markdown(f'<div class="ews-step" style="border:0;padding:0;background:none"><div class="n">{n}</div>'
                    f'<b>{judul}</b><span>{teks}</span></div>', unsafe_allow_html=True)
        st.page_link(hal, label=lab, icon=ik)

st.subheader("Model penelitian kami")
kiri, kanan = st.columns([1.4, 1])
with kiri:
    st.markdown(
        "Penelitian LPS–SBM ITB mengembangkan model EWS dari laporan keuangan asuransi 2016–2025. Model ini "
        "memperkirakan peluang perusahaan **mulai** mengalami financial distress tahun depan dari enam indikator: "
        "rasio klaim, ROA, ekuitas/aset, pertumbuhan premi, ukuran perusahaan, dan lini usaha.")
    kotak(f"Pada data uji 2023–2025, model ini membedakan perusahaan yang kemudian distress dengan AUC "
          f"<b>{fmt(b2['auc'], 3)}</b>, lebih baik daripada model yang hanya memakai modal "
          f"(<b>{fmt(b0['auc'], 3)}</b>). Seluruh {fmt(kunci['onset_rbc'], 0)} awal distress yang memiliki data RBC "
          f"masih ber-RBC di atas 120% setahun sebelumnya.")
    a, b = st.columns(2)
    a.page_link("halaman/ringkasan.py", label="Ringkasan temuan", icon=":material/dashboard:")
    b.page_link("halaman/model.py", label="Model dan validasi", icon=":material/fact_check:")
with kanan:
    with st.container(border=True):
        st.markdown("**Siapa yang cocok memakai aplikasi ini?**")
        st.markdown("- Mahasiswa dan akademisi yang mempelajari EWS\n"
                    "- Peserta seminar dan reviewer penelitian\n"
                    "- Regulator dan praktisi yang ingin mengenal pendekatan penilaian")

kotak("<b>Batas penggunaan.</b> Ini prototipe penelitian. Skor adalah alat penyaring untuk belajar dan "
      "memprioritaskan pemeriksaan, bukan dasar sanksi. Contoh perusahaan di aplikasi ini adalah rekaan. Jangan "
      "unggah data perusahaan bernama milik LPS ke versi online.", "awas")
kaki()

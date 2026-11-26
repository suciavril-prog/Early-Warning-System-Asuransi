from dataclasses import asdict

import pandas as pd
import streamlit as st

from ews.metode import CONTOH, PosLaporan, iris, model_b2, penanda, rasio, regulasi
from ews.model import muat_konfigurasi
from ews.ui import fmt, kaki, kepala, kotak, pill

cfg = muat_konfigurasi()

kepala("Bandingkan metode penilaian",
       "Isi pos laporan keuangan satu perusahaan. Aplikasi menghitung rasionya, lalu menilai perusahaan itu dengan "
       "empat metode sekaligus. Setiap metode memakai ukuran hasilnya sendiri, jadi hasilnya <b>tidak bisa "
       "dijumlahkan</b> menjadi satu skor.", label="Coba dan bandingkan")

FIELD = [
    ("total_aset", "Total aset"), ("total_liabilitas", "Total liabilitas"), ("ekuitas", "Ekuitas tahun ini"),
    ("ekuitas_lalu", "Ekuitas tahun lalu"), ("aset_likuid", "Aset likuid"),
    ("premi_bruto", "Premi bruto tahun ini"), ("premi_bruto_lalu", "Premi bruto tahun lalu"),
    ("premi_neto", "Pendapatan premi neto"), ("klaim_neto", "Beban klaim neto"),
    ("hasil_underwriting", "Hasil underwriting"), ("total_pendapatan", "Total pendapatan"),
    ("laba_bersih", "Laba bersih tahun ini"), ("laba_bersih_lalu", "Laba bersih tahun lalu"),
]


def isi(nama: str) -> None:
    for k, v in asdict(CONTOH[nama]).items():
        st.session_state[f"bd_{k}"] = v


if "bd_total_aset" not in st.session_state:
    isi(list(CONTOH)[0])

with st.container(border=True):
    st.markdown("**1. Data perusahaan** · semua angka dalam Rp miliar")
    a, b = st.columns([2, 1])
    pilih = a.selectbox("Isi dengan contoh rekaan", list(CONTOH), key="bd_contoh",
                        help="Perusahaan rekaan untuk belajar, bukan perusahaan nyata.")
    if st.session_state.get("_bd_terakhir") != pilih:
        isi(pilih)
        st.session_state["_bd_terakhir"] = pilih
        st.rerun()
    c1, c2 = b.columns(2)
    c1.radio("Lini usaha", ["Jiwa", "Umum"], key="bd_lini")
    c2.radio("Segmen", ["Konvensional", "Syariah"], key="bd_segmen")
    kol = st.columns(4)
    for i, (k, label) in enumerate(FIELD):
        kol[i % 4].number_input(label, key=f"bd_{k}", step=1.0, format="%.1f",
                                help="Kas, deposito, obligasi, dan saham" if k == "aset_likuid" else None)
    st.number_input("RBC dilaporkan (%), opsional", key="bd_rbc", min_value=0.0, step=1.0, format="%.0f",
                    placeholder="kosongkan bila tidak ada")

p = PosLaporan(**{k[3:]: v for k, v in st.session_state.items()
                  if k.startswith("bd_") and k[3:] in PosLaporan.__dataclass_fields__})
r = rasio(p)

st.markdown("**2. Rasio yang dihitung aplikasi**")
tampil = [("Rasio klaim", "rasio_klaim"), ("ROA", "roa"), ("Ekuitas/aset", "ekuitas_aset"),
          ("Pertumbuhan premi bruto", "pertumbuhan_premi"), ("Margin underwriting", "margin_uw"),
          ("Perubahan ekuitas", "perubahan_ekuitas")]
st.dataframe(pd.DataFrame([{n: (fmt(r[k]) + "%" if r[k] is not None else "–") for n, k in tampil}]),
             hide_index=True, width="stretch")

hr, hp, hi, hm = regulasi(p, cfg), penanda(p), iris(p), model_b2(p, cfg)

st.markdown("**3. Hasil keempat metode**")
ringkas = pd.DataFrame([
    {"Metode": "Aturan regulasi (RBC dan ekuitas minimum)", "Hasil": hr["hasil"],
     "Ukuran hasil": "memenuhi atau tidak"},
    {"Metode": "Penanda sederhana", "Hasil": hp["hasil"], "Ukuran hasil": "jumlah penanda"},
    {"Metode": "Rasio peringatan ala IRIS (adaptasi)", "Hasil": hi["hasil"],
     "Ukuran hasil": "jumlah rasio di luar rentang"},
    {"Metode": "Model EWS penelitian (B2)",
     "Hasil": f"{hm['hasil']} · {hm.get('status', '')}" if hm.get("baris") is not None else hm["hasil"],
     "Ukuran hasil": "peluang distress tahun depan"},
])
st.dataframe(ringkas, hide_index=True, width="stretch")

n_sinyal = sum(x["sinyal"] for x in (hr, hp, hi, hm))
if hr["sinyal"] is False and n_sinyal >= 2:
    kotak("<b>Perhatikan:</b> perusahaan ini <b>memenuhi aturan regulasi</b>, tetapi metode lain sudah memberi "
          "sinyal. Inilah alasan penelitian ini: RBC dan ekuitas minimum saja belum tentu cukup sebagai peringatan "
          "dini.", "awas")
elif hr["sinyal"] and not hm["sinyal"]:
    kotak("<b>Perhatikan:</b> model EWS tidak memberi alarm, tetapi aturan regulasi tidak terpenuhi. Model "
          "statistik dan aturan regulasi melihat hal yang berbeda, sehingga keduanya perlu dipakai bersama.", "awas")
else:
    kotak(f"{n_sinyal} dari 4 metode memberi sinyal untuk perusahaan ini.")

t1, t2, t3, t4 = st.tabs(["Regulasi", "Penanda sederhana", "Ala IRIS", "Model EWS (B2)"])
with t1:
    st.dataframe(pd.DataFrame([{"Ketentuan": a, "Hasil": "–" if b is None else ("Memenuhi" if b else "Tidak memenuhi"),
                                "Keterangan": c} for a, b, c in hr["rinci"]]), hide_index=True, width="stretch")
    st.caption("Sumber: POJK 71/2016 (RBC minimum 100% dan target internal 120%); POJK 23/2023 (ekuitas minimum "
               "tahap pertama).")
with t2:
    st.dataframe(pd.DataFrame([{"Penanda": a, "Menyala?": "Ya" if b else "Tidak"} for a, b in hp["rinci"]]),
                 hide_index=True, width="stretch")
    st.caption("Penanda ini dipakai sebagai Tingkat 2 dalam penelitian. Sensitif, tetapi tidak spesifik.")
with t3:
    st.dataframe(pd.DataFrame([{"Rasio": a, "Nilai": "–" if v is None else fmt(v) + "%", "Rentang wajar": t,
                                "Hasil": h} for a, v, t, h in hi["rinci"]]), hide_index=True, width="stretch")
    st.caption("Rentang wajar dari NAIC IRIS Ratios Manual (edisi 2024) untuk pasar Amerika Serikat. Sebagian rasio "
               "diadaptasi agar bisa dihitung dari laporan publik Indonesia, sehingga hanya untuk ilustrasi.")
with t4:
    if hm.get("baris") is not None:
        a, b = st.columns([1, 2])
        a.metric("Peluang distress tahun depan", hm["hasil"])
        b.markdown(pill(hm["status"]), unsafe_allow_html=True)
        b.caption(f"Ambang alarm bawaan {fmt(cfg.ambang * 100)}%. Dihitung dari enam indikator; rincian faktor "
                  "pendorong ada di halaman Simulator model EWS.")
    else:
        st.info("Lengkapi total aset, premi, klaim, laba, dan ekuitas untuk menghitung skor model.")

st.caption("Semua contoh adalah perusahaan rekaan. Hasil untuk belajar membaca metode, bukan penilaian resmi.")
kaki()

import pandas as pd
import streamlit as st

from ews import charts
from ews.model import kontribusi, muat_konfigurasi, nilai_entitas, peringatan_masukan
from ews.ui import fmt, pct, pill, kaki, kepala

cfg = muat_konfigurasi()

PRESET = {
    "Median jiwa konvensional": dict(lini="Jiwa", segmen="Konvensional", rasio_klaim=97.7, roa=0.8, ekuitas_aset=24.7,
                                     pertumbuhan_premi=8.0, total_aset_miliar=3630.0, margin_uw=2.0, roa_t2=1.0, rbc=None),
    "Median umum konvensional": dict(lini="Umum", segmen="Konvensional", rasio_klaim=44.0, roa=2.6, ekuitas_aset=36.2,
                                     pertumbuhan_premi=8.0, total_aset_miliar=985.0, margin_uw=49.5, roa_t2=2.5, rbc=None),
    "Median jiwa syariah": dict(lini="Jiwa", segmen="Syariah", rasio_klaim=87.3, roa=3.0, ekuitas_aset=69.1,
                                pertumbuhan_premi=8.0, total_aset_miliar=200.0, margin_uw=10.0, roa_t2=2.0, rbc=None),
    "Jiwa tertekan (hipotetis)": dict(lini="Jiwa", segmen="Konvensional", rasio_klaim=135.0, roa=-2.5, ekuitas_aset=12.0,
                                      pertumbuhan_premi=-5.0, total_aset_miliar=900.0, margin_uw=-18.0, roa_t2=-1.2, rbc=180.0),
}


def terapkan(nama: str) -> None:
    for k, v in PRESET[nama].items():
        st.session_state[f"sim_{k}"] = v


if "sim_rasio_klaim" not in st.session_state:
    terapkan("Median jiwa konvensional")

kepala("Simulator model EWS", label="Coba dan bandingkan")
st.caption("Isi rasio dari Laporan Publikasi tahun buku terakhir (t−1). Contoh berasal dari median segmen "
           "(Tabel 6.1) atau hipotetis, bukan entitas nyata.")

kiri, kanan = st.columns([1, 1.2])
with kiri:
    pilih = st.selectbox("Isi dengan contoh", ["–"] + list(PRESET), index=0)
    if pilih != "–" and st.session_state.get("_preset_terakhir") != pilih:
        terapkan(pilih)
        st.session_state["_preset_terakhir"] = pilih
        st.rerun()
    a, b = st.columns(2)
    a.radio("Lini usaha", ["Jiwa", "Umum"], key="sim_lini", horizontal=True)
    b.radio("Segmen", ["Konvensional", "Syariah"], key="sim_segmen", horizontal=True,
            help="Tidak masuk skor B2; dipakai untuk ambang ekuitas minimum")
    st.markdown("**Indikator Model B2**")
    a, b = st.columns(2)
    a.number_input("Rasio klaim (%)", key="sim_rasio_klaim", step=0.1, format="%.1f")
    b.number_input("ROA (%)", key="sim_roa", step=0.1, format="%.1f")
    a.number_input("Ekuitas/aset (%)", key="sim_ekuitas_aset", step=0.1, format="%.1f")
    b.number_input("Pertumbuhan premi bruto (%)", key="sim_pertumbuhan_premi", step=0.1, format="%.1f")
    a.number_input("Total aset (Rp miliar)", key="sim_total_aset_miliar", min_value=1.0, step=10.0, format="%.0f")
    st.markdown("**Data untuk penanda Tingkat 2**")
    a, b = st.columns(2)
    a.number_input("Margin underwriting (%)", key="sim_margin_uw", step=0.1, format="%.1f")
    b.number_input("ROA tahun t−2 (%)", key="sim_roa_t2", step=0.1, format="%.1f")
    a.number_input("RBC dilaporkan (%), opsional", key="sim_rbc", step=1.0, format="%.0f",
                   placeholder="kosongkan bila tidak ada")
    st.markdown("**Ambang alarm**")
    a, b = st.columns(2)
    th_j = a.number_input("Ambang jiwa (%)", value=cfg.ambang * 100, min_value=1.0, max_value=90.0, step=0.1)
    th_u = b.number_input("Ambang umum (%)", value=cfg.ambang * 100, min_value=1.0, max_value=90.0, step=0.1)
    st.caption("Ambang bawaan adalah pilihan statistik dari laporan. LPS perlu menetapkan ambang dari biaya relatif "
               "kegagalan deteksi dan alarm palsu, idealnya terpisah untuk jiwa dan umum.")

x = {k[4:]: st.session_state[k] for k in st.session_state if k.startswith("sim_")}
x["rbc_dilaporkan"] = x.pop("rbc", None)
x["nama"] = "Simulasi"
df = pd.DataFrame([x])
hasil = nilai_entitas(df, cfg, th_j / 100, th_u / 100).iloc[0]

with kanan:
    st.subheader("Hasil penilaian")
    a, b = st.columns([1, 1.6])
    a.metric("Peluang distress tahun depan", pct(hasil["probabilitas"]), help="Probabilitas awal distress D2 pada tahun t")
    pesan = {
        "Tinjauan Tingkat 2": "Entitas sudah memenuhi kriteria D2 pada laporan terakhir. Gunakan penanda kegagalan "
                              "di bawah untuk tinjauan pengawas.",
        "Alarm": "Melampaui ambang. Masuk daftar pantauan dan prioritas permintaan data tambahan.",
        "Pantau": "Di atas 10% tetapi di bawah ambang. Perhatikan tren rasio klaim dan ROA.",
        "Rendah-sedang": "Antara 5% dan 10%. Pemantauan rutin.",
        "Rendah": "Di bawah 5%, kelompok risiko terendah.",
    }
    b.markdown(pill(hasil["status"]), unsafe_allow_html=True)
    b.caption(pesan[hasil["status"]])

    st.markdown("**Kontribusi terhadap log-odds** (selisih dari profil median sampel)")
    st.plotly_chart(charts.kontribusi(kontribusi(x, cfg)), width="stretch")
    if x["lini"] == "Jiwa":
        st.caption(f"Lini jiwa menambah {fmt(cfg.koef['jiwa'], 2)} log-odds terhadap asuransi umum dengan kondisi "
                   "keuangan sama, di luar grafik ini.")

    st.markdown("**Sensitivitas terhadap rasio klaim**")
    st.plotly_chart(charts.sensitivitas(x, cfg, float(hasil["ambang"])), width="stretch")

    st.markdown("**Penanda Tingkat 2**")
    def tanda(v):
        return "Data kurang" if v is None else ("**Ya**" if bool(v) else "Tidak")
    mn = cfg.ekuitas_min["syariah" if x["segmen"] == "Syariah" else "konvensional"]
    st.markdown(
        f"| Penanda | Status |\n|---|---|\n"
        f"| Ekuitas negatif | {tanda(hasil['pn_ekuitas_negatif'])} |\n"
        f"| ROA negatif | {tanda(hasil['pn_roa_negatif'])} |\n"
        f"| Rugi dua tahun berturut-turut | {tanda(hasil['pn_rugi_dua_tahun'])} |\n"
        f"| Sudah memenuhi kriteria D2 | {tanda(hasil['pn_sudah_d2'])} |\n"
        f"| Ekuitas di bawah minimum POJK 23/2023 (Rp{mn} miliar) · ekuitas ≈ Rp{fmt(hasil['ekuitas_miliar'], 0)} miliar "
        f"| {tanda(hasil['pn_ekuitas_bawah_minimum'])} |"
    )
    for w in peringatan_masukan(df):
        st.warning(w)
    if x["segmen"] == "Syariah":
        st.info("Sampel estimasi hanya memuat 16 perusahaan syariah dengan 4 awal distress; skor memakai model gabungan.")
    if x.get("rbc_dilaporkan") and x["rbc_dilaporkan"] >= 120 and hasil["status"] == "Alarm":
        st.info("RBC dilaporkan di atas 120% tetapi skor beralarm. Pola ini sesuai temuan bahwa seluruh 11 awal "
                "distress dengan data RBC tercatat ber-RBC di atas 120% pada t−1.")
    st.caption("Skor ini alat penyaring, bukan dasar sanksi. Lengkapi dengan informasi nonkeuangan: sanksi OJK, "
               "keterlambatan laporan, pergantian pengurus, opini auditor, dan keluhan pemegang polis.")
kaki()

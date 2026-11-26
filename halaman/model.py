import pandas as pd
import streamlit as st

from ews import charts
from ews.data import muat_hasil
from ews.model import muat_konfigurasi
from ews.ui import fmt, sumber, kaki, kepala

cfg = muat_konfigurasi()
kin = muat_hasil("kinerja")
hip = muat_hasil("hipotesis")
kunci = muat_hasil("angka_kunci").set_index("kode")["nilai"]

kepala("Model dan validasi", label="Model penelitian kami")
kiri, kanan = st.columns([1.2, 1])
with kiri:
    st.subheader("Kinerja out-of-sample")
    st.plotly_chart(charts.oos(kin), width="stretch")
    sumber("Tabel 6.7; latih 2017–2022, uji outcome 2023–2025")
with kanan:
    st.subheader("Koefisien Model B2 yang dipakai aplikasi")
    nama = {"intersep": "Intersep", "ekuitas_aset": "Ekuitas/aset (%)", "roa": "ROA (%)",
            "rasio_klaim": "Rasio klaim (%)", "pertumbuhan_premi_per10": "Pertumbuhan premi (per 10 poin %)",
            "ln_aset": "ln total aset (juta Rp)", "jiwa": "Jiwa (1/0)"}
    import math
    koef = pd.DataFrame([{"Komponen": nama[k], "Koefisien": v,
                          "Odds ratio": None if k == "intersep" else round(math.exp(v), 3)}
                         for k, v in cfg.koef.items()])
    st.dataframe(koef, hide_index=True, width="stretch",
                 column_config={"Koefisien": st.column_config.NumberColumn(format="%.4f")})
    st.latex(r"p=\frac{1}{1+e^{-z}},\quad z=\alpha+\sum_j \beta_j x_{j,t-1}")
    st.caption(f"Versi {cfg.versi}. {cfg.meta.get('model', '')}. Ambang alarm {fmt(cfg.ambang * 100, 1)}%.")

st.subheader("Metrik lengkap per pendekatan")
st.caption(f"Brier lebih kecil lebih baik. Tingkat kejadian aktual data uji {fmt(kunci['laju_aktual_uji'])}%; "
           "model terkalibrasi memiliki rata-rata prediksi mendekati angka ini.")
st.dataframe(
    kin.rename(columns={"model": "Model · pendekatan", "auc": "AUC", "auc_lo": "IK bawah", "auc_hi": "IK atas",
                        "pr_auc": "PR-AUC", "brier": "Brier", "rata_prediksi": "Rata-rata prediksi (%)",
                        "tangkap_top10": "Tangkapan 10% teratas (%)"}),
    hide_index=True, width="stretch")

st.subheader("Ringkasan pengujian hipotesis")
st.caption("Taraf signifikansi 5% dua sisi. 'Tidak didukung' pada H2–H4 mencerminkan daya uji rendah, "
           "bukan bukti tidak ada efek.")
st.dataframe(hip.rename(columns={"kode": "Kode", "pertanyaan": "Hipotesis", "uji": "Uji", "statistik": "Statistik",
                                 "p": "p", "status": "Status", "kesimpulan": "Catatan"}),
             hide_index=True, width="stretch")
sumber("Tabel 6.16")
kaki()

import streamlit as st

from ews import charts
from ews.data import muat_hasil
from ews.ui import fmt, kaki, kartu_angka, kepala, sumber

komp = muat_hasil("komposisi")
kunci = muat_hasil("angka_kunci").set_index("kode")["nilai"]
kin = muat_hasil("kinerja").set_index("model")
auc = muat_hasil("auc").set_index("indikator")
seg26 = muat_hasil("skor2026_segmen").set_index("segmen")
total = komp.set_index("segmen").loc["Total"]
b2, b0 = kin.loc["B2 EWS keuangan · hazard"], kin.loc["B0 modal saja · hazard"]

kepala("Ringkasan temuan",
       f"Model EWS (B2) memprediksi awal <i>financial distress</i> (D2) pada tahun t dari laporan t−1. "
       f"Rasio klaim adalah sinyal dini paling kuat, sedangkan RBC univariat hanya ber-AUC "
       f"<b>{fmt(auc.loc['RBC dilaporkan (%)', 'auc_d2'], 3)}</b>.", label="Hasil penelitian")
kartu_angka([
    dict(label="AUC data uji 2023–2025", nilai=fmt(b2["auc"], 3), nada="utama",
         konteks=f"model EWS (B2); modal saja (B0) {fmt(b0['auc'], 3)}. Brier {fmt(b2['brier'], 3)}"),
    dict(label="Awal distress D2", nilai=fmt(kunci["onset"], 0), nada="waspada",
         konteks=f"dari {fmt(kunci['risk_set'], 0)} firm-year berisiko"),
    dict(label="Kegagalan terkait keuangan", nilai=fmt(kunci["gagal"], 0), nada="netral",
         konteks="pencabutan izin dalam periode observasi"),
    dict(label="Sampel utama", nilai=fmt(total["firm_year"], 0), nada="netral",
         konteks=f"firm-year dari {fmt(total['perusahaan'], 0)} perusahaan, 2016–2025"),
])

kiri, kanan = st.columns([1, 1])
with kiri:
    st.subheader("Tingkat distress per tahun")
    d = st.segmented_control("Definisi", ["D2 (utama)", "D1 (proposal)"], default="D2 (utama)",
                             label_visibility="collapsed")
    st.plotly_chart(charts.tren(muat_hasil("tren"), "d1" if d and d.startswith("D1") else "d2"),
                    width="stretch")
    sumber("Tabel 6.3, proporsi firm-year berstatus distress")
with kanan:
    st.subheader("Komposisi sampel")
    tab = komp.rename(columns={
        "segmen": "Segmen", "perusahaan": "Perusahaan", "firm_year": "Firm-year", "d2_pct": "D2 (%)",
        "d1_pct": "D1 (%)", "med_rk": "Median rasio klaim (%)", "med_roa": "Median ROA (%)",
        "med_ea": "Median ekuitas/aset (%)", "med_rbc": "Median RBC (%)", "n_rbc": "n RBC"})
    st.dataframe(tab, hide_index=True, width="stretch")
    sumber("Tabel 6.1, asuransi langsung 2016–2025")

with st.expander("Definisi yang dipakai", expanded=False):
    st.markdown(
        "- **Financial distress (D2):** ekuitas negatif, atau RBC dilaporkan di bawah 100% "
        "(batas minimum POJK 71/2016, dipertahankan POJK 26/2025), atau ROA negatif bersamaan dengan hasil "
        "underwriting negatif. Usulan tim; belum divalidasi terhadap status pengawasan OJK.\n"
        "- **D1 (proposal):** dua dari empat kondisi EWS; dilaporkan sebagai robustness.\n"
        "- **Masalah regulasi:** keputusan OJK seperti pengawasan khusus atau pembatasan kegiatan usaha (PKU).\n"
        "- **Kegagalan:** pencabutan izin usaha terkait kesehatan keuangan. Merger, single presence, dan "
        "pengembalian izin sukarela tidak dihitung."
    )
kaki()

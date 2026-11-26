import io
import json

import pandas as pd
import streamlit as st

from ews import charts
from ews.data import baca_unggahan, templat_csv
from ews.model import ROOT, STATUS_URUT, kontribusi, muat_konfigurasi, nilai_entitas, peringatan_masukan
from ews.ui import fmt, pct, pill, kaki, kepala

cfg = muat_konfigurasi()

kepala("Daftar pantauan", label="Alat skor")
st.caption("Unggah rasio Laporan Publikasi banyak entitas sekaligus. Berkas diolah di memori sesi Anda dan tidak "
           "disimpan oleh aplikasi. Saat dibuka pertama kali, tabel berisi sepuluh entitas ilustratif, bukan "
           "perusahaan nyata.")

a, b, c = st.columns([2, 1, 1])
berkas = a.file_uploader("Unggah CSV atau Excel", type=["csv", "xlsx"], label_visibility="collapsed")
b.download_button("Unduh templat CSV", templat_csv(), file_name="templat_daftar_pantauan.csv", mime="text/csv",
                  width="stretch")
with c.popover("Format kolom", width="stretch"):
    st.markdown(
        "**Wajib:** `nama`, `lini` (Jiwa/Umum), `rasio_klaim`, `roa`, `ekuitas_aset`, `pertumbuhan_premi` "
        "(semua %), `total_aset_miliar` (Rp miliar).\n\n"
        "**Opsional:** `segmen` (Konvensional/Syariah), `margin_uw`, `roa_t2`, `rbc_dilaporkan`, `tahun_laporan`.\n\n"
        "Desimal boleh titik atau koma. Jangan pakai pemisah ribuan. Reasuransi tidak dicakup model."
    )

if berkas is not None:
    try:
        data, pesan = baca_unggahan(berkas.name, berkas.getvalue())
        asal = f"berkas {berkas.name}"
    except Exception as e:  # noqa: BLE001
        st.error(f"Berkas tidak dapat dibaca. {e}")
        st.stop()
else:
    with open(ROOT / "data" / "contoh_pantauan.json", encoding="utf-8") as f:
        data = pd.DataFrame(json.load(f))
    pesan, asal = [], "data ilustratif"

for m in pesan:
    st.warning(m)
if data.empty:
    st.info("Tidak ada baris yang dapat dinilai.")
    st.stop()

with st.sidebar:
    st.markdown("**Ambang alarm daftar pantauan**")
    th_j = st.number_input("Jiwa (%)", value=cfg.ambang * 100, min_value=1.0, max_value=90.0, step=0.1, key="pt_j")
    th_u = st.number_input("Umum (%)", value=cfg.ambang * 100, min_value=1.0, max_value=90.0, step=0.1, key="pt_u")

hasil = nilai_entitas(data, cfg, th_j / 100, th_u / 100)
for w in peringatan_masukan(hasil):
    st.warning(w)

f1, f2, f3 = st.columns(3)
p_lini = f1.multiselect("Lini", ["Jiwa", "Umum"], default=["Jiwa", "Umum"])
p_seg = f2.multiselect("Segmen", ["Konvensional", "Syariah"], default=["Konvensional", "Syariah"])
p_st = f3.multiselect("Status", STATUS_URUT, default=STATUS_URUT)
tampil = hasil[hasil["lini"].isin(p_lini) & hasil["segmen"].isin(p_seg) & hasil["status"].isin(p_st)]
tampil = tampil.sort_values(["status_urut", "probabilitas"], ascending=[True, False])

m = st.columns(4)
m[0].metric("Entitas dinilai", fmt(len(hasil), 0), help=f"Sumber: {asal}")
m[1].metric("Alarm Tingkat 1", fmt((hasil["status"] == "Alarm").sum(), 0))
m[2].metric("Sudah D2, tinjauan Tingkat 2", fmt((hasil["status"] == "Tinjauan Tingkat 2").sum(), 0))
m[3].metric("Rata-rata probabilitas", pct(hasil["probabilitas"].mean()),
            help="Pembanding: 6,7% pada skor 2026 di laporan")

penanda_label = {"pn_ekuitas_negatif": "Ekuitas negatif", "pn_roa_negatif": "ROA negatif",
                 "pn_rugi_dua_tahun": "Rugi dua tahun", "pn_sudah_d2": "Sudah D2",
                 "pn_ekuitas_bawah_minimum": "Ekuitas < minimum"}


def daftar_penanda(r):
    return "; ".join(v for k, v in penanda_label.items() if r[k] is True or r[k] == True) or "–"  # noqa: E712


tabel = tampil.assign(
    penanda=tampil.apply(daftar_penanda, axis=1),
    prob_pct=tampil["probabilitas"] * 100,
)[["nama", "lini", "segmen", "rasio_klaim", "roa", "ekuitas_aset", "prob_pct", "status", "penanda"]]
st.dataframe(
    tabel, hide_index=True, width="stretch", height=min(560, 40 + 36 * len(tabel)),
    column_config={
        "nama": "Entitas", "lini": "Lini", "segmen": "Segmen",
        "rasio_klaim": st.column_config.NumberColumn("Rasio klaim (%)", format="%.1f"),
        "roa": st.column_config.NumberColumn("ROA (%)", format="%.1f"),
        "ekuitas_aset": st.column_config.NumberColumn("Ekuitas/aset (%)", format="%.1f"),
        "prob_pct": st.column_config.ProgressColumn("Probabilitas (%)", format="%.1f", min_value=0, max_value=50),
        "status": "Status", "penanda": "Penanda Tingkat 2",
    })

g1, g2 = st.columns([1.3, 1])
with g1:
    st.markdown("**Sebaran status**")
    st.plotly_chart(charts.status_bar(hasil), width="stretch")
with g2:
    st.markdown("**Unduh hasil**")
    st.caption("Berisi seluruh entitas yang dinilai, probabilitas, status, penanda, dan versi model.")
ekspor = hasil.drop(columns=["status_urut"]).assign(model_versi=cfg.versi)
x1, x2 = g2, g2
x1.download_button("Unduh hasil (CSV)", ekspor.to_csv(index=False).encode("utf-8"), file_name="hasil_ews.csv",
                   mime="text/csv", width="stretch")
buf = io.BytesIO()
ekspor.to_excel(buf, index=False, sheet_name="hasil_ews")
x2.download_button("Unduh hasil (Excel)", buf.getvalue(), file_name="hasil_ews.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")

st.subheader("Rincian satu entitas")
pilih = st.selectbox("Pilih entitas", list(tampil["nama"]))
if pilih:
    r = hasil[hasil["nama"] == pilih].iloc[0]
    a, b = st.columns([1, 2])
    a.metric("Probabilitas", pct(r["probabilitas"]))
    a.markdown(pill(r["status"]), unsafe_allow_html=True)
    a.caption(f"Ambang {fmt(r['ambang'] * 100, 1)}% · ekuitas ≈ Rp{fmt(r['ekuitas_miliar'], 0)} miliar")
    b.plotly_chart(charts.kontribusi(kontribusi(r.to_dict(), cfg)), width="stretch")
kaki()

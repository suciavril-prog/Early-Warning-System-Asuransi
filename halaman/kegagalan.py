import streamlit as st

from ews import charts
from ews.data import muat_hasil
from ews.ui import sumber, kaki, kepala

prof = muat_hasil("profil_waktu").sort_values("k")
kasus = muat_hasil("kasus_gagal")

kepala("Kasus kegagalan", label="Model penelitian kami")
st.markdown("ROA dan rasio klaim sudah memburuk pada k = −3, sekitar satu tahun sebelum ekuitas runtuh pada k = −2. "
            "Jendela ini memberi peringatan dua hingga tiga tahun sebelum tindakan OJK.")
c = st.columns(3)
c[0].plotly_chart(charts.profil(prof, "roa", "ROA (%)"), width="stretch")
c[1].plotly_chart(charts.profil(prof, "rasio_klaim", "Rasio klaim (%)", ambang=100), width="stretch")
c[2].plotly_chart(charts.profil(prof, "ea", "Ekuitas/aset (%)"), width="stretch")
sumber("Tabel 6.15, median tujuh perusahaan gagal, k tahun sebelum tindakan OJK")

st.subheader("Kondisi pada laporan terakhir")
st.caption("Kasus dianonimkan (Bagian 5.9). RBC: P = proksi, L = dilaporkan, I = imputasi. Kasus B tidak "
           "terdeteksi indikator mana pun; OJK menyebut pelanggaran ketentuan sebagai dasar sanksi.")
st.dataframe(kasus.rename(columns={"kasus": "Kasus", "jenis": "Jenis", "laporan_ke_tindakan": "Laporan → tindakan",
                                   "ea": "Ekuitas/aset (%)", "roa": "ROA (%)", "rasio_klaim": "Rasio klaim (%)",
                                   "rbc": "RBC (%)", "label_d2": "Label D2", "ekuitas_bawah_min": "Ekuitas < minimum"}),
             hide_index=True, width="stretch")
sumber("Tabel 6.14")
kaki()

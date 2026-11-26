import streamlit as st

from ews import charts
from ews.data import muat_hasil
from ews.ui import fmt, sumber, kaki, kepala

auc = muat_hasil("auc")
kunci = muat_hasil("angka_kunci").set_index("kode")["nilai"]
a = auc.set_index("indikator")

kepala("Indikator peringatan dini", label="Hasil penelitian")
kiri, kanan = st.columns([1.2, 1])
with kiri:
    st.subheader("Daya pembeda tiap indikator")
    st.plotly_chart(charts.auc_bar(auc), width="stretch")
    sumber("Tabel 6.4, AUC terhadap awal distress D2, prediktor t−1")
with kanan:
    st.subheader("Mengapa RBC tidak cukup")
    st.markdown(
        f"Dari **{fmt(kunci['onset_rbc'], 0)}** awal distress yang memiliki data RBC pada t−1, sebanyak "
        f"**{fmt(kunci['onset_rbc_120'], 0)}** tercatat dengan RBC di atas 120%. Median RBC perusahaan yang "
        f"kemudian distress **{fmt(a.loc['RBC dilaporkan (%)', 'med_onset'])}%**, sedikit lebih tinggi dari yang "
        f"tetap sehat (**{fmt(a.loc['RBC dilaporkan (%)', 'med_non'])}%**)."
    )
    st.markdown(
        f"Sebaliknya, median rasio klaim t−1 perusahaan yang kemudian distress "
        f"**{fmt(a.loc['Rasio klaim (%)', 'med_onset'])}%**, dibandingkan "
        f"**{fmt(a.loc['Rasio klaim (%)', 'med_non'])}%** pada yang tetap sehat."
    )
    st.info(
        "RBC ibarat isi tangki bahan bakar, rasio klaim dan ROA ibarat laju konsumsinya: tangki yang masih penuh "
        "tidak memberi tahu bahwa kendaraan sedang bocor. Kesimpulan yang didukung data adalah RBC tidak cukup "
        "sebagai peringatan dini tunggal, bukan RBC tidak berguna. IK 95% AUC RBC lebar (0,31–0,66) karena hanya "
        "11 kejadian."
    )

st.subheader("Median kelompok distress dan tidak distress")
st.dataframe(
    auc.rename(columns={"indikator": "Indikator (t−1)", "auc_d2": "AUC D2", "med_onset": "Median: awal distress",
                        "med_non": "Median: tidak distress", "p_mw": "p (Mann-Whitney)", "auc_d1": "AUC D1"}),
    hide_index=True, width="stretch",
    column_config={"AUC D2": st.column_config.NumberColumn(format="%.3f"),
                   "AUC D1": st.column_config.NumberColumn(format="%.3f")})
sumber("Tabel 6.4")
kaki()

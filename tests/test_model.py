import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ews.data import baca_unggahan  # noqa: E402
from ews.model import muat_konfigurasi, nilai_entitas, probabilitas  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from estimasi_ulang import firth_logit, siapkan_onset  # noqa: E402

CFG = muat_konfigurasi()


def _p(**kw):
    return float(probabilitas(pd.DataFrame([kw]), CFG)[0])


def test_median_segmen_mendekati_tabel_6_19():
    # Median skor 2026 di laporan: umum konvensional 1,8%, jiwa konvensional 11,0%
    umum = _p(lini="Umum", ekuitas_aset=36.2, roa=2.6, rasio_klaim=44, pertumbuhan_premi=8, total_aset_miliar=985)
    jiwa = _p(lini="Jiwa", ekuitas_aset=24.7, roa=0.8, rasio_klaim=97.7, pertumbuhan_premi=8, total_aset_miliar=3630)
    assert 0.01 < umum < 0.03
    assert 0.09 < jiwa < 0.18


def test_arah_koefisien():
    base = dict(lini="Jiwa", ekuitas_aset=30, roa=1, rasio_klaim=80, pertumbuhan_premi=8, total_aset_miliar=1000)
    assert _p(**{**base, "rasio_klaim": 120}) > _p(**base)
    assert _p(**{**base, "roa": -3}) > _p(**base)
    assert _p(**{**base, "total_aset_miliar": 20000}) < _p(**base)
    assert _p(**{**base, "lini": "Umum"}) < _p(**base)


def test_status_dan_penanda():
    df = pd.DataFrame([
        dict(nama="A", lini="Jiwa", segmen="Konvensional", ekuitas_aset=-3, roa=-1, rasio_klaim=90,
             pertumbuhan_premi=0, total_aset_miliar=600, margin_uw=-5, roa_t2=-2, rbc_dilaporkan=np.nan),
        dict(nama="B", lini="Umum", segmen="Syariah", ekuitas_aset=60, roa=2, rasio_klaim=40,
             pertumbuhan_premi=10, total_aset_miliar=150, margin_uw=30, roa_t2=np.nan, rbc_dilaporkan=250),
    ])
    h = nilai_entitas(df, CFG).set_index("nama")
    assert h.loc["A", "status"] == "Tinjauan Tingkat 2"
    assert bool(h.loc["A", "pn_ekuitas_negatif"]) and bool(h.loc["A", "pn_rugi_dua_tahun"])
    assert h.loc["B", "status"] == "Rendah"
    assert h.loc["B", "pn_rugi_dua_tahun"] is None
    assert bool(h.loc["B", "pn_ekuitas_bawah_minimum"])  # ekuitas 90 miliar < minimum syariah 100 miliar


def test_unggahan_titik_koma_dan_desimal_koma():
    csv = ("nama;lini;rasio_klaim;roa;ekuitas_aset;pertumbuhan_premi;total_aset_miliar;segmen\n"
           "PT X;Jiwa;97,7;0,8;24,7;8;3630;Konvensional\n"
           "PT Y;Reasuransi;50;1;30;5;1000;Konvensional\n").encode()
    df, pesan = baca_unggahan("x.csv", csv)
    assert len(df) == 1 and abs(df.loc[0, "rasio_klaim"] - 97.7) < 1e-9
    assert any("reasuransi" in m.lower() for m in pesan)


def test_firth_mendekati_mle_pada_sampel_besar():
    rng = np.random.default_rng(1)
    n = 5000
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
    b = np.array([-2.0, 0.8, -0.5])
    y = (rng.random(n) < 1 / (1 + np.exp(-(X @ b)))).astype(float)
    est, cov, _ = firth_logit(X, y)
    assert np.allclose(est, b, atol=0.15)


def test_kerangka_onset():
    panel = pd.DataFrame({
        "perusahaan": ["A"] * 4 + ["B"] * 3, "tahun": [2020, 2021, 2022, 2023, 2020, 2021, 2022],
        "lini": ["Jiwa"] * 4 + ["Umum"] * 3, "ekuitas_aset": [30, 25, 20, 10, 40, 41, 42],
        "roa": [1, 0.5, -1, -2, 2, 2, 2], "rasio_klaim": [80, 95, 110, 130, 40, 42, 41],
        "pertumbuhan_premi": [5, 3, 0, -5, 8, 9, 7], "total_aset_miliar": [1000] * 4 + [500] * 3,
        "d2": [0, 0, 1, 1, 0, 0, 0],
    })
    m = siapkan_onset(panel, winsor=False)
    # A: 2021 (berisiko, 0), 2022 (berisiko, onset 1), 2023 keluar (distress di 2022); B: 2021, 2022
    assert len(m) == 4 and int(m["d2"].sum()) == 1
    r = m[(m.perusahaan == "A") & (m.tahun == 2022)].iloc[0]
    assert r["rasio_klaim"] == 95  # prediktor dari t-1

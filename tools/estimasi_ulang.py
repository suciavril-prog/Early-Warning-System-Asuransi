"""Estimasi ulang koefisien Model B2 dari data panel firm-year.

Mereplikasi kerangka onset di Laporan Kemajuan (Bagian 6.3 dan 6.5):
- himpunan risiko tahun t = firm-year yang TIDAK distress D2 pada t-1;
- outcome = D2 pada t; prediktor keuangan diukur pada t-1;
- rasio di-winsorize P1/P99; estimasi Firth (penalized maximum likelihood).

Pemakaian:
    python tools/estimasi_ulang.py data_panel.csv --versi B2-2027-03 \
        --latih-sampai 2022 --keluaran config/koefisien_baru.json

Kolom panel (satu baris per perusahaan-tahun):
    perusahaan, tahun, lini (Jiwa/Umum), ekuitas_aset, roa, rasio_klaim,
    pertumbuhan_premi, total_aset_miliar, d2 (0/1)

Catatan: skrip ini menghasilkan koefisien titik dan galat baku klaster
PERKIRAAN. Inferensi resmi untuk manuskrip tetap memakai perangkat lunak
utama tim (mis. Stata firthlogit / R logistf dengan klaster per perusahaan).
Periksa hasilnya sebelum mengganti config/koefisien.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PREDIKTOR = ["ekuitas_aset", "roa", "rasio_klaim", "pertumbuhan_premi_per10", "ln_aset", "jiwa"]
RASIO = ["ekuitas_aset", "roa", "rasio_klaim", "pertumbuhan_premi"]


def firth_logit(X: np.ndarray, y: np.ndarray, maxit: int = 100, tol: float = 1e-8):
    """Regresi logistik Firth (Firth, 1993) dengan Newton-Raphson dan step-halving."""
    n, k = X.shape
    beta = np.zeros(k)

    def pll(b):
        eta = X @ b
        p = 1 / (1 + np.exp(-eta))
        w = p * (1 - p)
        info = X.T @ (X * w[:, None])
        sign, logdet = np.linalg.slogdet(info)
        ll = np.sum(y * eta - np.logaddexp(0, eta))
        return ll + 0.5 * logdet, p, w, info

    cur, p, w, info = pll(beta)
    for _ in range(maxit):
        inv = np.linalg.inv(info)
        h = np.einsum("ij,jk,ik->i", X * np.sqrt(w)[:, None], inv, X * np.sqrt(w)[:, None])
        u = X.T @ (y - p + h * (0.5 - p))
        step = inv @ u
        t = 1.0
        while True:
            nb = beta + t * step
            new, np_, nw, ninfo = pll(nb)
            if new >= cur - 1e-12 or t < 1e-6:
                break
            t /= 2
        beta, cur, p, w, info = nb, new, np_, nw, ninfo
        if np.max(np.abs(t * step)) < tol:
            break
    return beta, np.linalg.inv(info), p


def se_klaster(X, y, p, cov, klaster):
    """Galat baku sandwich terklaster (perkiraan) di sekitar estimasi Firth."""
    skor = X * (y - p)[:, None]
    meat = np.zeros((X.shape[1], X.shape[1]))
    for g in np.unique(klaster):
        s = skor[klaster == g].sum(axis=0)
        meat += np.outer(s, s)
    G = len(np.unique(klaster))
    adj = G / (G - 1) if G > 1 else 1.0
    V = cov @ meat @ cov * adj
    return np.sqrt(np.diag(V))


def auc(y, s):
    y, s = np.asarray(y), np.asarray(s)
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = pd.Series(np.concatenate([pos, neg])).rank().to_numpy()
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def siapkan_onset(panel: pd.DataFrame, winsor: bool = True) -> pd.DataFrame:
    d = panel.copy()
    d["tahun"] = d["tahun"].astype(int)
    d["d2"] = d["d2"].astype(int)
    d = d.sort_values(["perusahaan", "tahun"])
    if winsor:
        for c in RASIO:
            lo, hi = d[c].quantile([0.01, 0.99])
            d[c] = d[c].clip(lo, hi)
    d["ln_aset"] = np.log(d["total_aset_miliar"].astype(float) * 1000)
    d["pertumbuhan_premi_per10"] = d["pertumbuhan_premi"] / 10
    d["jiwa"] = d["lini"].astype(str).str.lower().str.startswith("jiwa").astype(int)
    lag = d[["perusahaan", "tahun", "ekuitas_aset", "roa", "rasio_klaim", "pertumbuhan_premi_per10", "ln_aset", "d2"]].copy()
    lag["tahun"] = lag["tahun"] + 1
    lag = lag.rename(columns={c: c + "_l1" for c in lag.columns if c not in ("perusahaan", "tahun")})
    m = d[["perusahaan", "tahun", "jiwa", "d2"]].merge(lag, on=["perusahaan", "tahun"], how="inner")
    m = m[m["d2_l1"] == 0]  # himpunan risiko: belum distress pada t-1
    m = m.rename(columns={c + "_l1": c for c in PREDIKTOR if c != "jiwa"})
    return m.dropna(subset=[c for c in PREDIKTOR] + ["d2"]).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("panel")
    ap.add_argument("--versi", required=True)
    ap.add_argument("--latih-sampai", type=int, default=None, help="tahun outcome terakhir untuk sampel latih")
    ap.add_argument("--ambang", type=float, default=None, help="ambang alarm baru (proporsi, mis. 0.173)")
    ap.add_argument("--keluaran", default=str(ROOT / "config" / "koefisien_baru.json"))
    ap.add_argument("--tanpa-winsor", action="store_true")
    a = ap.parse_args()

    panel = pd.read_csv(a.panel)
    perlu = {"perusahaan", "tahun", "lini", "ekuitas_aset", "roa", "rasio_klaim", "pertumbuhan_premi",
             "total_aset_miliar", "d2"}
    if perlu - set(panel.columns):
        sys.exit(f"Kolom kurang: {sorted(perlu - set(panel.columns))}")
    data = siapkan_onset(panel, winsor=not a.tanpa_winsor)
    latih = data if a.latih_sampai is None else data[data["tahun"] <= a.latih_sampai]
    uji = None if a.latih_sampai is None else data[data["tahun"] > a.latih_sampai]

    X = np.column_stack([np.ones(len(latih)), latih[PREDIKTOR].to_numpy(float)])
    y = latih["d2"].to_numpy(float)
    beta, cov, p = firth_logit(X, y)
    se = se_klaster(X, y, p, cov, latih["perusahaan"].to_numpy())
    nama = ["intersep"] + PREDIKTOR

    print(f"Sampel latih: {len(latih)} firm-year, {int(y.sum())} kejadian, {latih['perusahaan'].nunique()} perusahaan")
    print(f"Kejadian per parameter: {y.sum() / len(PREDIKTOR):.1f}")
    print(f"{'variabel':<26}{'koef':>10}{'SE klaster':>12}{'OR':>8}")
    for n_, b_, s_ in zip(nama, beta, se):
        print(f"{n_:<26}{b_:>10.4f}{s_:>12.4f}{np.exp(b_):>8.3f}")
    print(f"AUC dalam sampel: {auc(y, p):.3f}")
    if uji is not None and len(uji):
        Xu = np.column_stack([np.ones(len(uji)), uji[PREDIKTOR].to_numpy(float)])
        pu = 1 / (1 + np.exp(-(Xu @ beta)))
        yu = uji["d2"].to_numpy(float)
        print(f"Uji {a.latih_sampai + 1}+: {len(uji)} firm-year, {int(yu.sum())} kejadian, "
              f"AUC {auc(yu, pu):.3f}, Brier {np.mean((pu - yu) ** 2):.3f}, "
              f"rata-rata prediksi {pu.mean():.3f} vs aktual {yu.mean():.3f}")

    lama = json.loads((ROOT / "config" / "koefisien.json").read_text(encoding="utf-8"))
    baru = dict(lama)
    baru["versi"] = a.versi
    baru["sumber"] = f"Estimasi ulang dengan tools/estimasi_ulang.py pada {date.today().isoformat()} dari {Path(a.panel).name}"
    baru["periode_estimasi"] = (f"outcome {int(latih['tahun'].min())}-{int(latih['tahun'].max())}, {len(latih)} firm-year, "
                                f"{int(y.sum())} kejadian, {latih['perusahaan'].nunique()} perusahaan")
    baru["koefisien"] = {
        "intersep": round(float(beta[0]), 4), "ekuitas_aset": round(float(beta[1]), 4), "roa": round(float(beta[2]), 4),
        "rasio_klaim": round(float(beta[3]), 4), "pertumbuhan_premi_per10": round(float(beta[4]), 4),
        "ln_aset": round(float(beta[5]), 4), "jiwa": round(float(beta[6]), 4),
    }
    if a.ambang is not None:
        baru["ambang_alarm"] = a.ambang
    Path(a.keluaran).write_text(json.dumps(baru, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nKoefisien baru ditulis ke {a.keluaran}. Tinjau, lalu ganti config/koefisien.json bila disetujui tim.")


if __name__ == "__main__":
    main()

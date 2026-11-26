"""Model skor EWS tingkat pertama (Model B2) dan penanda tingkat kedua.

Semua angka model dibaca dari config/koefisien.json, sehingga pembaruan
koefisien setelah estimasi ulang tidak memerlukan perubahan kode.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "koefisien.json"

# Kolom masukan yang dibutuhkan model B2 (semua rasio dalam persen, aset dalam Rp miliar)
KOLOM_WAJIB = ["nama", "lini", "rasio_klaim", "roa", "ekuitas_aset", "pertumbuhan_premi", "total_aset_miliar"]
KOLOM_OPSIONAL = ["segmen", "margin_uw", "roa_t2", "rbc_dilaporkan", "tahun_laporan"]

STATUS_URUT = ["Tinjauan Tingkat 2", "Alarm", "Pantau", "Rendah-sedang", "Rendah"]


@dataclass(frozen=True)
class Konfigurasi:
    versi: str
    koef: dict
    ambang: float
    ekuitas_min: dict
    median: dict
    meta: dict


def muat_konfigurasi(path: Path | str = CONFIG_PATH) -> Konfigurasi:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    perlu = {"intersep", "ekuitas_aset", "roa", "rasio_klaim", "pertumbuhan_premi_per10", "ln_aset", "jiwa"}
    hilang = perlu - set(raw["koefisien"])
    if hilang:
        raise ValueError(f"koefisien.json tidak lengkap, kurang: {sorted(hilang)}")
    return Konfigurasi(
        versi=raw.get("versi", "?"),
        koef=raw["koefisien"],
        ambang=float(raw["ambang_alarm"]),
        ekuitas_min=raw["ekuitas_minimum_miliar"],
        median=raw["median_referensi"],
        meta={k: v for k, v in raw.items() if k not in {"koefisien"}},
    )


def ln_aset_juta(total_aset_miliar):
    """ln total aset dalam juta rupiah (asumsi satuan; lihat koefisien.json)."""
    return np.log(np.asarray(total_aset_miliar, dtype=float) * 1000.0)


def log_odds(df: pd.DataFrame, cfg: Konfigurasi) -> np.ndarray:
    k = cfg.koef
    jiwa = (df["lini"].astype(str).str.lower().str.startswith("jiwa")).astype(float)
    z = (
        k["intersep"]
        + k["ekuitas_aset"] * df["ekuitas_aset"].astype(float)
        + k["roa"] * df["roa"].astype(float)
        + k["rasio_klaim"] * df["rasio_klaim"].astype(float)
        + k["pertumbuhan_premi_per10"] * df["pertumbuhan_premi"].astype(float) / 10.0
        + k["ln_aset"] * ln_aset_juta(df["total_aset_miliar"])
        + k["jiwa"] * jiwa
    )
    return np.asarray(z, dtype=float)


def probabilitas(df: pd.DataFrame, cfg: Konfigurasi) -> np.ndarray:
    z = log_odds(df, cfg)
    return 1.0 / (1.0 + np.exp(-z))


def _num(s: pd.Series | None, n: int) -> pd.Series:
    if s is None:
        return pd.Series([np.nan] * n)
    return pd.to_numeric(s, errors="coerce")


def nilai_entitas(df: pd.DataFrame, cfg: Konfigurasi, ambang_jiwa: float | None = None,
                  ambang_umum: float | None = None) -> pd.DataFrame:
    """Hitung probabilitas, penanda Tingkat 2, dan status untuk setiap baris."""
    out = df.copy().reset_index(drop=True)
    n = len(out)
    out["probabilitas"] = probabilitas(out, cfg)

    ea, roa = _num(out["ekuitas_aset"], n), _num(out["roa"], n)
    uw = _num(out.get("margin_uw"), n)
    roa2 = _num(out.get("roa_t2"), n)
    rbc = _num(out.get("rbc_dilaporkan"), n)
    aset = _num(out["total_aset_miliar"], n)
    syariah = out.get("segmen", pd.Series(["Konvensional"] * n)).astype(str).str.lower().str.startswith("syariah")
    jiwa = out["lini"].astype(str).str.lower().str.startswith("jiwa")

    ekuitas = ea / 100.0 * aset
    minimum = np.where(syariah, cfg.ekuitas_min["syariah"], cfg.ekuitas_min["konvensional"])
    out["ekuitas_miliar"] = ekuitas

    # Definisi D2 pada laporan terakhir
    d2 = (ea < 0) | (rbc < 100) | ((roa < 0) & (uw < 0))
    out["pn_ekuitas_negatif"] = ea < 0
    out["pn_roa_negatif"] = roa < 0
    out["pn_rugi_dua_tahun"] = np.where(roa2.isna(), None, (roa < 0) & (roa2 < 0))
    out["pn_sudah_d2"] = d2
    out["pn_ekuitas_bawah_minimum"] = ekuitas < minimum
    out["jumlah_penanda"] = (
        out[["pn_ekuitas_negatif", "pn_roa_negatif", "pn_sudah_d2", "pn_ekuitas_bawah_minimum"]].sum(axis=1)
        + out["pn_rugi_dua_tahun"].fillna(False).astype(bool).astype(int)
    )

    aj = cfg.ambang if ambang_jiwa is None else ambang_jiwa
    au = cfg.ambang if ambang_umum is None else ambang_umum
    ambang = np.where(jiwa, aj, au)
    p = out["probabilitas"]
    status = np.select(
        [d2, p >= ambang, p > 0.10, p > 0.05],
        ["Tinjauan Tingkat 2", "Alarm", "Pantau", "Rendah-sedang"],
        default="Rendah",
    )
    out["ambang"] = ambang
    out["status"] = status
    out["status_urut"] = out["status"].map({s: i for i, s in enumerate(STATUS_URUT)})
    return out


def kontribusi(x: dict, cfg: Konfigurasi) -> pd.DataFrame:
    """Selisih log-odds tiap indikator terhadap profil median sampel."""
    k, m = cfg.koef, cfg.median
    lna = math.log(float(x["total_aset_miliar"]) * 1000.0)
    baris = [
        ("Rasio klaim", x["rasio_klaim"], m["rasio_klaim"], k["rasio_klaim"] * (x["rasio_klaim"] - m["rasio_klaim"])),
        ("ROA", x["roa"], m["roa"], k["roa"] * (x["roa"] - m["roa"])),
        ("Ekuitas/aset", x["ekuitas_aset"], m["ekuitas_aset"], k["ekuitas_aset"] * (x["ekuitas_aset"] - m["ekuitas_aset"])),
        ("Pertumbuhan premi", x["pertumbuhan_premi"], m["pertumbuhan_premi"],
         k["pertumbuhan_premi_per10"] * (x["pertumbuhan_premi"] - m["pertumbuhan_premi"]) / 10.0),
        ("Ukuran (ln aset)", lna, m["ln_aset"], k["ln_aset"] * (lna - m["ln_aset"])),
    ]
    return pd.DataFrame(baris, columns=["indikator", "nilai", "median", "delta_log_odds"])


def peringatan_masukan(df: pd.DataFrame) -> list[str]:
    """Peringatan untuk nilai yang jauh di luar rentang sampel estimasi."""
    w = []
    if (df["rasio_klaim"] > 500).any():
        w.append("Ada rasio klaim di atas 500%; probabilitas akan jenuh mendekati 100%.")
    if (df["roa"] < -30).any():
        w.append("Ada ROA di bawah -30%; di luar rentang sampel estimasi.")
    if (df["pertumbuhan_premi"].abs() > 200).any():
        w.append("Ada pertumbuhan premi di atas 200% (absolut); periksa apakah satuan sudah persen.")
    if (df["total_aset_miliar"] > 500_000).any():
        w.append("Ada total aset di atas Rp500 triliun; periksa apakah satuan sudah Rp miliar, bukan juta.")
    if (df["total_aset_miliar"] < 10).any():
        w.append("Ada total aset di bawah Rp10 miliar; periksa apakah satuan sudah Rp miliar.")
    return w

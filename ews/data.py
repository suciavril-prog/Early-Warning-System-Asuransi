"""Pembacaan data hasil laporan dan berkas unggahan pengguna."""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

import pandas as pd

from .model import KOLOM_OPSIONAL, KOLOM_WAJIB, ROOT

HASIL_DIR = ROOT / "data" / "hasil_laporan"

# Nama kolom alternatif yang diterima, dipetakan ke nama baku
ALIAS = {
    "nama_perusahaan": "nama", "perusahaan": "nama", "entitas": "nama",
    "jenis_usaha": "lini", "jenis": "lini", "lini_usaha": "lini",
    "claim_ratio": "rasio_klaim", "rasio_beban_klaim": "rasio_klaim",
    "ekuitas_per_aset": "ekuitas_aset", "equity_to_assets": "ekuitas_aset",
    "growth_premi": "pertumbuhan_premi", "pertumbuhan_premi_bruto": "pertumbuhan_premi",
    "aset_miliar": "total_aset_miliar", "total_aset": "total_aset_miliar",
    "margin_underwriting": "margin_uw", "roa_tahun_sebelumnya": "roa_t2",
    "rbc": "rbc_dilaporkan", "syariah_konvensional": "segmen",
}


def muat_hasil(nama: str) -> pd.DataFrame:
    with open(HASIL_DIR / f"{nama}.json", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


def _normal(col: str) -> str:
    c = re.sub(r"[^0-9a-z]+", "_", str(col).strip().lower()).strip("_")
    return ALIAS.get(c, c)


def _angka(s: pd.Series) -> pd.Series:
    """Ubah teks angka gaya Indonesia (1.234,5) maupun gaya titik (1234.5) menjadi float."""
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    t = s.astype(str).str.strip().str.replace("%", "", regex=False).str.replace(" ", "", regex=False)
    t = t.where(~t.isin(["", "nan", "None", "-", "–"]))
    has_comma = t.str.contains(",", na=False)
    t = t.where(~has_comma, t.str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    return pd.to_numeric(t, errors="coerce")


def _lini(v) -> str:
    s = str(v).strip().lower()
    if s in {"1", "jiwa", "life", "asuransi jiwa"} or s.startswith("jiwa"):
        return "Jiwa"
    if s in {"0", "umum", "general", "non-life", "asuransi umum", "kerugian"} or s.startswith("umum"):
        return "Umum"
    return "?"


def _segmen(v) -> str:
    s = str(v).strip().lower()
    if s in {"1", "syariah", "sharia", "takaful"} or s.startswith("syariah"):
        return "Syariah"
    return "Konvensional"


def baca_unggahan(nama_berkas: str, isi: bytes) -> tuple[pd.DataFrame, list[str]]:
    """Baca CSV/XLSX unggahan. Kembalikan (data bersih, daftar pesan)."""
    pesan: list[str] = []
    if nama_berkas.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(isi))
    else:
        teks = isi.decode("utf-8-sig", errors="replace")
        baris1 = teks.splitlines()[0] if teks else ""
        sep = ";" if baris1.count(";") > baris1.count(",") else ","
        df = pd.read_csv(io.StringIO(teks), sep=sep, dtype=str)
    df.columns = [_normal(c) for c in df.columns]

    # Kolom 'jiwa' (1/0) dan 'syariah' (1/0) seperti di prototipe HTML juga diterima
    if "lini" not in df.columns and "jiwa" in df.columns:
        df["lini"] = df["jiwa"]
    if "segmen" not in df.columns and "syariah" in df.columns:
        df["segmen"] = df["syariah"]

    hilang = [c for c in KOLOM_WAJIB if c not in df.columns]
    if hilang:
        raise ValueError("Kolom wajib tidak ditemukan: " + ", ".join(hilang)
                         + ". Unduh templat untuk melihat nama kolom yang benar.")

    keep = KOLOM_WAJIB + [c for c in KOLOM_OPSIONAL if c in df.columns]
    df = df[keep].copy()
    df["nama"] = df["nama"].astype(str).str.strip()
    df["lini"] = df["lini"].map(_lini)
    df["segmen"] = df["segmen"].map(_segmen) if "segmen" in df.columns else "Konvensional"
    for c in ["rasio_klaim", "roa", "ekuitas_aset", "pertumbuhan_premi", "total_aset_miliar",
              "margin_uw", "roa_t2", "rbc_dilaporkan"]:
        if c in df.columns:
            df[c] = _angka(df[c])

    lini_salah = df["lini"] == "?"
    if lini_salah.any():
        pesan.append(f"{int(lini_salah.sum())} baris dilewati: lini usaha bukan Jiwa/Umum "
                     "(reasuransi tidak dicakup model).")
    wajib_num = ["rasio_klaim", "roa", "ekuitas_aset", "pertumbuhan_premi", "total_aset_miliar"]
    kosong = df[wajib_num].isna().any(axis=1) | (df["total_aset_miliar"] <= 0)
    if kosong.any():
        pesan.append(f"{int((kosong & ~lini_salah).sum())} baris dilewati: indikator Model B2 tidak lengkap "
                     "atau total aset tidak positif.")
    df = df[~lini_salah & ~kosong].reset_index(drop=True)

    dup = df["nama"].duplicated(keep=False)
    if dup.any() and "tahun_laporan" not in df.columns:
        pesan.append("Ada nama entitas ganda. Tambahkan kolom tahun_laporan bila berisi beberapa tahun.")
    return df, pesan


def templat_csv() -> str:
    kolom = KOLOM_WAJIB + ["segmen", "margin_uw", "roa_t2", "rbc_dilaporkan", "tahun_laporan"]
    contoh = [
        ["Contoh PT A", "Jiwa", "97.7", "0.8", "24.7", "8", "3630", "Konvensional", "2.0", "1.0", "", "2025"],
        ["Contoh PT B", "Umum", "40.8", "2.2", "62.5", "10", "180", "Syariah", "45", "1.5", "220", "2025"],
    ]
    return ",".join(kolom) + "\n" + "\n".join(",".join(r) for r in contoh) + "\n"

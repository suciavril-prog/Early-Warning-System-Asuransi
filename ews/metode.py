"""Beberapa metode penilaian yang dibandingkan pada data perusahaan yang sama.

Setiap metode memakai satuan hasilnya sendiri (lolos/tidak, jumlah penanda,
jumlah rasio di luar rentang, peluang). Hasil tidak digabung menjadi satu skor.

Sumber:
- Batas RBC: POJK 71/2016 (minimum 100%, target internal minimal 120%).
- Ekuitas minimum tahap pertama: POJK 23/2023.
- Rentang wajar IRIS: NAIC, IRIS Ratios Manual, edisi 2024. Rentang dibuat untuk
  pasar Amerika Serikat; di sini dipakai sebagai ilustrasi dan sebagian rasio
  diadaptasi agar bisa dihitung dari laporan publik Indonesia.
- Model EWS B2: Laporan Kemajuan penelitian LPS–SBM ITB.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .model import Konfigurasi, nilai_entitas


@dataclass
class PosLaporan:
    """Pos laporan keuangan, semua dalam Rp miliar kecuali disebut lain."""
    lini: str = "Jiwa"
    segmen: str = "Konvensional"
    total_aset: float = 0.0
    total_liabilitas: float = 0.0
    ekuitas: float = 0.0
    ekuitas_lalu: float = 0.0
    aset_likuid: float = 0.0
    premi_bruto: float = 0.0
    premi_bruto_lalu: float = 0.0
    premi_neto: float = 0.0
    klaim_neto: float = 0.0
    hasil_underwriting: float = 0.0
    total_pendapatan: float = 0.0
    laba_bersih: float = 0.0
    laba_bersih_lalu: float = 0.0
    rbc: float | None = None  # persen, opsional


def _bagi(a: float, b: float) -> float | None:
    return None if not b else a / b * 100.0


def rasio(p: PosLaporan) -> dict:
    """Rasio yang diturunkan dari pos laporan (persen)."""
    return {
        "rasio_klaim": _bagi(p.klaim_neto, p.premi_neto),
        "roa": _bagi(p.laba_bersih, p.total_aset),
        "ekuitas_aset": _bagi(p.ekuitas, p.total_aset),
        "pertumbuhan_premi": _bagi(p.premi_bruto - p.premi_bruto_lalu, p.premi_bruto_lalu),
        "margin_uw": _bagi(p.hasil_underwriting, p.premi_neto),
        "roa_t2": _bagi(p.laba_bersih_lalu, p.total_aset),
        "premi_neto_ekuitas": _bagi(p.premi_neto, p.ekuitas) if p.ekuitas > 0 else None,
        "perubahan_ekuitas": _bagi(p.ekuitas - p.ekuitas_lalu, abs(p.ekuitas_lalu)),
        "liabilitas_aset_likuid": _bagi(p.total_liabilitas, p.aset_likuid),
        "laba_pendapatan": _bagi(p.laba_bersih, p.total_pendapatan),
    }


# ---------------------------------------------------------------- metode 1
def regulasi(p: PosLaporan, cfg: Konfigurasi) -> dict:
    mn = cfg.ekuitas_min["syariah" if p.segmen == "Syariah" else "konvensional"]
    cek = []
    if p.rbc is None:
        cek.append(("RBC minimal 100%", None, "RBC tidak diisi"))
        cek.append(("Target internal RBC minimal 120%", None, "RBC tidak diisi"))
    else:
        cek.append(("RBC minimal 100%", p.rbc >= 100, f"RBC {p.rbc:.0f}%"))
        cek.append(("Target internal RBC minimal 120%", p.rbc >= 120, f"RBC {p.rbc:.0f}%"))
    cek.append((f"Ekuitas minimal Rp{mn} miliar (POJK 23/2023, tahap pertama)", p.ekuitas >= mn,
                f"ekuitas Rp{p.ekuitas:,.0f} miliar".replace(",", ".")))
    gagal = [c for c in cek if c[1] is False]
    if gagal:
        ringkas = "Tidak memenuhi"
    elif any(c[1] is None for c in cek):
        ringkas = "Memenuhi (RBC tidak diisi)"
    else:
        ringkas = "Memenuhi"
    return {"hasil": ringkas, "rinci": cek, "sinyal": bool(gagal)}


# ---------------------------------------------------------------- metode 2
def penanda(p: PosLaporan) -> dict:
    r = rasio(p)
    cek = [
        ("Ekuitas negatif", p.ekuitas < 0),
        ("Rugi bersih (ROA negatif)", p.laba_bersih < 0),
        ("Rugi dua tahun berturut-turut", p.laba_bersih < 0 and p.laba_bersih_lalu < 0),
        ("Rasio klaim di atas 100%", r["rasio_klaim"] is not None and r["rasio_klaim"] > 100),
        ("Rugi underwriting", p.hasil_underwriting < 0),
    ]
    n = sum(bool(c[1]) for c in cek)
    return {"hasil": f"{n} dari {len(cek)} penanda menyala", "rinci": cek, "sinyal": n >= 2, "n": n}


# ---------------------------------------------------------------- metode 3
def iris(p: PosLaporan) -> dict:
    """Adaptasi sebagian rasio IRIS yang bisa dihitung dari laporan publik."""
    r = rasio(p)
    if p.lini == "Jiwa":
        daftar = [
            ("Perubahan ekuitas (Life ratio 2)", r["perubahan_ekuitas"], -10, 50,
             "di atas −10% dan di bawah 50%"),
            ("Laba bersih / total pendapatan (Life ratio 3)", r["laba_pendapatan"], 0, None, "di atas 0%"),
            ("Perubahan premi (Life ratio 9, memakai premi bruto)", r["pertumbuhan_premi"], -10, 50,
             "antara −10% dan 50%"),
        ]
    else:
        daftar = [
            ("Premi neto / ekuitas (P&C ratio 2)", r["premi_neto_ekuitas"], None, 300, "sampai 300%"),
            ("Perubahan premi (P&C ratio 3, memakai premi bruto)", r["pertumbuhan_premi"], -33, 33,
             "antara −33% dan 33%"),
            ("Perubahan ekuitas (P&C ratio 7)", r["perubahan_ekuitas"], -10, 50, "di atas −10% dan di bawah 50%"),
            ("Liabilitas / aset likuid (P&C ratio 9, disederhanakan)", r["liabilitas_aset_likuid"], None, 100,
             "di bawah 100%"),
        ]
    rinci = []
    luar = 0
    for nama, v, lo, hi, teks in daftar:
        if v is None:
            rinci.append((nama, None, teks, "tidak dapat dihitung"))
            continue
        if lo is not None and hi is not None:
            wajar = lo < v < hi
        elif lo is not None:
            wajar = v > lo
        else:
            wajar = v <= hi if teks.startswith("sampai") else v < hi
        luar += 0 if wajar else 1
        rinci.append((nama, v, teks, "wajar" if wajar else "di luar rentang"))
    dihitung = sum(1 for x in rinci if x[1] is not None)
    return {"hasil": f"{luar} dari {dihitung} rasio di luar rentang wajar", "rinci": rinci,
            "sinyal": luar >= 2, "n": luar}


# ---------------------------------------------------------------- metode 4
def model_b2(p: PosLaporan, cfg: Konfigurasi) -> dict:
    r = rasio(p)
    perlu = ["rasio_klaim", "roa", "ekuitas_aset", "pertumbuhan_premi"]
    if any(r[k] is None for k in perlu) or p.total_aset <= 0:
        return {"hasil": "Data belum lengkap", "sinyal": False, "baris": None}
    df = pd.DataFrame([{
        "nama": "Perbandingan", "lini": p.lini, "segmen": p.segmen, "rasio_klaim": r["rasio_klaim"],
        "roa": r["roa"], "ekuitas_aset": r["ekuitas_aset"], "pertumbuhan_premi": r["pertumbuhan_premi"],
        "total_aset_miliar": p.total_aset, "margin_uw": r["margin_uw"], "roa_t2": r["roa_t2"],
        "rbc_dilaporkan": p.rbc,
    }])
    baris = nilai_entitas(df, cfg).iloc[0]
    return {"hasil": f"{baris['probabilitas'] * 100:.1f}%".replace(".", ","), "status": baris["status"],
            "sinyal": baris["status"] in {"Alarm", "Tinjauan Tingkat 2"}, "baris": baris}


CONTOH = {
    "Jiwa yang sedang tertekan (rekaan)": PosLaporan(
        lini="Jiwa", segmen="Konvensional", total_aset=2400, total_liabilitas=2050, ekuitas=350, ekuitas_lalu=420,
        aset_likuid=1500, premi_bruto=900, premi_bruto_lalu=960, premi_neto=820, klaim_neto=1010,
        hasil_underwriting=-60, total_pendapatan=1050, laba_bersih=-35, laba_bersih_lalu=-12, rbc=165),
    "Umum yang sehat (rekaan)": PosLaporan(
        lini="Umum", segmen="Konvensional", total_aset=1500, total_liabilitas=930, ekuitas=570, ekuitas_lalu=530,
        aset_likuid=900, premi_bruto=800, premi_bruto_lalu=740, premi_neto=500, klaim_neto=230,
        hasil_underwriting=95, total_pendapatan=620, laba_bersih=45, laba_bersih_lalu=40, rbc=310),
    "Umum syariah kecil (rekaan)": PosLaporan(
        lini="Umum", segmen="Syariah", total_aset=180, total_liabilitas=95, ekuitas=85, ekuitas_lalu=82,
        aset_likuid=120, premi_bruto=110, premi_bruto_lalu=100, premi_neto=70, klaim_neto=38,
        hasil_underwriting=9, total_pendapatan=85, laba_bersih=2.5, laba_bersih_lalu=2.0, rbc=None),
}

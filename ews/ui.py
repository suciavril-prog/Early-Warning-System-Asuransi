"""Tampilan bersama: tema biru muda, kepala halaman, kartu angka, format angka."""
from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from .auth import wajib_login
from .model import muat_konfigurasi

ASET = Path(__file__).resolve().parent.parent / "assets"

WARNA = {
    "utama": "#1f6fb2",
    "muda": "#5aa9e6",
    "kedua": "#e08a2e",
    "kritis": "#c0392b",
    "redup": "#a9bccd",
    "baik": "#2e7d4f",
    "waspada": "#b86e00",
    "t2": "#3d4a5c",
}
STATUS_WARNA = {
    "Tinjauan Tingkat 2": WARNA["t2"],
    "Alarm": WARNA["kritis"],
    "Pantau": WARNA["waspada"],
    "Rendah-sedang": "#8f7a12",
    "Rendah": WARNA["baik"],
}
# latar lembut untuk label status (teks memakai warna penuh di atas latar ini)
_STATUS_LATAR = {
    "Tinjauan Tingkat 2": "#e4e8ee",
    "Alarm": "#fbe4e1",
    "Pantau": "#fdeed8",
    "Rendah-sedang": "#f6f0cf",
    "Rendah": "#dff1e6",
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
div[data-testid="stMetricValue"], .ews-num { font-variant-numeric: tabular-nums; }
.block-container { padding-top: 3.6rem; max-width: 1240px; }
h1, h2, h3 { letter-spacing: -0.01em; }

/* kepala halaman */
.ews-head { background:#ffffff; border:1px solid #cfe3f5; border-radius:18px; padding:22px 26px;
            margin-bottom:18px; display:flex; gap:20px; align-items:center; }
.ews-head .ews-eyebrow { font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#1f6fb2; }
.ews-head h1 { font-size:1.75rem; margin:.15rem 0 .35rem; padding:0; color:#14324d; }
.ews-head p { margin:0; color:#3f5f7a; font-size:1rem; line-height:1.55; max-width:62rem; }
.ews-head .ews-ico { flex:0 0 auto; width:56px; height:56px; border-radius:16px; background:#e3f0fb;
                     display:flex; align-items:center; justify-content:center; font-size:28px; }
.ews-hero { background:#dcecfa; border-color:#bcd9f2; }
.ews-hero h1 { font-size:2.05rem; }

/* kartu angka */
.ews-kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px; margin:4px 0 18px; }
.ews-kpi { background:#ffffff; border:1px solid #cfe3f5; border-radius:16px; padding:16px 18px; }
.ews-kpi .l { font-size:.86rem; color:#3f5f7a; font-weight:600; }
.ews-kpi .v { font-size:2rem; font-weight:700; color:#14324d; line-height:1.15; margin:.25rem 0; font-variant-numeric:tabular-nums; }
.ews-kpi .c { font-size:.84rem; color:#4a6a86; line-height:1.45; }
.ews-kpi.kritis { border-left:5px solid #c0392b; }
.ews-kpi.utama { border-left:5px solid #1f6fb2; }
.ews-kpi.waspada { border-left:5px solid #b86e00; }
.ews-kpi.netral { border-left:5px solid #a9bccd; }

/* kotak keterangan */
.ews-box { border-radius:14px; padding:14px 16px; margin:6px 0 14px; line-height:1.55; font-size:.95rem; }
.ews-box.info { background:#e6f1fb; border:1px solid #cfe3f5; color:#14324d; }
.ews-box.awas { background:#fff5e6; border:1px solid #f4dcb4; color:#5a3b00; }
.ews-box.analogi { background:#ffffff; border:1px dashed #9cc6ea; color:#14324d; }

/* langkah dan tangga */
.ews-steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin:6px 0 14px; }
.ews-step { background:#fff; border:1px solid #cfe3f5; border-radius:14px; padding:14px; }
.ews-step .n { width:30px; height:30px; border-radius:50%; background:#1f6fb2; color:#fff; font-weight:700;
               display:flex; align-items:center; justify-content:center; margin-bottom:8px; }
.ews-step b { color:#14324d; }
.ews-step span { color:#3f5f7a; font-size:.9rem; line-height:1.45; display:block; margin-top:4px; }
.ews-step.sorot { border:2px solid #1f6fb2; background:#f0f7fe; }

.ews-pill { display:inline-block; padding:3px 12px; border-radius:999px; font-weight:700; font-size:.85rem; }
.ews-note { color:#4a6a86; font-size:.85rem; }
.ews-foot { color:#4a6a86; font-size:.8rem; margin-top:28px; border-top:1px solid #cfe3f5; padding-top:10px; }

@media (max-width: 640px) {
  .ews-head { padding:16px; flex-direction:column; align-items:flex-start; gap:10px; }
  .ews-head h1, .ews-hero h1 { font-size:1.45rem; }
  .ews-kpi .v { font-size:1.6rem; }
}
</style>
"""


def inisialisasi() -> None:
    """Dipanggil sekali di app.py sebelum navigasi."""
    ikon = ASET / "ikon.png"
    st.set_page_config(page_title="EWS Asuransi · LPS–SBM ITB",
                       page_icon=str(ikon) if ikon.exists() else ":material/monitor_heart:",
                       layout="wide", initial_sidebar_state="auto")
    st.markdown(_CSS, unsafe_allow_html=True)
    st.logo(str(ASET / "logo.svg"), icon_image=str(ASET / "ikon.svg"), size="large")
    wajib_login()
    cfg = muat_konfigurasi()
    with st.sidebar:
        st.caption(f"Model {cfg.versi} · ambang bawaan {fmt(cfg.ambang * 100, 1)}%")
        st.caption("Prototipe penelitian LPS–SBM ITB. Alat penyaring, bukan dasar sanksi.")


def kepala(judul: str, keterangan: str = "", label: str = "", ikon: str = "", hero: bool = False) -> None:
    """Kepala halaman: label kecil, judul, satu kalimat penjelas."""
    ico = f'<div class="ews-ico" aria-hidden="true">{ikon}</div>' if ikon else ""
    lab = f'<div class="ews-eyebrow">{escape(label)}</div>' if label else ""
    ket = f"<p>{keterangan}</p>" if keterangan else ""
    st.markdown(f'<div class="ews-head{" ews-hero" if hero else ""}">{ico}<div>{lab}<h1>{escape(judul)}</h1>{ket}'
                f'</div></div>', unsafe_allow_html=True)


def kartu_angka(daftar: list[dict]) -> None:
    """daftar berisi dict: label, nilai, konteks, nada (utama/kritis/waspada/netral)."""
    isi = "".join(
        f'<div class="ews-kpi {k.get("nada", "utama")}"><div class="l">{escape(k["label"])}</div>'
        f'<div class="v">{escape(str(k["nilai"]))}</div><div class="c">{k.get("konteks", "")}</div></div>'
        for k in daftar)
    st.markdown(f'<div class="ews-kpis">{isi}</div>', unsafe_allow_html=True)


def kotak(teks: str, jenis: str = "info") -> None:
    st.markdown(f'<div class="ews-box {jenis}">{teks}</div>', unsafe_allow_html=True)


def langkah(daftar: list[tuple[str, str]], sorot: int | None = None, bernomor: bool = True) -> None:
    isi = ""
    for i, (judul, teks) in enumerate(daftar, 1):
        n = f'<div class="n">{i}</div>' if bernomor else ""
        kelas = "ews-step sorot" if sorot == i else "ews-step"
        isi += f'<div class="{kelas}">{n}<b>{judul}</b><span>{teks}</span></div>'
    st.markdown(f'<div class="ews-steps">{isi}</div>', unsafe_allow_html=True)


def kaki() -> None:
    st.markdown('<div class="ews-foot">Prototipe penelitian LPS–SBM ITB. Angka berasal dari Laporan Kemajuan '
                'penelitian; skor adalah alat penyaring, bukan dasar sanksi.</div>', unsafe_allow_html=True)


def fmt(v, d: int = 1) -> str:
    """Format angka gaya Indonesia: 1.234,5"""
    try:
        if v is None or v != v:
            return "–"
        s = f"{float(v):,.{d}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "–"


def pct(p: float, d: int = 1) -> str:
    return fmt(p * 100, d) + "%"


def pill(status: str) -> str:
    c = STATUS_WARNA.get(status, WARNA["redup"])
    bg = _STATUS_LATAR.get(status, "#eef2f6")
    return f'<span class="ews-pill" style="color:{c};background:{bg};border:1px solid {c}33">{escape(status)}</span>'


def sumber(teks: str) -> None:
    st.caption(f"Sumber: {teks}")

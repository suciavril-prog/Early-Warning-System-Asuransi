"""Login sederhana berbasis .streamlit/secrets.toml.

Kata sandi disimpan sebagai hash PBKDF2-SHA256 (bukan teks asli).
Buat hash dengan:  python tools/buat_hash.py
Untuk sistem produksi LPS, ganti modul ini dengan SSO/OIDC lembaga
(Streamlit mendukung st.login dengan penyedia OIDC).
"""
from __future__ import annotations

import hashlib
import hmac

import streamlit as st

ITERASI = 260_000


def hash_sandi(sandi: str, garam: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", sandi.encode(), garam.encode(), ITERASI)
    return f"pbkdf2_sha256${ITERASI}${garam}${dk.hex()}"


def cocok(sandi: str, tersimpan: str) -> bool:
    try:
        _, it, garam, hx = tersimpan.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", sandi.encode(), garam.encode(), int(it))
        return hmac.compare_digest(dk.hex(), hx)
    except Exception:
        return False


def _pengguna() -> dict:
    try:
        return dict(st.secrets.get("auth", {}).get("users", {}))
    except Exception:
        return {}


def wajib_login() -> None:
    """Panggil di awal setiap halaman. Menghentikan halaman bila belum login."""
    if st.session_state.get("pengguna"):
        with st.sidebar:
            st.caption(f"Masuk sebagai **{st.session_state['pengguna']}**")
            if st.button("Keluar", width="stretch"):
                st.session_state.clear()
                st.rerun()
        return

    users = _pengguna()
    if not users:
        try:
            wajib = bool(st.secrets.get("auth", {}).get("required", False))
        except Exception:
            wajib = False
        if wajib:
            st.error("Login diwajibkan, tetapi belum ada pengguna di secrets.toml. Hubungi admin aplikasi.")
            st.stop()
        st.sidebar.warning("Mode pengembangan: login belum diaktifkan. Jangan unggah data bernama.")
        return

    _, tengah, _ = st.columns([1, 1.3, 1])
    with tengah:
        st.markdown('<div class="ews-head ews-hero"><div><div class="ews-eyebrow">EWS Asuransi · LPS–SBM ITB</div>'
                    '<h1>Selamat datang</h1><p>Masuk untuk membuka sistem peringatan dini. Akses terbatas untuk tim '
                    'penelitian dan LPS.</p></div></div>', unsafe_allow_html=True)
        with st.form("login", border=True):
            u = st.text_input("Nama pengguna")
            p = st.text_input("Kata sandi", type="password")
            ok = st.form_submit_button("Masuk", type="primary", width="stretch")
        if ok:
            if u in users and cocok(p, str(users[u])):
                st.session_state["pengguna"] = u
                st.rerun()
            st.error("Nama pengguna atau kata sandi salah.")
    st.stop()

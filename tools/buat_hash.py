"""Buat hash kata sandi untuk .streamlit/secrets.toml.

Pemakaian:  python tools/buat_hash.py
"""
import getpass
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ews.auth import hash_sandi  # noqa: E402

nama = input("Nama pengguna: ").strip()
s1 = getpass.getpass("Kata sandi: ")
s2 = getpass.getpass("Ulangi kata sandi: ")
if s1 != s2 or len(s1) < 10:
    sys.exit("Kata sandi tidak sama atau kurang dari 10 karakter.")
h = hash_sandi(s1, secrets.token_hex(16))
print("\nSalin baris berikut ke bagian [auth.users] di .streamlit/secrets.toml:\n")
print(f'{nama} = "{h}"')

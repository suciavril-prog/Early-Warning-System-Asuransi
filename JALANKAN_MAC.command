#!/bin/bash
cd "$(dirname "$0")"
echo "EWS Asuransi LPS-SBM ITB - menyiapkan aplikasi"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python belum terpasang. Pasang dari https://www.python.org/downloads/"
  read -p "Tekan Enter untuk menutup..."; exit 1
fi
[ -d .venv ] || { echo "[1/3] Membuat lingkungan Python..."; python3 -m venv .venv; }
source .venv/bin/activate
echo "[2/3] Memasang komponen (pertama kali bisa 2-5 menit)..."
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt || { echo "Gagal memasang komponen. Periksa internet."; read -p "Enter..."; exit 1; }
echo "[3/3] Menjalankan aplikasi. Biarkan jendela ini terbuka; tutup untuk berhenti."
(sleep 6; open http://localhost:8501) &
streamlit run app.py --server.port 8501

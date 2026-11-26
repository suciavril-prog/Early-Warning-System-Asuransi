@echo off
title EWS Asuransi LPS-SBM ITB
cd /d "%~dp0"
echo.
echo  ==============================================
echo   EWS Asuransi LPS-SBM ITB - menyiapkan aplikasi
echo  ==============================================
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo  Python belum terpasang atau belum masuk PATH.
  echo  Pasang Python dari https://www.python.org/downloads/
  echo  dan centang "Add python.exe to PATH" saat instalasi.
  echo.
  pause
  exit /b
)
if not exist ".venv" (
  echo  [1/3] Membuat lingkungan Python khusus aplikasi...
  python -m venv .venv
)
call ".venv\Scripts\activate.bat"
echo  [2/3] Memasang komponen (pertama kali bisa 2-5 menit)...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo  Gagal memasang komponen. Periksa koneksi internet lalu coba lagi.
  pause
  exit /b
)
echo  [3/3] Menjalankan aplikasi. Browser akan terbuka otomatis.
echo  Biarkan jendela hitam ini tetap terbuka selama aplikasi dipakai.
echo  Untuk berhenti: tutup jendela ini.
echo.
start "" cmd /c "timeout /t 6 >nul & start http://localhost:8501"
streamlit run app.py --server.port 8501
pause

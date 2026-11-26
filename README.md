# EWS Asuransi LPS–SBM ITB (prototipe aplikasi web)

Aplikasi web Early Warning System untuk memprediksi awal *financial distress* perusahaan asuransi
di Indonesia, berbasis Model B2 (discrete-time hazard, Firth logit) dari Laporan Kemajuan Penelitian
LPS–SBM ITB, Oktober 2026.

> Prototipe penelitian. Skor adalah alat penyaring, bukan dasar pengenaan sanksi.

## Isi aplikasi

| Kelompok | Halaman | Fungsi |
|---|---|---|
| Hasil penelitian | Ringkasan, Indikator, Model dan validasi, Kasus kegagalan, Skor 2026 | Menyajikan hasil Laporan Kemajuan (Tabel 6.1–6.19) |
| Alat skor | Simulator entitas | Menilai satu entitas dari rasio laporan t−1, lengkap dengan kontribusi indikator, sensitivitas, dan penanda Tingkat 2 |
| Alat skor | Daftar pantauan | Unggah CSV/Excel banyak entitas, saring, urutkan, unduh hasil (CSV/Excel) |
| Bantuan | Panduan dan batasan | Cara kerja, versi model, batas penggunaan |

## Struktur folder

```
app.py                     titik masuk (navigasi + login)
halaman/                   satu berkas per halaman
ews/model.py               rumus skor B2, penanda Tingkat 2, status
ews/data.py                pembacaan data laporan dan berkas unggahan
ews/charts.py              grafik Plotly
ews/auth.py                login berbasis secrets.toml (hash PBKDF2)
config/koefisien.json      SATU-SATUNYA tempat koefisien dan ambang model
data/hasil_laporan/        tabel hasil Laporan Kemajuan (JSON)
data/contoh_pantauan.json  10 entitas ilustratif (bukan perusahaan nyata)
templates/                 templat CSV daftar pantauan
tools/estimasi_ulang.py    estimasi ulang koefisien dari data panel
tools/buat_hash.py         membuat hash kata sandi pengguna
tests/                     uji otomatis (pytest)
docs/                      panduan deploy dan pemutakhiran
```

## Menjalankan di laptop (uji coba)

Butuh Python 3.11 atau lebih baru.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Buka http://localhost:8501. Tanpa `secrets.toml`, aplikasi berjalan dalam **mode pengembangan**
tanpa login. Jangan unggah data bernama dalam mode ini.

## Mengaktifkan login

```bash
python tools/buat_hash.py                       # isi nama pengguna dan kata sandi
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# tempel baris hasil buat_hash.py ke bagian [auth.users]
```

Untuk produksi di LPS, ganti `ews/auth.py` dengan SSO/OIDC lembaga (Streamlit menyediakan `st.login`).

## Menjalankan uji

```bash
pip install pytest
pytest -q
```

Uji mencakup kecocokan skor dengan median Tabel 6.19, arah koefisien, status dan penanda, pembacaan
CSV gaya Indonesia, estimator Firth, dan kerangka onset.

## Deploy ke server

Lihat `docs/DEPLOY.md` (server Linux dengan systemd + Nginx + HTTPS, atau Docker).

## Memperbarui model

Lihat `docs/PANDUAN_PEMUTAKHIRAN.md`. Ringkasnya: jalankan `tools/estimasi_ulang.py` pada panel terbaru,
tinjau hasilnya bersama tim, lalu ganti `config/koefisien.json`. Kode tidak perlu diubah.

## Asumsi dan batasan yang harus dikonfirmasi

1. **Satuan ln total aset diasumsikan juta rupiah.** Laporan tidak menyebut satuannya. Asumsi ini konsisten
   dengan median skor Tabel 6.19 (umum konvensional sekitar 2%, jiwa konvensional sekitar 11–15%), tetapi harus
   dicocokkan dengan berkas data panel. Satuan yang keliru menggeser skor secara besar.
2. **Definisi D2** adalah usulan tim dan belum divalidasi terhadap status pengawasan OJK.
3. **Ambang 17,3%** adalah pilihan statistik; LPS perlu menetapkannya, idealnya terpisah untuk jiwa dan umum.
4. **Entitas spin-off baru dan segmen syariah** hampir tidak ada dalam sampel estimasi; skornya ekstrapolasi.
5. **Reasuransi** tidak dicakup model.

## Kerahasiaan

Skor per entitas bernama hanya untuk LPS sebagai pemberi mandat (Bagian 5.9 proposal). Berkas unggahan
diolah di memori sesi dan tidak disimpan aplikasi. Jalankan di server internal dengan login aktif dan HTTPS
bila memuat data bernama.

# Panduan pemutakhiran model

Model dibaca dari satu berkas: `config/koefisien.json`. Memperbarui model berarti mengganti berkas ini.

## Kapan diperbarui

1. Setelah laporan tahunan 2026 tersedia (estimasi ulang dengan outcome 2026).
2. Setelah tim menyepakati definisi distress final (D1, D2, atau versi per jenis usaha).
3. Bila LPS menetapkan ambang alarm kebijakan, termasuk ambang terpisah jiwa/umum.
4. Pengujian ulang H2 (spin-off) yang direncanakan 2028–2030.

## Langkah

### 1. Siapkan panel firm-year (CSV)

Satu baris per perusahaan-tahun, asuransi langsung saja:

| kolom | isi |
|---|---|
| perusahaan | kode atau nama perusahaan |
| tahun | tahun buku |
| lini | Jiwa / Umum |
| ekuitas_aset, roa, rasio_klaim, pertumbuhan_premi | dalam persen |
| total_aset_miliar | Rp miliar |
| d2 | 1 bila memenuhi kriteria D2 pada tahun itu, 0 bila tidak |

Skrip membuat sendiri kerangka onset: prediktor t−1, himpunan risiko = belum distress pada t−1,
winsorize P1/P99.

### 2. Estimasi ulang dengan validasi temporal

```bash
python tools/estimasi_ulang.py panel_2016_2026.csv --versi B2-2027-03 \
    --latih-sampai 2023 --keluaran config/koefisien_baru.json
```

Periksa keluaran di layar:
- jumlah kejadian per parameter (idealnya ≥ 10; laporan saat ini sekitar 8 untuk B2);
- tanda koefisien rasio klaim (positif) dan ROA (negatif) sesuai teori;
- AUC, Brier, dan rata-rata prediksi pada data uji dibanding tingkat kejadian aktual.

Setelah validasi, estimasi sekali lagi pada seluruh periode (tanpa `--latih-sampai`) untuk koefisien final.

### 3. Cocokkan dengan perangkat lunak utama tim

Skrip menghasilkan koefisien titik Firth dan galat baku klaster perkiraan. Untuk manuskrip dan laporan resmi,
cocokkan dengan estimasi di Stata (`firthlogit`) atau R (`logistf`) dengan klaster per perusahaan.
Selisih koefisien seharusnya hanya pada digit keempat.

### 4. Ganti konfigurasi

```bash
cp config/koefisien.json config/arsip/koefisien_B2-2026-10.json   # arsipkan versi lama
mv config/koefisien_baru.json config/koefisien.json
pytest -q                                                         # uji 1 mungkin perlu disesuaikan
sudo systemctl restart ews                                        # atau: docker restart ews
```

Halaman "Panduan dan batasan" dan sidebar akan menampilkan versi baru. Kolom `model_versi` pada
unduhan hasil daftar pantauan mencatat versi yang dipakai, sehingga skor lama dan baru dapat dibedakan.

### 5. Perbarui data hasil laporan (opsional)

Tabel hasil penelitian di `data/hasil_laporan/*.json` dapat diganti dengan tabel laporan akhir.
Nama kolom harus tetap sama.

## Mengubah ambang tanpa estimasi ulang

Ubah `"ambang_alarm"` di `config/koefisien.json` (proporsi, mis. `0.15`). Pengguna tetap dapat mencoba
ambang lain di Simulator dan Daftar pantauan tanpa mengubah berkas.

## Bila satuan aset ternyata bukan juta rupiah

Ubah fungsi `ln_aset_juta` di `ews/model.py` dan baris `ln_aset` di `tools/estimasi_ulang.py` agar sesuai
satuan berkas panel, lalu perbarui `satuan_aset_ln` di `config/koefisien.json` dan jalankan uji.

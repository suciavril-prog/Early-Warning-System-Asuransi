# Panduan deploy

Dua cara yang didukung. Pilih salah satu bersama admin TI SBM ITB atau LPS.

## A. Server Linux (Ubuntu 22.04/24.04) dengan systemd dan Nginx

### 1. Siapkan aplikasi

```bash
sudo adduser --system --group ews
sudo mkdir -p /opt/ews && sudo chown ews:ews /opt/ews
sudo -u ews git clone <repo-internal> /opt/ews/app      # atau salin folder aplikasi
cd /opt/ews/app
sudo -u ews python3 -m venv /opt/ews/venv
sudo -u ews /opt/ews/venv/bin/pip install -r requirements.txt
```

### 2. Aktifkan login

```bash
sudo -u ews /opt/ews/venv/bin/python tools/buat_hash.py
sudo -u ews cp .streamlit/secrets.toml.example .streamlit/secrets.toml
sudo -u ews nano .streamlit/secrets.toml      # tempel hash, set required = true
sudo chmod 600 .streamlit/secrets.toml
```

### 3. Layanan systemd

`/etc/systemd/system/ews.service`:

```ini
[Unit]
Description=EWS Asuransi (Streamlit)
After=network.target

[Service]
User=ews
WorkingDirectory=/opt/ews/app
ExecStart=/opt/ews/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now ews
```

### 4. Nginx sebagai reverse proxy (HTTPS)

`/etc/nginx/sites-available/ews`:

```nginx
server {
    listen 443 ssl;
    server_name ews.contoh-domain.ac.id;
    ssl_certificate     /etc/letsencrypt/live/ews.contoh-domain.ac.id/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ews.contoh-domain.ac.id/privkey.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;      # Streamlit memakai WebSocket
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
server { listen 80; server_name ews.contoh-domain.ac.id; return 301 https://$host$request_uri; }
```

```bash
sudo ln -s /etc/nginx/sites-available/ews /etc/nginx/sites-enabled/
sudo certbot --nginx -d ews.contoh-domain.ac.id      # sertifikat HTTPS
sudo nginx -t && sudo systemctl reload nginx
```

Ganti `ews.contoh-domain.ac.id` dengan subdomain yang diberikan admin TI. Bila hanya untuk jaringan
internal LPS, batasi akses di Nginx (`allow`/`deny`) atau lewat VPN.

## B. Docker

```bash
docker build -t ews-asuransi .
docker run -d --name ews -p 127.0.0.1:8501:8501 \
  -v $(pwd)/.streamlit/secrets.toml:/app/.streamlit/secrets.toml:ro \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped ews-asuransi
```

`secrets.toml` tidak ikut di-image; dipasang dari luar. Folder `config` dipasang agar koefisien bisa
diperbarui tanpa membangun ulang image. Pasang Nginx seperti langkah A.4 di depan container.

## Catatan keamanan

- Jangan memakai layanan hosting publik gratis untuk data bernama.
- Wajibkan HTTPS dan login (`required = true`).
- Simpan `secrets.toml` dengan izin 600 dan jangan masukkan ke Git.
- Aplikasi tidak menyimpan berkas unggahan; log server Streamlit tidak memuat isi data.
- Untuk sistem produksi LPS, gunakan SSO lembaga dan lakukan uji keamanan oleh tim TI LPS.

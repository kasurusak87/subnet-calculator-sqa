# Subnet & VLSM Calculator

Kalkulator Subnet IPv4 dan Variable Length Subnet Mask (VLSM) berbasis web, dibangun menggunakan Python 3.12, FastAPI, dan antarmuka web responsif.

## Fitur
- **Kalkulator Subnet**: Menghitung subnet mask, wildcard mask, network address, broadcast address, usable host range, dan jumlah host usable (termasuk dukungan RFC 3021 untuk /31 dan host route untuk /32).
- **Alokasi VLSM**: Alokasi subnet dinamis berdasarkan kebutuhan host yang diurutkan dari terbesar ke terkecil.
- **REST API**: Endpoint `GET /api/subnet` dan `POST /api/vlsm`.

## Menjalankan Secara Lokal

```bash
uv sync --dev
uv run fastapi dev main.py
```

Akses antarmuka melalui browser di: `http://127.0.0.1:8000`

## Menjalankan Pengujian

```bash
uv run pytest
```

## Docker

### 1. Build Container Image

```bash
docker build -t subnet-calculator .
```

### 2. Jalankan Container

```bash
docker run -d --name subnet-app -p 8000:8000 subnet-calculator
```

Aplikasi dapat diakses di `http://127.0.0.1:8000`.

### 3. Menjalankan Smoke Test ke Container Lokal

Pastikan container sudah berjalan, lalu eksekusi:

```bash
uv run python scripts/smoke_test.py http://127.0.0.1:8000
```

Untuk menghentikan dan menghapus container:

```bash
docker rm -f subnet-app
```

## Deploy

Aplikasi dideploy di Vercel pada URL produksi:
- **URL Produksi:** https://subnet-calculator-sqa.vercel.app

### Menjalankan Smoke Test Produksi

Jalankan skrip smoke test untuk memvalidasi deployment di lingkungan produksi:

```bash
uv run python scripts/smoke_test.py https://subnet-calculator-sqa.vercel.app
```


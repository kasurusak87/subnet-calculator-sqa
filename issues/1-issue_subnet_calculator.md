# [Feature] Kalkulator Subnet & VLSM Berbasis Web

## 1. Deskripsi
Mengembangkan aplikasi web Kalkulator Subnet IPv4 dan Variable Length Subnet Mask (VLSM) yang ditujukan untuk mendukung kegiatan pembelajaran guru dan siswa SMK Jurusan Teknik Komputer dan Jaringan (TKJ). Backend dibangun menggunakan Python 3.12 dengan framework FastAPI, dan antarmuka pengguna disajikan dalam satu halaman web interaktif (`index.html`).

Sistem harus menghitung subnet standar secara akurat (termasuk aturan khusus RFC 3021 untuk `/31` dan host route untuk `/32`) serta mengalokasikan subnet menggunakan algoritma VLSM berbasis urutan kebutuhan terbesar ke terkecil (*descending*).

---

## 2. Tugas
1. **Implementasi Logika Inti (`main.py`):**
   - Membuat fungsi `hitung_subnet(ip: str, prefix: int) -> dict` sesuai aturan bitwise, validasi ketat, dan kalkulasi host.
   - Membuat fungsi `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]` dengan algoritma alokasi berurutan dari kebutuhan terbesar.
2. **Implementasi API Endpoint (FastAPI di `main.py`):**
   - `GET /` : Menampilkan halaman antarmuka web `index.html`.
   - `GET /api/subnet` : Endpoint kalkulasi subnet dengan query parameter `ip` dan `prefix`.
   - `POST /api/vlsm` : Endpoint kalkulasi alokasi VLSM dengan payload JSON `{ "network": str, "kebutuhan_host": list[int] }`.
   - Error handling merespons status `HTTP 400 Bad Request` dengan body `{ "detail": "pesan error" }`.
3. **Pengujian Otomatis (`test_main.py`):**
   - Menulis pengujian unit dan integrasi menggunakan `pytest` dan `httpx` yang mencakup 100% kasus uji pada SPEC.md.
4. **Pengembangan Antarmuka Web (`index.html` & styling):**
   - Satu halaman dengan navigasi tab: **Mode Subnet** dan **Mode VLSM**.
   - Input, tombol aksi, visualisasi hasil (tabel & kartu), serta pesan error informatif.

---

## 3. Kriteria Penerimaan
Kriteria penerimaan diverifikasi melalui pengujian otomatis pada `test_main.py` dengan merujuk langsung pada **Tabel Test Case Lengkap di `SPEC.md`**:

| No | Kategori Uji | Skenario Input | Kriteria Hasil yang Diharapkan (Expected Result) |
|---|---|---|---|
| 1 | Subnet Standar | `172.16.5.130/25` | Network: `172.16.5.128`, Broadcast: `172.16.5.255`, Usable Hosts: `126`, Mask: `255.255.255.128` |
| 2 | Subnet Point-to-Point | `10.0.0.0/30` | First Host: `10.0.0.1`, Last Host: `10.0.0.2`, Broadcast: `10.0.0.3`, Usable Hosts: `2` |
| 3 | Subnet RFC 3021 | `192.168.1.0/31` | Usable Hosts: `2`, First Host: `192.168.1.0`, Last Host: `192.168.1.1`, Broadcast: `None` |
| 4 | Subnet Host Route | `192.168.1.5/32` | Usable Hosts: `1`, First Host: `192.168.1.5`, Last Host: `192.168.1.5`, Broadcast: `None` |
| 5 | Invalid IP (Oktet > 255) | `256.1.1.1/24` | Membangkitkan `ValueError` / HTTP 400 Bad Request |
| 6 | Invalid IP (Leading Zero) | `192.168.01.1/24` | Membangkitkan `ValueError` / HTTP 400 Bad Request (ditolak karena angka nol di depan) |
| 7 | Invalid IP (Format Cacat) | `192.168.1`, `abc`, `""` | Membangkitkan `ValueError` / HTTP 400 Bad Request |
| 8 | Invalid Prefix | Prefix `33` atau `-1` | Membangkitkan `ValueError` / HTTP 400 Bad Request (rentang valid 0–32) |
| 9 | VLSM Normal Alokasi | `192.168.1.0/24` & kebutuhan: `[100, 50, 20, 2]` | Alokasi berurutan berhasil:<br>• 100 host $\rightarrow$ `/25` (`192.168.1.0/25`)<br>• 50 host $\rightarrow$ `/26` (`192.168.1.128/26`)<br>• 20 host $\rightarrow$ `/27` (`192.168.1.192/27`)<br>• 2 host $\rightarrow$ `/30` (`192.168.1.224/30`) |
| 10 | VLSM Kapasitas Kurang | `192.168.1.0/24` & kebutuhan: `[200, 100]` | Membangkitkan `ValueError` / HTTP 400 Bad Request (blok subnet tidak cukup menampung kebutuhan) |

---

## 4. Alur Kerja (Workflow)
Pelaksanaan tugas wajib mengikuti siklus kerja terstruktur:
```text
issue -> branch -> test dulu -> implementasi -> commit -> pull request -> CI -> merge
```

1. **Issue:** Dibuat dan didokumentasikan di GitHub Issues.
2. **Branch:** Buat feature branch baru dari `main` dengan format `feature/issue-<nomor>-subnet-calculator`.
3. **Test Dulu (TDD):** Tulis rangkaian pengujian pada `test_main.py` berdasarkan matriks kasus uji SPEC.md sebelum atau bersamaan dengan kode fitur.
4. **Implementasi:** Tulis kode implementasi pada `main.py` dan antarmuka pada `index.html` hingga seluruh pengujian lulus (*green*).
5. **Commit:** Buat commit berkala dengan konvensi *Conventional Commits* yang jelas.
6. **Pull Request:** Ajukan PR ke branch `main` dengan mencantumkan tautan ke issue terkait (`Fixes #<nomor>`).
7. **CI:** Jalankan pipeline pengujian otomatis untuk memverifikasi lint, pytest, dan coverage.
8. **Merge:** Penggabungan kode ke branch utama (`main`) setelah seluruh check CI sukses.

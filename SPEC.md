# Spesifikasi Teknis: Kalkulator Subnet & VLSM Berbasis Web (SPEC.md)

---

## 1. Tujuan
Dokumen ini menetapkan spesifikasi teknis untuk pengembangan **Kalkulator Subnet & VLSM Berbasis Web** yang ditujukan bagi guru dan siswa SMK Program Keahlian Teknik Komputer dan Jaringan (TKJ). Aplikasi ini dirancang untuk melakukan perhitungan subnetting standar IPv4 serta alokasi Variable Length Subnet Mask (VLSM) secara akurat, konsisten, dan mudah diverifikasi berdasarkan standar rekayasa perangkat lunak dan protokol jaringan (termasuk RFC 3021).

---

## 2. Aturan Validasi
Validasi input dilakukan secara ketat sebelum proses perhitungan atau alokasi dijalankan untuk mencegah kesalahan data:

*   **Validasi Alamat IPv4 (`ip`):**
    *   Harus terdiri dari tepat 4 oktet yang dipisahkan oleh titik (`.`).
    *   Setiap oktet berupa bilangan bulat dengan rentang nilai $0$ s.d. $255$.
    *   **Tidak boleh memiliki angka nol di depan (*leading zeros*)** untuk setiap oktet (contoh: `192.168.01.1` atau `10.0.0.01` harus ditolak).
    *   Tidak boleh mengandung spasi atau karakter whitespace lainnya.
    *   Format string kosong, teks non-angka, atau oktet kurang/lebih dari 4 akan langsung memicu error.
*   **Validasi Prefix (`prefix`):**
    *   Harus berupa bilangan bulat (*integer*) dengan rentang nilai inklusif $0$ s.d. $32$.
*   **Penanganan Error:**
    *   Apabila ditemukan input yang tidak valid pada fungsi inti, modul wajib membangkitkan eksepsi `ValueError`.
    *   Pada lapisan API/Backend, kegagalan validasi atau kesalahan input akan merespons klien dengan status HTTP `400 Bad Request` serta menyertakan field JSON `"detail"` yang menjelaskan alasan kesalahan.

---

## 3. Kontrak Fungsi (`main.py`)

Backend menggunakan **Python 3.12** dengan modul inti di dalam `main.py` yang menyediakan dua fungsi utama:

### A. `hitung_subnet(ip: str, prefix: int) -> dict`
*   **Parameter:**
    *   `ip` (str): Alamat IPv4 (contoh: `"172.16.5.130"`).
    *   `prefix` (int): Nilai prefix CIDR (0 s.d. 32).
*   **Nilai Kembalian (`dict`):**
    Kamus dengan kunci yang distandarisasi:
    *   `mask` (str): Subnet mask dalam format desimal bertitik (contoh: `"255.255.255.128"`).
    *   `network` (str): Alamat jaringan hasil operasi bitwise `IP AND Subnet Mask`.
    *   `broadcast` (str | None): Alamat broadcast jaringan (bernilai `None` untuk prefix `/31` dan `/32`).
    *   `first_host` (str): Alamat host pertama yang dapat digunakan.
    *   `last_host` (str): Alamat host terakhir yang dapat digunakan.
    *   `usable_hosts` (int): Jumlah host efektif yang dapat digunakan.
*   **Aturan Khusus Perhitungan:**
    *   **Prefix 0–30:** Jumlah host efektif dihitung dengan rumus $2^{(32 - \text{prefix})} - 2$.
    *   **Prefix /31 (RFC 3021 - Point-to-Point):** Menggunakan aturan khusus 2 host efektif, di mana alamat network dan broadcast diperlakukan sebagai host usable, sehingga `broadcast = None`.
    *   **Prefix /32 (Host Route):** Menghasilkan 1 host tunggal di mana `broadcast = None`, serta `first_host = last_host = IP` (setelah disesuaikan ke base IP).

### B. `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]`
*   **Parameter:**
    *   `network_cidr` (str): Alamat jaringan induk dalam notasi CIDR (contoh: `"192.168.1.0/24"`).
    *   `kebutuhan_host` (list[int]): Daftar integer yang merepresentasikan jumlah host yang dibutuhkan untuk setiap subnet.
*   **Aturan Proses:**
    1.  Validasi bahwa `network_cidr` adalah alamat jaringan yang valid dan daftar `kebutuhan_host` tidak kosong serta seluruh nilainya $\ge 1$. Jika tidak valid, *raise* `ValueError`.
    2.  Urutkan `kebutuhan_host` dari nilai terbesar ke terkecil (*descending*).
    3.  Tentukan ukuran blok subnet terdekat berdasarkan pangkat 2 terkecil yang memenuhi syarat $\text{kebutuhan} + 2$ (dengan ukuran blok minimal setara prefix `/30`, yaitu 4 alamat IP).
    4.  Alokasikan blok subnet secara berurutan mulai dari alamat network induk.
    5.  Periksa apakah kapasitas subnet induk mencukupi seluruh daftar kebutuhan. Jika kapasitas habis / tidak muat, *raise* `ValueError`.
*   **Nilai Kembalian:**
    List berisi kamus (*dictionary*) yang masing-masing memuat: `kebutuhan`, `network_cidr`, beserta seluruh kunci hasil dari fungsi `hitung_subnet`.

---

## 4. Kontrak API (FastAPI)

Endpoint backend didesain menggunakan FastAPI dengan spesifikasi sebagai berikut:

1.  **`GET /`**
    *   **Deskripsi:** Mengembalikan halaman antarmuka pengguna statis/dinamis berbasis web (`index.html`).
2.  **`GET /api/subnet`**
    *   **Query Parameters:** `ip` (string), `prefix` (integer).
    *   **Respon Sukses (200 OK):** Objek JSON yang berisi hasil dari pemanggilan fungsi `hitung_subnet`.
    *   **Respon Gagal (400 Bad Request):** `{ "detail": "Pesan error deskriptif" }` jika parameter tidak valid.
3.  **`POST /api/vlsm`**
    *   **Request Body (JSON):**
        ```json
        {
          "network": "192.168.1.0/24",
          "kebutuhan_host": [100, 50, 20, 2]
        }
        ```
    *   **Respon Sukses (200 OK):** Daftar JSON (*array of objects*) hasil dari pemanggilan fungsi `alokasi_vlsm`.
    *   **Respon Gagal (400 Bad Request):** `{ "detail": "Pesan error deskriptif" }` jika kapasitas tidak cukup atau format input salah.

---

## 5. Halaman Web (`index.html`)

Antarmuka pengguna terdiri dari satu halaman web tunggal yang mengusung prinsip desain responsif dan ramah pengguna di laboratorium sekolah:
*   **Navigasi Mode:** Menyediakan tombol atau tab untuk beralih secara instan antara **Mode Subnet Kalkulator** dan **Mode VLSM Kalkulator**.
*   **Mode Subnet:** Menyediakan input teks untuk IPv4 dan angka untuk Prefix, tombol hitung, serta area penayangan tabel hasil yang bersih (Network, Mask, Broadcast, Range Host, Usable Hosts).
*   **Mode VLSM:** Menyediakan input untuk Network Induk (CIDR) dan daftar kebutuhan host (bisa dipisahkan dengan koma atau tombol tambah baris), tombol alokasi, serta tabel ringkasan alokasi per blok subnet.
*   **Penanganan Pesan Error:** Apabila terjadi kesalahan input atau respons `400` dari backend, antarmuka menampilkan pesan peringatan visual yang jelas, spesifik, dan mudah dibaca oleh siswa.

---

## 6. Tabel Test Case Lengkap (`test_main.py`)

Berikut adalah matriks kasus uji resmi yang wajib diimplementasikan di dalam `test_main.py` menggunakan kerangka kerja `pytest`:

| No | Kategori Uji | Input / Skenario | Hasil yang Diharapkan (Expected Result) | Status / Jenis Kasus |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Subnet Standar | `172.16.5.130 /25` | Network: `172.16.5.128`<br>Broadcast: `172.16.5.255`<br>Usable Hosts: 126 | Pasti (Sesuai tabel dasar) |
| 2 | Subnet Point-to-Point | `10.0.0.0 /30` | Host range: `.1` s.d. `.2`<br>Broadcast: `.3`<br>Usable Hosts: 2 | Pasti (Sesuai tabel dasar) |
| 3 | Subnet RFC 3021 | `192.168.1.0 /31` | 2 host usable, Broadcast = `None` | Pasti (Aturan RFC 3021) |
| 4 | Subnet Host Route | `192.168.1.5 /32` | 1 host, First = Last = `192.168.1.5`, Broadcast = `None` | Pasti (Aturan /32) |
| 5 | Edge Case: Invalid IP Format 1 | `256.1.1.1 /24` | Menghasilkan eksepsi `ValueError` / HTTP 400 | Pasti (Oktet > 255) |
| 6 | Edge Case: Leading Zero | `192.168.01.1 /24` | Menghasilkan eksepsi `ValueError` / HTTP 400 | Pasti (Angka nol di depan) |
| 7 | Edge Case: Format Salah | `192.168.1` / `abc` / string kosong | Menghasilkan eksepsi `ValueError` / HTTP 400 | Pasti (Format tidak lengkap) |
| 8 | Edge Case: Invalid Prefix | Prefix `33` atau `-1` | Menghasilkan eksepsi `ValueError` / HTTP 400 | Pasti (Diluar rentang 0-32) |
| 9 | VLSM Normal Alokasi | `192.168.1.0/24`<br>Kebutuhan: `100, 50, 20, 2` | Berhasil dialokasikan berurutan:<br>• 100 host $\rightarrow$ `/25` (net: `.0`)<br>• 50 host $\rightarrow$ `/26` (net: `.128`)<br>• 20 host $\rightarrow$ `/27` (net: `.192`)<br>• 2 host $\rightarrow$ `/30` (net: `.224`) | Pasti (Sesuai tabel acuan) |
| 10 | VLSM Kapasitas Kurang | `192.168.1.0/24`<br>Kebutuhan: `200` dan `100` | Menghasilkan eksepsi `ValueError` / HTTP 400 (Total kebutuhan melebihi kapasitas parent `/24`) | Pasti (Kapasitas tidak muat) |

---

## 7. Di Luar Cakupan (*Out of Scope*)
Fitur-fitur berikut tidak termasuk dalam cakupan versi spesifikasi ini:
*   Dukungan penuh pengalamatan IPv6.
*   Integrasi basis data eksternal (penyimpanan riwayat perhitungan secara persisten ke database SQL/NoSQL).
*   Sistem autentikasi dan manajemen akun pengguna (login guru/siswa).
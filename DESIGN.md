# Desain Antarmuka Pengguna: Kalkulator Subnet & VLSM (DESIGN.md)

---

## 1. Ikhtisar Desain
Antarmuka pengguna didesain sebagai **Single Page Application (SPA)** yang modern, bersih, dan intuitif. Desain ini dioptimalkan untuk kebutuhan praktikum jaringan di laboratorium sekolah (SMK TKJ) agar siswa dapat memahami konsep pembagian alamat IP, mask biner, dan alokasi VLSM secara visual.

Aplikasi menyediakan dua mode utama yang dapat dialihkan secara instan melalui sistem tab:
1. **Mode Subnet Kalkulator:** Menghitung parameter subnet standar IPv4 (mask, network, broadcast, host range, usable host, dan representasi biner).
2. **Mode VLSM Kalkulator:** Mengalokasikan blok-blok subnet dengan ukuran variabel secara dinamis berdasarkan urutan kebutuhan host dari yang terbesar ke terkecil.

---

## 2. Struktur Tata Letak (Layout & Wireframe)

```
+-------------------------------------------------------------+
|                      [Logo] Subnet & VLSM Calculator        |
|                      IPv4 Engineering & Education Tool       |
+-------------------------------------------------------------+
|  [ Tab: Kalkulator Subnet ]    |    [ Tab: Alokasi VLSM ]   |
+-------------------------------------------------------------+
|                                                             |
|  [ CARD INPUT ]                                             |
|  - Subnet Mode: [IP Input] / [Prefix Input] [Tombol Hitung] |
|  - VLSM Mode:   [Network CIDR] [Kebutuhan Host] [Alokasi]   |
|  - Pesan Error Visual (jika ada kesalahan)                  |
|                                                             |
+-------------------------------------------------------------+
|                                                             |
|  [ CARD HASIL ]                                             |
|  - Ringkasan Metrik (Grid 4 Kartu Kunci)                    |
|    * Network Address                                        |
|    * Broadcast Address                                      |
|    * Range Host Usable                                      |
|    * Jumlah Host Usable                                     |
|                                                             |
|  - Tabel Rincian Lengkap / Tabel Alokasi VLSM               |
|                                                             |
|  - Representasi Biner Titik-Titik (Mode Subnet)             |
|                                                             |
+-------------------------------------------------------------+
```

---

## 3. Komponen Antarmuka

### A. Header & Navigasi Tab
*   **Header:** Logo ikonik jaringan dengan judul "Subnet & VLSM Calculator" dan subjudul penjelasan.
*   **Tab Switcher:** Tombol tab segmented pill (`Kalkulator Subnet` vs `Alokasi VLSM`) dengan indikator status aktif berupa warna latar kontras dan bayangan lembut.

### B. Panel Input
1.  **Mode Subnet:**
    *   *Field IP:* Input teks dengan placeholder `192.168.1.0`, divalidasi ketat (tanpa *leading zero*, rentang oktet 0-255).
    *   *Field Prefix:* Input angka dengan awalan visual garis miring (`/`), rentang nilai $0$ hingga $32$.
    *   *Action Button:* Tombol "Hitung Subnet" dengan efek hover dan transisi halus.
2.  **Mode VLSM:**
    *   *Field Induk Jaringan:* Input teks dengan placeholder `192.168.1.0/24`.
    *   *Field Kebutuhan Host:* Input fleksibel (angka dipisahkan koma, contoh: `100, 50, 20, 2`) dilengkapi petunjuk otomatis pengurutan kebutuhan dari terbesar.
    *   *Action Button:* Tombol "Alokasikan VLSM".

### C. Komponen Penanganan Kesalahan (Error Banner)
*   Komponen banner peringatan visual dengan warna latar merah muda lembut (`#fee2e2`), batas merah tegas (`#ef4444`), dan ikon peringatan (`⚠`).
*   Menampilkan pesan error spesifik dari backend (misalnya: `"Oktet kedua tidak boleh memiliki leading zero: '01'"` atau `"Kapasitas blok subnet tidak cukup"`).

### D. Panel Hasil
1.  **Mode Subnet:**
    *   **Kartu Metrik (Summary Cards):** 4 blok ringkasan berlatar warna tematik untuk *Network*, *Broadcast*, *Range Host*, dan *Usable Hosts*.
    *   **Tabel Detail:** Menampilkan subnet mask, wildcard mask, kelas IP, serta jenis alamat (Private RFC 1918 / Public / Loopback).
    *   **Visualisasi Biner:** Membandingkan format biner IP, subnet mask, network, dan broadcast untuk mempermudah pemahaman operasi bitwise AND.
2.  **Mode VLSM:**
    *   **Tabel Alokasi Subnet:** Menampilkan baris untuk setiap subnet yang berhasil dialokasikan:
        *   Nama / Subnet #
        *   Kebutuhan Host
        *   Alokasi CIDR (misal `/25`)
        *   Network Address
        *   Subnet Mask
        *   Usable Host Range (First – Last)
        *   Broadcast Address
        *   Sisa Kapasitas Ruang IP

---

## 4. Sistem Desain Visual (Design System)

### A. Palet Warna (Color Palette)
| Token | Nilai Hex | Penggunaan |
|---|---|---|
| `--bg-body` | `#f8fafc` (Slate 50) | Latar belakang halaman |
| `--surface` | `#ffffff` | Latar kartu komponen |
| `--border` | `#e2e8f0` (Slate 200) | Garis pemisah dan border |
| `--primary` | `#4f46e5` (Indigo 600) | Warna aksen utama, tombol, tab aktif |
| `--primary-hover` | `#4338ca` (Indigo 700) | Status hover tombol |
| `--text-main` | `#0f172a` (Slate 900) | Tipografi teks utama |
| `--text-muted` | `#64748b` (Slate 500) | Label, teks sekunder, hint |
| `--success` | `#10b981` (Emerald 500) | Indikator host & status valid |
| `--warning` | `#f59e0b` (Amber 500) | Indikator kapasitas |
| `--danger` | `#ef4444` (Red 500) | Pesan error dan input tidak valid |

### B. Tipografi
*   **Font Antarmuka:** `'Plus Jakarta Sans'`, `'Segoe UI'`, system-ui, sans-serif (mudah dibaca dan ramah pengguna).
*   **Font Nilai Jaringan & Biner:** `'Cascadia Code'`, `'Fira Code'`, monospace (memastikan perataan karakter presisi pada alamat IP dan biner 32-bit).

### C. Responsivitas
*   **Desktop (> 768px):** Grid 4 kolom untuk kartu metrik, tata letak input berdampingan.
*   **Tablet & Mobile (< 768px):** Grid 2 kolom atau 1 kolom adaptif, tabel dilengkapi *overflow-x scroll* agar data subnet tetap terbaca utuh tanpa terpotong.

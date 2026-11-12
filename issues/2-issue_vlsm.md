# [Feature] Alokasi Variable Length Subnet Mask (VLSM)

## 1. Deskripsi
Mengembangkan fitur alokasi subnetting dinamis berbasis Variable Length Subnet Mask (VLSM) untuk Kalkulator Subnet & VLSM Berbasis Web. Fitur ini memungkinkan pengguna (guru dan siswa SMK TKJ) membagi satu alamat jaringan induk (*parent network CIDR*) menjadi subnet-subnet dengan ukuran yang bervariasi sesuai dengan kebutuhan spesifik tiap segmen jaringan secara efisien dan optimal.

---

## 2. Tugas
1. **Implementasi Fungsi Inti (`main.py`):**
   - Membuat fungsi `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]`.
   - Melakukan validasi `network_cidr`: harus merupakan alamat jaringan yang valid (IP bertepatan dengan network address blok tersebut).
   - Melakukan validasi `kebutuhan_host`: tidak boleh kosong dan seluruh nilainya berupa integer $\ge 1$.
   - Mengurutkan daftar kebutuhan secara menurun (*descending*).
   - Menghitung ukuran blok minimum: pangkat 2 terkecil yang memenuhi $\ge \text{kebutuhan} + 2$ (minimal blok /30 atau 4 IP).
   - Mengalokasikan blok subnet berurutan dari alamat network induk.
   - Memvalidasi batas kapasitas subnet induk; bangkitkan `ValueError` jika kapasitas tidak mencukupi.
2. **Implementasi API Endpoint (`main.py`):**
   - `POST /api/vlsm`: Menerima payload JSON `{ "network": str, "kebutuhan_host": list[int] }`.
   - Mengembalikan HTTP 200 dengan daftar blok subnet hasil alokasi.
   - Mengembalikan HTTP 400 Bad Request dengan format `{ "detail": "pesan error" }` jika input tidak valid atau kapasitas tidak cukup.
3. **Pengujian Otomatis (`test_main.py`):**
   - Menambahkan pengujian unit dan integrasi untuk kasus sukses dan kasus gagal (kapasitas kurang, format salah, dsb) sesuai SPEC.md.
4. **Integrasi Antarmuka Web (`index.html` & `subnet.js`):**
   - Menghubungkan form input tab VLSM ke endpoint `POST /api/vlsm`.
   - Menampilkan tabel rincian alokasi per subnet dan menampilkan pesan error dari field `detail` pada banner peringatan.

---

## 3. Kriteria Penerimaan
Berdasarkan Matriks Kasus Uji pada `SPEC.md`:

| No | Kategori Uji | Skenario Input | Kriteria Hasil yang Diharapkan |
|---|---|---|---|
| 1 | VLSM Alokasi Normal | `192.168.1.0/24`<br>Kebutuhan: `[100, 50, 20, 2]` | Berhasil dialokasikan berurutan:<br>• 100 host $\rightarrow$ `/25` (`192.168.1.0/25`)<br>• 50 host $\rightarrow$ `/26` (`192.168.1.128/26`)<br>• 20 host $\rightarrow$ `/27` (`192.168.1.192/27`)<br>• 2 host $\rightarrow$ `/30` (`192.168.1.224/30`) |
| 2 | VLSM Kapasitas Kurang | `192.168.1.0/24`<br>Kebutuhan: `[200, 100]` | `ValueError` / HTTP 400 Bad Request (total kebutuhan melebihi kapasitas induk /24) |
| 3 | Network CIDR Bukan Network Address | `192.168.1.5/24`<br>Kebutuhan: `[10, 5]` | `ValueError` / HTTP 400 Bad Request (`.5` bukan network address dari `/24`) |
| 4 | Daftar Kebutuhan Kosong | `192.168.1.0/24`<br>Kebutuhan: `[]` | `ValueError` / HTTP 400 Bad Request |
| 5 | Kebutuhan Host Tidak Valid | `192.168.1.0/24`<br>Kebutuhan: `[10, 0]` atau `[-5]` | `ValueError` / HTTP 400 Bad Request (nilai kebutuhan harus $\ge 1$) |

---

## 4. Alur Kerja (Workflow)
```text
issue -> branch -> test dulu -> implementasi -> commit -> pull request -> CI -> merge
```

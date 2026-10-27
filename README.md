# KasirFIFO - Sistem Point of Sale (POS) Berbasis Logika FIFO

Aplikasi kasir Command Line Interface (CLI) berbasis Python yang dirancang untuk usaha retail mikro. Sistem ini mencatat setiap barang masuk sebagai *batch* tersendiri dan menghitung Harga Pokok Penjualan (HPP) menggunakan metode *First-In, First-Out* (FIFO) untuk menghasilkan laporan laba kotor.

## 👥 Tim Pengembang
* **Prima Aditama** - Modul Inventaris & Database JSON (`inventory.py`)
* **Bachtiar Arief N** - Engine HPP Metode FIFO (`cogs.py`)
* **Andra Putra P** - Modul Kasir & Transaksi (`pos.py`)
* **Wisam Ikbar D** - Integrasi CLI, Struk & Unit Test (`main.py`, `report.py`)

---

## 📖 Cara Menjalankan Program (How It Works)

Pastikan Python sudah terinstal di komputermu. Buka terminal (CMD / Git Bash / Terminal VS Code) di folder utama proyek, lalu jalankan perintah:

python main.py

### Langkah 1: Restock Barang (Menu 2)
Karena gudang masih kosong, hal pertama yang harus dilakukan adalah memasukkan barang.
1. Pada Menu Utama, pilih **`2`** (Restock).
2. Masukkan ID Produk baru (contoh: `P001`). Karena belum ada, sistem akan meminta kamu memasukkan **Nama Produk** (contoh: `Kopi Susu`) dan **Harga Jual** (contoh: `15000`).
3. Selanjutnya, masukkan **Jumlah Stok Masuk** (contoh: `10`) dan **Harga Beli Satuan** dari supplier (contoh: `6000`).
4. Sistem akan menyimpan data ini ke dalam *Batch 1* dan otomatis menyimpannya ke database JSON.

### Langkah 2: Cek Stok (Menu 3)
Untuk memastikan barang sudah masuk:
1. Pilih **`3`** (Lihat Stok & Batch).
2. Layar akan menampilkan tabel produk beserta sisa stok saat ini. Pastikan Kopi Susu berjumlah 10.

### Langkah 3: Transaksi Kasir (Menu 1)
Simulasi pelanggan membeli barang.
1. Pilih **`1`** (Kasir).
2. Masukkan ID Produk (`P001`) dan Jumlah yang dibeli (contoh: `2`).
3. Ketik `0` untuk menyelesaikan input keranjang.
4. Sistem akan menampilkan **Total Belanja** (2 x Rp 15.000 = Rp 30.000).
5. Masukkan nominal **Uang Bayar** (contoh: `50000`).
6. **Di balik layar:** Mesin HPP FIFO (First-In, First-Out) bekerja dengan mengambil modal dari *Batch 1* (2 x Rp 6.000 = Rp 12.000). Stok Kopi Susu otomatis berkurang menjadi 8.
7. Struk belanja akan tercetak di layar beserta uang kembalian (Rp 20.000), dan transaksi disimpan ke dalam riwayat laporan.

### Langkah 4: Laporan Laba/Rugi (Menu 4)
Untuk melihat performa toko:
1. Pilih **`4`** (Laporan Laba/Rugi).
2. Sistem akan merekap seluruh transaksi yang terjadi di sesi tersebut:
   * **Total Omzet:** Rp 30.000
   * **Total Laba Kotor:** Rp 18.000 (didapat dari Omzet Rp 30.000 dikurangi Modal HPP Rp 12.000).

### Langkah 5: Keluar Aplikasi (Menu 5)
1. Pilih **`5`** untuk mengakhiri program.
2. Seluruh data inventaris dan sisa stok yang terakhir sudah tersimpan aman di file `database_inventory.json`. Saat kamu membuka `main.py` lagi besok, datanya tidak akan hilang.
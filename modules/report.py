
class Receipt:                                                                          # Class untuk mengurus format dan cetak struk belanja
    def __init__(self, transaction):                                                    # Constructor: dipanggil saat struk baru dibuat
        self.transaction = transaction                                                  # Simpan objek transaksi (dari pos.py) ke dalam class ini

    def format_receipt(self):                                                           # Fungsi untuk merangkai teks struk
        lines = []                                                                      # Siapkan list kosong untuk menampung setiap baris teks
        lines.append("\n" + "="*40)                                                     # Tambahkan garis atas (40 karakter '=')
        lines.append("          KASIR FIFO MART          ".center(40))                  # Teks judul di tengah (total 40 karakter)
        lines.append("="*40)                                                            # Tambahkan garis bawah judul
        
        # Header tabel
        lines.append(f"{'Barang':<15} | {'Qty':>5} | {'Subtotal':>12}")                 # Format header: Barang (kiri), Qty (kanan), Subtotal (kanan)
        lines.append("-" * 40)                                                          # Garis pemisah tabel
        
        # Isi tabel
        for item in self.transaction.items:                                             # Looping setiap barang yang ada di keranjang transaksi
            nama = item.product.name[:15]                                               # Ambil nama produk, potong max 15 huruf agar tabel rapi
            lines.append(f"{nama:<15} | {item.qty:>5} | {item.subtotal():>12,.0f}")     # Masukkan data barang & subtotal ke baris teks
            
        lines.append("-" * 40)                                                          # Garis pemisah bawah tabel
        
        # Ringkasan
        total_belanja = self.transaction.total_sales()                                  # Ambil total tagihan akhir (setelah diskon) dari transaksi
        diskon = self.transaction.discount                                              # Ambil nominal diskon
        uang_bayar = self.transaction.paid_amount                                       # Ambil nominal uang yang dibayarkan pelanggan
        kembalian = self.transaction.change_due()                                       # Ambil nominal uang kembalian
        
        # f-string padding (rata kanan)
        lines.append(f"{'Total Belanja:':<25} Rp {total_belanja:>10,.0f}")              # Cetak total belanja
        if diskon > 0:                                                                  # Cek apakah ada diskon?
            lines.append(f"{'Diskon:':<25} Rp {diskon:>10,.0f}")                        # Jika ada, cetak nominal diskonnya
        lines.append(f"{'Uang Bayar:':<25} Rp {uang_bayar:>10,.0f}")                    # Cetak nominal uang yang dibayarkan
        lines.append(f"{'Kembalian:':<25} Rp {kembalian:>10,.0f}")                      # Cetak nominal uang kembalian
        
        lines.append("="*40)                                                            # Garis penutup struk
        lines.append("    Terima Kasih Sudah Berbelanja!    ".center(40))               # Pesan penutup di tengah
        lines.append("="*40 + "\n")                                                     # Garis penutup akhir
        
        return "\n".join(lines)                                                         # Gabungkan semua baris teks menjadi satu string panjang

    def print_receipt(self):                                                            # Fungsi untuk mencetak struk ke layar terminal
        print(self.format_receipt())                                                    # Panggil fungsi format_receipt() lalu tampilkan hasilnya


class Report:
    def __init__(self):                                                                 # Constructor: dipanggil saat Report baru dibuat
        self.history = []                                                               # List untuk menyimpan transaksi

    def add_transaction(self, transaction):                                             # Fungsi untuk menyimpan transaksi
        self.history.append(transaction)                                                # Masukkan objek transaksi ke dalam list riwayat

    def total_revenue(self):                                                            # Fungsi untuk menghitung total omzet
        return sum(t.total_sales() for t in self.history)                               # Hitung total omzet

    def total_profit(self):                                                             # Fungsi untuk menghitung total laba kotor
        return sum(t.gross_profit() for t in self.history)                              # Hitung total laba kotor

    def print_report(self):                                                             # Fungsi untuk mencetak laporan
        print("\n" + "="*40)                                                            # Garis awal laporan
        print("        LAPORAN LABA/RUGI HARI INI       ".center(40))                   # Judul laporan
        print("="*40)                                                                   # Garis bawah judul
        
        if not self.history:                                                            # Jika list history masih kosong (belum ada transaksi)
            print("Belum ada transaksi hari ini.")                                      # Pesan jika tidak ada transaksi
            return                                                                      # Hentikan fungsi (jangan print angka 0)
            
        print(f"Total Transaksi : {len(self.history)} kali")                            # Jumlah transaksi
        print(f"Total Omzet     : Rp {self.total_revenue():,.2f}")                      # Total omzet
        print(f"Total Laba Kotor: Rp {self.total_profit():,.2f}")                       # Total laba kotor
        print("="*40 + "\n")

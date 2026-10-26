
import sys                                                                      # Modul bawaan Python yang berfungsi untuk keluar dari program (exit)     
from modules.inventory import Inventory, proses_restock                         # Impor class gudang dan fungsi restock milik Prima
from modules.pos import proses_kasir                                            # Impor fungsi kasir milik Andra
from modules.report import Receipt, Report                                      # Impor class struk dan laporan milik Wisam

class KasirApp:                                                                 # Class utama yang merangkai semua modul menjadi satu aplikasi
    def __init__(self):                                                         # Constructor: dijalankan pertama kali aplikasi dibuat
        self.inventory = Inventory()                                            # Buat objek gudang (inventory) baru
        self.inventory.load_data()                                              # <--- 1. Muat data dari file JSON saat aplikasi pertama kali dibuka
        self.report = Report()                                                  # Buat objek laporan baru (riwayat transaksi masih kosong)

    def validate_choice(self, choice_input):                                    # Fungsi untuk memvalidasi input menu dari user
        if not choice_input.isdigit():                                          # Cek apakah input BUKAN angka (misal user ketik huruf 'a')
            return False                                                        # Jika bukan angka, kembalikan False (tidak valid)
        return 1 <= int(choice_input) <= 5                                      # Jika angka, cek apakah berada di rentang 1 sampai 5

    def main_menu(self):                                                        # Fungsi utama untuk menampilkan menu dan menerima pilihan
        while True:                                                             # Loop selamanya (infinity) sampai user memilih menu 5 (Keluar)
            print("\n" + "="*40)                                                # Cetak garis atas (40 karakter '=')
            print("       APLIKASI KASIRFIFO (CLI)       ".center(40))          # Cetak judul aplikasi di tengah-tengah
            print("="*40)                                                       # Cetak garis bawah judul
            print("1. Kasir (Transaksi Penjualan)")                             # Tampilkan menu 1
            print("2. Restock (Tambah Stok Batch)")                             # Tampilkan menu 2
            print("3. Lihat Stok & Batch")                                      # Tampilkan menu 3
            print("4. Laporan Laba/Rugi")                                       # Tampilkan menu 4
            print("5. Keluar")                                                  # Tampilkan menu 5
            print("="*40)                                                       # Cetak garis bawah menu
            
            pilihan = input("Pilih Menu (1-5): ").strip()                       # Minta input dari user dan hapus spasi di awal/akhir
            
            # Validasi input menu
            if not self.validate_choice(pilihan):                               # Cek apakah input tidak valid
                print("❌ Pilihan tidak valid! Masukkan angka 1 sampai 5.")     # Tampilkan pesan error
                continue                                                        # Ulangi loop (kembali ke atas)
                
            pilihan = int(pilihan)                                              # Ubah input string menjadi integer (angka)

            if pilihan == 1:
                # Panggil fungsi kasir
                transaksi_selesai = proses_kasir(self.inventory)               # Lempar data gudang ke Andra, tunggu sampai transaksi selesai
                
                # Jika transaksi tidak batal, cetak struk & simpan laporan
                if transaksi_selesai:                                          # Cek apakah transaksi tidak dibatalkan
                    struk = Receipt(transaksi_selesai)                         # Buat struk dari transaksi yang selesai
                    struk.print_receipt()                                      # Cetak struk
                    self.report.add_transaction(transaksi_selesai)             # Simpan nota ke dalam riwayat laporan
                    self.inventory.save_data()                                 # <--- 2. SIMPAN DATA SETELAH TRANSAKSI (KARENA STOK BERKURANG)
                    
            elif pilihan == 2:                                                 # Jika user memilih menu 2 (Restock) 
                # Panggil fungsi restock
                proses_restock(self.inventory)                                 # (Simpan otomatis sudah dihandle di dalam fungsi ini)
                
            elif pilihan == 3:                                                 # Jika user memilih menu 3 (Lihat Stok) 
                # Panggil fungsi lihat stok
                self.inventory.list_products()                                 # Tampilkan semua stok barang yang ada
                
            elif pilihan == 4:                                                 # Jika user memilih menu 4 (Laporan) 
                # Panggil fungsi laporan
                self.report.print_report()                                     # Tampilkan laporan
                
            elif pilihan == 5:                                                 # Jika user memilih menu 5 (Keluar) 
                print("\nTerima kasih! Program selesai.")                      # Tampilkan pesan terima kasih
                sys.exit(0)                                                    # Keluar dari program

# --- TITIK MASUK PROGRAM ---
if __name__ == "__main__":                                                     # Memastikan kode di bawah hanya jalan jika file ini dieksekusi langsung
    app = KasirApp()                                                           # Buat objek aplikasi utama
    app.main_menu()                                                            # Jalankan fungsi menu utama

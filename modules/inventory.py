import json                                                             # Modul untuk menyimpan dan membaca data berformat JSON
import os                                                               # Modul untuk mengecek keberadaan file di komputer
from datetime import datetime                                           # Modul untuk mengambil waktu/tanggal saat ini


class Batch:                                                            # Class untuk menyimpan riwayat satu kali kulakan
    def __init__(self, purchase_price, qty, arrival_date=None):         # Constructor: dipanggil saat batch baru dibuat
        self.purchase_price = float(purchase_price)                     # Harga beli modal per unit (ubah ke desimal/float)
        self.qty = int(qty)                                             # Jumlah stok yang masuk (ubah ke bilangan bulat)
        self.arrival_date = arrival_date if arrival_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Set tanggal otomatis jika kosong

    def to_dict(self):                                                  # Fungsi untuk mengubah objek Batch menjadi Dictionary
        return {                                                        # (Dictionary ini nanti yang disimpan ke file JSON)
            "purchase_price": self.purchase_price,                      # Simpan harga beli
            "qty": self.qty,                                            # Simpan jumlah stok
            "arrival_date": self.arrival_date                           # Simpan tanggal masuk
        }

    @classmethod                                                        # Decorator: fungsi ini milik Class, bukan objek
    def from_dict(cls, data):                                           # Fungsi untuk mengubah Dictionary kembali menjadi objek Batch
        return cls(                                                     # (Dipakai saat membaca file JSON)
            purchase_price=data["purchase_price"],                      # Ambil harga beli dari data
            qty=data["qty"],                                            # Ambil jumlah stok dari data
            arrival_date=data.get("arrival_date")                       # Ambil tanggal dari data
        )


class Product:                                                          # Class untuk menyimpan data master barang
    def __init__(self, id, name, selling_price):                        # Constructor: dipanggil saat produk baru didaftarkan
        self.id = str(id)                                               # ID produk (pastikan formatnya teks/string)
        self.name = str(name)                                           # Nama produk (teks)
        self.selling_price = float(selling_price)                       # Harga jual ke pelanggan (desimal/float)
        self.batches = []                                               # List kosong untuk menampung riwayat batch (antrean FIFO)

    def add_batch(self, purchase_price, qty):                           # Fungsi untuk menambah stok (batch baru)
        batch = Batch(purchase_price, qty)                              # Buat objek Batch baru
        self.batches.append(batch)                                      # Masukkan batch baru tersebut ke list paling belakang (antrean)

    def total_stock(self):                                              # Fungsi untuk menghitung total stok yang ada
        return sum(batch.qty for batch in self.batches)                 # Jumlahkan semua sisa qty dari setiap batch

    def to_dict(self):                                                  # Fungsi untuk mengubah objek Product menjadi Dictionary
        return {                                                        # (Untuk keperluan simpan ke JSON)
            "id": self.id,                                              # Simpan ID
            "name": self.name,                                          # Simpan Nama
            "selling_price": self.selling_price,                        # Simpan Harga Jual
            "batches": [batch.to_dict() for batch in self.batches]      # Looping semua batch dan ubah masing-masing ke Dictionary
        }

    @classmethod                                                        # Decorator: fungsi milik Class
    def from_dict(cls, data):                                           # Fungsi untuk mengubah Dictionary menjadi objek Product
        product = cls(                                                  # Buat objek Product baru dari data Dictionary
            id=data["id"],
            name=data["name"],
            selling_price=data["selling_price"]
        )
        for b_data in data.get("batches", []):                          # Looping setiap data batch di dalam JSON
            product.batches.append(Batch.from_dict(b_data))             # Ubah data batch itu jadi objek, masukkan ke list
        return product                                                  # Kembalikan objek produk yang sudah lengkap


class Inventory:                                                        # Class untuk mengelola semua produk (sebagai gudang utama)
    def __init__(self, filename="database_inventory.json"):             # Constructor
        self.products = {}                                              # Dictionary kosong untuk menampung produk. Format: {"P001": <Objek Product>}
        self.filename = filename                                        # Simpan nama file database JSON

    def add_product(self, id, name, price):                             # Fungsi untuk mendaftarkan produk baru ke sistem
        if id in self.products:                                         # Cek apakah ID tersebut sudah ada di gudang
            print(f"Peringatan: Produk dengan ID '{id}' sudah ada!")    # Jika sudah ada, tolak
            return False                                                # Kembalikan False (gagal)
        self.products[id] = Product(id, name, price)                    # Jika belum ada, buat objek produk dan simpan di dictionary
        return True                                                     # Kembalikan True (berhasil)

    def find_product(self, id):                                         # Fungsi untuk mencari produk berdasarkan ID
        return self.products.get(id, None)                              # Cari di dictionary, kalau tidak ketemu kembalikan None

    def restock(self, id, purchase_price, qty):                         # Fungsi untuk menambah stok (batch) ke produk tertentu
        product = self.find_product(id)                                 # Cari dulu produknya
        if product:                                                     # Jika produk ditemukan
            product.add_batch(purchase_price, qty)                      # Tambahkan batch baru ke dalam produk tersebut
            return True                                                 # Kembalikan True (berhasil)
        print(f"Error: Produk dengan ID '{id}' tidak ditemukan.")       # Jika produk tidak ada, kasih error
        return False                                                    # Kembalikan False (gagal)

    def list_products(self):                                            # Fungsi untuk menampilkan semua produk ke layar
        if not self.products:                                           # Cek jika dictionary produk masih kosong
            print("\n[ Stok Gudang Kosong ]")                           # Tampilkan pesan kosong
            return                                                      # Hentikan fungsi

        print("\n" + "=" * 65)                                          # Cetak garis atas tabel
        print(f"{'ID':<8} | {'Nama Barang':<25} | {'Harga Jual':<12} | {'Total Stok':<10}") # Cetak judul kolom (rata kiri/kanan)
        print("-" * 65)                                                 # Garis pemisah header
        for p in self.products.values():                                # Looping setiap objek produk di dictionary
            print(f"{p.id:<8} | {p.name:<25} | Rp {p.selling_price:>9,.0f} | {p.total_stock():>10}") # Cetak data produk agar rapi
        print("=" * 65 + "\n")                                          # Garis penutup tabel

    def save_data(self):                                                # Fungsi untuk menyimpan seluruh isi gudang ke file JSON
        data = {pid: prod.to_dict() for pid, prod in self.products.items()} # Ubah semua objek produk menjadi dictionary
        with open(self.filename, "w", encoding="utf-8") as f:           # Buka file JSON dengan mode 'w' (write/timpa)
            json.dump(data, f, indent=4)                                # Tulis data dictionary ke file, indent=4 agar rapi
        print(f"Data inventaris berhasil disimpan ke '{self.filename}'.") # Konfirmasi ke layar

    def load_data(self):                                                # Fungsi untuk memuat data dari file JSON ke dalam program
        if not os.path.exists(self.filename):                           # Cek apakah file JSON-nya ada di folder?
            print(f"File '{self.filename}' belum ada, membuat sesi baru.") # Jika belum ada (baru pertama jalan), beri info
            return                                                      # Hentikan fungsi (gudang tetap kosong)

        try:                                                            # Coba jalankan blok ini
            with open(self.filename, "r", encoding="utf-8") as f:       # Buka file JSON dengan mode 'r' (read/baca)
                data = json.load(f)                                     # Baca isi file dan ubah jadi dictionary Python
                self.products = {pid: Product.from_dict(p_data) for pid, p_data in data.items()} # Looping data, ubah ke objek Product, simpan ke gudang
            print(f"Data inventaris berhasil dimuat dari '{self.filename}'.") # Konfirmasi ke layar
        except Exception as e:                                          # Jika file rusak atau formatnya salah
            print(f"Gagal membaca data dari file: {e}")                 # Tampilkan pesan error


def proses_restock(inventory):                                          # Fungsi CLI (tampilan layar) untuk menu restock
    print("\n--- MENU RESTOCK BARANG ---")                              # Judul menu
    p_id = input("Masukkan ID Produk: ").strip()                        # Minta input ID, hapus spasi
    if not p_id:                                                        # Jika user tidak mengisi apa-apa (langsung enter)
        print("ID produk tidak boleh kosong!")                          # Kasih peringatan
        return                                                          # Batalkan fungsi

    product = inventory.find_product(p_id)                              # Cari produk tersebut di gudang

    if not product:                                                     # Jika produk BELUM terdaftar
        print(f"ID '{p_id}' belum terdaftar. Silakan daftarkan produk baru.") # Info ke user
        name = input("Nama Barang: ").strip()                           # Minta nama barang
        while True:                                                     # Loop sampai input harga jual benar
            try:
                selling_price = float(input("Harga Jual (Rp): "))       # Minta harga jual, ubah ke float
                if selling_price <= 0:                                  # Cek jika harga 0 atau minus
                    print("Harga jual harus lebih dari 0!")             # Kasih peringatan
                    continue                                            # Ulangi minta input
                break                                                   # Jika valid, keluar dari loop
            except ValueError:                                          # Jika user ketik huruf
                print("Format salah! Masukkan angka untuk harga jual.") # Kasih peringatan

        inventory.add_product(p_id, name, selling_price)                # Daftarkan produk baru tersebut ke gudang

    while True:                                                         # Loop sampai input qty benar
        try:
            qty = int(input("Jumlah barang yang datang (qty): "))       # Minta jumlah stok masuk
            if qty <= 0:                                                # Cek jika 0 atau minus
                print("Jumlah harus lebih dari 0!")                     # Kasih peringatan
                continue
            break                                                       # Jika valid, keluar loop
        except ValueError:
            print("Format salah! Masukkan bilangan bulat untuk jumlah stok.") # Jika input bukan angka

    while True:                                                         # Loop sampai input harga beli benar
        try:
            purchase_price = float(input("Harga Beli / Modal per unit (Rp): ")) # Minta harga beli dari supplier
            if purchase_price <= 0:
                print("Harga beli harus lebih dari 0!")
                continue
            break
        except ValueError:
            print("Format salah! Masukkan angka untuk harga beli.")

    inventory.restock(p_id, purchase_price, qty)                        # Panggil fungsi restock di atas untuk menyimpan batch
    inventory.save_data()                                               # Langsung simpan ke file JSON setelah ditambah
    print(f"Restock untuk produk '{p_id}' berhasil dicatat dan disimpan!") # Konfirmasi ke layar


# Bagian ini hanya untuk testing mandiri (bisa diabaikan)
if __name__ == "__main__":                                              # Hanya berjalan jika file ini dieksekusi langsung
    gudang = Inventory()                                                # Buat gudang baru
    gudang.load_data()                                                  # Muat data dari JSON

    print("Mencoba flow registrasi dan restock...")                     # Info testing
    gudang.add_product("P01", "Susu Kotak", 7000)                       # Tambah produk dummy
    gudang.restock("P01", purchase_price=4000, qty=10)                  # Restock batch 1
    gudang.restock("P01", purchase_price=4500, qty=5)                   # Restock batch 2

    susu = gudang.find_product("P01")                                   # Cari produk
    if susu:
        print("Total stok susu sekarang:", susu.total_stock())          # Harusnya 15

    gudang.list_products()                                              # Tampilkan di layar
    gudang.save_data()                                                  # Simpan ke JSON
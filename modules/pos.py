from modules.cogs import HPPEngine                              # ambil class penghitung HPP FIFO milik Bachtiar


def rp(angka):                                                  # fungsi format angka ke Rupiah
    return "Rp {:,.0f}".format(angka).replace(",", ".")         # 15000 -> "Rp 15,000" lalu koma diganti titik -> "Rp 15.000"


class TransactionItem:                                          # satu baris barang di keranjang

    def __init__(self, product, qty):                           # constructor: dipanggil saat baris baru dibuat
        self.product = product                                  # simpan objek produk yang dibeli
        self.qty = qty                                          # simpan jumlah yang dibeli
        self.hpp_item = 0.0                                     # modal (HPP) baris ini, awalnya 0 sampai transaksi difinalisasi

    def subtotal(self):                                         # hitung total harga jual baris ini
        return self.product.selling_price * self.qty            # harga jual x jumlah beli

    def item_cogs(self):                                        # ambil modal (HPP) baris ini
        return self.hpp_item                                    # nilai yang diisi oleh finalize_checkout()


class Transaction:                                              # satu nota / satu kali transaksi pelanggan

    def __init__(self):                                         # constructor: membuat nota kosong
        self.items = []                                         # daftar barang (TransactionItem)
        self.discount = 0.0                                     # diskon dalam rupiah, default tanpa diskon
        self.paid_amount = 0.0                                  # uang tunai yang diserahkan pembeli
        self.is_finalized = False                               # penanda: apakah stok sudah dipotong (cegah potong 2 kali)

    def add_item(self, product, qty):                           # tambah barang ke keranjang
        self.items.append(TransactionItem(product, qty))        # buat baris baru lalu masukkan ke daftar items

    def subtotal_all(self):                                     # total belanja sebelum diskon
        return sum(item.subtotal() for item in self.items)      # jumlahkan subtotal semua baris

    def total_sales(self):                                      # total tagihan yang harus dibayar
        return self.subtotal_all() - self.discount              # jumlah semua subtotal dikurangi diskon

    def change_due(self):                                       # hitung uang kembalian
        return self.paid_amount - self.total_sales()            # uang diterima dikurangi tagihan

    def total_cogs(self):                                       # total modal (HPP) seluruh barang
        return sum(item.item_cogs() for item in self.items)     # jumlahkan HPP semua baris

    def gross_profit(self):                                     # hitung laba kotor
        return self.total_sales() - self.total_cogs()           # total penjualan dikurangi total modal

    def finalize_checkout(self):                                # proses akhir: potong stok FIFO & hitung HPP
        if self.is_finalized:                                   # cek apakah nota ini sudah pernah diproses
            raise RuntimeError("Transaksi ini sudah difinalisasi.")  # tolak supaya stok tidak terpotong dua kali

        kebutuhan = {}                                          # kamus: id produk -> [produk, total qty diminta]
        for item in self.items:                                 # periksa setiap baris di keranjang
            entri = kebutuhan.setdefault(item.product.id, [item.product, 0])  # ambil entri produk, buat baru jika belum ada
            entri[1] += item.qty                                # tambahkan qty (gabung jika produk sama muncul 2x)
        for produk, total in kebutuhan.values():                # cek stok tiap produk SEBELUM ada yang dipotong
            if produk.total_stock() < total:                    # jika stok gudang kurang dari yang diminta
                raise ValueError(                               # hentikan proses dengan pesan error
                    f"Stok '{produk.name}' tidak cukup "        # sebutkan nama produk yang bermasalah
                    f"(sisa {produk.total_stock()}, diminta {total})."  # tampilkan sisa stok dan jumlah diminta
                )                                               # tutup raise ValueError

        for item in self.items:                                 # semua stok aman -> mulai potong stok
            item.hpp_item = HPPEngine.compute_fifo(item.product, item.qty)  # hitung HPP FIFO sekaligus potong batch tertua
        self.is_finalized = True                                # tandai nota sudah final


# Helper input
def _baca_angka(prompt, minimum=0.0):                           # minta angka dari kasir, ulangi sampai valid
    while True:                                                 # loop terus sampai input benar
        try:                                                    # coba ubah input jadi angka
            nilai = float(input(prompt))                        # baca input kasir lalu ubah ke bilangan desimal
            if nilai < minimum:                                 # tolak angka di bawah batas minimum (mis. negatif)
                print(f"  ! Angka tidak boleh kurang dari {minimum:g}.")  # beri tahu batas minimumnya
                continue                                        # kembali ke awal loop, minta input lagi
            return nilai                                        # input valid -> kembalikan angkanya
        except ValueError:                                      # jika input bukan angka (mis. huruf)
            print("  ! Input harus berupa angka.")              # beri peringatan tanpa membuat program crash


# Alur layar kasir
def proses_kasir(inventory):                                    # fungsi utama kasir, menerima objek Inventory milik Prima
    transaksi = Transaction()                                   # buat nota kosong untuk pelanggan ini

    # ---------- Babak 1: Belanja ----------
    print("\n=== KASIR ===  (ketik '0' jika selesai belanja)")   # tampilkan judul dan petunjuk keluar
    while True:                                                 # loop input barang sampai kasir ketik 0
        kode = input("Kode produk: ").strip()                   # baca kode produk, buang spasi di awal/akhir
        if kode == "0":                                         # kasir mengetik 0 = pelanggan selesai belanja
            break                                               # keluar dari loop input barang

        produk = inventory.find_product(kode)                   # cari produk di gudang berdasarkan kode
        if produk is None:                                      # jika produk tidak ada di gudang
            print("  ! Produk tidak ditemukan.")                # beri tahu kasir
            continue                                            # ulangi, minta kode lagi

        try:                                                    # coba baca jumlah beli
            qty = int(input(f"Jumlah '{produk.name}': "))       # tanya jumlah, ubah ke bilangan bulat
            if qty <= 0:                                        # jumlah nol atau negatif tidak valid
                raise ValueError                                # lempar error agar ditangkap except di bawah
        except ValueError:                                      # tangkap input huruf, desimal, atau angka <= 0
            print("  ! Jumlah harus bilangan bulat positif.")   # beri peringatan ke kasir
            continue                                            # ulangi dari kode produk

        sudah_di_keranjang = sum(i.qty for i in transaksi.items if i.product is produk)  # hitung produk yang sama yang sudah dikeranjang
        if produk.total_stock() < sudah_di_keranjang + qty:     # stok gudang tidak cukup untuk total yang diminta
            sisa = produk.total_stock() - sudah_di_keranjang    # hitung sisa yang masih boleh dibeli
            print(f"  ! Stok tidak cukup. Sisa yang bisa dibeli: {sisa}")  # beri tahu sisa stok
            continue                                            # ulangi dari kode produk

        transaksi.add_item(produk, qty)                         # semua pengecekan lolos -> masukkan ke keranjang
        print(f"  + {produk.name} x{qty} = {rp(produk.selling_price * qty)}")  # konfirmasi barang & harganya

    if not transaksi.items:                                     # jika keranjang kosong (tidak ada barang)
        print("Keranjang kosong, transaksi dibatalkan.")        # beri tahu transaksi batal
        return None                                             # kembalikan None agar main.py tidak mencetak struk

    # ---------- Babak 2: Pembayaran & diskon ----------
    subtotal = transaksi.subtotal_all()                         # hitung total belanja sebelum diskon
    print(f"\nSubtotal belanja: {rp(subtotal)}")                # tampilkan subtotal

    while True:                                                 # loop input diskon sampai valid
        diskon = _baca_angka("Diskon (Rp, ketik 0 jika tidak ada): ")  # baca diskon dengan validasi angka
        if diskon > subtotal:                                   # diskon tidak boleh lebih besar dari belanjaan
            print("  ! Diskon tidak boleh melebihi subtotal.")  # beri peringatan
            continue                                            # minta diskon lagi
        transaksi.discount = diskon                            # simpan diskon ke nota
        break                                                   # diskon valid -> keluar loop

    tagihan = transaksi.total_sales()                           # hitung tagihan akhir (subtotal - diskon)
    print(f"Total tagihan   : {rp(tagihan)}")                   # tampilkan tagihan ke kasir

    while True:                                                 # loop input uang bayar sampai cukup
        bayar = _baca_angka("Uang diterima (Rp): ")             # baca uang tunai dari pembeli
        if bayar < tagihan:                                     # uang yang diberikan kurang dari tagihan
            print(f"  ! Uang kurang {rp(tagihan - bayar)}. Masukkan nominal yang cukup.")  # tampilkan kekurangannya
            continue                                            # minta nominal uang lagi
        transaksi.paid_amount = bayar                           # simpan uang bayar ke nota
        break                                                   # uang cukup -> keluar loop

    # ---------- Babak 3: Finalisasi ----------
    try:                                                        # coba finalisasi transaksi
        transaksi.finalize_checkout()                           # potong stok FIFO & hitung HPP
    except ValueError as e:                                     # jika stok ternyata tidak cukup
        print(f"  ! Transaksi gagal: {e}")                      # tampilkan alasan gagal
        return None                                             # batalkan: kembalikan None

    inventory.save_data()  # simpan stok terbaru ke JSON setelah terpotong  # tulis stok baru ke file database
    print(f"\nKembalian: {rp(transaksi.change_due())}")         # tampilkan uang kembalian
    print("Transaksi selesai.")                                 # tanda transaksi berhasil
    return transaksi                                            # kirim nota ke main.py (untuk struk & laporan Wisam)
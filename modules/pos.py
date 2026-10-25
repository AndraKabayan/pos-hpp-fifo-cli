from modules.cogs import HPPEngine


def rp(angka):
    return "Rp {:,.0f}".format(angka).replace(",", ".")


class TransactionItem:

    def __init__(self, product, qty):
        self.product = product
        self.qty = qty
        self.hpp_item = 0.0  

    def subtotal(self):
        return self.product.selling_price * self.qty

    def item_cogs(self):
        return self.hpp_item


class Transaction:

    def __init__(self):
        self.items = []
        self.discount = 0.0
        self.paid_amount = 0.0
        self.is_finalized = False

    def add_item(self, product, qty):
        self.items.append(TransactionItem(product, qty))

    def subtotal_all(self):
        return sum(item.subtotal() for item in self.items)
 
    def total_sales(self):
        return self.subtotal_all() - self.discount

    def change_due(self):
        return self.paid_amount - self.total_sales()

    def total_cogs(self):
        return sum(item.item_cogs() for item in self.items)

    def gross_profit(self):
        return self.total_sales() - self.total_cogs()

    def finalize_checkout(self):
        if self.is_finalized:
            raise RuntimeError("Transaksi ini sudah difinalisasi.")

        kebutuhan = {}
        for item in self.items:
            entri = kebutuhan.setdefault(item.product.id, [item.product, 0])
            entri[1] += item.qty
        for produk, total in kebutuhan.values():
            if produk.total_stock() < total:
                raise ValueError(
                    f"Stok '{produk.name}' tidak cukup "
                    f"(sisa {produk.total_stock()}, diminta {total})."
                )

        for item in self.items:
            item.hpp_item = HPPEngine.compute_fifo(item.product, item.qty)
        self.is_finalized = True


# Helper input
def _baca_angka(prompt, minimum=0.0):
    while True:
        try:
            nilai = float(input(prompt))
            if nilai < minimum:
                print(f"  ! Angka tidak boleh kurang dari {minimum:g}.")
                continue
            return nilai
        except ValueError:
            print("  ! Input harus berupa angka.")


def _stok_tersedia(inventory_item_qty_di_keranjang, product):
    return product.total_stock() - inventory_item_qty_di_keranjang

# Alur layar kasir
def proses_kasir(inventory):
    transaksi = Transaction()

    # ---------- Babak 1: Belanja ----------
    print("\n=== KASIR ===  (ketik '0' jika selesai belanja)")
    while True:
        kode = input("Kode produk: ").strip()
        if kode == "0":
            break

        produk = inventory.find_product(kode)
        if produk is None:
            print("  ! Produk tidak ditemukan.")
            continue

        try:
            qty = int(input(f"Jumlah '{produk.name}': "))
            if qty <= 0:
                raise ValueError
        except ValueError:
            print("  ! Jumlah harus bilangan bulat positif.")
            continue

        sudah_di_keranjang = sum(i.qty for i in transaksi.items if i.product is produk)
        if produk.total_stock() < sudah_di_keranjang + qty:
            sisa = produk.total_stock() - sudah_di_keranjang
            print(f"  ! Stok tidak cukup. Sisa yang bisa dibeli: {sisa}")
            continue

        transaksi.add_item(produk, qty)
        print(f"  + {produk.name} x{qty} = {rp(produk.selling_price * qty)}")

    if not transaksi.items:
        print("Keranjang kosong, transaksi dibatalkan.")
        return None

    # ---------- Babak 2: Pembayaran & diskon ----------
    subtotal = transaksi.subtotal_all()
    print(f"\nSubtotal belanja: {rp(subtotal)}")

    while True:
        diskon = _baca_angka("Diskon (Rp, ketik 0 jika tidak ada): ")
        if diskon > subtotal:
            print("  ! Diskon tidak boleh melebihi subtotal.")
            continue
        transaksi.discount = diskon
        break

    tagihan = transaksi.total_sales()
    print(f"Total tagihan   : {rp(tagihan)}")

    while True:
        bayar = _baca_angka("Uang diterima (Rp): ")
        if bayar < tagihan:
            print(f"  ! Uang kurang {rp(tagihan - bayar)}. Masukkan nominal yang cukup.")
            continue
        transaksi.paid_amount = bayar
        break

    # ---------- Babak 3: Finalisasi ----------
    try:
        transaksi.finalize_checkout()
    except ValueError as e:
        print(f"  ! Transaksi gagal: {e}")
        return None

    inventory.save_data()  # simpan stok terbaru ke JSON setelah terpotong
    print(f"\nKembalian: {rp(transaksi.change_due())}")
    print("Transaksi selesai.")
    return transaksi
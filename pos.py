from cogs import HPPEngine

class transactionItems:
    def __init__(self, product, qty):
        self.product = product
        self.qty = qty
        self.hpp_item = 0.0

    def subtotal(self):
        return self.product.harga_jual * self.qty
    
    def item_cogs(self):
        return self.hpp_item
    
class Transaction:
    def __init__(self):
        self.items = []
        self.discount = 0.0
        self.paid_amount = 0.0
        self.is_finalized = False
        
    def add_item(self, product, qty):
        self.items.append(transactionItems(product, qty))
        
    def subtotal_all(self):
        return sum(item.subtotal() for item in self.items)
    
    def total_sales(self):
        return self.subtotal_all() - self.discount
    
    def change_due(self):
        return self.paid_amount() - self.total_sales()
    
    def total_cogs(self):
        return sum(item.item_cogs() for item in self.items)
    
    def gross_profit(self):
        return self.total_sales() - self.total_cogs()
    
    def finalize_checkout(self):
        if self.is_finalized:
            raise RuntimeError("Transaksi ini sudah difinalisasi.")
        for item in self.items:
            item.hpp_item = HPPEngine.compute_fifo(item.product, item.qty)
        self.is_finalized = True


def proses_kasir(inventory):
    transaksi = Transaction()

    print("\n=== KASIR === (ketik '0' jika selesai belanja)")
    while True:
        kode = input("Kode produk:").strip()
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
        
        
        
        

if __name__ == "__main__":
    from inventory import Inventory
    
    # Menyiapkan toko tiruan
    inv = Inventory()
    inv.add_product("P01", "Minyak Goreng 1L", 20000)
    inv.restock("P01", purchase_price=14000, qty=5)
    
    # Menjalankan mesin kasir Andra
    transaksi = proses_kasir(inv)
    
    # Mengecek apakah data tercatat dengan benar
    if transaksi:
        print("\n=== HASIL UJI KASIR ANDRA ===")
        print("Total Tagihan : Rp", transaksi.total_sales())
        print("Laba Toko     : Rp", transaksi.gross_profit())
        print("Kembalian     : Rp", transaksi.change_due())
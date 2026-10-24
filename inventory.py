import json
import os
from datetime import datetime


class Batch:
    def __init__(self, purchase_price, qty, arrival_date=None):
        self.purchase_price = float(purchase_price)
        self.qty = int(qty)
        self.arrival_date = arrival_date if arrival_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "purchase_price": self.purchase_price,
            "qty": self.qty,
            "arrival_date": self.arrival_date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            purchase_price=data["purchase_price"],
            qty=data["qty"],
            arrival_date=data.get("arrival_date")
        )


class Product:
    def __init__(self, id, name, selling_price):
        self.id = str(id)
        self.name = str(name)
        self.selling_price = float(selling_price)
        self.batches = []

    def add_batch(self, purchase_price, qty):
        batch = Batch(purchase_price, qty)
        self.batches.append(batch)

    def total_stock(self):
        return sum(batch.qty for batch in self.batches)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "selling_price": self.selling_price,
            "batches": [batch.to_dict() for batch in self.batches]
        }

    @classmethod
    def from_dict(cls, data):
        product = cls(
            id=data["id"],
            name=data["name"],
            selling_price=data["selling_price"]
        )
        for b_data in data.get("batches", []):
            product.batches.append(Batch.from_dict(b_data))
        return product


class Inventory:
    def __init__(self, filename="database_inventory.json"):
        self.products = {}
        self.filename = filename

    def add_product(self, id, name, price):
        if id in self.products:
            print(f"Peringatan: Produk dengan ID '{id}' sudah ada!")
            return False
        self.products[id] = Product(id, name, price)
        return True

    def find_product(self, id):
        return self.products.get(id, None)

    def restock(self, id, purchase_price, qty):
        product = self.find_product(id)
        if product:
            product.add_batch(purchase_price, qty)
            return True
        print(f"Error: Produk dengan ID '{id}' tidak ditemukan.")
        return False

    def list_products(self):
        if not self.products:
            print("\n[ Stok Gudang Kosong ]")
            return

        print("\n" + "=" * 65)
        print(f"{'ID':<8} | {'Nama Barang':<25} | {'Harga Jual':<12} | {'Total Stok':<10}")
        print("-" * 65)
        for p in self.products.values():
            print(f"{p.id:<8} | {p.name:<25} | Rp {p.selling_price:>9,.0f} | {p.total_stock():>10}")
        print("=" * 65 + "\n")

    def save_data(self):
        data = {pid: prod.to_dict() for pid, prod in self.products.items()}
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Data inventaris berhasil disimpan ke '{self.filename}'.")

    def load_data(self):
        if not os.path.exists(self.filename):
            print(f"File '{self.filename}' belum ada, membuat sesi baru.")
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.products = {pid: Product.from_dict(p_data) for pid, p_data in data.items()}
            print(f"Data inventaris berhasil dimuat dari '{self.filename}'.")
        except Exception as e:
            print(f"Gagal membaca data dari file: {e}")


def proses_restock(inventory):
    print("\n--- MENU RESTOCK BARANG ---")
    p_id = input("Masukkan ID Produk: ").strip()
    if not p_id:
        print("ID produk tidak boleh kosong!")
        return

    product = inventory.find_product(p_id)

    if not product:
        print(f"ID '{p_id}' belum terdaftar. Silakan daftarkan produk baru.")
        name = input("Nama Barang: ").strip()
        while True:
            try:
                selling_price = float(input("Harga Jual (Rp): "))
                if selling_price <= 0:
                    print("Harga jual harus lebih dari 0!")
                    continue
                break
            except ValueError:
                print("Format salah! Masukkan angka untuk harga jual.")

        inventory.add_product(p_id, name, selling_price)

    while True:
        try:
            qty = int(input("Jumlah barang yang datang (qty): "))
            if qty <= 0:
                print("Jumlah harus lebih dari 0!")
                continue
            break
        except ValueError:
            print("Format salah! Masukkan bilangan bulat untuk jumlah stok.")

    while True:
        try:
            purchase_price = float(input("Harga Beli / Modal per unit (Rp): "))
            if purchase_price <= 0:
                print("Harga beli harus lebih dari 0!")
                continue
            break
        except ValueError:
            print("Format salah! Masukkan angka untuk harga beli.")

    inventory.restock(p_id, purchase_price, qty)
    inventory.save_data()
    print(f"Restock untuk produk '{p_id}' berhasil dicatat dan disimpan!")


if __name__ == "__main__":
    gudang = Inventory()
    gudang.load_data()

    print("Mencoba flow registrasi dan restock...")
    gudang.add_product("P01", "Susu Kotak",7000)
    gudang.restock("P01", purchase_price=4000, qty=10)
    gudang.restock("P01", purchase_price=4500, qty=5)

    susu = gudang.find_product("P01")
    if susu:
        print("Total stok susu sekarang:", susu.total_stock())

    gudang.list_products()
    gudang.save_data()
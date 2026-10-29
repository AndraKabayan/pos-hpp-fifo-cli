import unittest                                                             # Modul bawaan Python untuk membuat unit test
import sys                                                                  # Modul untuk memanipulasi path direktori
import os                                                                   # Modul untuk urusan sistem operasi (path)

# Menambahkan folder utama (root) ke dalam sistem path Python
# Agar file ini bisa memanggil folder 'modules' saat dijalankan
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.inventory import Product                                       # Ambil class Product milik Prima
from modules.cogs import HPPEngine                                          # Ambil class mesin HPP milik Bachtiar

class TestFIFOEngine(unittest.TestCase):                                    # Class untuk mengelompokkan test FIFO

    def setUp(self):                                                        # Fungsi ini otomatis jalan SEBELUM setiap test dimulai
        """Menyiapkan data dummy (produk gula) sebelum pengujian."""
        # Membuat produk "Gula" dengan harga jual Rp 15.000
        self.gula = Product("P001", "Gula Pasir", selling_price=15000)
        
        # Memasukkan 3 batch kulakan dengan harga modal berbeda
        self.gula.add_batch(purchase_price=5000, qty=10)                    # Batch 1 (Terlama): 10 unit @ Rp 5.000
        self.gula.add_batch(purchase_price=6000, qty=15)                    # Batch 2: 15 unit @ Rp 6.000
        self.gula.add_batch(purchase_price=6500, qty=20)                    # Batch 3: 20 unit @ Rp 6.500

    # --- TEST 1: PENGUJIAN MULTI-BATCH ---
    def test_hitung_hpp_multi_batch(self):                                  # Skenario: Beli 18 unit (memotong 2 batch)
        """Menguji perhitungan HPP saat pembelian menembus lebih dari 1 batch."""
        # Hitung HPP menggunakan mesin milik Bachtiar
        hpp_total = HPPEngine.compute_fifo(self.gula, qty_beli=18)
        
        # Ekspektasi HPP: (10 x 5000) + (8 x 6000) = 50.000 + 48.000 = 98.000
        self.assertEqual(hpp_total, 98000)                                  # Cek apakah HPP pas Rp 98.000
        
        # Ekspektasi Sisa Stok: Total awal 45 - 18 = 27 unit
        self.assertEqual(self.gula.total_stock(), 27)                       # Cek apakah sisa stok benar 27 unit

    # --- TEST 2: PENGUJIAN STOK TIDAK CUKUP ---
    def test_stok_tidak_cukup(self):                                        # Skenario: Beli melebihi stok gudang
        """Menguji apakah sistem menolak pembelian jika stok tidak mencukupi."""
        # Kita memakai 'with self.assertRaises' untuk memastikan program MEMANG error (ValueError)
        with self.assertRaises(ValueError):                                 # Jika tidak error, test ini akan GAGAL
            # Minta 50 unit, padahal total stok cuma 45 unit
            HPPEngine.compute_fifo(self.gula, qty_beli=50)

    # --- TEST 3: PENGUJIAN SATU BATCH ---
    def test_hitung_hpp_satu_batch(self):                                   # Skenario: Beli 5 unit (hanya memotong batch 1)
        """Menguji perhitungan HPP jika pembelian hanya memotong batch pertama."""
        hpp_total = HPPEngine.compute_fifo(self.gula, qty_beli=5)
        
        # Ekspektasi HPP: 5 unit x Rp 5.000 = Rp 25.000
        self.assertEqual(hpp_total, 25000)
        
        # Ekspektasi Sisa Batch 1: 10 - 5 = 5 unit (Batch 2 & 3 tidak tersentuh)
        self.assertEqual(self.gula.batches[0].qty, 5)                       # Cek apakah sisa batch terlama benar 5

    # --- TEST 4: PENGUJIAN RUMUS MATEMATIKA (MARGIN & MARKUP) ---
    def test_hitung_margin_markup(self):                                    # Skenario: Uji fungsi persentase
        laba_kotor = 82000                                                  # Angka dummy laba
        total_penjualan = 180000                                            # Angka dummy omzet
        hpp_total = 98000                                                   # Angka dummy modal

        # Panggil fungsi margin & markup milik Bachtiar
        margin = HPPEngine.compute_margin(total_penjualan, hpp_total)
        markup = HPPEngine.compute_markup(total_penjualan / 18, hpp_total / 18) # Harga satuan & HPP satuan

        # Ekspektasi Margin: (82.000 / 180.000) * 100 = 45.555%
        self.assertAlmostEqual(margin, 45.5555, places=3)                   
        
        # Ekspektasi Markup: (Laba per unit / HPP per unit) * 100 = 83.673%
        self.assertAlmostEqual(markup, 83.6734, places=3)   # <--- Ubah angkanya ke 83.6734


# --- TITIK MASUK PROGRAM ---
if __name__ == '__main__':                                                  # Jika file ini dieksekusi langsung
    unittest.main()                                                         # Jalankan semua test di atas
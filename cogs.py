class HPPEngine:
    @staticmethod
    def compute_fifo(product, qty_beli):
        # Validasi Stock
        if product.total_stock() < qty_beli:
            raise ValueError("Stok habis!")

        total_hpp = 0.0
        stock_tersedia = qty_beli

        # Looping FIFO Stock
        while stock_tersedia > 0:
            batch_terlama = product.batches[0]

            if batch_terlama.qty > stock_tersedia:
                # Kondisi A: Bacth ini sisa
                total_hpp += stock_tersedia * batch_terlama.purchase_price
                batch_terlama.qty -= stock_tersedia
                stock_tersedia = 0
            else:
                # Kondisi B: Batch ini kurang atau pas (habiskan isi batch)
                total_hpp += batch_terlama.qty * batch_terlama.purchase_price
                stock_tersedia -= batch_terlama.qty
                # Hapus batch terlama karena sudah kosong
                product.batches.pop(0)

        return total_hpp

    @staticmethod
    def compute_margin(total_penjualan, total_hpp):
        # Menghitung laba kotor
        if total_penjualan == 0:
            return 0.0
        laba_kotor = total_penjualan - total_hpp
        return (laba_kotor / total_hpp) * 100

    @staticmethod
    def compute_markup(harga_jual, rata_rata_hpp):
        # Markup dihitung dari harga jual per unit terhadap rata-rata HPP per unit
        if rata_rata_hpp == 0:
            return 0.0
        laba_per_unit = harga_jual - rata_rata_hpp
        return (laba_per_unit / rata_rata_hpp) * 100

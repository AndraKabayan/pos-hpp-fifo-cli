class HPPEngine:  # Kelas untuk menghitung HPP, margin, dan markup
    @staticmethod  # decorator di Python
    def compute_fifo(
        product, qty_beli
    ):  # Menghitung HPP berdasarkan metode FIFO (First In First Out)
        if (
            product.total_stock() < qty_beli
        ):  # Validasi apakah stok mencukupi jumlah yang dibeli
            raise ValueError(
                "Stok habis!"
            )  # Jika stok tidak mencukupi, lemparkan exception

        total_hpp = 0.0  # Inisialisasi total HPP
        stock_tersedia = (
            qty_beli  # Jumlah stok yang masih perlu diproses untuk pembelian
        )

        # Looping FIFO Stock
        while (
            stock_tersedia > 0
        ):  # Looping stok FIFO selama masih ada stok yang perlu diproses
            batch_terlama = product.batches[0]  # Ambil batch terlama (FIFO)

            if batch_terlama.qty > stock_tersedia:  # Periksa stok
                total_hpp += (
                    stock_tersedia * batch_terlama.purchase_price
                )  # Tambahkan HPP dari stok yang tersisa di batch ini
                batch_terlama.qty -= stock_tersedia  # Kurangi jumlah stok di batch ini sesuai yang dibeli
                stock_tersedia = 0
            else:  # Kondisi jika stok di batch terlama ternyata kurang dari atau pas dengan sisa pesanan
                total_hpp += (
                    batch_terlama.qty * batch_terlama.purchase_price
                )  # Tambahkan HPP dari seluruh stok di batch ini
                stock_tersedia -= (
                    batch_terlama.qty
                )  # Kurangi jumlah stok yang masih perlu diproses
                # Hapus batch terlama karena sudah kosong
                product.batches.pop(0)

        return total_hpp  # Kembalikan total HPP yang telah dihitung

    @staticmethod  # decorator untuk metode statis compute_margin
    def compute_margin(
        total_penjualan, total_hpp
    ):  # Menghitung margin laba kotor dalam persen
        # Menghitung laba kotor
        if total_penjualan == 0:  # Jika total penjualan nol, margin dianggap nol
            return 0.0  # Kembalikan margin nol jika tidak ada penjualan
        laba_kotor = total_penjualan - total_hpp  # Hitung laba kotor
        return (laba_kotor / total_hpp) * 100  # Kembalikan margin dalam persen

    @staticmethod  # decorator untuk metode statis compute_markup
    def compute_markup(harga_jual, rata_rata_hpp):  # Menghitung markup dalam persen
        # Markup dihitung dari harga jual per unit terhadap rata-rata HPP per unit
        if rata_rata_hpp == 0:  # Jika rata-rata HPP nol, markup dianggap nol
            return 0.0  # Kembalikan markup nol jika rata-rata HPP nol
        laba_per_unit = harga_jual - rata_rata_hpp  # Hitung laba per unit
        return (laba_per_unit / rata_rata_hpp) * 100  # Kembalikan markup dalam persen

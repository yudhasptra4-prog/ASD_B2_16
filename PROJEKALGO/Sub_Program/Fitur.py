# ===========================
# Fitur
# ===========================

def validasi_tanggal(tanggal):
    try:
        tahun, bulan, hari = map(int, tanggal.split("-"))
        return 1 <= bulan <= 12 and 1 <= hari <= 31 and len(str(tahun)) == 4
    except Exception:
        return False

def input_transaksi():
    while True:
        tanggal = input("Masukkan tanggal (YYYY-MM-DD): ").strip()
        if validasi_tanggal(tanggal):
            break
        print("Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")

    keterangan = input("Masukkan keterangan transaksi: ").strip()
    while not keterangan:
        print("Keterangan tidak boleh kosong.")
        keterangan = input("Masukkan keterangan transaksi: ").strip()

    tipe = input("Masukkan tipe transaksi (debit/kredit): ").strip().lower()
    while tipe not in ["debit", "kredit"]:
        print("Tipe harus 'debit' atau 'kredit'.")
        tipe = input("Masukkan tipe transaksi (debit/kredit): ").strip().lower()

    while True:
        jumlah = input("Masukkan jumlah transaksi: ").strip()
        if jumlah.isdigit() and int(jumlah) > 0:
            break
        print("Jumlah harus berupa angka positif.")

    return {
        "tanggal": tanggal,
        "keterangan": keterangan,
        "tipe": tipe,
        "jumlah": jumlah
    }

def hitung_saldo(linked_list):
    saldo = 0
    temp = linked_list.head
    while temp:
        jumlah = int(temp.data["jumlah"])
        if temp.data["tipe"] == "kredit":
            saldo += jumlah
        else:
            saldo -= jumlah
        temp = temp.next
    return saldo

def tampilkan_daftar(linked_list):
    if linked_list.head is None:
        print("Tidak ada transaksi.")
        return

    print("{:3} | {:10} | {:20} | {:6} | {:10}".format("No", "Tanggal", "Keterangan", "Tipe", "Jumlah"))
    print("-" * 60)
    index = 1
    temp = linked_list.head
    while temp:
        data = temp.data
        print("{:3} | {:10} | {:20} | {:6} | {:10}".format(
            index,
            data["tanggal"],
            data["keterangan"],
            data["tipe"],
            data["jumlah"]
        ))
        temp = temp.next
        index += 1
    print("-" * 60)
    print(f"Saldo akhir: {hitung_saldo(linked_list)}")

def cari_transaksi(linked_list):
    if linked_list.head is None:
        print("Tidak ada transaksi untuk dicari.")
        return

    kata = input("Masukkan kata kunci untuk mencari (tanggal/keterangan/tipe): ").strip().lower()
    if not kata:
        print("Kata kunci tidak boleh kosong.")
        return

    ditemukan = False
    index = 1
    temp = linked_list.head
    while temp:
        data = temp.data
        if kata in data["tanggal"].lower() or kata in data["keterangan"].lower() or kata in data["tipe"].lower():
            if not ditemukan:
                print("Hasil pencarian:")
                print("{:3} | {:10} | {:20} | {:6} | {:10}".format("No", "Tanggal", "Keterangan", "Tipe", "Jumlah"))
                print("-" * 60)
            print("{:3} | {:10} | {:20} | {:6} | {:10}".format(
                index,
                data["tanggal"],
                data["keterangan"],
                data["tipe"],
                data["jumlah"]
            ))
            ditemukan = True
        temp = temp.next
        index += 1

    if not ditemukan:
        print("Transaksi tidak ditemukan.")

def hapus_transaksi(linked_list):
    if linked_list.head is None:
        print("Tidak ada transaksi untuk dihapus.")
        return

    tampilkan_daftar(linked_list)
    pilihan = input("Masukkan nomor transaksi yang akan dihapus: ").strip()
    if not pilihan.isdigit():
        print("Masukan harus angka.")
        return

    nomor = int(pilihan)
    if nomor < 1:
        print("Nomor transaksi tidak valid.")
        return

    prev = None
    temp = linked_list.head
    index = 1
    while temp and index < nomor:
        prev = temp
        temp = temp.next
        index += 1

    if temp is None:
        print("Nomor transaksi tidak ditemukan.")
        return

    if prev is None:
        linked_list.head = temp.next
    else:
        prev.next = temp.next

    print("Transaksi berhasil dihapus.")

def menu():
    print("\\n=== SISTEM RIWAYAT TRANSAKSI REKENING ===")
    print("1. Lihat semua transaksi")
    print("2. Tambah transaksi")
    print("3. Cari transaksi")
    print("4. Hapus transaksi")
    print("5. Keluar")
    return input("Pilih menu (1-5): ").strip()

def main():
    ll = LinkedList()
    init_file()
    baca_file(ll)

    while True:
        pilihan = menu()
        if pilihan == "1":
            tampilkan_daftar(ll)
        elif pilihan == "2":
            transaksi = input_transaksi()
            ll.tambah(transaksi)
            simpan_file(ll)
            print("Transaksi berhasil ditambahkan.")
        elif pilihan == "3":
            cari_transaksi(ll)
        elif pilihan == "4":
            hapus_transaksi(ll)
            simpan_file(ll)
        elif pilihan == "5":
            print("Terima kasih. Program selesai.")
            break
        else:
            print("Pilihan tidak valid. Silakan pilih antara 1 sampai 5.")

if __name__ == "__main__":
    main()
"""Bagian Yudha: frontend, dashboard, pencarian, periode, dan tabel mutasi.

Jalankan aplikasi dari file ini:
    python PROJEKFIKS.py
"""

import os

from Testing_Debugging import (
    cetak_debug_info,
    cetak_dokumentasi,
    cetak_panduan_presentasi,
    input_valid,
    jalankan_self_test,
    validasi_periode,
)
from Struktur_Data_Utama import (
    LinkedListPeriode,
    baca_rekening,
    baca_transaksi,
    cari_rekening,
    cetak_header_app,
    cetak_judul_menu,
    edit_transaksi,
    format_periode,
    format_rupiah,
    garis,
    hapus_transaksi,
    hitung_saldo_akhir,
    inisialisasi_file,
    lihat_rekening,
    manajemen_saldo,
    reset_mutasi,
    tambah_nasabah,
    tambah_transaksi,
)


def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def lihat_mutasi(no_rek: str = None, periode: str = None, dari_menu: bool = True):
    """Tampilkan mutasi rekening dalam bentuk tabel buku tabungan."""
    if dari_menu:
        cetak_judul_menu("LIHAT MUTASI REKENING")
        no_rek = input("  Nomor Rekening : ").strip()

    rek = cari_rekening(no_rek)
    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()
    mutasi = sorted(
        [
            trx for trx in transaksi_list
            if trx["no_rekening"] == no_rek
            and (periode is None or trx["tanggal"].startswith(periode))
        ],
        key=lambda trx: (trx["tanggal"], trx["id_transaksi"]),
    )

    garis()
    print(f"{'BANK BUMI ARTHA':^72}")
    print(f"{'LAPORAN MUTASI REKENING':^72}")
    garis()
    print(f"  No. Rekening  : {rek['no_rekening']}")
    print(f"  Nama Nasabah  : {rek['nama_nasabah']}")
    print(f"  Tgl Buka      : {rek['tanggal_buka']}")
    print(f"  Saldo Awal    : {format_rupiah(rek['saldo_awal'])}")
    if periode:
        print(f"  Periode       : {format_periode(periode)}")
    garis("-")

    if not mutasi:
        pesan = f" pada periode {format_periode(periode)}." if periode else "."
        print("  Tidak ada transaksi" + pesan)
    else:
        lebar = {
            "tgl": 12,
            "id": 24,
            "ket": 16,
            "masuk": 14,
            "keluar": 14,
            "saldo": 15,
        }
        print(
            f"  {'Tanggal':<{lebar['tgl']}} "
            f"{'ID Transaksi':<{lebar['id']}} "
            f"{'Keterangan':<{lebar['ket']}} "
            f"{'Debit':>{lebar['masuk']}} "
            f"{'Kredit':>{lebar['keluar']}} "
            f"{'Saldo':>{lebar['saldo']}}"
        )
        garis("-")

        saldo_running = float(rek["saldo_awal"])
        if periode:
            batas_awal = periode + "-01"
            for trx in transaksi_list:
                if trx["no_rekening"] == no_rek and trx["tanggal"] < batas_awal:
                    if trx["jenis"].lower() == "masuk":
                        saldo_running += float(trx["nominal"])
                    else:
                        saldo_running -= float(trx["nominal"])

        total_masuk = 0.0
        total_keluar = 0.0

        for trx in mutasi:
            nominal = float(trx["nominal"])
            if trx["jenis"].lower() == "masuk":
                saldo_running += nominal
                total_masuk += nominal
                nilai_masuk = format_rupiah(nominal)
                nilai_keluar = "-"
            else:
                saldo_running -= nominal
                total_keluar += nominal
                nilai_masuk = "-"
                nilai_keluar = format_rupiah(nominal)

            keterangan = trx["keterangan"] or "-"
            if len(keterangan) > 14:
                keterangan = keterangan[:13] + "..."

            print(
                f"  {trx['tanggal']:<{lebar['tgl']}} "
                f"{trx['id_transaksi'][:22]:<{lebar['id']}} "
                f"{keterangan:<{lebar['ket']}} "
                f"{nilai_masuk:>{lebar['masuk']}} "
                f"{nilai_keluar:>{lebar['keluar']}} "
                f"{format_rupiah(saldo_running):>{lebar['saldo']}}"
            )

        garis("-")
        kolom_total = lebar["tgl"] + lebar["id"] + lebar["ket"] + 3
        print(
            f"  {'TOTAL':<{kolom_total}} "
            f"{format_rupiah(total_masuk):>{lebar['masuk']}} "
            f"{format_rupiah(total_keluar):>{lebar['keluar']}} "
            f"{format_rupiah(saldo_running):>{lebar['saldo']}}"
        )

    garis()
    saldo_akhir = hitung_saldo_akhir(no_rek, rek["saldo_awal"], transaksi_list)
    print(f"  Saldo Akhir: {format_rupiah(saldo_akhir)}")
    garis()


def navigasi_periode():
    cetak_judul_menu("NAVIGASI PERIODE MUTASI")
    no_rek = input("  Nomor Rekening : ").strip()
    rek = cari_rekening(no_rek)

    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()
    daftar_periode = LinkedListPeriode()
    for trx in transaksi_list:
        if trx["no_rekening"] == no_rek:
            daftar_periode.tambah_periode(trx["tanggal"][:7])

    semua_periode = daftar_periode.get_all_periode()
    if not semua_periode:
        print("  Rekening ini belum memiliki transaksi.")
        return

    daftar_periode.set_current(semua_periode[-1])

    while True:
        bersihkan_layar()
        cetak_header_app()
        cetak_judul_menu("NAVIGASI PERIODE MUTASI")

        kiri = (
            format_periode(daftar_periode.current.prev.periode)
            if daftar_periode.current.prev else "(awal)"
        )
        kanan = (
            format_periode(daftar_periode.current.next.periode)
            if daftar_periode.current.next else "(akhir)"
        )

        print(f"  Nasabah      : {rek['nama_nasabah']}")
        print(f"  No. Rekening : {no_rek}")
        garis("-")
        print(f"  <  {kiri}   *  [{format_periode(daftar_periode.current.periode)}]   >  {kanan}")
        garis("-")

        print("\n  Semua Periode Tersedia:")
        for i, periode in enumerate(semua_periode, 1):
            penanda = " < aktif" if periode == daftar_periode.current.periode else ""
            print(f"    [{i}] {format_periode(periode)}{penanda}")

        garis("-")
        print("  [1] <  Periode Sebelumnya")
        print("  [2] >  Periode Berikutnya")
        print("  [3]    Lihat Mutasi Periode Ini")
        print("  [4]    Pilih Periode Manual")
        print("  [0]    Kembali")

        pilih = input("\n  Pilihan : ").strip()

        if pilih == "1":
            periode = daftar_periode.periode_sebelumnya()
            print(f"  -> Pindah ke: {format_periode(periode)}" if periode else "  [!] Sudah di periode paling awal.")
            input("  Tekan Enter...")
        elif pilih == "2":
            periode = daftar_periode.periode_berikutnya()
            print(f"  -> Pindah ke: {format_periode(periode)}" if periode else "  [!] Sudah di periode paling akhir.")
            input("  Tekan Enter...")
        elif pilih == "3":
            lihat_mutasi(no_rek, daftar_periode.current.periode, dari_menu=False)
            input("\n  Tekan Enter...")
        elif pilih == "4":
            nomor = input_valid("  Nomor periode: ", tipe="int", min_val=1) - 1
            if 0 <= nomor < len(semua_periode):
                daftar_periode.set_current(semua_periode[nomor])
            else:
                print("  [!] Nomor periode tidak valid.")
            input("  Tekan Enter...")
        elif pilih == "0":
            break
        else:
            print("  [!] Pilihan tidak valid.")
            input("  Tekan Enter...")


def searching_filtering():
    cetak_judul_menu("SEARCHING & FILTERING TRANSAKSI")
    no_rek = input("  Nomor Rekening : ").strip()
    rek = cari_rekening(no_rek)

    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    print(f"  Nasabah: {rek['nama_nasabah']}")
    garis("-")
    print("  [1] Cari berdasarkan Tanggal")
    print("  [2] Cari berdasarkan Nominal")
    print("  [3] Cari berdasarkan Jenis Transaksi")
    print("  [4] Filter: Transaksi Masuk")
    print("  [5] Filter: Transaksi Keluar")
    print("  [6] Filter: Berdasarkan Periode")
    garis("-")

    pilih = input("  Pilihan : ").strip()
    transaksi_list = baca_transaksi()
    hasil = []
    judul = ""

    if pilih == "1":
        kata_kunci = input("  Tanggal (YYYY-MM-DD / YYYY-MM / YYYY): ").strip()
        hasil = [
            trx for trx in transaksi_list
            if trx["no_rekening"] == no_rek and kata_kunci in trx["tanggal"]
        ]
        judul = f"Pencarian Tanggal: '{kata_kunci}'"
    elif pilih == "2":
        kata_kunci = input("  Nominal (sebagian angka): ").strip()
        hasil = [
            trx for trx in transaksi_list
            if trx["no_rekening"] == no_rek and kata_kunci in trx["nominal"]
        ]
        judul = f"Pencarian Nominal: '{kata_kunci}'"
    elif pilih == "3":
        kata_kunci = input("  Jenis (masuk/keluar): ").strip().lower()
        hasil = [
            trx for trx in transaksi_list
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == kata_kunci
        ]
        judul = f"Pencarian Jenis: '{kata_kunci}'"
    elif pilih == "4":
        hasil = [
            trx for trx in transaksi_list
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == "masuk"
        ]
        judul = "Filter: Transaksi Masuk"
    elif pilih == "5":
        hasil = [
            trx for trx in transaksi_list
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == "keluar"
        ]
        judul = "Filter: Transaksi Keluar"
    elif pilih == "6":
        periode = input("  Periode (YYYY-MM): ").strip()
        if not validasi_periode(periode):
            print("  [!] Format periode harus YYYY-MM, contoh: 2025-03.")
            return
        hasil = [
            trx for trx in transaksi_list
            if trx["no_rekening"] == no_rek and trx["tanggal"].startswith(periode)
        ]
        judul = f"Filter Periode: {format_periode(periode)}"
    else:
        print("  [!] Pilihan tidak valid.")
        return

    tampilkan_hasil_pencarian(judul, hasil)


def tampilkan_hasil_pencarian(judul: str, hasil: list):
    garis()
    print(f"  > {judul}")
    print(f"  Ditemukan: {len(hasil)} transaksi")
    garis("-")

    if not hasil:
        print("  Tidak ada transaksi yang cocok.")
        garis()
        return

    total_masuk = sum(float(trx["nominal"]) for trx in hasil if trx["jenis"].lower() == "masuk")
    total_keluar = sum(float(trx["nominal"]) for trx in hasil if trx["jenis"].lower() == "keluar")

    print(f"  {'Tanggal':<12} {'ID Transaksi':<24} {'Jenis':<8} {'Nominal':>14} {'Keterangan'}")
    garis("-")
    for trx in sorted(hasil, key=lambda item: (item["tanggal"], item["id_transaksi"])):
        print(
            f"  {trx['tanggal']:<12} "
            f"{trx['id_transaksi'][:22]:<24} "
            f"{trx['jenis']:<8} "
            f"{format_rupiah(trx['nominal']):>14} "
            f"{trx['keterangan']}"
        )

    garis("-")
    print(f"  Total Masuk  : {format_rupiah(total_masuk)}")
    print(f"  Total Keluar : {format_rupiah(total_keluar)}")
    garis()


def dashboard():
    bersihkan_layar()
    cetak_header_app()
    cetak_judul_menu("DASHBOARD MUTASI REKENING")

    rekening_list = baca_rekening()
    transaksi_list = baca_transaksi()

    total_rekening = len(rekening_list)
    total_transaksi = len(transaksi_list)
    total_masuk = sum(float(trx["nominal"]) for trx in transaksi_list if trx["jenis"].lower() == "masuk")
    total_keluar = sum(float(trx["nominal"]) for trx in transaksi_list if trx["jenis"].lower() == "keluar")

    print("  +-----------------------------------------------------+")
    print(f"  |  Total Rekening     : {total_rekening:<5}                          |")
    print(f"  |  Total Transaksi    : {total_transaksi:<5}                          |")
    print(f"  |  Total Pemasukan    : {format_rupiah(total_masuk):<28}|")
    print(f"  |  Total Pengeluaran  : {format_rupiah(total_keluar):<28}|")
    print("  +-----------------------------------------------------+")

    if rekening_list:
        garis("-")
        print(f"  {'No. Rekening':<15} {'Nama Nasabah':<26} {'Tgl Buka':<13} {'Saldo Akhir':>15}")
        garis("-")
        for rek in rekening_list:
            saldo = hitung_saldo_akhir(rek["no_rekening"], rek["saldo_awal"], transaksi_list)
            print(
                f"  {rek['no_rekening']:<15} "
                f"{rek['nama_nasabah']:<26} "
                f"{rek['tanggal_buka']:<13} "
                f"{format_rupiah(saldo):>15}"
            )
        garis("-")

    if transaksi_list:
        print("\n  5 Transaksi Terbaru:")
        garis("-")
        transaksi_terbaru = sorted(transaksi_list, key=lambda trx: (trx["tanggal"], trx["id_transaksi"]))[-5:]
        for trx in reversed(transaksi_terbaru):
            rek = cari_rekening(trx["no_rekening"])
            nama = rek["nama_nasabah"] if rek else "-"
            print(
                f"  {trx['tanggal']}  {trx['no_rekening']}  "
                f"{nama:<20}  {trx['jenis']:<8}  {format_rupiah(trx['nominal'])}"
            )
        garis()


def menu_crud():
    while True:
        bersihkan_layar()
        cetak_header_app()
        cetak_judul_menu("CRUD REKENING & TRANSAKSI")
        print("  [1]  Tambah Nasabah Baru")
        print("  [2]  Lihat Daftar Rekening")
        print("  [3]  Tambah Transaksi")
        print("  [4]  Lihat Mutasi Rekening")
        print("  [5]  Edit Transaksi")
        print("  [6]  Hapus Transaksi")
        print("  [7]  Reset Mutasi Rekening")
        print("  [0]  Kembali ke Menu Utama")
        garis()

        pilih = input("  Pilihan : ").strip()
        print()

        aksi = {
            "1": tambah_nasabah,
            "2": lihat_rekening,
            "3": tambah_transaksi,
            "4": lihat_mutasi,
            "5": edit_transaksi,
            "6": hapus_transaksi,
            "7": reset_mutasi,
        }

        if pilih == "0":
            break
        if pilih in aksi:
            aksi[pilih]()
        else:
            print("  [!] Pilihan tidak valid.")

        input("\n  Tekan Enter untuk melanjutkan...")


def menu_ibnu():
    while True:
        bersihkan_layar()
        cetak_header_app()
        cetak_judul_menu("DOKUMENTASI, TESTING & DEBUGGING")
        print("  [1]  Dokumentasi Project")
        print("  [2]  Panduan Presentasi")
        print("  [3]  Debug Info CSV")
        print("  [4]  Jalankan Self-test")
        print("  [0]  Kembali ke Menu Utama")
        garis()

        pilih = input("  Pilihan : ").strip()
        print()

        if pilih == "1":
            cetak_dokumentasi()
        elif pilih == "2":
            cetak_panduan_presentasi()
        elif pilih == "3":
            cetak_debug_info()
        elif pilih == "4":
            jalankan_self_test()
        elif pilih == "0":
            break
        else:
            print("  [!] Pilihan tidak valid.")

        input("\n  Tekan Enter untuk melanjutkan...")


def main():
    inisialisasi_file()

    while True:
        bersihkan_layar()
        cetak_header_app()
        print("  MENU UTAMA")
        garis("-")
        print("  [1]  CRUD Rekening & Transaksi")
        print("  [2]  Navigasi Periode Mutasi")
        print("  [3]  Searching & Filtering")
        print("  [4]  Manajemen Saldo")
        print("  [5]  Dashboard Mutasi")
        print("  [6]  Dokumentasi, Testing & Debugging")
        print("  [0]  Keluar")
        garis()

        pilih = input("  Pilihan : ").strip()

        menu = {
            "1": menu_crud,
            "2": navigasi_periode,
            "3": searching_filtering,
            "4": manajemen_saldo,
            "5": dashboard,
            "6": menu_ibnu,
        }

        if pilih == "0":
            garis()
            print(f"{'Terima kasih telah menggunakan Bank BUMI ARTHA':^72}")
            print(f"{'Sampai jumpa kembali!':^72}")
            garis()
            break
        if pilih in menu:
            bersihkan_layar()
            cetak_header_app()
            menu[pilih]()
            input("\n  Tekan Enter untuk kembali ke Menu Utama...")
        else:
            print("  [!] Pilihan tidak valid.")
            input("  Tekan Enter untuk melanjutkan...")


if __name__ == "__main__":
    main()

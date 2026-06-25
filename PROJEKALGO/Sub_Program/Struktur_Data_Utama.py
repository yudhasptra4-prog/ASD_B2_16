import csv
import os
import uuid
from collections import deque
from datetime import datetime

from Testing_Debugging import (
    input_tanggal,
    input_valid,
    konfirmasi,
    validasi_format_tanggal,
    validasi_jenis_transaksi,
)


FILE_REKENING = "rekening.csv"
FILE_TRANSAKSI = "transaksi.csv"

HEADER_REKENING = ["no_rekening", "nama_nasabah", "tanggal_buka", "saldo_awal"]
HEADER_TRANSAKSI = ["id_transaksi", "no_rekening", "tanggal", "jenis", "nominal", "keterangan"]

NAMA_BULAN = {
    "01": "Januari",
    "02": "Februari",
    "03": "Maret",
    "04": "April",
    "05": "Mei",
    "06": "Juni",
    "07": "Juli",
    "08": "Agustus",
    "09": "September",
    "10": "Oktober",
    "11": "November",
    "12": "Desember",
}


class NodePeriode:
    """Node doubly linked list untuk satu periode bulan."""

    def __init__(self, periode: str):
        self.periode = periode
        self.next = None
        self.prev = None


class LinkedListPeriode:
    """Doubly linked list untuk navigasi periode mutasi."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def tambah_periode(self, periode: str):
        if not periode:
            return

        node_baru = NodePeriode(periode)
        if not self.head:
            self.head = node_baru
            self.tail = node_baru
            self.current = node_baru
            return

        temp = self.head
        while temp:
            if temp.periode == periode:
                return
            temp = temp.next

        temp = self.head
        while temp and temp.periode < periode:
            temp = temp.next

        if temp is None:
            node_baru.prev = self.tail
            self.tail.next = node_baru
            self.tail = node_baru
        elif temp == self.head:
            node_baru.next = self.head
            self.head.prev = node_baru
            self.head = node_baru
        else:
            node_baru.prev = temp.prev
            node_baru.next = temp
            temp.prev.next = node_baru
            temp.prev = node_baru

    def set_current(self, periode: str) -> bool:
        temp = self.head
        while temp:
            if temp.periode == periode:
                self.current = temp
                return True
            temp = temp.next
        return False

    def periode_sebelumnya(self):
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current.periode
        return None

    def periode_berikutnya(self):
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.periode
        return None

    def get_all_periode(self) -> list:
        hasil = []
        temp = self.head
        while temp:
            hasil.append(temp.periode)
            temp = temp.next
        return hasil


class TransaksiQueue:
    """Queue FIFO untuk memproses transaksi sesuai urutan masuk."""

    def __init__(self):
        self._queue = deque()

    def enqueue(self, transaksi: dict):
        self._queue.append(transaksi)

    def dequeue(self):
        return self._queue.popleft() if self._queue else None

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)


def inisialisasi_file():
    """Buat file CSV beserta header jika belum tersedia."""
    daftar_file = [
        (FILE_REKENING, HEADER_REKENING),
        (FILE_TRANSAKSI, HEADER_TRANSAKSI),
    ]
    for nama_file, header in daftar_file:
        if not os.path.exists(nama_file):
            with open(nama_file, "w", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(header)


def baca_rekening() -> list:
    data = []
    if os.path.exists(FILE_REKENING):
        with open(FILE_REKENING, "r", encoding="utf-8") as file:
            for baris in csv.DictReader(file):
                data.append(dict(baris))
    return data


def simpan_rekening(data: list):
    with open(FILE_REKENING, "w", newline="", encoding="utf-8") as file:
        penulis = csv.DictWriter(file, fieldnames=HEADER_REKENING)
        penulis.writeheader()
        penulis.writerows(data)


def baca_transaksi() -> list:
    data = []
    if os.path.exists(FILE_TRANSAKSI):
        with open(FILE_TRANSAKSI, "r", encoding="utf-8") as file:
            for baris in csv.DictReader(file):
                data.append(dict(baris))
    return data


def simpan_transaksi(data: list):
    data_urut = sorted(data, key=lambda trx: (trx["tanggal"], trx["id_transaksi"]))
    with open(FILE_TRANSAKSI, "w", newline="", encoding="utf-8") as file:
        penulis = csv.DictWriter(file, fieldnames=HEADER_TRANSAKSI)
        penulis.writeheader()
        penulis.writerows(data_urut)


def buat_no_rekening(rekening_list: list) -> str:
    nomor = [
        int(rek["no_rekening"])
        for rek in rekening_list
        if str(rek.get("no_rekening", "")).isdigit()
    ]
    return str(max(nomor, default=1000000) + 1)


def buat_id_transaksi() -> str:
    waktu = datetime.now().strftime("%Y%m%d%H%M%S")
    acak = uuid.uuid4().hex[:4].upper()
    return f"TRX{waktu}{acak}"


def format_rupiah(nominal) -> str:
    try:
        return f"Rp {int(float(nominal)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return f"Rp {nominal}"


def format_periode(periode: str) -> str:
    try:
        tahun, bulan = periode.split("-")
        return f"{NAMA_BULAN.get(bulan, bulan)} {tahun}"
    except (ValueError, AttributeError):
        return str(periode)


def garis(karakter="=", panjang=72):
    print(karakter * panjang)


def cetak_header_app():
    garis()
    print(f"{'BANK BUMI ARTHA':^72}")
    print(f"{'Sistem Informasi Mutasi Rekening':^72}")
    garis()


def cetak_judul_menu(judul: str):
    garis("-")
    print(f"  > {judul}")
    garis("-")


def cari_rekening(no_rekening: str) -> dict:
    for rekening in baca_rekening():
        if rekening["no_rekening"] == no_rekening:
            return rekening
    return None


def hitung_saldo_akhir(no_rekening: str, saldo_awal, transaksi_list: list) -> float:
    saldo = float(saldo_awal)
    for transaksi in transaksi_list:
        if transaksi["no_rekening"] != no_rekening:
            continue
        if transaksi["jenis"].lower() == "masuk":
            saldo += float(transaksi["nominal"])
        else:
            saldo -= float(transaksi["nominal"])
    return saldo


def hitung_ringkasan_saldo(no_rekening: str, transaksi_list: list, periode: str = None) -> tuple:
    queue = TransaksiQueue()
    transaksi_urut = sorted(
        [trx for trx in transaksi_list if trx["no_rekening"] == no_rekening],
        key=lambda trx: (trx["tanggal"], trx["id_transaksi"]),
    )
    for transaksi in transaksi_urut:
        queue.enqueue(transaksi)

    total_masuk = 0.0
    total_keluar = 0.0

    while not queue.is_empty():
        transaksi = queue.dequeue()
        if periode and not transaksi["tanggal"].startswith(periode):
            continue
        if transaksi["jenis"].lower() == "masuk":
            total_masuk += float(transaksi["nominal"])
        else:
            total_keluar += float(transaksi["nominal"])

    return total_masuk, total_keluar


def tambah_nasabah():
    cetak_judul_menu("TAMBAH NASABAH BARU")
    rekening_list = baca_rekening()

    nama = input("  Nama Nasabah     : ").strip()
    if not nama:
        print("  [!] Nama tidak boleh kosong.")
        return

    tanggal_buka = input_tanggal("  Tanggal Buka     : ")
    saldo_awal = input_valid("  Saldo Awal (Rp)  : ", tipe="float", min_val=0)

    no_rek = buat_no_rekening(rekening_list)
    rekening_baru = {
        "no_rekening": no_rek,
        "nama_nasabah": nama,
        "tanggal_buka": tanggal_buka,
        "saldo_awal": str(int(saldo_awal)),
    }

    rekening_list.append(rekening_baru)
    simpan_rekening(rekening_list)

    garis("-")
    print("  [OK] Nasabah berhasil didaftarkan!")
    print(f"      Nomor Rekening  : {no_rek}")
    print(f"      Nama Nasabah    : {nama}")
    print(f"      Tanggal Buka    : {tanggal_buka}")
    print(f"      Saldo Awal      : {format_rupiah(saldo_awal)}")
    garis("-")


def lihat_rekening():
    cetak_judul_menu("DAFTAR REKENING NASABAH")
    rekening_list = baca_rekening()
    transaksi_list = baca_transaksi()

    if not rekening_list:
        print("  Belum ada data rekening.")
        return

    print(f"  {'No':<4} {'No. Rekening':<14} {'Nama Nasabah':<26} {'Tgl Buka':<13} {'Saldo Akhir':>16}")
    garis("-")

    for nomor, rekening in enumerate(rekening_list, 1):
        saldo = hitung_saldo_akhir(rekening["no_rekening"], rekening["saldo_awal"], transaksi_list)
        print(
            f"  {nomor:<4} {rekening['no_rekening']:<14} "
            f"{rekening['nama_nasabah']:<26} {rekening['tanggal_buka']:<13} "
            f"{format_rupiah(saldo):>16}"
        )

    garis("-")
    print(f"  Total: {len(rekening_list)} rekening terdaftar")


def tambah_transaksi():
    cetak_judul_menu("TAMBAH TRANSAKSI")
    no_rek = input("  Nomor Rekening : ").strip()
    rekening = cari_rekening(no_rek)

    if not rekening:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()
    saldo_kini = hitung_saldo_akhir(no_rek, rekening["saldo_awal"], transaksi_list)

    print(f"  Nasabah        : {rekening['nama_nasabah']}")
    print(f"  Saldo Saat Ini : {format_rupiah(saldo_kini)}")
    garis("-")

    tanggal = input_tanggal("  Tanggal             : ")
    jenis = input_valid("  Jenis (masuk/keluar): ", pilihan=["masuk", "keluar"])
    nominal = input_valid("  Nominal (Rp)        : ", tipe="float", min_val=1)
    keterangan = input("  Keterangan          : ").strip() or "-"

    if jenis == "keluar" and nominal > saldo_kini:
        print(f"  [!] Saldo tidak mencukupi. Saldo tersedia: {format_rupiah(saldo_kini)}")
        return

    id_trx = buat_id_transaksi()
    transaksi_baru = {
        "id_transaksi": id_trx,
        "no_rekening": no_rek,
        "tanggal": tanggal,
        "jenis": jenis,
        "nominal": str(int(nominal)),
        "keterangan": keterangan,
    }

    queue = TransaksiQueue()
    queue.enqueue(transaksi_baru)
    while not queue.is_empty():
        transaksi_list.append(queue.dequeue())

    simpan_transaksi(transaksi_list)
    saldo_baru = hitung_saldo_akhir(no_rek, rekening["saldo_awal"], baca_transaksi())

    garis("-")
    print("  [OK] Transaksi berhasil disimpan!")
    print(f"      ID Transaksi : {id_trx}")
    print(f"      Saldo Akhir  : {format_rupiah(saldo_baru)}")
    garis("-")


def edit_transaksi():
    cetak_judul_menu("EDIT TRANSAKSI")
    id_trx = input("  ID Transaksi : ").strip()
    transaksi_list = baca_transaksi()

    indeks = None
    for i, transaksi in enumerate(transaksi_list):
        if transaksi["id_transaksi"] == id_trx:
            indeks = i
            break

    if indeks is None:
        print("  [!] ID transaksi tidak ditemukan.")
        return

    transaksi = transaksi_list[indeks]
    rekening = cari_rekening(transaksi["no_rekening"])
    nama = rekening["nama_nasabah"] if rekening else "-"

    garis("-")
    print("  Data Transaksi Saat Ini:")
    print(f"  |- Rekening   : {transaksi['no_rekening']} ({nama})")
    print(f"  |- Tanggal    : {transaksi['tanggal']}")
    print(f"  |- Jenis      : {transaksi['jenis']}")
    print(f"  |- Nominal    : {format_rupiah(transaksi['nominal'])}")
    print(f"  |- Keterangan : {transaksi['keterangan']}")
    garis("-")
    print("  Kosongkan field jika tidak ingin mengubah data.")

    tanggal_baru = input("  Tanggal baru (YYYY-MM-DD): ").strip()
    jenis_baru = input("  Jenis baru (masuk/keluar): ").strip().lower()
    nominal_baru = input("  Nominal baru             : ").strip()
    keterangan_baru = input("  Keterangan baru          : ").strip()

    ada_perubahan = False

    if tanggal_baru:
        if validasi_format_tanggal(tanggal_baru):
            transaksi_list[indeks]["tanggal"] = tanggal_baru
            ada_perubahan = True
        else:
            print("  [!] Format tanggal salah, perubahan tanggal diabaikan.")

    if jenis_baru:
        if validasi_jenis_transaksi(jenis_baru):
            transaksi_list[indeks]["jenis"] = jenis_baru
            ada_perubahan = True
        else:
            print("  [!] Jenis harus 'masuk' atau 'keluar', perubahan jenis diabaikan.")

    if nominal_baru:
        try:
            nilai_nominal = float(nominal_baru)
            if nilai_nominal <= 0:
                print("  [!] Nominal harus lebih dari 0, perubahan nominal diabaikan.")
            else:
                transaksi_list[indeks]["nominal"] = str(int(nilai_nominal))
                ada_perubahan = True
        except ValueError:
            print("  [!] Nominal tidak valid, perubahan nominal diabaikan.")

    if keterangan_baru:
        transaksi_list[indeks]["keterangan"] = keterangan_baru
        ada_perubahan = True

    if ada_perubahan:
        simpan_transaksi(transaksi_list)
        print("  [OK] Transaksi berhasil diperbarui!")
    else:
        print("  [i] Tidak ada perubahan.")


def hapus_transaksi():
    cetak_judul_menu("HAPUS TRANSAKSI")
    id_trx = input("  ID Transaksi : ").strip()
    transaksi_list = baca_transaksi()

    transaksi_ditemukan = any(transaksi["id_transaksi"] == id_trx for transaksi in transaksi_list)
    if not transaksi_ditemukan:
        print("  [!] ID transaksi tidak ditemukan.")
        return

    if konfirmasi(f"Yakin menghapus transaksi '{id_trx}'?"):
        transaksi_baru = [
            transaksi for transaksi in transaksi_list
            if transaksi["id_transaksi"] != id_trx
        ]
        simpan_transaksi(transaksi_baru)
        print("  [OK] Transaksi berhasil dihapus!")
    else:
        print("  [i] Penghapusan dibatalkan.")


def reset_mutasi():
    cetak_judul_menu("RESET MUTASI REKENING")
    no_rek = input("  Nomor Rekening : ").strip()
    rekening = cari_rekening(no_rek)

    if not rekening:
        print("  [!] Rekening tidak ditemukan.")
        return

    print(f"  Nasabah: {rekening['nama_nasabah']}")
    if konfirmasi(f"Yakin mereset semua mutasi rekening {no_rek}?"):
        transaksi_list = baca_transaksi()
        transaksi_baru = [
            transaksi for transaksi in transaksi_list
            if transaksi["no_rekening"] != no_rek
        ]
        simpan_transaksi(transaksi_baru)
        print("  [OK] Seluruh mutasi rekening berhasil direset!")
    else:
        print("  [i] Reset dibatalkan.")


def manajemen_saldo():
    cetak_judul_menu("MANAJEMEN SALDO REKENING")
    no_rek = input("  Nomor Rekening : ").strip()
    rekening = cari_rekening(no_rek)

    if not rekening:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()
    total_masuk, total_keluar = hitung_ringkasan_saldo(no_rek, transaksi_list)

    saldo_awal = float(rekening["saldo_awal"])
    saldo_akhir = saldo_awal + total_masuk - total_keluar

    garis()
    print(f"  REKENING  : {rekening['no_rekening']}")
    print(f"  NASABAH   : {rekening['nama_nasabah']}")
    print(f"  TGL BUKA  : {rekening['tanggal_buka']}")
    garis("-")
    print(f"  {'Saldo Awal':<30} : {format_rupiah(saldo_awal)}")
    print(f"  {'(+) Total Pemasukan':<30} : {format_rupiah(total_masuk)}")
    print(f"  {'(-) Total Pengeluaran':<30} : {format_rupiah(total_keluar)}")
    garis("-")
    print(f"  {'= SALDO AKHIR':<30} : {format_rupiah(saldo_akhir)}")
    garis()

    daftar_periode = LinkedListPeriode()
    for transaksi in transaksi_list:
        if transaksi["no_rekening"] == no_rek:
            daftar_periode.tambah_periode(transaksi["tanggal"][:7])

    semua_periode = daftar_periode.get_all_periode()
    if not semua_periode:
        return

    print("\n  Rincian Saldo per Periode:")
    garis("-")
    print(f"  {'Periode':<20} {'Total Masuk':>16} {'Total Keluar':>16} {'Saldo Akhir':>16}")
    garis("-")

    saldo_berjalan = saldo_awal
    for periode in semua_periode:
        masuk, keluar = hitung_ringkasan_saldo(no_rek, transaksi_list, periode)
        saldo_berjalan += masuk - keluar
        print(
            f"  {format_periode(periode):<20} "
            f"{format_rupiah(masuk):>16} "
            f"{format_rupiah(keluar):>16} "
            f"{format_rupiah(saldo_berjalan):>16}"
        )
    garis("-")

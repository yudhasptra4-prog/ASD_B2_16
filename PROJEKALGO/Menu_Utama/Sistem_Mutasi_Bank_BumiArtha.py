# ===================================================================
# JUDUL PROGRAM  : Sistem Riwayat Transaksi Rekening Bank Bumi Artha
# MATA KULIAH    : Algoritma & Struktur Data    
# KELAS          : TPL-B
# KELOMPOK       : 16
#
# ANGGOTA KELOMPOK:
# 1. Muhammad Ibnu Akbar       (J0403251028)
# 2. Yudha Saputra             (J0403251119)
# 3. Muhammad Ridzqi Badarudin (J0403251146)
# ===================================================================
# Struktur Data yang digunakan:
# - List / Array List    : Penyimpanan data rekening & transaksi
# - Linked List          : Navigasi antar periode mutasi
# - Queue (deque)        : Pemrosesan transaksi urut waktu
# - File CSV             : Penyimpanan data permanen

# Konsep Algoritma:
# - CRUD                 : Kelola rekening & transaksi
# - Sequential Searching : Cari transaksi berdasarkan kriteria
# - Filtering            : Saring transaksi tertentu
# - Traversal            : Hitung saldo & tampilkan mutasi
# ===================================================================

import csv
import os
import uuid
from datetime import datetime
from collections import deque


# =================================================================
#                     STRUKTUR DATA: LINKED LIST                  
#               (Navigasi antar periode bulan mutasi)            
# =================================================================

class NodePeriode:
    """
    Node dalam Doubly Linked List untuk merepresentasikan satu periode (bulan).
    Setiap node memiliki pointer ke periode sebelum dan sesudahnya.
    """
    def __init__(self, periode: str):
        self.periode = periode   # Format: "YYYY-MM"
        self.next = None         # Pointer ke periode berikutnya
        self.prev = None         # Pointer ke periode sebelumnya


class LinkedListPeriode:
    """
    Doubly Linked List yang menyimpan daftar periode (bulan-tahun) secara urut.
    Digunakan untuk navigasi maju/mundur antar periode mutasi.
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None   # Pointer posisi periode yang sedang aktif

    def tambah_periode(self, periode: str):
        """Tambah periode baru ke linked list secara terurut (tidak duplikat)."""
        node_baru = NodePeriode(periode)

        if not self.head:
            self.head = node_baru
            self.tail = node_baru
            self.current = node_baru
            return

        # Cek duplikat dengan traversal
        temp = self.head
        while temp:
            if temp.periode == periode:
                return   # Periode sudah ada, abaikan
            temp = temp.next

        # Cari posisi insert agar urut ascending
        temp = self.head
        while temp and temp.periode < periode:
            temp = temp.next

        if not temp:
            # Insert di akhir (tail)
            node_baru.prev = self.tail
            self.tail.next = node_baru
            self.tail = node_baru
        elif temp == self.head:
            # Insert di awal (head)
            node_baru.next = self.head
            self.head.prev = node_baru
            self.head = node_baru
        else:
            # Insert di tengah
            node_baru.prev = temp.prev
            node_baru.next = temp
            temp.prev.next = node_baru
            temp.prev = node_baru

    def set_current(self, periode: str) -> bool:
        """Pindahkan posisi current ke periode tertentu."""
        temp = self.head
        while temp:
            if temp.periode == periode:
                self.current = temp
                return True
            temp = temp.next
        return False

    def periode_sebelumnya(self):
        """Geser current mundur ke periode sebelumnya (traversal backward)."""
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current.periode
        return None

    def periode_berikutnya(self):
        """Geser current maju ke periode berikutnya (traversal forward)."""
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.periode
        return None

    def get_all_periode(self) -> list:
        """Traversal seluruh linked list, kembalikan semua periode dalam list."""
        hasil = []
        temp = self.head
        while temp:
            hasil.append(temp.periode)
            temp = temp.next
        return hasil


# =================================================================
#              STRUKTUR DATA: QUEUE (ANTRIAN)               
#      (Pemrosesan transaksi sesuai urutan waktu masuk)     
# =================================================================

class TransaksiQueue:
    """
    Queue berbasis deque untuk memproses transaksi secara FIFO.
    Transaksi yang masuk lebih awal akan diproses lebih dahulu (urutan waktu).
    """

    def __init__(self):
        self._queue = deque()

    def enqueue(self, transaksi: dict):
        """Tambahkan transaksi ke antrian (masuk dari belakang)."""
        self._queue.append(transaksi)

    def dequeue(self) -> dict:
        """Ambil & hapus transaksi paling awal dari antrian (keluar dari depan)."""
        return self._queue.popleft() if self._queue else None

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)


# =================================================================
#               KONSTANTA & KONFIGURASI FILE CSV             
# =================================================================

FILE_REKENING   = "rekening.csv"
FILE_TRANSAKSI  = "transaksi.csv"

HEADER_REKENING   = ["no_rekening", "nama_nasabah", "tanggal_buka", "saldo_awal"]
HEADER_TRANSAKSI  = ["id_transaksi", "no_rekening", "tanggal", "jenis", "nominal", "keterangan"]

NAMA_BULAN = {
    "01": "Januari",  "02": "Februari", "03": "Maret",    "04": "April",
    "05": "Mei",      "06": "Juni",     "07": "Juli",     "08": "Agustus",
    "09": "September","10": "Oktober",  "11": "November", "12": "Desember"
}


# ===================================================================
#                   MODUL: PENGELOLAAN FILE CSV                
# ===================================================================

def inisialisasi_file():
    """Buat file CSV jika belum ada, dengan header yang sesuai."""
    for file, header in [(FILE_REKENING, HEADER_REKENING),
                         (FILE_TRANSAKSI, HEADER_TRANSAKSI)]:
        if not os.path.exists(file):
            with open(file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(header)


def baca_rekening() -> list:
    """Baca semua data rekening dari CSV ke dalam List."""
    data = []
    if os.path.exists(FILE_REKENING):
        with open(FILE_REKENING, "r", encoding="utf-8") as f:
            for baris in csv.DictReader(f):
                data.append(dict(baris))
    return data


def simpan_rekening(data: list):
    """Simpan List rekening ke file CSV (overwrite)."""
    with open(FILE_REKENING, "w", newline="", encoding="utf-8") as f:
        penulis = csv.DictWriter(f, fieldnames=HEADER_REKENING)
        penulis.writeheader()
        penulis.writerows(data)


def baca_transaksi() -> list:
    """Baca semua data transaksi dari CSV ke dalam List."""
    data = []
    if os.path.exists(FILE_TRANSAKSI):
        with open(FILE_TRANSAKSI, "r", encoding="utf-8") as f:
            for baris in csv.DictReader(f):
                data.append(dict(baris))
    return data


def simpan_transaksi(data: list):
    """Simpan List transaksi ke file CSV (overwrite)."""
    with open(FILE_TRANSAKSI, "w", newline="", encoding="utf-8") as f:
        penulis = csv.DictWriter(f, fieldnames=HEADER_TRANSAKSI)
        penulis.writeheader()
        penulis.writerows(data)


# ================================================================
#                           UTILITAS                        
# ================================================================

def buat_no_rekening(rekening_list: list) -> str:
    """Generate nomor rekening baru secara otomatis (increment +1)."""
    if not rekening_list:
        return "1000001"
    nomor_terakhir = max(int(r["no_rekening"]) for r in rekening_list)
    return str(nomor_terakhir + 1)


def buat_id_transaksi() -> str:
    """Generate ID transaksi unik berdasarkan timestamp + UUID."""
    return "TRX" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:4].upper()


def format_rupiah(nominal) -> str:
    """Format angka menjadi string mata uang Rupiah."""
    try:
        return f"Rp {int(float(nominal)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return f"Rp {nominal}"


def format_periode(periode: str) -> str:
    """Ubah format 'YYYY-MM' menjadi 'Nama Bulan YYYY'."""
    try:
        tahun, bln = periode.split("-")
        return f"{NAMA_BULAN.get(bln, bln)} {tahun}"
    except Exception:
        return periode


def garis(karakter="=", panjang=72):
    print(karakter * panjang)


def pendekkan_teks(nilai, lebar: int) -> str:
    """Potong teks agar tidak melewati lebar kolom tabel."""
    teks = " ".join(str(nilai).split())
    if len(teks) <= lebar:
        return teks
    if lebar <= 3:
        return teks[:lebar]
    return teks[:lebar - 3] + "..."


def format_kolom(nilai, lebar: int, rata: str = "left") -> str:
    """Format satu nilai tabel sesuai lebar dan perataan kolom."""
    teks = pendekkan_teks(nilai, lebar)
    if rata == "right":
        return f"{teks:>{lebar}}"
    if rata == "center":
        return f"{teks:^{lebar}}"
    return f"{teks:<{lebar}}"


def cetak_garis_tabel(lebar_kolom: list):
    """Cetak garis pemisah tabel dengan panjang mengikuti total kolom."""
    print("  " + "-+-".join("-" * lebar for lebar in lebar_kolom))


def cetak_baris_tabel(nilai_kolom: list, lebar_kolom: list, rata_kolom: list = None):
    """Cetak satu baris tabel supaya semua kolom tetap sejajar."""
    if rata_kolom is None:
        rata_kolom = ["left"] * len(lebar_kolom)

    kolom = [
        format_kolom(nilai, lebar, rata)
        for nilai, lebar, rata in zip(nilai_kolom, lebar_kolom, rata_kolom)
    ]
    print("  " + " | ".join(kolom))


def cetak_header_tabel(header: list, lebar_kolom: list):
    """Cetak header tabel beserta garis bawahnya."""
    cetak_baris_tabel(header, lebar_kolom, ["center"] * len(lebar_kolom))
    cetak_garis_tabel(lebar_kolom)


def cetak_header_app():
    garis()
    print(f"{'BANK BUMI ARTHA':^72}")
    print(f"{'Sistem Informasi Mutasi Rekening':^72}")
    garis()


def cetak_judul_menu(judul: str):
    garis("-")
    print(f"  ▸ {judul}")
    garis("-")


def input_valid(prompt: str, tipe="str", min_val=None, pilihan=None):
    """Input dengan validasi tipe, nilai minimal, dan pilihan."""
    while True:
        try:
            nilai = input(prompt).strip()
            if tipe == "int":
                nilai = int(nilai)
                if min_val is not None and nilai < min_val:
                    print(f"  [!] Nilai minimal adalah {min_val}")
                    continue
            elif tipe == "float":
                nilai = float(nilai)
                if min_val is not None and nilai < min_val:
                    print(f"  [!] Nilai minimal adalah {min_val}")
                    continue
            if pilihan and nilai not in pilihan:
                print(f"  [!] Pilih salah satu dari: {', '.join(pilihan)}")
                continue
            return nilai
        except ValueError:
            print("  [!] Input tidak valid, coba lagi.")


def input_tanggal(prompt: str) -> str:
    """Input tanggal dengan validasi format YYYY-MM-DD."""
    while True:
        tgl = input(prompt).strip()
        try:
            datetime.strptime(tgl, "%Y-%m-%d")
            return tgl
        except ValueError:
            print("  [!] Format salah. Gunakan: YYYY-MM-DD  (contoh: 2025-03-15)")


def konfirmasi(pesan: str) -> bool:
    """Minta konfirmasi ya/tidak dari pengguna."""
    jawab = input(f"  {pesan} (y/n): ").strip().lower()
    return jawab == "y"


# ==================================================================
#                      LOGIKA REKENING & SALDO             
# ==================================================================

def cari_rekening(no_rekening: str) -> dict:
    """Sequential search rekening berdasarkan nomor rekening."""
    for rek in baca_rekening():      # Traversal list
        if rek["no_rekening"] == no_rekening:
            return rek
    return None


def hitung_saldo_akhir(no_rekening: str, saldo_awal, transaksi_list: list) -> float:
    """
    Hitung saldo akhir dengan traversal seluruh transaksi.
    Saldo akhir = Saldo awal + Total masuk - Total keluar
    """
    saldo = float(saldo_awal)
    for trx in transaksi_list:       # Traversal list transaksi
        if trx["no_rekening"] == no_rekening:
            if trx["jenis"].lower() == "masuk":
                saldo += float(trx["nominal"])
            else:
                saldo -= float(trx["nominal"])
    return saldo


def hitung_ringkasan_saldo(no_rekening: str, transaksi_list: list,
                           periode: str = None) -> tuple:
    """
    Hitung total masuk & keluar dengan Queue dan traversal.
    Gunakan parameter `periode` (YYYY-MM) untuk filter per bulan.
    """
    queue = TransaksiQueue()

    # Masukkan semua transaksi ke Queue sesuai urutan waktu
    trx_terurut = sorted(
        [t for t in transaksi_list if t["no_rekening"] == no_rekening],
        key=lambda x: x["tanggal"]
    )
    for trx in trx_terurut:
        queue.enqueue(trx)

    total_masuk = 0.0
    total_keluar = 0.0

    # Proses antrian (FIFO)
    while not queue.is_empty():
        trx = queue.dequeue()
        if periode and not trx["tanggal"].startswith(periode):
            continue
        if trx["jenis"].lower() == "masuk":
            total_masuk += float(trx["nominal"])
        else:
            total_keluar += float(trx["nominal"])

    return total_masuk, total_keluar


# =================================================================
#              FITUR 1: CRUD REKENING & TRANSAKSI            
# =================================================================

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
        "no_rekening" : no_rek,
        "nama_nasabah": nama,
        "tanggal_buka": tanggal_buka,
        "saldo_awal"  : str(int(saldo_awal))
    }

    rekening_list.append(rekening_baru)
    simpan_rekening(rekening_list)

    garis("-")
    print("  [✓] Nasabah berhasil didaftarkan!")
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

    # Lebar kolom dibuat tetap agar nama atau saldo panjang tidak menggeser tabel.
    lebar_kolom = [4, 14, 26, 13, 16]
    rata_kolom = ["right", "left", "left", "left", "right"]
    cetak_header_tabel(
        ["No", "No. Rekening", "Nama Nasabah", "Tgl Buka", "Saldo Akhir"],
        lebar_kolom
    )

    # Traversal list rekening
    for i, rek in enumerate(rekening_list, 1):
        saldo = hitung_saldo_akhir(rek["no_rekening"], rek["saldo_awal"], transaksi_list)
        cetak_baris_tabel(
            [i, rek["no_rekening"], rek["nama_nasabah"], rek["tanggal_buka"], format_rupiah(saldo)],
            lebar_kolom,
            rata_kolom
        )

    cetak_garis_tabel(lebar_kolom)
    print(f"  Total: {len(rekening_list)} rekening terdaftar")


def tambah_transaksi():
    cetak_judul_menu("TAMBAH TRANSAKSI")

    no_rek = input("  Nomor Rekening : ").strip()
    rek = cari_rekening(no_rek)
    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()
    saldo_kini = hitung_saldo_akhir(no_rek, rek["saldo_awal"], transaksi_list)

    print(f"  Nasabah        : {rek['nama_nasabah']}")
    print(f"  Saldo Saat Ini : {format_rupiah(saldo_kini)}")
    garis("-")

    tanggal   = input_tanggal("  Tanggal           : ")
    jenis     = input_valid("  Jenis (masuk/keluar): ", pilihan=["masuk", "keluar"])
    nominal   = input_valid("  Nominal (Rp)       : ", tipe="float", min_val=1)
    keterangan = input("  Keterangan         : ").strip() or "-"

    if jenis == "keluar" and nominal > saldo_kini:
        print(f"  [!] Saldo tidak mencukupi. Saldo tersedia: {format_rupiah(saldo_kini)}")
        return

    id_trx = buat_id_transaksi()
    transaksi_baru = {
        "id_transaksi": id_trx,
        "no_rekening" : no_rek,
        "tanggal"     : tanggal,
        "jenis"       : jenis,
        "nominal"     : str(int(nominal)),
        "keterangan"  : keterangan
    }

    # Gunakan Queue untuk memastikan urutan pemrosesan
    q = TransaksiQueue()
    q.enqueue(transaksi_baru)
    while not q.is_empty():
        transaksi_list.append(q.dequeue())

    # Sort berdasarkan tanggal agar urut
    transaksi_list.sort(key=lambda x: x["tanggal"])
    simpan_transaksi(transaksi_list)

    saldo_baru = hitung_saldo_akhir(no_rek, rek["saldo_awal"], transaksi_list)
    garis("-")
    print("  [✓] Transaksi berhasil disimpan!")
    print(f"      ID Transaksi : {id_trx}")
    print(f"      Saldo Akhir  : {format_rupiah(saldo_baru)}")
    garis("-")


def lihat_mutasi(no_rek: str = None, periode: str = None, dari_menu: bool = True):
    """
    Tampilkan mutasi rekening dalam format tabel menyerupai buku tabungan.
    Menggunakan traversal data dan perhitungan saldo berjalan.
    """
    if dari_menu:
        cetak_judul_menu("LIHAT MUTASI REKENING")
        no_rek = input("  Nomor Rekening : ").strip()

    rek = cari_rekening(no_rek)
    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()

    # Traversal: filter transaksi sesuai rekening & periode
    mutasi = []
    for trx in transaksi_list:
        if trx["no_rekening"] == no_rek:
            if periode is None or trx["tanggal"].startswith(periode):
                mutasi.append(trx)

    # Cetak Header Mutasi
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
        print("  Tidak ada transaksi" + (f" pada periode {format_periode(periode)}." if periode else "."))
    else:
        # Helper tabel menjaga kolom debit/kredit/saldo tetap rata kanan.
        lebar_kolom = [10, 22, 22, 16, 16, 16]
        rata_kolom = ["left", "left", "left", "right", "right", "right"]
        cetak_header_tabel(
            ["Tanggal", "ID Transaksi", "Keterangan", "Debit", "Kredit", "Saldo"],
            lebar_kolom
        )

        # Hitung saldo awal sebelum periode aktif (jika ada filter)
        saldo_running = float(rek["saldo_awal"])
        if periode:
            for trx in transaksi_list:
                if (trx["no_rekening"] == no_rek
                        and trx["tanggal"] < periode + "-01"):
                    if trx["jenis"].lower() == "masuk":
                        saldo_running += float(trx["nominal"])
                    else:
                        saldo_running -= float(trx["nominal"])

        total_masuk = 0.0
        total_keluar = 0.0

        # Traversal data mutasi untuk ditampilkan
        for trx in mutasi:
            nominal = float(trx["nominal"])
            if trx["jenis"].lower() == "masuk":
                saldo_running += nominal
                total_masuk  += nominal
                str_masuk  = format_rupiah(nominal)
                str_keluar = "-"
            else:
                saldo_running -= nominal
                total_keluar  += nominal
                str_masuk  = "-"
                str_keluar = format_rupiah(nominal)

            cetak_baris_tabel(
                [
                    trx["tanggal"],
                    trx["id_transaksi"],
                    trx["keterangan"],
                    str_masuk,
                    str_keluar,
                    format_rupiah(saldo_running)
                ],
                lebar_kolom,
                rata_kolom
            )

        cetak_garis_tabel(lebar_kolom)
        # Baris total dibuat sebagai baris tabel agar sejajar dengan nominal transaksi.
        cetak_baris_tabel(
            ["", "", "TOTAL", format_rupiah(total_masuk),
             format_rupiah(total_keluar), format_rupiah(saldo_running)],
            lebar_kolom,
            rata_kolom
        )

    garis()
    print(f"  Saldo Akhir: {format_rupiah(hitung_saldo_akhir(no_rek, rek['saldo_awal'], transaksi_list))}")
    garis()


def edit_transaksi():
    cetak_judul_menu("EDIT TRANSAKSI")
    id_trx = input("  ID Transaksi : ").strip()

    transaksi_list = baca_transaksi()
    idx = None

    # Sequential search ID transaksi
    for i, trx in enumerate(transaksi_list):
        if trx["id_transaksi"] == id_trx:
            idx = i
            break

    if idx is None:
        print("  [!] ID transaksi tidak ditemukan.")
        return

    trx = transaksi_list[idx]
    rek = cari_rekening(trx["no_rekening"])
    nama = rek["nama_nasabah"] if rek else "-"

    garis("-")
    print("  Data Transaksi Saat Ini:")
    print(f" Rekening   : {trx['no_rekening']} ({nama})")
    print(f" Tanggal    : {trx['tanggal']}")
    print(f" Jenis      : {trx['jenis']}")
    print(f" Nominal    : {format_rupiah(trx['nominal'])}")
    print(f" Keterangan : {trx['keterangan']}")
    garis("-")
    print("  (Kosongkan field = tidak diubah)")

    nominal_baru   = input("  Nominal baru      : ").strip()
    jenis_baru     = input("  Jenis baru        : ").strip().lower()
    ket_baru       = input("  Keterangan baru   : ").strip()

    ada_perubahan = False

    if nominal_baru:
        try:
            transaksi_list[idx]["nominal"] = str(int(float(nominal_baru)))
            ada_perubahan = True
        except ValueError:
            print("  [!] Nominal tidak valid, perubahan nominal diabaikan.")

    if jenis_baru:
        if jenis_baru not in ["masuk", "keluar"]:
            print("  [!] Jenis harus 'masuk' atau 'keluar', perubahan jenis diabaikan.")
        else:
            transaksi_list[idx]["jenis"] = jenis_baru
            ada_perubahan = True

    if ket_baru:
        transaksi_list[idx]["keterangan"] = ket_baru
        ada_perubahan = True

    if ada_perubahan:
        simpan_transaksi(transaksi_list)
        print("  [✓] Transaksi berhasil diperbarui!")
    else:
        print("  [i] Tidak ada perubahan.")


def hapus_transaksi():
    cetak_judul_menu("HAPUS TRANSAKSI")
    id_trx = input("  ID Transaksi : ").strip()

    transaksi_list = baca_transaksi()
    transaksi_ditemukan = any(t["id_transaksi"] == id_trx for t in transaksi_list)

    if not transaksi_ditemukan:
        print("  [!] ID transaksi tidak ditemukan.")
        return

    if konfirmasi(f"Yakin menghapus transaksi '{id_trx}'?"):
        transaksi_baru = [t for t in transaksi_list if t["id_transaksi"] != id_trx]
        simpan_transaksi(transaksi_baru)
        print("  [✓] Transaksi berhasil dihapus!")
    else:
        print("  [i] Penghapusan dibatalkan.")


def reset_mutasi():
    cetak_judul_menu("RESET MUTASI REKENING")
    no_rek = input("  Nomor Rekening : ").strip()
    rek = cari_rekening(no_rek)

    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    print(f"  Nasabah: {rek['nama_nasabah']}")

    if konfirmasi(f"Yakin mereset SEMUA mutasi rekening {no_rek}?"):
        transaksi_list = baca_transaksi()
        transaksi_baru = [t for t in transaksi_list if t["no_rekening"] != no_rek]
        simpan_transaksi(transaksi_baru)
        print("  [✓] Seluruh mutasi rekening berhasil direset!")
    else:
        print("  [i] Reset dibatalkan.")


# =================================================================
#             FITUR 2: NAVIGASI PERIODE MUTASI                
#           (Menggunakan Linked List & Traversal)  
# =================================================================               

def navigasi_periode():
    cetak_judul_menu("NAVIGASI PERIODE MUTASI")
    no_rek = input("  Nomor Rekening : ").strip()
    rek = cari_rekening(no_rek)

    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()

    # Bangun Linked List periode dari data transaksi
    ll = LinkedListPeriode()
    for trx in transaksi_list:
        if trx["no_rekening"] == no_rek:
            periode = trx["tanggal"][:7]   # Ambil "YYYY-MM"
            ll.tambah_periode(periode)

    semua_periode = ll.get_all_periode()

    if not semua_periode:
        print("  Rekening ini belum memiliki transaksi.")
        return

    # Set posisi awal ke periode terkini
    ll.set_current(semua_periode[-1])

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        cetak_header_app()
        cetak_judul_menu("NAVIGASI PERIODE MUTASI")

        print(f"  Nasabah      : {rek['nama_nasabah']}")
        print(f"  No. Rekening : {no_rek}")
        garis("-")
        print(f"  ◀  {ll.current.prev.periode if ll.current.prev else '(awal)'}"
              f"   ●  [{format_periode(ll.current.periode)}]"
              f"   ▶  {format_periode(ll.current.next.periode) if ll.current.next else '(akhir)'}")
        garis("-")

        print(f"\n  Semua Periode Tersedia:")
        for i, p in enumerate(semua_periode):
            penanda = " ◄ (aktif)" if p == ll.current.periode else ""
            print(f"    [{i+1}] {format_periode(p)}{penanda}")

        garis("-")
        print("  [1]    Periode Sebelumnya")
        print("  [2]    Periode Berikutnya")
        print("  [3]    Lihat Mutasi Periode Ini")
        print("  [4]    Pilih Periode Manual")
        print("  [0]    Kembali")

        pilih = input("\n  Pilihan : ").strip()

        if pilih == "1":
            p = ll.periode_sebelumnya()
            print(f"  → Pindah ke: {format_periode(p)}" if p else
                  "  [!] Sudah di periode paling awal.")
            input("  Tekan Enter...")

        elif pilih == "2":
            p = ll.periode_berikutnya()
            print(f"  → Pindah ke: {format_periode(p)}" if p else
                  "  [!] Sudah di periode paling akhir.")
            input("  Tekan Enter...")

        elif pilih == "3":
            lihat_mutasi(no_rek, ll.current.periode, dari_menu=False)
            input("\n  Tekan Enter...")

        elif pilih == "4":
            for i, p in enumerate(semua_periode):
                print(f"  [{i+1}] {format_periode(p)}")
            idx_pilih = input_valid("  Nomor periode: ", tipe="int",
                                    min_val=1) - 1
            if 0 <= idx_pilih < len(semua_periode):
                ll.set_current(semua_periode[idx_pilih])
            else:
                print("  [!] Nomor tidak valid.")
            input("  Tekan Enter...")

        elif pilih == "0":
            break


# =================================================================
#           FITUR 3: SEARCHING & FILTERING TRANSAKSI         
#          (Sequential Searching & Filter Traversal)          
# =================================================================

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
    print("  [4] Filter: Transaksi Masuk saja")
    print("  [5] Filter: Transaksi Keluar saja")
    print("  [6] Filter: Berdasarkan Periode (Bulan)")
    garis("-")

    pilih = input("  Pilihan : ").strip()

    transaksi_list = baca_transaksi()
    hasil = []
    judul = ""

    if pilih == "1":
        kata_kunci = input("  Tanggal (YYYY-MM-DD / YYYY-MM / YYYY): ").strip()
        # Sequential searching berdasarkan tanggal
        for trx in transaksi_list:
            if trx["no_rekening"] == no_rek and kata_kunci in trx["tanggal"]:
                hasil.append(trx)
        judul = f"Pencarian Tanggal: '{kata_kunci}'"

    elif pilih == "2":
        kata_kunci = input("  Nominal (sebagian angka): ").strip()
        # Sequential searching berdasarkan nominal
        for trx in transaksi_list:
            if trx["no_rekening"] == no_rek and kata_kunci in trx["nominal"]:
                hasil.append(trx)
        judul = f"Pencarian Nominal: '{kata_kunci}'"

    elif pilih == "3":
        kata_kunci = input("  Jenis (masuk/keluar): ").strip().lower()
        for trx in transaksi_list:
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == kata_kunci:
                hasil.append(trx)
        judul = f"Pencarian Jenis: '{kata_kunci}'"

    elif pilih == "4":
        for trx in transaksi_list:
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == "masuk":
                hasil.append(trx)
        judul = "Filter: Transaksi Masuk"

    elif pilih == "5":
        for trx in transaksi_list:
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == "keluar":
                hasil.append(trx)
        judul = "Filter: Transaksi Keluar"

    elif pilih == "6":
        periode = input("  Periode (YYYY-MM): ").strip()
        for trx in transaksi_list:
            if trx["no_rekening"] == no_rek and trx["tanggal"].startswith(periode):
                hasil.append(trx)
        judul = f"Filter Periode: {format_periode(periode)}"

    else:
        print("  [!] Pilihan tidak valid.")
        return

    # Tampilkan Hasil 
    garis()
    print(f"  {judul}")
    print(f"  Ditemukan: {len(hasil)} transaksi")
    garis("-")

    if not hasil:
        print("  Tidak ada transaksi yang cocok.")
    else:
        total_masuk  = sum(float(t["nominal"]) for t in hasil if t["jenis"].lower() == "masuk")
        total_keluar = sum(float(t["nominal"]) for t in hasil if t["jenis"].lower() == "keluar")

        # Format tabel pencarian disamakan dengan tabel mutasi.
        lebar_kolom = [10, 22, 10, 16, 28]
        rata_kolom = ["left", "left", "left", "right", "left"]
        cetak_header_tabel(
            ["Tanggal", "ID Transaksi", "Jenis", "Nominal", "Keterangan"],
            lebar_kolom
        )

        # Traversal hasil pencarian
        for trx in hasil:
            cetak_baris_tabel(
                [trx["tanggal"], trx["id_transaksi"], trx["jenis"],
                 format_rupiah(trx["nominal"]), trx["keterangan"]],
                lebar_kolom,
                rata_kolom
            )

        cetak_garis_tabel(lebar_kolom)
        print(f"  Total Masuk  : {format_rupiah(total_masuk)}")
        print(f"  Total Keluar : {format_rupiah(total_keluar)}")

    garis()


# =================================================================
#            FITUR 4: MANAJEMEN SALDO REKENING               
#              (Queue + Traversal Transaksi)                 
# =================================================================

def manajemen_saldo():
    cetak_judul_menu("MANAJEMEN SALDO REKENING")
    no_rek = input("  Nomor Rekening : ").strip()
    rek = cari_rekening(no_rek)

    if not rek:
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi()
    total_masuk, total_keluar = hitung_ringkasan_saldo(no_rek, transaksi_list)

    saldo_awal  = float(rek["saldo_awal"])
    saldo_akhir = saldo_awal + total_masuk - total_keluar

    garis()
    print(f"  REKENING  : {rek['no_rekening']}")
    print(f"  NASABAH   : {rek['nama_nasabah']}")
    print(f"  TGL BUKA  : {rek['tanggal_buka']}")
    garis("-")
    print(f"  {'Saldo Awal':<30} : {format_rupiah(saldo_awal)}")
    print(f"  {'(+) Total Pemasukan':<30} : {format_rupiah(total_masuk)}")
    print(f"  {'(-) Total Pengeluaran':<30} : {format_rupiah(total_keluar)}")
    garis("-")
    print(f"  {'= SALDO AKHIR':<30} : {format_rupiah(saldo_akhir)}")
    garis()

    # Rincian per periode menggunakan Linked List
    ll = LinkedListPeriode()
    for trx in transaksi_list:
        if trx["no_rekening"] == no_rek:
            ll.tambah_periode(trx["tanggal"][:7])

    semua_periode = ll.get_all_periode()
    if semua_periode:
        print(f"\n  Rincian Saldo per Periode:")
        # Tabel periode memakai lebar kolom tetap agar nominal tetap sejajar.
        lebar_kolom = [20, 16, 16, 16]
        rata_kolom = ["left", "right", "right", "right"]
        cetak_header_tabel(
            ["Periode", "Total Masuk", "Total Keluar", "Saldo Akhir"],
            lebar_kolom
        )

        saldo_berjalan = saldo_awal
        for p in semua_periode:            # Traversal linked list periode
            m, k = hitung_ringkasan_saldo(no_rek, transaksi_list, p)
            saldo_berjalan += m - k
            cetak_baris_tabel(
                [format_periode(p), format_rupiah(m),
                 format_rupiah(k), format_rupiah(saldo_berjalan)],
                lebar_kolom,
                rata_kolom
            )
        cetak_garis_tabel(lebar_kolom)


# =================================================================
#               FITUR 5: DASHBOARD MUTASI                   
# =================================================================

def dashboard():
    os.system("cls" if os.name == "nt" else "clear")
    cetak_header_app()
    cetak_judul_menu("DASHBOARD MUTASI REKENING")

    rekening_list  = baca_rekening()
    transaksi_list = baca_transaksi()

    total_rek = len(rekening_list)
    total_trx = len(transaksi_list)
    total_masuk_global  = sum(float(t["nominal"]) for t in transaksi_list
                              if t["jenis"].lower() == "masuk")
    total_keluar_global = sum(float(t["nominal"]) for t in transaksi_list
                              if t["jenis"].lower() == "keluar")

    # Ringkasan dashboard dibuat sebagai tabel agar nilai panjang tetap rapi.
    lebar_ringkasan = [20, 28]
    rata_ringkasan = ["left", "right"]
    cetak_garis_tabel(lebar_ringkasan)
    cetak_baris_tabel(["Total Rekening", total_rek], lebar_ringkasan, rata_ringkasan)
    cetak_baris_tabel(["Total Transaksi", total_trx], lebar_ringkasan, rata_ringkasan)
    cetak_baris_tabel(["Total Pemasukan", format_rupiah(total_masuk_global)], lebar_ringkasan, rata_ringkasan)
    cetak_baris_tabel(["Total Pengeluaran", format_rupiah(total_keluar_global)], lebar_ringkasan, rata_ringkasan)
    cetak_garis_tabel(lebar_ringkasan)

    if rekening_list:
        print()
        lebar_kolom = [15, 26, 13, 16]
        rata_kolom = ["left", "left", "left", "right"]
        cetak_header_tabel(
            ["No. Rekening", "Nama Nasabah", "Tgl Buka", "Saldo Akhir"],
            lebar_kolom
        )

        # Traversal seluruh rekening
        for rek in rekening_list:
            saldo = hitung_saldo_akhir(rek["no_rekening"], rek["saldo_awal"], transaksi_list)
            cetak_baris_tabel(
                [rek["no_rekening"], rek["nama_nasabah"],
                 rek["tanggal_buka"], format_rupiah(saldo)],
                lebar_kolom,
                rata_kolom
            )
        cetak_garis_tabel(lebar_kolom)

    # Transaksi terbaru (5 terakhir)
    if transaksi_list:
        print("\n  5 Transaksi Terbaru:")
        lebar_kolom = [10, 14, 22, 10, 16]
        rata_kolom = ["left", "left", "left", "left", "right"]
        cetak_header_tabel(
            ["Tanggal", "No. Rekening", "Nama Nasabah", "Jenis", "Nominal"],
            lebar_kolom
        )
        for trx in transaksi_list[-5:][::-1]:
            rek_info = cari_rekening(trx["no_rekening"])
            nama = rek_info["nama_nasabah"] if rek_info else "-"
            cetak_baris_tabel(
                [trx["tanggal"], trx["no_rekening"], nama,
                 trx["jenis"], format_rupiah(trx["nominal"])],
                lebar_kolom,
                rata_kolom
            )
        cetak_garis_tabel(lebar_kolom)


# ==================================================================
#                     MENU NAVIGASI                         
# ==================================================================

def menu_crud():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
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
        elif pilih in aksi:
            aksi[pilih]()
        else:
            print("  [!] Pilihan tidak valid.")

        input("\n  Tekan Enter untuk melanjutkan...")


def main():
    inisialisasi_file()

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        cetak_header_app()

        print("  MENU UTAMA")
        garis("-")
        print("  [1]  CRUD Rekening & Transaksi")
        print("  [2]  Navigasi Periode Mutasi")
        print("  [3]  Searching & Filtering")
        print("  [4]  Manajemen Saldo")
        print("  [5]  Dashboard Mutasi")
        print("  [0]  Keluar")
        garis()

        pilih = input("  Pilihan : ").strip()

        menu = {
            "1": menu_crud,
            "2": navigasi_periode,
            "3": searching_filtering,
            "4": manajemen_saldo,
            "5": dashboard,
        }

        if pilih == "0":
            garis()
            print(f"{'Terima kasih telah menggunakan Bank BUMI ARTHA':^72}")
            print(f"{'Sampai jumpa kembali!':^72}")
            garis()
            break
        elif pilih in menu:
            os.system("cls" if os.name == "nt" else "clear")
            cetak_header_app()
            menu[pilih]()
            input("\n  Tekan Enter untuk kembali ke Menu Utama...")
        else:
            print("  [!] Pilihan tidak valid.")
            input("  Tekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()

# ===================================================================
# JUDUL PROGRAM  : Sistem Riwayat Transaksi Rekening Bank Bumi Artha
# MATA KULIAH    : Algoritma & Struktur Data    
# KELAS          : TPL-B
# KELOMPOK       : 16

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

# NodePeriode merepresentasikan satu periode (bulan) dalam linked list.
class NodePeriode:
    
    #Node dalam Doubly Linked List untuk merepresentasikan satu periode (bulan).
    #Setiap node memiliki pointer ke periode sebelum dan sesudahnya.
    
    def __init__(self, periode: str):
        self.periode = periode   # Format: "YYYY-MM"
        self.next = None         # Pointer ke periode berikutnya
        self.prev = None         # Pointer ke periode sebelumnya

# LinkedListPeriode mengelola daftar periode secara terurut dan memungkinkan navigasi maju/mundur.
class LinkedListPeriode:
    
    #Doubly Linked List yang menyimpan daftar periode (bulan-tahun) secara urut.
    #Digunakan untuk navigasi maju/mundur antar periode mutasi.
    
    def __init__(self):
        self.head = None # Pointer ke node pertama (periode paling awal)
        self.tail = None # Pointer ke node terakhir untuk memudahkan penambahan periode baru
        self.current = None   # Pointer posisi periode yang sedang aktif

    # Tambah periode baru ke linked list secara terurut (ascending) tanpa duplikat.
    def tambah_periode(self, periode: str):
        #Tambah periode baru ke linked list secara terurut (tidak duplikat).
        node_baru = NodePeriode(periode)

        if not self.head:
            self.head = node_baru
            self.tail = node_baru
            self.current = node_baru
            return

        # Cek duplikat dengan traversal
        temp = self.head # Traversal untuk cek apakah periode sudah ada
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
            node_baru.prev = self.tail # Pointer ke node terakhir saat ini
            self.tail.next = node_baru # Update pointer next node terakhir ke node baru
            self.tail = node_baru # Update tail ke node baru
        elif temp == self.head:
            # Insert di awal (head)
            node_baru.next = self.head # Pointer next node baru ke node pertama saat ini
            self.head.prev = node_baru # Update pointer prev node pertama ke node baru
            self.head = node_baru # Update head ke node baru
        else:
            # Insert di tengah
            node_baru.prev = temp.prev # Pointer prev node baru ke node sebelum temp
            node_baru.next = temp # Pointer next node baru ke temp
            temp.prev.next = node_baru # Update pointer next node sebelum temp ke node baru
            temp.prev = node_baru # Update pointer prev temp ke node baru

    # Pindahkan posisi current ke periode tertentu.
    def set_current(self, periode: str) -> bool:
       
        temp = self.head # Traversal untuk cari periode yang cocok
        while temp: 
            if temp.periode == periode: # Jika ditemukan, set current ke node tersebut
                self.current = temp # Update pointer current ke node yang ditemukan
                return True  # Periode ditemukan dan current berhasil diupdate
            temp = temp.next # Lanjutkan traversal ke node berikutnya
        return False 

    def periode_sebelumnya(self):
        #Geser current mundur ke periode sebelumnya (traversal backward).
        if self.current and self.current.prev: # Cek apakah current valid dan ada periode sebelumnya
            self.current = self.current.prev # Update pointer current ke periode sebelumnya
            return self.current.periode # Kembalikan periode yang sekarang aktif setelah geser
        return None

    def periode_berikutnya(self):
        #Geser current maju ke periode berikutnya (traversal forward).
        if self.current and self.current.next: # Cek apakah current valid dan ada periode berikutnya
            self.current = self.current.next # Update pointer current ke periode berikutnya
            return self.current.periode # Kembalikan periode yang sekarang aktif setelah geser
        return None

    def get_all_periode(self) -> list:
        #Traversal seluruh linked list, kembalikan semua periode dalam list.
        hasil = []
        temp = self.head # Traversal dari head ke tail untuk kumpulkan semua periode
        while temp: 
            hasil.append(temp.periode)
            temp = temp.next
        return hasil


# =================================================================
#              STRUKTUR DATA: QUEUE (ANTRIAN)               
#      (Pemrosesan transaksi sesuai urutan waktu masuk)     
# =================================================================

# Queue berbasis deque untuk memproses transaksi secara FIFO (First-In-First-Out).
class TransaksiQueue:
    
    #Queue berbasis deque untuk memproses transaksi secara FIFO.
    #Transaksi yang masuk lebih awal akan diproses lebih dahulu (urutan waktu).
    

    def __init__(self):
        self._queue = deque()

    def enqueue(self, transaksi: dict):
        # Tambahkan transaksi ke antrian (masuk dari belakang).
        self._queue.append(transaksi)

    def dequeue(self) -> dict:
        # Ambil & hapus transaksi paling awal dari antrian (keluar dari depan).
        return self._queue.popleft() if self._queue else None

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)


# =================================================================
#               KONSTANTA & KONFIGURASI FILE CSV             
# =================================================================

# Nama file CSV untuk penyimpanan data rekening dan transaksi.
FILE_REKENING   = "rekening.csv"
FILE_TRANSAKSI  = "transaksi.csv"

HEADER_REKENING   = ["no_rekening", "nama_nasabah", "tanggal_buka", "saldo_awal"]
HEADER_TRANSAKSI  = ["id_transaksi", "no_rekening", "tanggal", "jenis", "nominal", "keterangan"]

# Mapping nomor bulan ke nama bulan untuk tampilan periode yang lebih user-friendly.
NAMA_BULAN = {
    "01": "Januari",  "02": "Februari", "03": "Maret",    "04": "April",
    "05": "Mei",      "06": "Juni",     "07": "Juli",     "08": "Agustus",
    "09": "September","10": "Oktober",  "11": "November", "12": "Desember"
}


# ===================================================================
#                   MODUL: PENGELOLAAN FILE CSV                
# ===================================================================

# Fungsi-fungsi untuk membaca dan menulis data rekening dan transaksi ke file CSV.
def inisialisasi_file():
    #Buat file CSV jika belum ada, dengan header yang sesuai.
    for file, header in [(FILE_REKENING, HEADER_REKENING), # Cek dan buat file rekening.csv dengan header jika belum ada
                         (FILE_TRANSAKSI, HEADER_TRANSAKSI)]: # Cek dan buat file transaksi.csv dengan header jika belum ada
        if not os.path.exists(file): # Cek apakah file sudah ada, jika tidak maka buat file baru dengan header
            with open(file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(header) 

# Fungsi untuk membaca dan menyimpan data rekening dan transaksi dari/ke file CSV.
def baca_rekening() -> list: 
    #Baca semua data rekening dari CSV ke dalam List.
    data = []
    if os.path.exists(FILE_REKENING):
        with open(FILE_REKENING, "r", encoding="utf-8") as f:
            for baris in csv.DictReader(f):
                data.append(dict(baris))
    return data

def simpan_rekening(data: list):
    #Simpan List rekening ke file CSV 
    with open(FILE_REKENING, "w", newline="", encoding="utf-8") as f:
        penulis = csv.DictWriter(f, fieldnames=HEADER_REKENING)
        penulis.writeheader()
        penulis.writerows(data)


def baca_transaksi() -> list:
    #Baca semua data transaksi dari CSV ke dalam List
    data = []
    if os.path.exists(FILE_TRANSAKSI):
        with open(FILE_TRANSAKSI, "r", encoding="utf-8") as f:
            for baris in csv.DictReader(f):
                data.append(dict(baris))
    return data


def simpan_transaksi(data: list):
    #Simpan List transaksi ke file CSV
    with open(FILE_TRANSAKSI, "w", newline="", encoding="utf-8") as f:
        penulis = csv.DictWriter(f, fieldnames=HEADER_TRANSAKSI)
        penulis.writeheader()
        penulis.writerows(data)


# ================================================================
#                           FUNGSI BANTU                        
# ================================================================

def buat_no_rekening(rekening_list: list) -> str:
    #Generate nomor rekening baru secara otomatis (increment +1).
    if not rekening_list:
        return "1000001"
    nomor_terakhir = max(int(r["no_rekening"]) for r in rekening_list)
    return str(nomor_terakhir + 1)


def buat_id_transaksi() -> str:
    #Generate ID transaksi unik berdasarkan timestamp + UUID.
    return "TRX" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:4].upper()


def format_rupiah(nominal) -> str:
    #Format angka menjadi string mata uang Rupiah.
    try:
        return f"Rp {int(float(nominal)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return f"Rp {nominal}"


def format_periode(periode: str) -> str:
    #Ubah format 'YYYY-MM' menjadi 'Nama Bulan YYYY'.
    try:
        tahun, bln = periode.split("-")
        return f"{NAMA_BULAN.get(bln, bln)} {tahun}"
    except Exception:
        return periode


def garis(karakter="=", panjang=72):
    print(karakter * panjang)


def pendekkan_teks(nilai, lebar: int) -> str:
    #Potong teks agar tidak melewati lebar kolom tabel.
    teks = " ".join(str(nilai).split())
    if len(teks) <= lebar:
        return teks
    if lebar <= 3:
        return teks[:lebar]
    return teks[:lebar - 3] + "..."


def format_kolom(nilai, lebar: int, rata: str = "left") -> str:
    #Format satu nilai tabel sesuai lebar dan perataan kolom.
    teks = pendekkan_teks(nilai, lebar)
    if rata == "right":
        return f"{teks:>{lebar}}"
    if rata == "center":
        return f"{teks:^{lebar}}"
    return f"{teks:<{lebar}}"


def cetak_garis_tabel(lebar_kolom: list):
    #Cetak garis pemisah tabel dengan panjang mengikuti total kolom.
    print("  " + "-+-".join("-" * lebar for lebar in lebar_kolom))


def cetak_baris_tabel(nilai_kolom: list, lebar_kolom: list, rata_kolom: list = None):
    #Cetak satu baris tabel supaya semua kolom tetap sejajar.
    if rata_kolom is None:
        rata_kolom = ["left"] * len(lebar_kolom)

    kolom = [
        format_kolom(nilai, lebar, rata)
        for nilai, lebar, rata in zip(nilai_kolom, lebar_kolom, rata_kolom)
    ]
    print("  " + " | ".join(kolom))


def cetak_header_tabel(header: list, lebar_kolom: list):
    #Cetak header tabel beserta garis bawahnya.
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
    #Input dengan validasi tipe, nilai minimal, dan pilihan.
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
    #Input tanggal dengan validasi format YYYY-MM-DD.
    while True:
        tgl = input(prompt).strip()
        try:
            datetime.strptime(tgl, "%Y-%m-%d")
            return tgl
        except ValueError:
            print("  [!] Format salah. Gunakan: YYYY-MM-DD  (contoh: 2025-03-15)")


def konfirmasi(pesan: str) -> bool:
    #Minta konfirmasi ya/tidak dari pengguna.
    jawab = input(f"  {pesan} (y/n): ").strip().lower()
    return jawab == "y"


# ==================================================================
#                      LOGIKA REKENING & SALDO             
# ==================================================================

def cari_rekening(no_rekening: str) -> dict:
    #Sequential search rekening berdasarkan nomor rekening.
    for rek in baca_rekening():      # Traversal list
        if rek["no_rekening"] == no_rekening:
            return rek
    return None


def hitung_saldo_akhir(no_rekening: str, saldo_awal, transaksi_list: list) -> float:

    #Hitung saldo akhir dengan traversal seluruh transaksi.
    #Saldo akhir = Saldo awal + Total masuk - Total keluar

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
    
    #Hitung total masuk & keluar dengan Queue dan traversal.
    #Gunakan parameter `periode` (YYYY-MM) untuk filter per bulan.
    
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
# Fitur untuk menambah rekening baru, melihat daftar rekening, menambah transaksi, dan melihat mutasi rekening.
def tambah_nasabah(): #definisikan fungsi untuk menambah nasabah baru, input data, validasi, dan simpan ke file CSV.
    cetak_judul_menu("TAMBAH NASABAH BARU")  #cetak judul menu untuk menambah nasabah baru
    rekening_list = baca_rekening() # Baca daftar rekening yang sudah ada dari file CSV

    nama = input("  Nama Nasabah     : ").strip() # Input nama nasabah, pastikan tidak kosong
    if not nama:
        print("  [!] Nama tidak boleh kosong.") 
        return

    tanggal_buka = input_tanggal("  Tanggal Buka     : ") # Input tanggal buka dengan validasi format YYYY-MM-DD
    saldo_awal = input_valid("  Saldo Awal (Rp)  : ", tipe="float", min_val=0) 

    no_rek = buat_no_rekening(rekening_list) # Generate nomor rekening baru secara otomatis (increment +1)
    rekening_baru = {
        "no_rekening" : no_rek, 
        "nama_nasabah": nama,
        "tanggal_buka": tanggal_buka,
        "saldo_awal"  : str(int(saldo_awal))
    }

    rekening_list.append(rekening_baru) # Tambahkan rekening baru ke list
    simpan_rekening(rekening_list) # Simpan kembali daftar rekening ke file CSV setelah penambahan nasabah baru

    garis("-") # Cetak garis pemisah setelah proses tambah nasabah
    print("  [✓] Nasabah berhasil didaftarkan!")
    print(f"      Nomor Rekening  : {no_rek}")
    print(f"      Nama Nasabah    : {nama}")
    print(f"      Tanggal Buka    : {tanggal_buka}")
    print(f"      Saldo Awal      : {format_rupiah(saldo_awal)}")
    garis("-")


def lihat_rekening():
    cetak_judul_menu("DAFTAR REKENING NASABAH") # Tampilkan daftar rekening nasabah dalam format tabel dengan perhitungan saldo akhir.
    rekening_list = baca_rekening() 
    transaksi_list = baca_transaksi() 

    if not rekening_list: # Cek apakah ada rekening yang terdaftar, jika tidak tampilkan pesan dan keluar dari fungsi
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

    cetak_garis_tabel(lebar_kolom) # Cetak garis pemisah di bawah tabel
    print(f"  Total: {len(rekening_list)} rekening terdaftar") # Tampilkan jumlah total rekening yang terdaftar di bawah tabel


def tambah_transaksi():
    cetak_judul_menu("TAMBAH TRANSAKSI") # Tampilkan form input transaksi baru, validasi input, dan simpan ke file CSV.

    no_rek = input("  Nomor Rekening : ").strip() # Input nomor rekening untuk transaksi, pastikan tidak kosong
    rek = cari_rekening(no_rek)  # Cari rekening berdasarkan nomor rekening yang diinputkan, jika tidak ditemukan tampilkan pesan dan keluar dari fungsi
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

    id_trx = buat_id_transaksi() # Generate ID transaksi unik berdasarkan timestamp + UUID
    transaksi_baru = { 
        "id_transaksi": id_trx,  # ID unik untuk transaksi baru
        "no_rekening" : no_rek,  # Nomor rekening yang terkait dengan transaksi
        "tanggal"     : tanggal, # Tanggal transaksi dalam format YYYY-MM-DD
        "jenis"       : jenis,   # Jenis transaksi: "masuk" atau "keluar"
        "nominal"     : str(int(nominal)),  # Nominal transaksi dalam bentuk string (dikonversi ke integer)
        "keterangan"  : keterangan  # Keterangan tambahan untuk transaksi, default "-" jika kosong
    }

    # Gunakan Queue untuk memastikan urutan pemrosesan
    q = TransaksiQueue()
    q.enqueue(transaksi_baru)
    while not q.is_empty(): # Proses antrian transaksi, meskipun dalam kasus ini hanya ada satu transaksi baru, ini memastikan konsistensi jika nanti ada fitur batch transaksi.
        transaksi_list.append(q.dequeue()) # Tambahkan transaksi baru ke list transaksi utama

    # Sort berdasarkan tanggal agar urut
    transaksi_list.sort(key=lambda x: x["tanggal"]) # Urutkan transaksi berdasarkan tanggal setelah penambahan transaksi baru
    simpan_transaksi(transaksi_list) # Simpan kembali seluruh list transaksi ke file CSV setelah penambahan dan pengurutan

    saldo_baru = hitung_saldo_akhir(no_rek, rek["saldo_awal"], transaksi_list)  # Hitung saldo akhir setelah transaksi baru ditambahkan
    garis("-")
    print("  [✓] Transaksi berhasil disimpan!") 
    print(f"      ID Transaksi : {id_trx}") # Tampilkan ID transaksi yang baru dibuat sebagai konfirmasi
    print(f"      Saldo Akhir  : {format_rupiah(saldo_baru)}") 
    garis("-")


def lihat_mutasi(no_rek: str = None, periode: str = None, dari_menu: bool = True):   
    
    #Tampilkan mutasi rekening dalam format tabel menyerupai buku tabungan.
    #Menggunakan traversal data dan perhitungan saldo berjalan.
    
    if dari_menu:  # Jika dipanggil dari menu utama, minta input nomor rekening dan periode.
        cetak_judul_menu("LIHAT MUTASI REKENING")  #cetak judul menu untuk melihat mutasi rekening
        no_rek = input("  Nomor Rekening : ").strip()  

    rek = cari_rekening(no_rek)  # Cari rekening berdasarkan nomor rekening yang diinputkan, jika tidak ditemukan tampilkan pesan dan keluar dari fungsi
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

    if not mutasi:  # Jika tidak ada transaksi yang sesuai filter, tampilkan pesan dan keluar dari fungsi
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
        saldo_running = float(rek["saldo_awal"])  #saldo awal sebelum periode aktif
        if periode:   # Jika ada filter periode, hitung saldo awal sebelum periode tersebut dengan traversal seluruh transaksi
            for trx in transaksi_list: 
                if (trx["no_rekening"] == no_rek  # Filter transaksi sesuai rekening
                        and trx["tanggal"] < periode + "-01"):  
                    if trx["jenis"].lower() == "masuk":
                        saldo_running += float(trx["nominal"])
                    else:
                        saldo_running -= float(trx["nominal"])

        total_masuk = 0.0
        total_keluar = 0.0

        # Traversal data mutasi untuk ditampilkan
        for trx in mutasi:
            nominal = float(trx["nominal"]) # Hitung saldo berjalan dan total masuk/keluar sesuai jenis transaksi
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
    cetak_judul_menu("EDIT TRANSAKSI")  # Tampilkan form edit transaksi berdasarkan ID transaksi, validasi input, dan simpan perubahan ke file CSV.
    id_trx = input("  ID Transaksi : ").strip()

    transaksi_list = baca_transaksi()
    idx = None 

    # Sequential search ID transaksi
    for i, trx in enumerate(transaksi_list): # Traversal list transaksi untuk mencari ID transaksi yang sesuai
        if trx["id_transaksi"] == id_trx:  # Jika ditemukan, simpan indeksnya dan keluar dari loop
            idx = i
            break

    if idx is None:  # Jika ID transaksi tidak ditemukan, tampilkan pesan dan keluar dari fungsi
        print("  [!] ID transaksi tidak ditemukan.")
        return

    trx = transaksi_list[idx]  # Ambil data transaksi yang akan diedit
    rek = cari_rekening(trx["no_rekening"]) # Cari rekening terkait transaksi untuk menampilkan nama nasabah
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

    if nominal_baru:  # Jika ada input nominal baru, validasi dan update nilai nominal transaksi
        try:  # Validasi input nominal baru, jika valid update nilai nominal transaksi
            transaksi_list[idx]["nominal"] = str(int(float(nominal_baru))) 
            ada_perubahan = True 
        except ValueError:  # Jika input nominal baru tidak valid, tampilkan pesan peringatan dan abaikan perubahan nominal
            print("  [!] Nominal tidak valid, perubahan nominal diabaikan.") 

    if jenis_baru: # Jika ada input jenis baru, validasi dan update nilai jenis transaksi
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


def hapus_transaksi(): #definisikan fungsi untuk menghapus transaksi berdasarkan ID transaksi, validasi input, dan simpan perubahan ke file CSV.
    cetak_judul_menu("HAPUS TRANSAKSI") #cetak judul menu untuk menghapus transaksi
    id_trx = input("  ID Transaksi : ").strip() #ambil input ID transaksi yang akan dihapus dari pengguna

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


def reset_mutasi(): #definisikan fungsi untuk mereset seluruh mutasi transaksi pada rekening tertentu, validasi input, dan simpan perubahan ke file CSV.
    cetak_judul_menu("RESET MUTASI REKENING") #cetak judul menu untuk mereset seluruh mutasi transaksi pada rekening tertentu
    no_rek = input("  Nomor Rekening : ").strip() #ambil input nomor rekening yang akan direset mutasinya dari pengguna
    rek = cari_rekening(no_rek) #cari rekening berdasarkan nomor rekening yang diinputkan, jika tidak ditemukan tampilkan pesan dan keluar dari fungsi

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
#fungsi untuk menavigasi antar periode bulan mutasi menggunakan linked list.
def navigasi_periode(): #definisikan fungsi untuk menavigasi antar periode bulan mutasi menggunakan linked list.
    cetak_judul_menu("NAVIGASI PERIODE MUTASI") 
    no_rek = input("  Nomor Rekening : ").strip() #ambil input nomor rekening yang akan dinavigasi peride mutasinya dari pengguna
    rek = cari_rekening(no_rek) #cari rekening berdasarkan nomor rekening yang diinputkan, jika tidak ditemukan tampilkan pesan dan keluar dari fungsi

    if not rek: 
        print("  [!] Rekening tidak ditemukan.")
        return

    transaksi_list = baca_transaksi() #ambil seluruh data transaksi dari file CSV untuk digunakan dalam navigasi periode mutasi

    # Bangun Linked List periode dari data transaksi
    ll = LinkedListPeriode()
    for trx in transaksi_list: # Traversal list transaksi untuk menambahkan periode unik ke linked list
        if trx["no_rekening"] == no_rek: # Filter transaksi sesuai rekening yang diinputkan
            periode = trx["tanggal"][:7]   # Ambil "YYYY-MM"
            ll.tambah_periode(periode) # Tambahkan periode ke linked list jika belum ada

    semua_periode = ll.get_all_periode() # Tampilkan semua periode

    if not semua_periode: # Jika tidak ada periode yang tersedia, tampilkan pesan dan keluar dari fungsi
        print("  Rekening ini belum memiliki transaksi.")
        return

    # Set posisi awal ke periode terkini
    ll.set_current(semua_periode[-1]) # -1 untuk mengambil periode terakhir (terkini) dari daftar semua periode

    # Loop navigasi periode
    while True:
        os.system("cls" if os.name == "nt" else "clear") # Bersihkan layar terminal
        cetak_header_app() #cetak header aplikasi di bagian atas layar terminal
        cetak_judul_menu("NAVIGASI PERIODE MUTASI") # cetak judul menu navigasi periode mutasi

        print(f"  Nasabah      : {rek['nama_nasabah']}") # Tampilkan nama nasabah yang terkait dengan nomor rekening yang diinputkan
        print(f"  No. Rekening : {no_rek}") # Tampilkan nomor rekening yang diinputkan
        garis("-")
        print(f"   {ll.current.prev.periode if ll.current.prev else '(awal)'}" # Tampilkan periode sebelumnya jika ada, jika tidak tampilkan "(awal)"
              f"   [{format_periode(ll.current.periode)}]" # Tampilkan periode saat ini dalam format "Nama Bulan YYYY"
              f"   {format_periode(ll.current.next.periode) if ll.current.next else '(akhir)'}") # Tampilkan periode berikutnya jika ada, jika tidak tampilkan "(akhir)"
        garis("-") 

        print(f"\n  Semua Periode Tersedia:") # Tampilkan daftar semua periode 
        for i, p in enumerate(semua_periode): # Traversal list semua periode untuk menampilkan daftar periode yang tersedia
            penanda = "  (aktif)" if p == ll.current.periode else "" # Tandai periode yang sedang aktif dengan "(aktif)"
            print(f"    [{i+1}] {format_periode(p)}{penanda}") # Tampilkan nomor urut dan format periode untuk setiap periode yang tersedia

        garis("-")
        print("  [1]    Periode Sebelumnya")
        print("  [2]    Periode Berikutnya")
        print("  [3]    Lihat Mutasi Periode Ini")
        print("  [4]    Pilih Periode Manual")
        print("  [0]    Kembali")

        pilih = input("\n  Pilihan : ").strip() 

        if pilih == "1": # Jika pengguna memilih opsi 1, 
            p = ll.periode_sebelumnya() # Pindah ke periode sebelumnya
            print(f"  → Pindah ke: {format_periode(p)}" if p else # Tampilkan periode sebelumnya jika ada, 
                  "  [!] Sudah di periode paling awal.") # Tampilkan pesan jika sudah di periode paling awal
            input("  Tekan Enter...")

        elif pilih == "2": # Jika pengguna memilih opsi 2,
            p = ll.periode_berikutnya() # Pindah ke periode berikutnya
            print(f"  → Pindah ke: {format_periode(p)}" if p else # Tampilkan periode berikutnya jika ada,
                  "  [!] Sudah di periode paling akhir.") # Tampilkan pesan jika sudah di periode paling akhir
            input("  Tekan Enter...")

        elif pilih == "3": # Jika pengguna memilih opsi 3,
            lihat_mutasi(no_rek, ll.current.periode, dari_menu=False) # Tampilkan mutasi rekening untuk periode saat ini tanpa meminta input nomor rekening dan periode lagi
            input("\n  Tekan Enter...")

        elif pilih == "4": # Jika pengguna memilih opsi 4,
            for i, p in enumerate(semua_periode): # Traversal list semua periode untuk menampilkan daftar periode yang tersedia
                print(f"  [{i+1}] {format_periode(p)}") # Tampilkan nomor urut dan format periode untuk setiap periode yang tersedia
            idx_pilih = input_valid("  Nomor periode: ", tipe="int", 
                                    min_val=1) - 1 # Minta pengguna memilih nomor periode
            if 0 <= idx_pilih < len(semua_periode): # Jika nomor periode yang dipilih valid, pindah ke periode tersebut
                ll.set_current(semua_periode[idx_pilih]) # Tampilkan pesan konfirmasi periode yang dipilih
            else:
                print("  [!] Nomor tidak valid.") # Tampilkan pesan jika nomor periode yang dipilih tidak valid
            input("  Tekan Enter...")

        elif pilih == "0":
            break


# =================================================================
#           FITUR 3: SEARCHING & FILTERING TRANSAKSI         
#          (Sequential Searching & Filter Traversal)          
# =================================================================

def searching_filtering(): # definisikan fungsi untuk mencari dan memfilter transaksi 
    cetak_judul_menu("SEARCHING & FILTERING TRANSAKSI") 
    no_rek = input("  Nomor Rekening : ").strip() # ambil input nomor rekening yang akan dicari 
    rek = cari_rekening(no_rek) #cari rekening berdasarkan nomor rekening yang diinputkan

    if not rek:
        print("  [!] Rekening tidak ditemukan.") # Tampilkan pesan jika rekening tidak ditemukan
        return

    print(f"  Nasabah: {rek['nama_nasabah']}") # Tampilkan nama nasabah
    garis("-")
    print("  [1] Cari berdasarkan Tanggal") # Tampilkan opsi pencarian dan filter transaksi
    print("  [2] Cari berdasarkan Nominal") # Tampilkan opsi pencarian dan filter transaksi
    print("  [3] Cari berdasarkan Jenis Transaksi") # Tampilkan opsi pencarian dan filter transaksi
    print("  [4] Filter: Transaksi Masuk saja") # Tampilkan opsi pencarian dan filter transaksi
    print("  [5] Filter: Transaksi Keluar saja") # Tampilkan opsi pencarian dan filter transaksi
    print("  [6] Filter: Berdasarkan Periode (Bulan)") # Tampilkan opsi pencarian dan filter transaksi
    garis("-")

    pilih = input("  Pilihan : ").strip() 

    transaksi_list = baca_transaksi() # ambil seluruh data transaksi dari file CSV untuk digunakan dalam pencarian dan filter transaksi
    hasil = []
    judul = "" 

    if pilih == "1": # Jika pengguna memilih opsi 1,
        kata_kunci = input("  Tanggal (YYYY-MM-DD / YYYY-MM / YYYY): ").strip() # ambil input kata kunci tanggal untuk pencarian transaksi
        # Sequential searching berdasarkan tanggal
        for trx in transaksi_list: # Traversal list transaksi untuk mencari transaksi yang sesuai dengan kata kunci tanggal
            if trx["no_rekening"] == no_rek and kata_kunci in trx["tanggal"]: # Jika nomor rekening sesuai dan kata kunci tanggal ditemukan dalam tanggal transaksi, tambahkan transaksi ke hasil pencarian
                hasil.append(trx) # Tampilkan judul pencarian berdasarkan kata kunci tanggal
        judul = f"Pencarian Tanggal: '{kata_kunci}'" 

    elif pilih == "2": # Jika pengguna memilih opsi 2,
        kata_kunci = input("  Nominal (sebagian angka): ").strip() # ambil input kata kunci nominal untuk pencarian transaksi
        # Sequential searching berdasarkan nominal
        for trx in transaksi_list: # Traversal list transaksi untuk mencari transaksi yang sesuai dengan kata kunci nominal
            if trx["no_rekening"] == no_rek and kata_kunci in trx["nominal"]: # Jika nomor rekening sesuai dan kata kunci nominal ditemukan dalam nominal transaksi, tambahkan transaksi ke hasil pencarian
                hasil.append(trx) # Tampilkan judul pencarian berdasarkan kata kunci nominal
        judul = f"Pencarian Nominal: '{kata_kunci}'"

    elif pilih == "3": # Jika pengguna memilih opsi 3,
        kata_kunci = input("  Jenis (masuk/keluar): ").strip().lower() # ambil input kata kunci jenis transaksi untuk pencarian transaksi
        for trx in transaksi_list: # Traversal list transaksi untuk mencari transaksi yang sesuai dengan kata kunci jenis transaksi
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == kata_kunci: # Jika nomor rekening sesuai dan kata kunci jenis transaksi sesuai dengan jenis transaksi, tambahkan transaksi ke hasil pencarian
                hasil.append(trx) # Tampilkan judul pencarian berdasarkan kata kunci jenis transaksi
        judul = f"Pencarian Jenis: '{kata_kunci}'" # Tampilkan judul pencarian berdasarkan kata kunci jenis transaksi

    elif pilih == "4": # Jika pengguna memilih opsi 4,
        for trx in transaksi_list: # Traversal list transaksi untuk mencari transaksi yang sesuai dengan jenis "masuk"
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == "masuk": # Jika nomor rekening sesuai dan jenis transaksi adalah "masuk", tambahkan transaksi ke hasil pencarian
                hasil.append(trx) # Tampilkan judul pencarian untuk filter transaksi masuk
        judul = "Filter: Transaksi Masuk"

    elif pilih == "5": # Jika pengguna memilih opsi 5,
        for trx in transaksi_list: # Traversal list transaksi untuk mencari transaksi yang sesuai dengan jenis "keluar"
            if trx["no_rekening"] == no_rek and trx["jenis"].lower() == "keluar": # Jika nomor rekening sesuai dan jenis transaksi adalah "keluar", tambahkan transaksi ke hasil pencarian
                hasil.append(trx) # Tampilkan judul pencarian untuk filter transaksi keluar
        judul = "Filter: Transaksi Keluar"

    elif pilih == "6": # Jika pengguna memilih opsi 6,
        periode = input("  Periode (YYYY-MM): ").strip() # ambil input periode bulan untuk filter transaksi
        for trx in transaksi_list: # Traversal list transaksi untuk mencari transaksi yang sesuai dengan periode bulan yang diinputkan
            if trx["no_rekening"] == no_rek and trx["tanggal"].startswith(periode): # Jika nomor rekening sesuai dan tanggal transaksi dimulai dengan periode bulan yang diinputkan, tambahkan transaksi ke hasil pencarian
                hasil.append(trx) # Tampilkan judul pencarian untuk filter transaksi berdasarkan periode bulan
        judul = f"Filter Periode: {format_periode(periode)}"

    else: # Jika pengguna memilih opsi yang tidak valid, tampilkan pesan peringatan dan keluar dari fungsi
        print("  [!] Pilihan tidak valid.")
        return

    # Tampilkan Hasil 
    garis() 
    print(f"  {judul}") # Tampilkan judul pencarian atau filter yang sesuai dengan pilihan pengguna
    print(f"  Ditemukan: {len(hasil)} transaksi") # Tampilkan jumlah transaksi yang ditemukan sesuai dengan kriteria pencarian atau filter
    garis("-")

    if not hasil:
        print("  Tidak ada transaksi yang cocok.") # Tampilkan pesan jika tidak ada transaksi yang cocok dengan kriteria pencarian atau filter
    else:
        total_masuk  = sum(float(t["nominal"]) for t in hasil if t["jenis"].lower() == "masuk") # Hitung total nominal transaksi masuk dari hasil pencarian atau filter
        total_keluar = sum(float(t["nominal"]) for t in hasil if t["jenis"].lower() == "keluar") # Hitung total nominal transaksi keluar dari hasil pencarian atau filter

        # Format tabel pencarian disamakan dengan tabel mutasi.
        lebar_kolom = [10, 22, 10, 16, 28] # Lebar kolom untuk tabel hasil pencarian atau filter transaksi
        rata_kolom = ["left", "left", "left", "right", "left"] # rata kiri untuk kolom tanggal, ID transaksi, jenis, dan keterangan; rata kanan untuk kolom nominal
        cetak_header_tabel( 
            ["Tanggal", "ID Transaksi", "Jenis", "Nominal", "Keterangan"], # Tampilkan header tabel hasil pencarian atau filter transaksi dengan judul kolom yang sesuai
            lebar_kolom 
        )

        # Traversal hasil pencarian
        for trx in hasil: # Traversal list hasil pencarian atau filter transaksi untuk menampilkan setiap transaksi yang sesuai dengan kriteria
            cetak_baris_tabel( # Tampilkan setiap transaksi dalam bentuk baris tabel
                [trx["tanggal"], trx["id_transaksi"], trx["jenis"], 
                 format_rupiah(trx["nominal"]), trx["keterangan"]],
                lebar_kolom,
                rata_kolom
            )

        cetak_garis_tabel(lebar_kolom) # Tampilkan garis pemisah di bawah tabel hasil pencarian atau filter transaksi
        print(f"  Total Masuk  : {format_rupiah(total_masuk)}") # Tampilkan total nominal transaksi masuk dari hasil pencarian atau filter
        print(f"  Total Keluar : {format_rupiah(total_keluar)}") # Tampilkan total nominal transaksi keluar dari hasil pencarian atau filter

    garis()


# =================================================================
#            FITUR 4: MANAJEMEN SALDO REKENING               
#              (Queue + Traversal Transaksi)                 
# =================================================================

def manajemen_saldo(): # definisikan fungsi untuk menampilkan ringkasan saldo rekening, termasuk saldo awal, total pemasukan, total pengeluaran, dan saldo akhir, serta rincian per periode menggunakan linked list.
    cetak_judul_menu("MANAJEMEN SALDO REKENING") # Tampilkan ringkasan saldo rekening, termasuk saldo awal, total pemasukan, total pengeluaran, dan saldo akhir, serta rincian per periode menggunakan linked list.
    no_rek = input("  Nomor Rekening : ").strip() # ambil input nomor rekening yang akan ditampilkan ringkasan saldonya dari pengguna
    rek = cari_rekening(no_rek) # cari rekening berdasarkan nomor rekening yang diinputkan, jika tidak ditemukan tampilkan pesan dan keluar dari fungsi

    if not rek: # Jika rekening tidak ditemukan, tampilkan pesan peringatan dan keluar dari fungsi
        print("  [!] Rekening tidak ditemukan.") # Tampilkan pesan peringatan jika rekening tidak ditemukan
        return # Keluar dari fungsi

    transaksi_list = baca_transaksi() # ambil seluruh data transaksi dari file CSV untuk digunakan dalam perhitungan ringkasan saldo rekening
    total_masuk, total_keluar = hitung_ringkasan_saldo(no_rek, transaksi_list) # Hitung total pemasukan dan total pengeluaran dari transaksi yang sesuai dengan nomor rekening yang diinputkan

    saldo_awal  = float(rek["saldo_awal"]) # Ambil saldo awal dari data rekening yang ditemukan
    saldo_akhir = saldo_awal + total_masuk - total_keluar # Hitung saldo akhir berdasarkan saldo awal, total pemasukan, dan total pengeluaran

    garis()
    print(f"  REKENING  : {rek['no_rekening']}") # Tampilkan nomor rekening yang diinputkan
    print(f"  NASABAH   : {rek['nama_nasabah']}") # Tampilkan nama nasabah yang terkait dengan nomor rekening yang diinputkan
    print(f"  TGL BUKA  : {rek['tanggal_buka']}") # Tampilkan tanggal buka rekening yang terkait dengan nomor rekening yang diinputkan
    garis("-") # Tampilkan ringkasan saldo rekening, termasuk saldo awal, total pemasukan, total pengeluaran, dan saldo akhir
    print(f"  {'Saldo Awal':<30} : {format_rupiah(saldo_awal)}") # Tampilkan saldo awal rekening yang diinputkan
    print(f"  {'(+) Total Pemasukan':<30} : {format_rupiah(total_masuk)}") # Tampilkan total pemasukan dari transaksi yang sesuai dengan nomor rekening yang diinputkan
    print(f"  {'(-) Total Pengeluaran':<30} : {format_rupiah(total_keluar)}") # Tampilkan total pengeluaran dari transaksi yang sesuai dengan nomor rekening yang diinputkan
    garis("-") # Tampilkan saldo akhir rekening yang dihitung berdasarkan saldo awal, total pemasukan, dan total pengeluaran
    print(f"  {'= SALDO AKHIR':<30} : {format_rupiah(saldo_akhir)}") # Tampilkan saldo akhir rekening yang dihitung berdasarkan saldo awal, total pemasukan, dan total pengeluaran
    garis() # Tampilkan garis pemisah di bawah ringkasan saldo rekening

    # Rincian per periode menggunakan Linked List
    ll = LinkedListPeriode() # Buat linked list untuk menyimpan periode unik dari transaksi yang sesuai dengan nomor rekening yang diinputkan
    for trx in transaksi_list: # Traversal list transaksi untuk menambahkan periode unik ke linked list
        if trx["no_rekening"] == no_rek: # Filter transaksi sesuai rekening yang diinputkan
            ll.tambah_periode(trx["tanggal"][:7]) # Ambil "YYYY-MM" dari tanggal transaksi dan tambahkan periode ke linked list jika belum ada

    semua_periode = ll.get_all_periode() # Tampilkan semua periode yang tersedia dalam linked list
    if semua_periode: # Jika ada periode yang tersedia, tampilkan rincian saldo per periode
        print(f"\n  Rincian Saldo per Periode:") # Tampilkan judul untuk rincian saldo per periode
        # Tabel periode memakai lebar kolom tetap agar nominal tetap sejajar.
        lebar_kolom = [20, 16, 16, 16] # Lebar kolom untuk tabel rincian saldo per periode
        rata_kolom = ["left", "right", "right", "right"] # rata kiri untuk kolom periode, rata kanan untuk kolom total masuk, total keluar, dan saldo akhir
        cetak_header_tabel( # Tampilkan header tabel rincian saldo per periode dengan judul kolom yang sesuai
            ["Periode", "Total Masuk", "Total Keluar", "Saldo Akhir"], # Tampilkan header tabel rincian saldo per periode dengan judul kolom yang sesuai
            lebar_kolom # Lebar kolom untuk tabel rincian saldo per periode
        ) 

        saldo_berjalan = saldo_awal # Inisialisasi saldo berjalan dengan saldo awal rekening
        for p in semua_periode: # Traversal list semua periode untuk menampilkan rincian saldo per periode
            m, k = hitung_ringkasan_saldo(no_rek, transaksi_list, p) # Hitung total pemasukan dan total pengeluaran dari transaksi yang sesuai dengan nomor rekening dan periode yang diinputkan
            saldo_berjalan += m - k # Hitung saldo berjalan berdasarkan saldo awal, total pemasukan, dan total pengeluaran untuk periode saat ini
            cetak_baris_tabel( # Tampilkan setiap periode dalam bentuk baris tabel dengan rincian saldo per periode
                [format_periode(p), format_rupiah(m), # Tampilkan total pemasukan untuk periode saat ini dalam format rupiah
                 format_rupiah(k), format_rupiah(saldo_berjalan)], # Tampilkan total pengeluaran untuk periode saat ini dalam format rupiah
                lebar_kolom, # Lebar kolom untuk tabel rincian saldo per periode
                rata_kolom # rata kiri untuk kolom periode, rata kanan untuk kolom total masuk, total keluar, dan saldo akhir
            )
        cetak_garis_tabel(lebar_kolom) # Tampilkan garis pemisah di bawah tabel rincian saldo per periode


# =================================================================
#               FITUR 5: DASHBOARD MUTASI                   
# =================================================================

def dashboard(): # definisikan fungsi untuk menampilkan ringkasan dashboard mutasi rekening, termasuk total rekening, total transaksi, total pemasukan, total pengeluaran, dan daftar rekening dengan saldo akhir serta 5 transaksi terbaru.
    os.system("cls" if os.name == "nt" else "clear") # Bersihkan layar terminal
    cetak_header_app() # cetak header aplikasi di bagian atas layar terminal
    cetak_judul_menu("DASHBOARD MUTASI REKENING") # Tampilkan ringkasan dashboard mutasi rekening, termasuk total rekening, total transaksi, total pemasukan, total pengeluaran, dan daftar rekening dengan saldo akhir serta 5 transaksi terbaru.

    rekening_list  = baca_rekening() # ambil seluruh data rekening dari file CSV untuk digunakan dalam perhitungan ringkasan dashboard mutasi rekening
    transaksi_list = baca_transaksi() # ambil seluruh data transaksi dari file CSV untuk digunakan dalam perhitungan ringkasan dashboard mutasi rekening

    total_rek = len(rekening_list) # Hitung total rekening yang tersedia dalam data rekening
    total_trx = len(transaksi_list) # Hitung total transaksi yang tersedia dalam data transaksi
    total_masuk_global  = sum(float(t["nominal"]) for t in transaksi_list # Hitung total pemasukan dari seluruh transaksi yang tersedia dalam data transaksi
                              if t["jenis"].lower() == "masuk") # Filter transaksi berdasarkan jenis "masuk"
    total_keluar_global = sum(float(t["nominal"]) for t in transaksi_list # Hitung total pengeluaran dari seluruh transaksi yang tersedia dalam data transaksi
                              if t["jenis"].lower() == "keluar") # Filter transaksi berdasarkan jenis "keluar"

    # Ringkasan dashboard dibuat sebagai tabel agar nilai panjang tetap rapi.
    lebar_ringkasan = [20, 28] # Lebar kolom untuk tabel ringkasan dashboard mutasi rekening
    rata_ringkasan = ["left", "right"] # rata kiri untuk kolom judul, rata kanan untuk kolom nilai
    cetak_garis_tabel(lebar_ringkasan) # Tampilkan garis pemisah di atas tabel ringkasan dashboard mutasi rekening
    cetak_baris_tabel(["Total Rekening", total_rek], lebar_ringkasan, rata_ringkasan) # Tampilkan total rekening dalam bentuk baris tabel
    cetak_baris_tabel(["Total Transaksi", total_trx], lebar_ringkasan, rata_ringkasan) # Tampilkan total transaksi dalam bentuk baris tabel
    cetak_baris_tabel(["Total Pemasukan", format_rupiah(total_masuk_global)], lebar_ringkasan, rata_ringkasan) # Tampilkan total pemasukan dalam bentuk baris tabel
    cetak_baris_tabel(["Total Pengeluaran", format_rupiah(total_keluar_global)], lebar_ringkasan, rata_ringkasan) # Tampilkan total pengeluaran dalam bentuk baris tabel
    cetak_garis_tabel(lebar_ringkasan) # Tampilkan garis pemisah di bawah tabel ringkasan dashboard mutasi rekening

    if rekening_list: # Jika ada rekening yang tersedia, tampilkan daftar rekening dengan saldo akhir
        print() # Tampilkan judul untuk daftar rekening dengan saldo akhir
        lebar_kolom = [15, 26, 13, 16] # Lebar kolom untuk tabel daftar rekening dengan saldo akhir
        rata_kolom = ["left", "left", "left", "right"] # rata kiri untuk kolom nomor rekening, nama nasabah, dan tanggal buka; rata kanan untuk kolom saldo akhir
        cetak_header_tabel( # Tampilkan header tabel daftar rekening dengan saldo akhir dengan judul kolom yang sesuai
            ["No. Rekening", "Nama Nasabah", "Tgl Buka", "Saldo Akhir"], # Tampilkan header tabel daftar rekening dengan saldo akhir dengan judul kolom yang sesuai
            lebar_kolom # Lebar kolom untuk tabel daftar rekening dengan saldo akhir
        )

        # Traversal seluruh rekening
        for rek in rekening_list: # Traversal list rekening untuk menampilkan setiap rekening dengan saldo akhir
            saldo = hitung_saldo_akhir(rek["no_rekening"], rek["saldo_awal"], transaksi_list) # Hitung saldo akhir untuk setiap rekening berdasarkan saldo awal dan transaksi yang sesuai dengan nomor rekening
            cetak_baris_tabel( # Tampilkan setiap rekening dalam bentuk baris tabel dengan rincian nomor rekening, nama nasabah, tanggal buka, dan saldo akhir
                [rek["no_rekening"], rek["nama_nasabah"], # Tampilkan nomor rekening, nama nasabah, tanggal buka, dan saldo akhir untuk setiap rekening
                 rek["tanggal_buka"], format_rupiah(saldo)], # Tampilkan saldo akhir dalam format rupiah
                lebar_kolom, # Lebar kolom untuk tabel daftar rekening dengan saldo akhir
                rata_kolom # rata kiri untuk kolom nomor rekening, nama nasabah, dan tanggal buka; rata kanan untuk kolom saldo akhir
            )
        cetak_garis_tabel(lebar_kolom) # Tampilkan garis pemisah di bawah tabel daftar rekening dengan saldo akhir

    # Transaksi terbaru (5 terakhir)
    if transaksi_list: # Jika ada transaksi yang tersedia, tampilkan 5 transaksi terbaru
        print("\n  5 Transaksi Terbaru:") # Tampilkan judul untuk 5 transaksi terbaru
        lebar_kolom = [10, 14, 22, 10, 16] # Lebar kolom untuk tabel 5 transaksi terbaru
        rata_kolom = ["left", "left", "left", "left", "right"] # rata kiri untuk kolom tanggal, nomor rekening, nama nasabah, dan jenis; rata kanan untuk kolom nominal
        cetak_header_tabel( # Tampilkan header tabel 5 transaksi terbaru dengan judul kolom yang sesuai
            ["Tanggal", "No. Rekening", "Nama Nasabah", "Jenis", "Nominal"], # Tampilkan header tabel 5 transaksi terbaru dengan judul kolom yang sesuai
            lebar_kolom # Lebar kolom untuk tabel 5 transaksi terbaru
        )
        for trx in transaksi_list[-5:][::-1]: # Traversal 5 transaksi terbaru dari list transaksi (5 terakhir, dibalik urutannya agar yang terbaru tampil di atas)
            rek_info = cari_rekening(trx["no_rekening"]) # Cari informasi rekening terkait transaksi untuk menampilkan nama nasabah
            nama = rek_info["nama_nasabah"] if rek_info else "-" # Jika rekening ditemukan, ambil nama nasabah; jika tidak, tampilkan "-"
            cetak_baris_tabel( # Tampilkan setiap transaksi terbaru dalam bentuk baris tabel dengan rincian tanggal, nomor rekening, nama nasabah, jenis transaksi, dan nominal
                [trx["tanggal"], trx["no_rekening"], nama, # Tampilkan tanggal, nomor rekening, nama nasabah, jenis transaksi, dan nominal untuk setiap transaksi terbaru
                 trx["jenis"], format_rupiah(trx["nominal"])], # Tampilkan nominal dalam format rupiah
                lebar_kolom, # Lebar kolom untuk tabel 5 transaksi terbaru``
                rata_kolom # rata kiri untuk kolom tanggal, nomor rekening, nama nasabah, dan jenis; rata kanan untuk kolom nominal
            )
        cetak_garis_tabel(lebar_kolom) # Tampilkan garis pemisah di bawah tabel 5 transaksi terbaru


# ==================================================================
#                     MENU NAVIGASI                         
# ==================================================================

# Menu navigasi utama untuk fitur CRUD rekening & transaksi, dengan pemilihan aksi berdasarkan input pengguna.
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

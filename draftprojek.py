# ===================================================================
# JUDUL PROGRAM  : Sistem Riwayat Transaksi Rekening
# MATA KULIAH    : Algoritma & Struktur Data    
# KELAS          : TPL-B
# KELOMPOK       : 16
#
# ANGGOTA KELOMPOK:
# 1. Muhammad Ibnu Akbar       (J0403251028)
# 2. Yudha Saputra             (J0403251119)
# 3. Muhammad Ridzqi Badarudin (J0403251146)
#
# DESKRIPSI:
# Program ini digunakan untuk mencatat riwayat transaksi rekening.
# Data disimpan menggunakan file CSV (file handling).
# Struktur data yang digunakan adalah Linked List dan Array (List).
# ===================================================================

import csv
import os
import datetime
import json
from pathlib import Path
import sys

# ============================ ANSI COLORS MANUAL ============================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

Fore = Colors()
Style = Colors()
Back = Colors()

# KONFIGURASI FILE
TRANSAKSI_FILE = "rekening_transaksi.csv"
REKENING_FILE = "data_rekening.json"
BACKUP_FILE = "backup_rekening.json"

class Rekening:
    def __init__(self, nomor_rekening, nama_pemilik, saldo_awal=0):
        self.nomor_rekening = nomor_rekening
        self.nama_pemilik = nama_pemilik
        self.saldo_awal = saldo_awal
        self.transaksi = LinkedList()

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.length = 0

    def tambah(self, data):
        node = Node(data)
        if not self.head:
            self.head = node
        else:
            temp = self.head
            while temp.next:
                temp = temp.next
            temp.next = node
        self.length += 1

    def hapus(self, index):
        if index < 1 or index > self.length or not self.head:
            return False
        if index == 1:
            self.head = self.head.next
        else:
            prev, temp = None, self.head
            i = 1
            while i < index:
                prev = temp
                temp = temp.next
                i += 1
            prev.next = temp.next
        self.length -= 1
        return True

    def ke_list(self):
        result = []
        temp = self.head
        while temp:
            result.append(temp.data)
            temp = temp.next
        return result

    def kosong(self):
        self.head = None
        self.length = 0

# ============================ VISUAL SYSTEM ============================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    clear_screen()
    print(f"{Fore.CYAN}{Style.BOLD}")
    print("╔" + "═" * 88 + "╗")
    print("║" + f"{' ':<26}🏦 SISTEM BANK DIGITAL v3.0 🏦{' ':<39}" + "║")
    print("║" + f"{' ':<88}" + "║")
    print("║" + f"{' ':<15}Kelompok 16 - TPL-B - Algoritma & Struktur Data{' ':<53}" + "║")
    print("╠" + "═" * 88 + "╣")
    print("║" + f"{' ':<88}" + "║")
    print("╚" + "═" * 88 + "╝")
    print(f"{Style.RESET}")

def print_header(title):
    print(f"\n{Fore.MAGENTA}{'═'*100}{Style.RESET}")
    print(f"{Fore.CYAN}{Style.BOLD}{' '*38}{title.center(24)}{' '*38}{Style.RESET}")
    print(f"{Fore.MAGENTA}{'═'*100}{Style.RESET}")

def print_table_header(columns, widths):
    header = "│"
    separator = "├" + "─" * (sum(widths) + len(widths) - 1) + "┤"
    for i, (col, width) in enumerate(zip(columns, widths)):
        header += f" {col:<{width}}│"
    print(f"{Fore.CYAN}{Style.BOLD}{header}{Style.RESET}")
    print(f"{Fore.CYAN}{Style.BOLD}{separator}{Style.RESET}")

def print_table_row(data, widths, colors=None):
    row = "│"
    for i, (item, width) in enumerate(zip(data, widths)):
        color = colors[i] if colors and i < len(colors) else Fore.WHITE
        row += f" {color}{str(item):<{width}}{Style.RESET}│"
    print(row)

def print_success(msg): 
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET}")
def print_error(msg):   
    print(f"{Fore.RED}❌ {msg}{Style.RESET}")
def print_warning(msg): 
    print(f"{Fore.YELLOW}⚠️  {msg}{Style.RESET}")
def print_info(msg):    
    print(f"{Fore.CYAN}ℹ️  {msg}{Style.RESET}")

# ============================ VALIDASI ============================
def validasi_tanggal(tanggal):
    try:
        datetime.datetime.strptime(tanggal, "%Y-%m-%d")
        return True
    except:
        return False

def input_pilihan(prompt, options):
    while True:
        print(prompt, end="")
        pilihan = input().strip()
        if pilihan in options:
            return pilihan
        print_error(f"Pilihan harus {', '.join(options)}!")

# ============================ FILE SYSTEM ============================
def init_files():
    if not os.path.exists(TRANSAKSI_FILE):
        with open(TRANSAKSI_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["nomor_rekening", "tanggal", "keterangan", "tipe", "jumlah"])
    
    if not os.path.exists(REKENING_FILE):
        rekening_data = {
            "rekenings": [
                {"nomor_rekening": "1234567890", "nama_pemilik": "Muhammad Ibnu Akbar", "saldo_awal": 1000000},
                {"nomor_rekening": "0987654321", "nama_pemilik": "Yudha Saputra", "saldo_awal": 500000}
            ]
        }
        with open(REKENING_FILE, 'w', encoding='utf-8') as f:
            json.dump(rekening_data, f, indent=2, ensure_ascii=False)
        print_success("File inisialisasi berhasil!")

def load_rekenings():
    try:
        with open(REKENING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        rekenings = {}
        for acc in data["rekenings"]:
            rekening = Rekening(acc["nomor_rekening"], acc["nama_pemilik"], acc["saldo_awal"])
            baca_transaksi(rekening.transaksi, acc["nomor_rekening"])
            rekenings[acc["nomor_rekening"]] = rekening
        return rekenings
    except:
        print_warning("Memuat data default")
        return {}

def simpan_rekenings(rekenings):
    data = {"rekenings": []}
    for nomor, rekening in rekenings.items():
        data["rekenings"].append({
            "nomor_rekening": nomor,
            "nama_pemilik": rekening.nama_pemilik,
            "saldo_awal": rekening.saldo_awal
        })
    with open(REKENING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def baca_transaksi(ll, nomor_rekening):
    try:
        with open(TRANSAKSI_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["nomor_rekening"] == nomor_rekening:
                    ll.tambah(row)
    except: pass

def simpan_transaksi(rekenings):
    with open(TRANSAKSI_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["nomor_rekening", "tanggal", "keterangan", "tipe", "jumlah"])
        for nomor, rekening in rekenings.items():
            for transaksi in rekening.transaksi.ke_list():
                writer.writerow([nomor, transaksi["tanggal"], transaksi["keterangan"], 
                               transaksi["tipe"], transaksi["jumlah"]])

# ============================ FITUR REKENING ============================
def input_transaksi(rekening):
    print_header("➕ INPUT TRANSAKSI BARU")
    print(f"🏦 Rekening: {Fore.CYAN}{rekening.nama_pemilik} ({rekening.nomor_rekening}){Style.RESET}")
    
    tanggal = input(f"{Fore.CYAN}📅 Tanggal [YYYY-MM-DD]: {Style.RESET}").strip()
    if not validasi_tanggal(tanggal):
        tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
        print_info(f"Menggunakan tanggal hari ini: {tanggal}")
    
    keterangan = input(f"{Fore.CYAN}📝 Keterangan: {Style.RESET}").strip()
    tipe = input_pilihan(f"{Fore.CYAN}💳 Tipe [D]Ebit/[K]redit: {Style.RESET}", ["D", "K"])
    tipe = "debit" if tipe.upper() == "D" else "kredit"
    
    while True:
        try:
            jumlah = input(f"{Fore.CYAN}💰 Nominal: Rp {Style.RESET}").strip()
            jumlah = int(jumlah.replace(".", "").replace(",", ""))
            if jumlah > 0: break
        except: 
            print_error("Nominal harus angka positif!")
    
    return {
        "tanggal": tanggal,
        "keterangan": keterangan[:30],
        "tipe": tipe,
        "jumlah": str(jumlah)
    }

def tampilkan_saldo(rekening):
    saldo = hitung_saldo(rekening)
    print(f"\n{Fore.MAGENTA}{'═'*60}{Style.RESET}")
    print(f"{Fore.GREEN}{Style.BOLD}💳 SALDO REKENING{Style.RESET}")
    print(f"{Fore.MAGENTA}{'═'*60}{Style.RESET}")
    print(f"{'Nama':<20} : {Fore.CYAN}{rekening.nama_pemilik}{Style.RESET}")
    print(f"{'No. Rekening':<20} : {Fore.CYAN}{rekening.nomor_rekening}{Style.RESET}")
    print(f"{'Saldo Saat Ini':<20} : {Fore.GREEN if saldo >= 0 else Fore.RED}Rp {saldo:,}{Style.RESET}")
    print(f"{Fore.MAGENTA}{'═'*60}{Style.RESET}")

def hitung_saldo(rekening):
    saldo = rekening.saldo_awal
    for transaksi in rekening.transaksi.ke_list():
        jumlah = int(transaksi["jumlah"])
        saldo += jumlah if transaksi["tipe"] == "kredit" else -jumlah
    return saldo

def tampilkan_mutasi(rekening, filter_periode=None):
    print_header("📊 MUTASI REKENING")
    tampilkan_saldo(rekening)
    
    data = rekening.transaksi.ke_list()
    if filter_periode:
        data = [d for d in data if filter_periode(d)]
    
    if not data:
        print_warning("Tidak ada transaksi!")
        return
    
    columns = ["Tgl", "Keterangan", "Tipe", "Kredit", "Debit", "Saldo"]
    widths = [10, 25, 8, 12, 12, 15]
    print_table_header(columns, widths)
    
    saldo = rekening.saldo_awal
    for transaksi in data:
        jumlah = int(transaksi["jumlah"])
        if transaksi["tipe"] == "kredit":
            kredit = f"Rp {jumlah:,}"
            debit = ""
            saldo += jumlah
        else:
            kredit = ""
            debit = f"Rp {jumlah:,}"
            saldo -= jumlah
        
        colors = [Fore.WHITE, Fore.WHITE, Fore.BLUE, Fore.GREEN, Fore.RED, Fore.YELLOW]
        print_table_row([
            transaksi["tanggal"][5:],
            transaksi["keterangan"],
            transaksi["tipe"].upper(),
            kredit, debit, f"Rp {saldo:,}"
        ], widths, colors)
    
    print(f"{Fore.CYAN}└{'─'*(sum(widths)+len(widths)-1)}┘{Style.RESET}")

def mutasi_filter():
    print(f"{Fore.YELLOW}Filter Mutasi:{Style.RESET}")
    print("1. Semua Transaksi")
    print("2. 7 Hari Terakhir") 
    print("3. Bulan Ini")
    print("4. Custom Periode")
    return input_pilihan("Pilih filter: ", ["1","2","3","4"])

def cari_transaksi(rekening):
    print_header("🔍 PENCARIAN TRANSAKSI")
    keyword = input(f"{Fore.CYAN}Cari (keterangan/tanggal): {Style.RESET}").strip().lower()
    data = [t for t in rekening.transaksi.ke_list() 
            if keyword in t["keterangan"].lower() or keyword in t["tanggal"].lower()]
    
    if data:
        tampilkan_mutasi(rekening, lambda x: x in data)
    else:
        print_warning("Transaksi tidak ditemukan!")

# ============================ MENU SYSTEM ============================
def menu_utama():
    banner()
    print(f"{Fore.WHITE}1. 👤 Pilih Rekening{Style.RESET}")
    print(f"2. ➕ Tambah Rekening Baru")
    print(f"3. 📊 Lihat Semua Rekening")
    print(f"0. ❌ Keluar")
    return input(f"{Fore.YELLOW}Pilih: {Style.RESET}").strip()

def menu_rekening(rekening):
    print_header(f"REKENING {rekening.nomor_rekening}")
    tampilkan_saldo(rekening)
    print(f"\n{Fore.WHITE}1. 📊 Mutasi Rekening{Style.RESET}")
    print(f"2. ➕ Transaksi Baru")
    print(f"3. 🔍 Cari Transaksi")
    print(f"4. 🗑️  Hapus Transaksi")
    print(f"5. 📈 Statistik")
    print(f"0. 🔙 Kembali")
    return input(f"{Fore.YELLOW}Pilih: {Style.RESET}").strip()

def main():
    print(f"{Fore.CYAN}🚀 Inisialisasi sistem...{Style.RESET}")
    init_files()
    rekenings = load_rekenings()
    print_success("Sistem siap digunakan!")
    
    while True:
        try:
            pilihan = menu_utama()
            
            if pilihan == "1":
                if not rekenings:
                    print_error("Belum ada rekening!")
                    input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
                    continue
                
                print_header("👤 PILIH REKENING")
                columns = ["No", "No.Rekening", "Nama Pemilik", "Saldo"]
                widths = [4, 12, 25, 15]
                print_table_header(columns, widths)
                
                for i, (nomor, rekening) in enumerate(rekenings.items(), 1):
                    saldo = hitung_saldo(rekening)
                    print_table_row([i, nomor, rekening.nama_pemilik, f"Rp {saldo:,}"], 
                                  widths, [Fore.YELLOW, Fore.CYAN, Fore.WHITE, Fore.GREEN])
                
                try:
                    idx = int(input(f"\n{Fore.YELLOW}Pilih nomor rekening: {Style.RESET}")) - 1
                    rekening = list(rekenings.values())[idx]
                    menu_rekening_loop(rekenings, rekening)
                except:
                    print_error("Pilihan tidak valid!")
            
            elif pilihan == "2":
                nomor = input(f"{Fore.CYAN}No.Rekening baru (10 digit): {Style.RESET}")
                if len(nomor) != 10 or not nomor.isdigit():
                    print_error("No.rekening harus 10 digit angka!")
                    input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
                    continue
                nama = input(f"{Fore.CYAN}Nama pemilik: {Style.RESET}")
                saldo_awal = input(f"{Fore.CYAN}Saldo awal [0]: Rp {Style.RESET}") or "0"
                rekenings[nomor] = Rekening(nomor, nama, int(saldo_awal))
                simpan_rekenings(rekenings)
                print_success("Rekening berhasil dibuat!")
                input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
            
            elif pilihan == "3":
                if rekenings:
                    print_header("📊 SEMUA REKENING")
                    columns = ["No.Rekening", "Nama", "Transaksi", "Saldo"]
                    widths = [12, 25, 10, 15]
                    print_table_header(columns, widths)
                    for nomor, rekening in rekenings.items():
                        print_table_row([
                            nomor, rekening.nama_pemilik, 
                            rekening.transaksi.length, f"Rp {hitung_saldo(rekening):,}"
                        ], widths)
                else:
                    print_warning("Belum ada rekening!")
                input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
            
            elif pilihan == "0":
                print(f"\n{Fore.GREEN}👋 Terima kasih! Sistem ditutup.{Style.RESET}")
                if rekenings:
                    simpan_transaksi(rekenings)
                break
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Program dihentikan oleh user{Style.RESET}")
            break
        except Exception as e:
            print_error(f"Kesalahan: {str(e)}")
            input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")

def menu_rekening_loop(rekenings, rekening):
    while True:
        pilihan = menu_rekening(rekening)
        
        if pilihan == "1":
            filter_type = mutasi_filter()
            if filter_type == "4":
                tgl_awal = input(f"{Fore.CYAN}Tanggal awal [YYYY-MM-DD]: {Style.RESET}")
                tgl_akhir = input(f"{Fore.CYAN}Tanggal akhir [YYYY-MM-DD]: {Style.RESET}")
                filter_func = lambda x: tgl_awal <= x["tanggal"] <= tgl_akhir
            elif filter_type == "2":
                filter_func = lambda x: (datetime.datetime.now().date() - 
                                       datetime.timedelta(days=7) <= 
                                       datetime.datetime.strptime(x["tanggal"], "%Y-%m-%d").date())
            elif filter_type == "3":
                bulan_ini = datetime.datetime.now().strftime("%Y-%m")
                filter_func = lambda x: x["tanggal"].startswith(bulan_ini)
            else:
                filter_func = None
            tampilkan_mutasi(rekening, filter_func)
            input(f"\n{Fore.CYAN}⏎ Enter...{Style.RESET}")
        
        elif pilihan == "2":
            transaksi = input_transaksi(rekening)
            rekening.transaksi.tambah(transaksi)
            simpan_transaksi(rekenings)
            print_success("Transaksi berhasil ditambahkan!")
            input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
        
        elif pilihan == "3":
            cari_transaksi(rekening)
            input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
        
        elif pilihan == "4":
            if rekening.transaksi.length > 0:
                tampilkan_mutasi(rekening)
                try:
                    idx = int(input(f"{Fore.RED}🗑️  Hapus no (0=batal): {Style.RESET}"))
                    if idx == 0: continue
                    if rekening.transaksi.hapus(idx):
                        simpan_transaksi(rekenings)
                        print_success("Transaksi dihapus!")
                    else:
                        print_error("Nomor tidak valid!")
                except:
                    print_error("Input tidak valid!")
            else:
                print_warning("Tidak ada transaksi!")
            input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
        
        elif pilihan == "5":
            data = rekening.transaksi.ke_list()
            debit = sum(int(d["jumlah"]) for d in data if d["tipe"] == "debit")
            kredit = sum(int(d["jumlah"]) for d in data if d["tipe"] == "kredit")
            print_header("📈 STATISTIK TRANSAKSI")
            print(f"{Fore.YELLOW}{'Total Transaksi':<20}{Style.RESET}: {Fore.WHITE}{len(data)}{Style.RESET}")
            print(f"{Fore.YELLOW}{'Total Debit':<20}{Style.RESET}: {Fore.RED}Rp {debit:,}{Style.RESET}")
            print(f"{Fore.YELLOW}{'Total Kredit':<20}{Style.RESET}: {Fore.GREEN}Rp {kredit:,}{Style.RESET}")
            print(f"{Fore.YELLOW}{'Saldo Bersih':<20}{Style.RESET}: {Fore.MAGENTA}Rp {hitung_saldo(rekening):,}{Style.RESET}")
            input(f"{Fore.CYAN}⏎ Enter...{Style.RESET}")
        
        elif pilihan == "0":
            break

if __name__ == "__main__":
    main()
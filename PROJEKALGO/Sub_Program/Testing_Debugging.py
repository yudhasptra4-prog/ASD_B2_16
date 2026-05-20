"""Bagian Ibnu: validasi, testing, dokumentasi, debugging, dan presentasi."""

import csv
import os
import tempfile
from datetime import datetime
from pathlib import Path


def validasi_format_tanggal(tanggal: str) -> bool:
    """Cek format tanggal YYYY-MM-DD."""
    try:
        datetime.strptime(str(tanggal), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validasi_periode(periode: str) -> bool:
    """Cek format periode YYYY-MM."""
    try:
        datetime.strptime(str(periode) + "-01", "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validasi_jenis_transaksi(jenis: str) -> bool:
    """Cek jenis transaksi yang diizinkan."""
    return str(jenis).lower() in {"masuk", "keluar"}


def validasi_nominal(nominal, min_val=0) -> bool:
    """Cek nominal berbentuk angka dan tidak kurang dari batas minimal."""
    try:
        return float(nominal) >= min_val
    except (ValueError, TypeError):
        return False


def input_valid(prompt: str, tipe="str", min_val=None, pilihan=None):
    """Input dengan validasi tipe data, nilai minimal, dan daftar pilihan."""
    while True:
        try:
            nilai = input(prompt).strip()

            if tipe == "int":
                nilai = int(nilai)
            elif tipe == "float":
                nilai = float(nilai)

            if min_val is not None and nilai < min_val:
                print(f"  [!] Nilai minimal adalah {min_val}.")
                continue

            if pilihan:
                if isinstance(nilai, str):
                    nilai = nilai.lower()
                pilihan_normal = [str(item).lower() for item in pilihan]
                if str(nilai).lower() not in pilihan_normal:
                    print(f"  [!] Pilih salah satu dari: {', '.join(pilihan)}.")
                    continue

            return nilai
        except ValueError:
            print("  [!] Input tidak valid, coba lagi.")


def input_tanggal(prompt: str) -> str:
    """Input tanggal dengan format wajib YYYY-MM-DD."""
    while True:
        tanggal = input(prompt).strip()
        if validasi_format_tanggal(tanggal):
            return tanggal
        print("  [!] Format salah. Gunakan YYYY-MM-DD, contoh: 2025-03-15.")


def konfirmasi(pesan: str) -> bool:
    """Minta konfirmasi ya/tidak dari pengguna."""
    while True:
        jawab = input(f"  {pesan} (y/n): ").strip().lower()
        if jawab in {"y", "ya"}:
            return True
        if jawab in {"n", "no", "tidak"}:
            return False
        print("  [!] Jawab dengan y atau n.")


def cek_file_csv(path: str, header: list) -> tuple:
    """Validasi keberadaan dan header file CSV."""
    file_path = Path(path)
    if not file_path.exists():
        return False, "file belum ada"

    try:
        with file_path.open("r", encoding="utf-8") as file:
            pembaca = csv.reader(file)
            header_aktual = next(pembaca, [])
    except OSError as error:
        return False, f"gagal dibaca: {error}"

    if header_aktual != header:
        return False, f"header tidak sesuai: {header_aktual}"
    return True, "OK"


def cetak_debug_info(file_rekening="rekening.csv", file_transaksi="transaksi.csv"):
    """Tampilkan status file CSV untuk membantu debugging."""
    garis = "=" * 72
    print(garis)
    print(f"{'DEBUG INFO CSV':^72}")
    print(garis)

    daftar_file = [
        (file_rekening, ["no_rekening", "nama_nasabah", "tanggal_buka", "saldo_awal"]),
        (file_transaksi, ["id_transaksi", "no_rekening", "tanggal", "jenis", "nominal", "keterangan"]),
    ]

    for nama_file, header in daftar_file:
        valid, pesan = cek_file_csv(nama_file, header)
        ukuran = Path(nama_file).stat().st_size if Path(nama_file).exists() else 0
        status = "valid" if valid else "perlu dicek"
        print(f"  {nama_file:<15} : {status:<11} | {pesan} | {ukuran} byte")
    print(garis)


def cetak_dokumentasi():
    """Cetak dokumentasi singkat pembagian modul."""
    garis = "=" * 72
    print(garis)
    print(f"{'DOKUMENTASI PROJECT':^72}")
    print(garis)
    print("  Nama Aplikasi : Sistem Informasi Mutasi Rekening Bank Bumi Artha")
    print("  File Utama    : PROJEKFIKS.py")
    print()
    print("  Pembagian File:")
    print("  1. udin_backend.py")
    print("     Backend, CRUD, CSV, manajemen saldo, dan struktur data utama.")
    print("  2. PROJEKFIKS.py")
    print("     Frontend, dashboard, searching/filtering, navigasi periode,")
    print("     dan tampilan tabel mutasi.")
    print("  3. ibnu_testing.py")
    print("     Validasi input, self-test, dokumentasi, debugging, dan bahan presentasi.")
    print(garis)


def cetak_panduan_presentasi():
    """Cetak poin presentasi agar alur demo lebih rapi."""
    garis = "=" * 72
    print(garis)
    print(f"{'PANDUAN PRESENTASI':^72}")
    print(garis)
    print("  1. Jelaskan masalah: pencatatan mutasi rekening berbasis CSV.")
    print("  2. Tunjukkan struktur data: list, queue, dan doubly linked list periode.")
    print("  3. Demo CRUD rekening dan transaksi.")
    print("  4. Demo dashboard, pencarian/filtering, dan navigasi periode.")
    print("  5. Jalankan self-test dan debug info sebagai bukti validasi.")
    print("  6. Tutup dengan pembagian tugas setiap anggota.")
    print(garis)


def jalankan_self_test(verbose=True) -> bool:
    """Self-test ringan tanpa mengubah data CSV asli pengguna."""
    import udin_backend as backend

    hasil = []

    def cek(kondisi, nama):
        hasil.append((nama, bool(kondisi)))

    cwd_awal = os.getcwd()
    with tempfile.TemporaryDirectory() as folder_uji:
        os.chdir(folder_uji)
        try:
            backend.inisialisasi_file()
            cek(Path(backend.FILE_REKENING).exists(), "inisialisasi_file membuat rekening.csv")
            cek(Path(backend.FILE_TRANSAKSI).exists(), "inisialisasi_file membuat transaksi.csv")
            cek(backend.buat_no_rekening([]) == "1000001", "nomor rekening awal benar")

            transaksi = [
                {"no_rekening": "1000001", "tanggal": "2025-01-01", "jenis": "masuk", "nominal": "50000"},
                {"no_rekening": "1000001", "tanggal": "2025-01-02", "jenis": "keluar", "nominal": "20000"},
            ]
            saldo = backend.hitung_saldo_akhir("1000001", "100000", transaksi)
            cek(saldo == 130000.0, "perhitungan saldo akhir benar")

            daftar_periode = backend.LinkedListPeriode()
            for periode in ["2025-03", "2025-01", "2025-02", "2025-02"]:
                daftar_periode.tambah_periode(periode)
            cek(
                daftar_periode.get_all_periode() == ["2025-01", "2025-02", "2025-03"],
                "linked list periode urut dan tanpa duplikat",
            )

            queue = backend.TransaksiQueue()
            queue.enqueue({"id": "A"})
            queue.enqueue({"id": "B"})
            cek(queue.dequeue()["id"] == "A" and queue.dequeue()["id"] == "B", "queue berjalan FIFO")

            cek(validasi_format_tanggal("2025-03-15"), "validasi tanggal benar")
            cek(validasi_periode("2025-03"), "validasi periode benar")
            cek(validasi_jenis_transaksi("masuk"), "validasi jenis transaksi benar")
            cek(validasi_nominal("1000", min_val=1), "validasi nominal benar")
        finally:
            os.chdir(cwd_awal)

    semua_lulus = all(status for _, status in hasil)
    if verbose:
        garis = "=" * 72
        print(garis)
        print(f"{'HASIL SELF-TEST':^72}")
        print(garis)
        for nama, status in hasil:
            label = "LULUS" if status else "GAGAL"
            print(f"  [{label}] {nama}")
        print(garis)
        print("  Semua test lulus." if semua_lulus else "  Ada test yang gagal.")

    return semua_lulus


if __name__ == "__main__":
    jalankan_self_test()

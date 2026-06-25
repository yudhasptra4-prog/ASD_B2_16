from pathlib import Path

path = Path('Menu_Utama/Sistem_Mutasi_Bank_BumiArtha.py')
text = path.read_text(encoding='utf-8')
lines = text.splitlines()
keywords = [
    ('import ', '# impor modul'),
    ('from ', '# impor modul'),
    ('class ', '# definisi kelas'),
    ('def ', '# definisi fungsi'),
    ('return ', '# kembalikan nilai'),
    ('if ', '# percabangan kondisi'),
    ('elif ', '# percabangan kondisi'),
    ('else:', '# cabang lain'),
    ('for ', '# loop for'),
    ('while ', '# loop while'),
    ('with ', '# blok context manager'),
    ('try:', '# blok percobaan'),
    ('except ', '# tangkap exception'),
    ('print(', '# cetak output'),
    ('input(', '# baca input pengguna'),
    ('open(', '# buka file'),
    ('append(', '# tambahkan ke list/queue'),
    ('sort(', '# urutkan daftar'),
    ('csv.writer', '# tulis data CSV'),
    ('csv.DictReader', '# baca data CSV sebagai dict'),
    ('uuid.uuid4', '# buat UUID unik'),
    ('datetime.now', '# ambil timestamp saat ini'),
    ('format_rupiah', '# format ke rupiah'),
    ('format_periode', '# format nama periode'),
    ('os.system', '# jalankan perintah sistem'),
    ('main()', '# jalankan fungsi utama'),
]

new_lines = []
for line in lines:
    stripped = line.rstrip()
    if not stripped or stripped.lstrip().startswith('#'):
        new_lines.append(line)
        continue
    if '#' in stripped:
        new_lines.append(line)
        continue
    prefix = line.lstrip()
    comment = '# kode'
    for key, val in keywords:
        if prefix.startswith(key):
            comment = val
            break
    if comment == '# kode':
        if prefix.startswith('return'):
            comment = '# kembalikan nilai'
        elif prefix.startswith('raise '):
            comment = '# lempar exception'
        elif prefix.startswith('pass'):
            comment = '# tidak melakukan apa-apa'
        elif prefix.startswith('break'):
            comment = '# keluar dari loop'
        elif prefix.startswith('continue'):
            comment = '# lanjutkan ke iterasi berikutnya'
        elif prefix.startswith('else:'):
            comment = '# cabang lain'
        elif prefix.startswith('elif '):
            comment = '# percabangan kondisi'
        elif prefix.startswith('if '):
            comment = '# percabangan kondisi'
        elif prefix.startswith('for '):
            comment = '# loop for'
        elif prefix.startswith('while '):
            comment = '# loop while'
        elif prefix.startswith('with '):
            comment = '# blok context manager'
        elif prefix.startswith('try:'):
            comment = '# blok percobaan'
        elif prefix.startswith('except '):
            comment = '# tangkap exception'
        elif prefix.startswith('print('):
            comment = '# cetak output'
        elif prefix.startswith('input('):
            comment = '# baca input pengguna'
        elif prefix.startswith('assert '):
            comment = '# asersi kondisi'
        elif '=' in prefix and not prefix.startswith(('==', '!=', '<=', '>=', '+=', '-=', '*=', '/=')):
            comment = '# set nilai / inisialisasi'
        else:
            comment = '# kode fungsi/aksi'
    new_lines.append(f"{line} {comment}")

path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
print('Updated file with comments')

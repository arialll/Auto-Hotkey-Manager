"""Module pemungut/inspector untuk PyQtInspect.

Impor file ini di main.py untuk mengaktifkan inspeksi devtools.
Jika tidak dibutuhkan, cukup hapus atau beri komentar pada baris import.
"""

import os
import subprocess
import sys


def start_inspector():
  if "--devtools" not in sys.argv:
    # Mengambil file utama yang sedang dijalankan
    main_file = sys.argv[0] if sys.argv[0] else __file__
    cmd = [
        sys.executable,
        "-m",
        "PyQtInspect",
        "--direct",
        "--file",
        os.path.abspath(main_file),
        "--",
        "--devtools",
    ]
    subprocess.run(cmd)
    sys.exit()


# Jalankan otomatis saat modul di-import
start_inspector()
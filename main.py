"""Entry point for AutoHotkey Manager."""

import os
import subprocess
import sys

# Ensure project root is on path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
  sys.path.insert(0, ROOT)

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
  # Jalankan ulang skrip via CLI PyQtInspect secara otomatis jika belum dalam mode devtools
  if "--devtools" not in sys.argv:
    cmd = [
        sys.executable,
        "-m",
        "PyQtInspect",
        "--direct",
        "--file",
        __file__,
        "--",
        "--devtools",
    ]
    subprocess.run(cmd)
    sys.exit()

  app = QApplication(sys.argv)
  app.setApplicationName("AutoHotkey Manager")

  window = MainWindow()
  window.show()

  sys.exit(app.exec())


if __name__ == "__main__":
  main()
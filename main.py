"""Entry point for AutoHotkey Manager."""

import os
import sys

# Hapus atau beri komentar pada baris di bawah jika tidak ingin menggunakan inspector:
#import inspector

# Ensure project root is on path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
  sys.path.insert(0, ROOT)

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def set_app_id():
  """Set AppUserModelID agar Windows mengenali icon & taskbar group secara independen."""
  if sys.platform == "win32":
    try:
      import ctypes

      # Format: Organization.Product.SubProduct.Version
      my_app_id = "autohotkeymanager.desktop.app.1.0"
      ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
    except Exception:
      pass


def main():
  set_app_id()

  app = QApplication(sys.argv)
  app.setApplicationName("AutoHotkey Manager")

  # Path ke file icon (sesuaikan lokasi & nama file icon Anda)
  icon_path = os.path.join(ROOT, "assets", "icons", "icon.png")  # atau icon.ico

  if os.path.exists(icon_path):
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)

  window = MainWindow()

  if os.path.exists(icon_path):
    window.setWindowIcon(QIcon(icon_path))

  window.show()

  sys.exit(app.exec())


if __name__ == "__main__":
  main()
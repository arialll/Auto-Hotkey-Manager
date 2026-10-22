# Development Plan: AutoHotkey Manager

## Phase 1: Environment & Core Logic Setup
- [ ] Inisialisasi repository & virtual environment (`venv`).
- [ ] Buat `requirements.txt` (`PySide6`, `psutil`, `PyQt6-QScintilla`).
- [ ] **`core/file_manager.py`**:
  - Buat fungsi pembacaan dan penyimpan data hirarki JSON.
  - Buat fungsi CRUD file `.ahk` di disk.
- [ ] **`core/process_manager.py`**:
  - Implementasi fungsi `run_script(file_path)` via `subprocess.Popen`.
  - Implementasi fungsi `stop_script(pid)` via `psutil`.
  - Implementasi fungsi `restart_script(file_path)`.
  - Buat mekanisme status checker (`is_running(pid)`).

## Phase 2: UI Layout Framework
- [ ] **`main.py` & `ui/main_window.py`**:
  - Setup `QMainWindow` dengan `QSplitter` horizontal.
  - Tambahkan shortcut / toggle button untuk hide/show Left Panel.
- [ ] **`ui/left_panel.py`**:
  - Setup `QTreeWidget` untuk Kategori > Sub-Kategori > File AHK.
  - Hubungkan data dari `file_manager.py` ke `QTreeWidget`.
  - Tambahkan dialog CRUD (Tambah Kategori, Tambah File, Hapus).
- [ ] **`ui/styles.py`**:
  - Atur tema gelap (Dark Mode QSS) untuk UI dan status button disabled.

## Phase 3: Control Bar & Process Synchronization
- [ ] **`ui/right_panel.py`**:
  - Buat layout Control Bar atas (`Run`, `Edit`, `Stop`, `Restart`).
  - Hubungkan event klik tombol ke `process_manager.py`.
- [ ] **Status Loop Integrasi**:
  - Pasang `QTimer` (interval 1000ms) di UI untuk cek status PID script yang aktif.
  - Otomatis ubah state tombol (disabled/enabled & visual gelap) berdasarkan hasil cek PID.

## Phase 4: Code Editor Integration
- [ ] **`ui/editor.py`**:
  - Integrasikan QScintilla / Custom Text Editor.
  - Konfigurasi *line numbers*, *font monospace*, dan pembacaan/penulisan file AHK.
  - Tambahkan fiturnya saat file dipilih dari `QTreeWidget` / tombol `Edit` diklik.

## Phase 5: Polish & Testing
- [ ] Test interaksi GUI (Drag splitter, hide panel, multiterminal AHK run).
- [ ] Verifikasi penanganan *orphan process* (pastikan AHK mati jika GUI utama ditutup).
- [ ] Tambahkan icon SVG ke tombol-tombol action.
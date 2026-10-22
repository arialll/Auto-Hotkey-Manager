# Specification: AutoHotkey Manager

## 1. Overview
AutoHotkey Manager adalah aplikasi desktop GUI berbasis Python (PySide6) untuk mengelola, mengkategori, mengedit, dan mengontrol eksekusi script AutoHotkey (.ahk) secara terpusat.

## 2. Target Features
### 2.1 Left Panel (Category & File Tree)
- **Hierarchical View**: Menampilkan hirarki Kategori, Sub-Kategori, dan File AHK menggunakan `QTreeWidget`.
- **Category & File Management**: 
  - Tambah / Hapus Kategori & Sub-Kategori.
  - Tambah / Hapus File AHK.
- **Collapsible & Resizable**:
  - Panel kiri berada di dalam `QSplitter` (bisa di-drag lebarnya).
  - Bisa di-hide / show menggunakan tombol toggle atau shortcut.

### 2.2 Right Panel (Control Bar & Editor)
- **Control Bar (Per-File Actions)**:
  - Header menampilkan nama file AHK yang sedang dipilih.
  - Action Buttons: `Run` (▶), `Edit` (✏), `Stop` (⏹), `Restart` (🔄).
  - Dynamic Button States:
    - Status **Stopped**: `Run` & `Edit` Aktif. `Stop` & `Restart` Disabled (gelap/tidak bisa diklik).
    - Status **Running**: `Run` Disabled. `Stop`, `Restart`, & `Edit` Aktif.
- **Embedded Code Editor**:
  - Mengintegrasikan komponen editor (QScintilla / PySide6 Text Editor).
  - Menyediakan *syntax highlighting* dasar untuk AutoHotkey, *line numbers*, dan auto-save/manual save (`Ctrl+S`).

### 2.3 Process Management
- Tracking PID (Process ID) untuk setiap script AHK yang dijalankan.
- Monitoring status background process secara periodik via `QTimer` dan `psutil`.
- Kemampuan *Force Kill* dan *Graceful Restart* untuk script AHK.

## 3. Tech Stack & Dependencies
- **GUI Framework**: PySide6
- **Code Editor Component**: PyQt6-QScintilla / QScintilla (atau `QTextEdit` dengan `QSyntaxHighlighter` custom AHK)
- **Process & System**: `psutil`, `subprocess`
- **Data Persistence**: JSON (`config/categories.json`)
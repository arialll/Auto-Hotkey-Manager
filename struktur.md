ahk-manager/
├── assets/
│   └── icons/              # Icon SVG untuk Run, Stop, Edit, Restart, Folder
├── config/
│   └── categories.json     # Menyimpan hirarki kategori & daftar file AHK
├── core/
│   ├── __init__.py
│   ├── process_manager.py  # Logika run, stop, restart, & monitoring PID AHK
│   └── file_manager.py     # CRUD file AHK & struktur kategori JSON
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Window utama & QSplitter
│   ├── left_panel.py       # QTreeWidget kategori & file AHK + tombol CRUD
│   ├── right_panel.py      # Control bar (Run/Edit/Stop/Restart) + Code Editor
│   ├── editor.py           # Komponen Editor berbasis QScintilla / QTextEdit
│   └── styles.py           # QSS stylesheet (Dark Theme & state disabled)
├── main.py                 # Entry point aplikasi
├── requirements.txt
├── spec.md
└── plan.md
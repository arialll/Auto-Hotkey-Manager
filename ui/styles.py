"""Stylesheet (QSS) for AutoHotkey Manager - Dark Theme."""
DARK_STYLE = """
/* Global */
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Consolas", sans-serif;
    font-size: 10pt;
}

/* Splitter handle */
QSplitter::handle {
    background-color: #2b2b2b;
    width: 6px;
}
QSplitter::handle:hover {
    background-color: #3c3c3c;
}
QSplitterHandle QPushButton {
    background-color: #313244;
    color: #89b4fa;
    border: 1px solid #45475a;
    border-radius: 1px;
    font-size: 9pt;
    font-weight: 700;
    padding: 0;
}
QSplitterHandle QPushButton:hover {
    background-color: #89b4fa;
    color: #1e1e2e;
}

/* Toolbar */
QToolBar {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    spacing: 4px;
    padding: 4px;
}
QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px;
}
QToolBar QToolButton:hover {
    background-color: #313244;
    border-color: #45475a;
}

/* Tree widget */
QTreeWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 4px;
    outline: 0;
}
QTreeWidget::item {
    padding: 4px 6px;
    border-radius: 4px;
}
QTreeWidget::item:hover {
    background-color: #313244;
}
QTreeWidget::item:selected {
    background-color: #45475a;
    color: #cdd6f4;
}

/* Buttons */
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}
QPushButton:pressed {
    background-color: #585b70;
}
QPushButton:disabled {
    background-color: #1e1e2e;
    color: #585b70;
    border-color: #313244;
}

/* Action buttons in control bar */
QPushButton#runBtn {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border-color: #a6e3a1;
}
QPushButton#runBtn:hover { background-color: #94e2d5; }
QPushButton#runBtn:disabled { background-color: #313244; color: #585b70; border-color: #313244; }

QPushButton#stopBtn {
    background-color: #f38ba8;
    color: #1e1e2e;
    border-color: #f38ba8;
}
QPushButton#stopBtn:hover { background-color: #eba0ac; }
QPushButton#stopBtn:disabled { background-color: #313244; color: #585b70; border-color: #313244; }

QPushButton#restartBtn {
    background-color: #fab387;
    color: #1e1e2e;
    border-color: #fab387;
}
QPushButton#restartBtn:hover { background-color: #f9e2af; }
QPushButton#restartBtn:disabled { background-color: #313244; color: #585b70; border-color: #313244; }

QPushButton#editBtn {
    background-color: #89b4fa;
    color: #1e1e2e;
    border-color: #89b4fa;
}
QPushButton#editBtn:hover { background-color: #b4befe; }
QPushButton#editBtn:disabled { background-color: #313244; color: #585b70; border-color: #313244; }

/* Line edit / inputs */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #45475a;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #89b4fa;
}

/* Labels */
QLabel {
    color: #cdd6f4;
}
QLabel#headerLabel {
    font-size: 12pt;
    font-weight: 700;
    color: #89b4fa;
}

/* Status label */
QLabel#statusLabel {
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;
}
QLabel#statusStopped {
    color: #a6adc8;
    background-color: #313244;
}
QLabel#statusRunning {
    color: #1e1e2e;
    background-color: #a6e3a1;
}

/* Scroll bars */
QScrollBar:vertical {
    background: #181825;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #181825;
    height: 10px;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* Dialogs */
QDialog {
    background-color: #1e1e2e;
}
QMessageBox {
    background-color: #1e1e2e;
}

/* Menu */
QMenu {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #45475a;
}
QMenu::separator {
    height: 1px;
    background: #313244;
    margin: 4px 8px;
}

/* Tool bar / frame */
QFrame#controlBar {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px;
}
"""

"""Settings dialog for AutoHotkey Manager (shortcuts, toolbar visibility)."""
import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QKeySequenceEdit, QCheckBox, QHeaderView, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence

from core import settings_manager as sm
from core import file_manager as fm

SHORTCUT_LABELS = {
    "run": "Run Script",
    "stop": "Stop Script",
    "restart": "Restart Script",
    "save": "Save File",
    "edit_focus": "Focus Editor",
    "new_category": "New Category",
    "new_file": "New File",
    "import_file": "Import .ahk",
    "delete_selected": "Delete Selected",
    "rename_selected": "Rename Selected",
    "toggle_left_panel": "Toggle Left Panel",
    "toggle_toolbar": "Toggle Toolbar",
    "open_settings": "Open Settings",
    "quit": "Quit",
}


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(520, 520)
        self.settings = settings if settings is not None else sm.load_settings()
        self._edits = {}

        layout = QVBoxLayout(self)

        # Toolbar visibility
        self.toolbar_cb = QCheckBox("Show toolbar")
        self.toolbar_cb.setChecked(self.settings.get("toolbar_visible", True))
        layout.addWidget(self.toolbar_cb)

        # Shortcuts table
        layout.addWidget(QLabel("Shortcuts (click to edit):"))
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        keys = list(SHORTCUT_LABELS.keys())
        self.table.setRowCount(len(keys))
        for i, k in enumerate(keys):
            item = QTableWidgetItem(SHORTCUT_LABELS[k])
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, item)
            edit = QKeySequenceEdit()
            edit.setKeySequence(QKeySequence(self.settings["shortcuts"].get(k, sm.DEFAULT_SHORTCUTS[k])))
            self.table.setCellWidget(i, 1, edit)
            self._edits[k] = edit
        layout.addWidget(self.table)

        # Buttons
        btn_row = QHBoxLayout()
        reset_btn = QPushButton("Reset Defaults")
        reset_btn.clicked.connect(self._reset)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        ok_btn = QPushButton("Save")
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _reset(self):
        for k, edit in self._edits.items():
            edit.setKeySequence(QKeySequence(sm.DEFAULT_SHORTCUTS[k]))
        self.toolbar_cb.setChecked(True)

    def get_result(self):
        sc = {}
        for k, edit in self._edits.items():
            sc[k] = edit.keySequence().toString()
        return {
            "shortcuts": sc,
            "toolbar_visible": self.toolbar_cb.isChecked(),
        }
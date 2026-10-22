"""Right panel: Pure Code Editor (control bar removed)."""
import os

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QTimer

from core import process_manager as pm
from core import file_manager as fm
from ui.editor import CodeEditor
from ui.toast import show_toast


class RightPanel(QWidget):
    status_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracker = pm.ProcessTracker()
        self.current_category_id = None
        self.current_file_id = None
        self.current_file_entry = None

        # Editor murni tanpa Control Bar
        self.editor = CodeEditor()
        self.editor.save_requested.connect(self._on_save)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.editor, 1)

        # Polling timer untuk sync status ke Main Toolbar & Window Title
        self.status_timer = QTimer(self)
        self.status_timer.setInterval(1000)
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start()

        self._update_status()

    def load_file(self, category_id: str, file_entry: dict):
        self.current_category_id = category_id
        self.current_file_id = file_entry["id"]
        self.current_file_entry = file_entry
        content = fm.read_file_content(file_entry)
        self.editor.set_content(content)
        self._update_status()

    def _title_base(self):
        return "AutoHotkey Manager"

    def _set_window_title(self, status=None):
        w = self.window()
        if w is None:
            return
        if self.current_file_entry is None:
            w.setWindowTitle(self._title_base())
            return
        name = self.current_file_entry["name"]
        if status:
            w.setWindowTitle(f"{self._title_base()} - {name} - {status}")
        else:
            w.setWindowTitle(f"{self._title_base()} - {name}")

    def get_tracker(self):
        return self.tracker

    def _is_running(self) -> bool:
        if self.current_file_id is None:
            return False
        return self.tracker.is_file_running(self.current_file_id)

    def _update_status(self):
        has_file = self.current_file_entry is not None
        running = self._is_running()

        if not has_file:
            self._set_window_title()
            self.status_changed.emit({
                'run': False,
                'stop': False,
                'restart': False,
                'save': False
            })
            return

        if running:
            self._set_window_title("Running")
            self.status_changed.emit({
                'run': False,
                'stop': True,
                'restart': True,
                'save': True
            })
        else:
            self._set_window_title("Stopped")
            self.status_changed.emit({
                'run': True,
                'stop': False,
                'restart': False,
                'save': True
            })

    # Action Handlers (Dipanggil dari Toolbar / Shortcut)
    def _on_run(self):
        if self.current_file_entry is None:
            return
        self._on_save()
        path = fm.get_file_path(self.current_file_entry)
        pid = pm.run_script(path)
        if pid is not None:
            self.tracker.set_pid(self.current_file_id, pid)
            show_toast(self.window(), f"Running: {self.current_file_entry['name']}")
        self._update_status()

    def _on_stop(self):
        if self.current_file_id is None:
            return
        pid = self.tracker.get_pid(self.current_file_id)
        pm.stop_script(pid)
        self.tracker.remove(self.current_file_id)
        show_toast(self.window(), f"Stopped: {self.current_file_entry['name']}")
        self._update_status()

    def _on_restart(self):
        if self.current_file_entry is None:
            return
        self._on_save()
        path = fm.get_file_path(self.current_file_entry)
        old_pid = self.tracker.get_pid(self.current_file_id)
        pid = pm.restart_script(path, old_pid)
        if pid is not None:
            self.tracker.set_pid(self.current_file_id, pid)
            show_toast(self.window(), f"Restarted: {self.current_file_entry['name']}")
        self._update_status()

    def _on_edit(self):
        self.editor.setFocus()

    def _on_save(self):
        if self.current_file_entry is None:
            return
        content = self.editor.get_content()
        fm.write_file_content(self.current_file_entry, content)

    def save_current(self):
        self._on_save()

    def stop_all(self):
        self.tracker.stop_all()
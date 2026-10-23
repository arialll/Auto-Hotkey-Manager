"""Main window with splitter (toggle handle), toolbar, settings, shortcuts."""

import os

"""Main window with splitter (toggle handle), toolbar, settings, shortcuts."""

import os

from core import settings_manager as sm
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut  # <-- QShortcut di sini sudah benar
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    # HAPUS QShortcut DI SINI
    QSplitter,
    QSplitterHandle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel
from ui.settings_dialog import SettingsDialog
from ui.styles import DARK_STYLE
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")


def _icon(name):
  p = os.path.join(ICONS_DIR, name)
  if os.path.exists(p):
    return QIcon(p)
  return QIcon()


class ToggleSplitterHandle(QSplitterHandle):

  toggle_requested = Signal()

  def __init__(self, orientation, parent):
    super().__init__(orientation, parent)
    self._btn = QPushButton(self)
    self._btn.setFlat(True)
    self._btn.setCursor(Qt.PointingHandCursor)
    self._btn.clicked.connect(self.toggle_requested.emit)
    self.setMouseTracking(True)
    self._update_icon(False)

  def _update_icon(self, collapsed):
    if collapsed:
      self._btn.setText("▶")
      self._btn.setToolTip("Show left panel")
    else:
      self._btn.setText("◀")
      self._btn.setToolTip("Hide left panel")

  def set_collapsed(self, collapsed):
    self._update_icon(collapsed)

  def resizeEvent(self, event):
    super().resizeEvent(event)
    # Sesuaikan ukuran tombol agar muat di handle yang lebih tipis (lebar 6px)
    bw, bh = 12, 24
    x = (self.width() - bw) // 2
    y = (self.height() - bh) // 2
    self._btn.setGeometry(x, y, bw, bh)

  def mouseDoubleClickEvent(self, event):
    self.toggle_requested.emit()
    event.accept()


class ToggleSplitter(QSplitter):

  def __init__(self, orientation, parent=None):
    super().__init__(orientation, parent)
    self._handle = None

  def createHandle(self):
    h = ToggleSplitterHandle(self.orientation(), self)
    h.toggle_requested.connect(self._on_toggle)
    self._handle = h
    return h

  def _on_toggle(self):
    w = self.parent()
    while w is not None and not isinstance(w, QMainWindow):
      w = w.parent()
    if w is not None and hasattr(w, "_toggle_left_panel"):
      w._toggle_left_panel()

  def set_handle_collapsed(self, collapsed):
    if self._handle is not None:
      self._handle.set_collapsed(collapsed)


class MainWindow(QMainWindow):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("AutoHotkey Manager")
    self.resize(1150, 720)
    self.setStyleSheet(DARK_STYLE)

    self.settings = sm.load_settings()

    # Dynamic branch icons
    ar = os.path.join(ICONS_DIR, "arrow_right.svg").replace("\\", "/")
    ad = os.path.join(ICONS_DIR, "arrow_down.svg").replace("\\", "/")
    branch_qss = f"""
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    image: url("file:///{ar}");
}}
QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {{
    image: url("file:///{ad}");
}}
"""
    self.setStyleSheet(DARK_STYLE + branch_qss)

    # Left panel
    self.left_panel = LeftPanel()
    self.left_panel.file_selected.connect(self._on_file_selected)
    self.left_panel.file_open_requested.connect(self._on_file_open)

    # Right panel
    self.right_panel = RightPanel()
    self.right_panel.status_changed.connect(self._sync_toolbar_states)

    # Splitter
    self.splitter = ToggleSplitter(Qt.Horizontal)
    self.splitter.addWidget(self.left_panel)
    self.splitter.addWidget(self.right_panel)
    self.splitter.setSizes([self.settings.get("left_panel_width", 280), 870])
    self.splitter.setCollapsible(0, True)
    self.splitter.setCollapsible(1, False)
    self.splitter.setHandleWidth(6)

    central = QWidget()
    cl = QVBoxLayout(central)
    cl.setContentsMargins(0, 0, 0, 0)
    cl.setSpacing(0)
    cl.addWidget(self.splitter, 1)
    self.setCentralWidget(central)

    # Main toolbar
    self.toolbar = QToolBar("Main Toolbar")
    self.toolbar.setMovable(False)
    self.toolbar.setContextMenuPolicy(Qt.CustomContextMenu)
    self.toolbar.customContextMenuRequested.connect(self._toolbar_context_menu)
    self.addToolBar(self.toolbar)

    self._new_cat_action = self.toolbar.addAction(
        _icon("new_folder.svg"), "New Folder", self.left_panel._add_category
    )
    self._new_file_action = self.toolbar.addAction(
        _icon("new_file.svg"), "New File", self.left_panel._add_file
    )
    self._import_action = self.toolbar.addAction(
        _icon("import.svg"), "Import", self.left_panel._import_file
    )
    self._delete_action = self.toolbar.addAction(
        _icon("delete.svg"), "Delete", self.left_panel._delete_selected
    )
    self.toolbar.addSeparator()
    self._save_action = self.toolbar.addAction(
        _icon("save.svg"), "Save", self.right_panel.save_current
    )
    self.toolbar.addSeparator()
    self._run_action = self.toolbar.addAction(
        _icon("run.svg"), "Run", self.right_panel._on_run
    )
    self._stop_action = self.toolbar.addAction(
        _icon("stop.svg"), "Stop", self.right_panel._on_stop
    )
    self._restart_action = self.toolbar.addAction(
        _icon("restart.svg"), "Restart", self.right_panel._on_restart
    )
    self.toolbar.addSeparator()
    self._settings_action = self.toolbar.addAction(
        _icon("settings.svg"), "Settings", self._open_settings
    )

    # Menu bar
    menubar = self.menuBar()
    file_menu = menubar.addMenu("File")
    file_menu.addAction(self._save_action)
    file_menu.addSeparator()
    quit_act = QAction("Quit", self)
    quit_act.triggered.connect(self.close)
    file_menu.addAction(quit_act)

    view_menu = menubar.addMenu("View")
    self._toolbar_action = QAction("Toolbar", self)
    self._toolbar_action.setCheckable(True)
    self._toolbar_action.setChecked(self.settings.get("toolbar_visible", True))
    self._toolbar_action.triggered.connect(self._toggle_toolbar_checked)
    view_menu.addAction(self._toolbar_action)
    left_act = QAction("Left Panel", self)
    left_act.setCheckable(True)
    left_act.setChecked(self.settings.get("left_panel_visible", True))
    left_act.triggered.connect(self._toggle_left_panel_checked)
    view_menu.addAction(left_act)

    tools_menu = menubar.addMenu("Tools")
    settings_act = QAction("Settings", self)
    settings_act.triggered.connect(self._open_settings)
    tools_menu.addAction(settings_act)

    help_menu = menubar.addMenu("Help")
    about_act = QAction("About", self)
    about_act.triggered.connect(self._about)
    help_menu.addAction(about_act)

    # State
    self._shortcuts = {}
    self._left_visible = self.settings.get("left_panel_visible", True)
    if not self._left_visible:
      self.splitter.setSizes([0, self.width()])

    self._apply_toolbar_visibility()
    self._apply_shortcuts(self.settings.get("shortcuts", sm.DEFAULT_SHORTCUTS))

    # Restore geometry
    geom = self.settings.get("window_geometry")
    if geom:
      from PySide6.QtCore import QByteArray

      self.restoreGeometry(QByteArray.fromHex(geom.encode()))

  def _sync_toolbar_states(self, states: dict):
    self._run_action.setEnabled(states.get("run", False))
    self._stop_action.setEnabled(states.get("stop", False))
    self._restart_action.setEnabled(states.get("restart", False))
    self._save_action.setEnabled(states.get("save", False))

  def _toolbar_context_menu(self, pos):
    menu = QMenu(self)
    hide_act = menu.addAction("Hide Toolbar")
    hide_act.triggered.connect(lambda: self._set_toolbar_visible(False))
    menu.exec(self.toolbar.mapToGlobal(pos))

  def _toggle_toolbar_checked(self, checked):
    self._set_toolbar_visible(checked)

  def _set_toolbar_visible(self, visible):
    self.toolbar.setVisible(visible)
    self.settings["toolbar_visible"] = visible
    sm.save_settings(self.settings)
    self._toolbar_action.setChecked(visible)

  def _apply_toolbar_visibility(self):
    self._set_toolbar_visible(self.settings.get("toolbar_visible", True))

  def _toggle_toolbar(self):
    self._set_toolbar_visible(not self.toolbar.isVisible())

  def _toggle_left_panel_checked(self, checked):
    if checked != self._left_visible:
      self._toggle_left_panel()

  def _toggle_left_panel(self):
    if self._left_visible:
      self._saved_width = (
          self.splitter.sizes()[0]
          if self.splitter.sizes()[0] > 0
          else self.settings.get("left_panel_width", 280)
      )
      self.splitter.setSizes([0, self.width()])
      self._left_visible = False
      self.splitter.set_handle_collapsed(True)
    else:
      w = (
          self._saved_width
          if hasattr(self, "_saved_width")
          else self.settings.get("left_panel_width", 280)
      )
      self.splitter.setSizes([w, self.width() - w])
      self._left_visible = True
      self.splitter.set_handle_collapsed(False)
    self.settings["left_panel_visible"] = self._left_visible
    if self._left_visible:
      self.settings["left_panel_width"] = self.splitter.sizes()[0]
    sm.save_settings(self.settings)

  def _apply_shortcuts(self, sc):
    for sh in self._shortcuts.values():
      sh.deleteLater()
    self._shortcuts.clear()

    def bind(key, fn):
      if not key:
        return
      sh = QShortcut(QKeySequence(key), self)
      sh.activated.connect(fn)
      return sh

    self._shortcuts["run"] = bind(sc.get("run"), self.right_panel._on_run)
    self._shortcuts["stop"] = bind(sc.get("stop"), self.right_panel._on_stop)
    self._shortcuts["restart"] = bind(
        sc.get("restart"), self.right_panel._on_restart
    )
    self._save_action.setShortcut(QKeySequence(sc.get("save", "")))
    self._shortcuts["edit_focus"] = bind(
        sc.get("edit_focus"), self.right_panel._on_edit
    )
    self._shortcuts["new_category"] = bind(
        sc.get("new_category"), self.left_panel._add_category
    )
    self._shortcuts["new_file"] = bind(
        sc.get("new_file"), self.left_panel._add_file
    )
    self._shortcuts["import_file"] = bind(
        sc.get("import_file"), self.left_panel._import_file
    )
    self._shortcuts["delete_selected"] = bind(
        sc.get("delete_selected"), self.left_panel._delete_selected
    )
    self._shortcuts["rename_selected"] = bind(
        sc.get("rename_selected"), self.left_panel._rename_selected
    )
    self._shortcuts["toggle_left_panel"] = bind(
        sc.get("toggle_left_panel"), self._toggle_left_panel
    )
    self._shortcuts["toggle_toolbar"] = bind(
        sc.get("toggle_toolbar"), self._toggle_toolbar
    )
    self._shortcuts["open_settings"] = bind(
        sc.get("open_settings"), self._open_settings
    )
    self._shortcuts["quit"] = bind(sc.get("quit"), self.close)

  def _open_settings(self):
    dlg = SettingsDialog(self, self.settings)
    if dlg.exec():
      res = dlg.get_result()
      self.settings["shortcuts"] = res["shortcuts"]
      self.settings["toolbar_visible"] = res["toolbar_visible"]
      sm.save_settings(self.settings)
      self._apply_toolbar_visibility()
      self._apply_shortcuts(self.settings["shortcuts"])
      if hasattr(self, "_toolbar_action"):
        self._toolbar_action.setChecked(res["toolbar_visible"])

  def showEvent(self, event):
    super().showEvent(event)
    self.splitter.set_handle_collapsed(not self._left_visible)

  def _on_file_selected(self, category_id, file_entry):
    self.right_panel.load_file(category_id, file_entry)

  def _on_file_open(self, category_id, file_entry):
    self.right_panel.load_file(category_id, file_entry)
    self.right_panel._on_edit()

  def _about(self):
    QMessageBox.about(
        self,
        "About",
        "AutoHotkey Manager\nPython + PySide6\nManage your .ahk scripts with"
        " drag & drop.",
    )

  def closeEvent(self, event):
    try:
      self.settings = sm.load_settings()
      self.settings["left_panel_visible"] = self._left_visible
      if self._left_visible:
        self.settings["left_panel_width"] = self.splitter.sizes()[0]
      self.settings["window_geometry"] = (
          self.saveGeometry().toHex().data().decode()
      )
      sm.save_settings(self.settings)
      self.right_panel.stop_all()
    except Exception:
      pass
    event.accept()
"""Left panel: Category & File tree with search, CRUD, drag & drop, icons."""
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QInputDialog, QMessageBox, QMenu, QFileDialog,
    QAbstractItemView, QLineEdit, QLabel,
)
from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel, QSize
from PySide6.QtGui import QAction, QIcon, QStandardItemModel

from core import file_manager as fm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")

chevron_right = os.path.join(ICONS_DIR, "chevron_right.svg").replace("\\", "/")
chevron_down = os.path.join(ICONS_DIR, "chevron_down.svg").replace("\\", "/")

def _icon(name):
    p = os.path.join(ICONS_DIR, name)
    if os.path.exists(p):
        return QIcon(p)
    return QIcon()


class LeftPanel(QWidget):
    file_selected = Signal(str, dict)
    file_open_requested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search files/folders...")
        self.search_box.textChanged.connect(self._apply_filter)
        self.search_box.setClearButtonEnabled(True)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setAnimated(True)
        self.tree.setIconSize(QSize(20, 20))
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.itemExpanded.connect(self._on_expand_toggle)
        self.tree.itemCollapsed.connect(self._on_expand_toggle)
        self.tree.setStyleSheet(f"""
    /* Mengatur lebar area branch agar tidak terlalu renggang */
    QTreeView::branch {{
        background: transparent;
    }}

    QTreeView::branch:has-children:closed {{
        image: url("{chevron_right}");
        width: 12px;
        height: 12px;
    }}

    QTreeView::branch:has-children:open {{
        image: url("{chevron_down}");
        width: 12px;
        height: 12px;
    }}

    /* Merapatkan jarak item teks/folder ke ikon branch */
    QTreeWidget::item {{
        padding-left: 0px;
        margin-left: -1px; /* Tarik item ke kiri mendekati chevron */
    }}
""")

        # Drag & drop
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree.setDefaultDropAction(Qt.MoveAction)
        self.tree.setDropIndicatorShown(True)
        self.tree.startDrag = self._start_drag
        self.tree.dropEvent = self._drop_event

        self._drag_item = None
        self._filter_text = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(self.search_box)
        layout.addWidget(self.tree)

        self.refresh()

    # ---------- drag & drop ----------
    def _start_drag(self, supportedActions):
        self._drag_item = self.tree.currentItem()
        QTreeWidget.startDrag(self.tree, supportedActions)

    def _drop_event(self, event):
        target = self.tree.itemAt(event.position().toPoint())
        source = self._drag_item
        if source is None or source is target:
            event.ignore()
            self._drag_item = None
            return
        sdata = source.data(0, Qt.UserRole)
        if not sdata:
            event.ignore()
            self._drag_item = None
            return

        target_cat_id = None
        if target is None:
            target_cat_id = None
        else:
            tdata = target.data(0, Qt.UserRole)
            if not tdata:
                event.ignore()
                self._drag_item = None
                return
            if tdata[0] == "category":
                target_cat_id = tdata[1]
            elif tdata[0] == "file":
                parent = target.parent()
                if parent is not None:
                    pdata = parent.data(0, Qt.UserRole)
                    if pdata and pdata[0] == "category":
                        target_cat_id = pdata[1]
                if target_cat_id is None:
                    event.ignore()
                    self._drag_item = None
                    return

        if sdata[0] == "category":
            cat_id = sdata[1]
            ok = fm.move_category(cat_id, target_cat_id)
        elif sdata[0] == "file":
            _, src_cat_id, file_id = sdata
            if target_cat_id is None:
                event.ignore()
                self._drag_item = None
                return
            ok = fm.move_file(file_id, target_cat_id)
        else:
            ok = False

        self._drag_item = None
        if ok:
            event.accept()
            self.refresh()
            self._apply_filter(self.search_box.text())
        else:
            event.ignore()

    # ---------- data refresh ----------
    def refresh(self):
        expanded = self._expanded_ids()
        if not expanded:
            expanded = self._load_state()
        if not expanded:
            # default: expand all
            data = fm.load_categories()
            expanded = self._all_category_ids(data)
        self.tree.clear()
        data = fm.load_categories()
        for cat in data.get("categories", []):
            self._add_category_node(None, cat)
        self._restore_expanded(expanded)
        self._save_state(expanded)
        self._apply_filter(self.search_box.text())

    def _all_category_ids(self, data):
        ids = set()
        def walk(cat):
            ids.add(cat["id"])
            for sub in cat.get("subcategories", []):
                walk(sub)
        for c in data.get("categories", []):
            walk(c)
        return ids

    def _state_path(self):
        return None

    def _load_state(self):
        try:
            from core import settings_manager as sm
            s = sm.load_settings()
            return set(s.get("expanded_categories", []))
        except Exception:
            return set()

    def _save_state(self, ids):
        try:
            from core import settings_manager as sm
            s = sm.load_settings()
            s["expanded_categories"] = list(ids)
            sm.save_settings(s)
        except Exception:
            pass

    def _on_expand_toggle(self, item):
        self._save_state(self._expanded_ids())

    def _expanded_ids(self):
        ids = set()
        def walk(item):
            data = item.data(0, Qt.UserRole)
            if data and data[0] == "category":
                if item.isExpanded():
                    ids.add(data[1])
            for i in range(item.childCount()):
                walk(item.child(i))
        walk(self.tree.invisibleRootItem())
        return ids

    def _restore_expanded(self, ids):
        def walk(item):
            data = item.data(0, Qt.UserRole)
            if data and data[0] == "category" and data[1] in ids:
                item.setExpanded(True)
            for i in range(item.childCount()):
                walk(item.child(i))
        walk(self.tree.invisibleRootItem())

    def _add_category_node(self, parent_item, cat):
        item = QTreeWidgetItem()
        item.setText(0, cat["name"])
        item.setIcon(0, _icon("folder.svg"))
        item.setData(0, Qt.UserRole, ("category", cat["id"]))
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        if parent_item is None:
            self.tree.addTopLevelItem(item)
        else:
            parent_item.addChild(item)
        for sub in cat.get("subcategories", []):
            self._add_category_node(item, sub)
        for f in cat.get("files", []):
            fitem = QTreeWidgetItem()
            fitem.setText(0, f["name"])
            fitem.setIcon(0, _icon("file.svg"))
            fitem.setData(0, Qt.UserRole, ("file", cat["id"], f["id"]))
            item.addChild(fitem)
        item.setExpanded(False)

    # ---------- filter ----------
    def _apply_filter(self, text):
        self._filter_text = (text or "").strip().lower()
        self._filter_items(self.tree.invisibleRootItem())

    def _filter_items(self, parent):
        for i in range(parent.childCount()):
            item = parent.child(i)
            data = item.data(0, Qt.UserRole)
            # leaf?
            has_children = item.childCount() > 0
            if has_children:
                self._filter_items(item)
            # determine if any descendant visible
            any_child_visible = any(self._item_visible(item.child(j)) for j in range(item.childCount()))
            name = item.text(0).lower()
            matches = (self._filter_text in name) if self._filter_text else True
            visible = matches or any_child_visible
            item.setHidden(not visible)
            if self._filter_text and matches:
                item.setExpanded(True)

    def _item_visible(self, item):
        if item.isHidden():
            return False
        return True

    # ---------- selection ----------
    def _on_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        if data[0] == "file":
            _, cat_id, file_id = data
            cats = fm.load_categories()
            res = fm.find_file(cats, file_id)
            if res:
                cat, entry = res
                self.file_selected.emit(cat_id, entry)

    def _on_item_double_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data and data[0] == "file":
            _, cat_id, file_id = data
            cats = fm.load_categories()
            res = fm.find_file(cats, file_id)
            if res:
                cat, entry = res
                self.file_open_requested.emit(cat_id, entry)

    def get_selected(self):
        item = self.tree.currentItem()
        if item is None:
            return None
        return item.data(0, Qt.UserRole)

    # ---------- CRUD ----------
    def _add_category(self):
        selected = self.get_selected()
        parent_id = None
        if selected and selected[0] == "category":
            parent_id = selected[1]
        elif selected and selected[0] == "file":
            item = self.tree.currentItem()
            parent = item.parent()
            if parent is not None:
                pdata = parent.data(0, Qt.UserRole)
                if pdata and pdata[0] == "category":
                    parent_id = pdata[1]
        name, ok = QInputDialog.getText(self, "Tambah Kategori", "Nama kategori:")
        if ok and name.strip():
            try:
                fm.add_category(name.strip(), parent_id)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _add_file(self):
        selected = self.get_selected()
        cat_id = None
        if selected and selected[0] == "category":
            cat_id = selected[1]
        elif selected and selected[0] == "file":
            item = self.tree.currentItem()
            parent = item.parent()
            if parent is not None:
                pdata = parent.data(0, Qt.UserRole)
                if pdata and pdata[0] == "category":
                    cat_id = pdata[1]
        if cat_id is None:
            QMessageBox.information(self, "Info", "Pilih kategori terlebih dahulu.")
            return
        name, ok = QInputDialog.getText(self, "Tambah File AHK", "Nama file (tanpa .ahk):")
        if ok and name.strip():
            try:
                fm.add_file(cat_id, name.strip())
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _import_file(self):
        selected = self.get_selected()
        cat_id = None
        if selected and selected[0] == "category":
            cat_id = selected[1]
        elif selected and selected[0] == "file":
            item = self.tree.currentItem()
            parent = item.parent()
            if parent is not None:
                pdata = parent.data(0, Qt.UserRole)
                if pdata and pdata[0] == "category":
                    cat_id = pdata[1]
        if cat_id is None:
            QMessageBox.information(self, "Info", "Pilih kategori terlebih dahulu.")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Import .ahk", "", "AutoHotkey (*.ahk)")
        if path:
            try:
                fm.import_external_file(cat_id, path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _rename_selected(self):
        selected = self.get_selected()
        if not selected:
            return
        if selected[0] == "category":
            cat_id = selected[1]
            name, ok = QInputDialog.getText(self, "Rename Kategori", "Nama baru:")
            if ok and name.strip():
                fm.rename_category(cat_id, name.strip())
                self.refresh()
        elif selected[0] == "file":
            _, cat_id, file_id = selected
            name, ok = QInputDialog.getText(self, "Rename File", "Nama file (tanpa .ahk):")
            if ok and name.strip():
                fm.rename_file(file_id, name.strip())
                self.refresh()
    def _delete_selected(self):
        selected = self.get_selected()
        if not selected:
            return
        if selected[0] == "category":
            cat_id = selected[1]
            reply = QMessageBox.question(self, "Hapus", "Hapus kategori ini dan semua isinya?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                fm.delete_category(cat_id)
                self.refresh()
        elif selected[0] == "file":
            _, cat_id, file_id = selected
            reply = QMessageBox.question(self, "Hapus", "Hapus file ini?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                fm.delete_file(cat_id, file_id)
                self.refresh()
        selected = self.get_selected()
        if not selected:
            return
        if selected[0] == "category":
            cat_id = selected[1]
            reply = QMessageBox.question(self, "Hapus", "Hapus kategori ini dan semua isinya?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                fm.delete_category(cat_id)
                self.refresh()
        elif selected[0] == "file":
            _, cat_id, file_id = selected
            reply = QMessageBox.question(self, "Hapus", "Hapus file ini?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                fm.delete_file(cat_id, file_id)
                self.refresh()

    def _context_menu(self, pos):
        item = self.tree.itemAt(pos)
        menu = QMenu(self)
        add_cat = QAction(_icon("new_folder.svg"), "Tambah Kategori", self)
        add_cat.triggered.connect(self._add_category)
        menu.addAction(add_cat)
        add_file = QAction(_icon("new_file.svg"), "Tambah File", self)
        add_file.triggered.connect(self._add_file)
        menu.addAction(add_file)
        import_act = QAction(_icon("import.svg"), "Import .ahk", self)
        import_act.triggered.connect(self._import_file)
        menu.addAction(import_act)
        rename_act = QAction(_icon("rename.svg"), "Rename", self)
        rename_act.triggered.connect(self._rename_selected)
        menu.addAction(rename_act)
        menu.addSeparator()
        del_act = QAction(_icon("delete.svg"), "Hapus", self)
        del_act.triggered.connect(self._delete_selected)
        menu.addAction(del_act)
        menu.exec(self.tree.viewport().mapToGlobal(pos))
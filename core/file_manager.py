"""File manager for AutoHotkey Manager.

Handles JSON persistence of category/file hierarchy and CRUD operations on .ahk files.
"""
import json
import os
import shutil
from typing import List, Dict, Optional

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "categories.json")
AHK_STORAGE_DIR = os.path.join(BASE_DIR, "ahk_scripts")


def _ensure_dirs():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    os.makedirs(AHK_STORAGE_DIR, exist_ok=True)


def load_categories() -> Dict:
    """Load the category hierarchy from JSON."""
    _ensure_dirs()
    if not os.path.exists(CONFIG_PATH):
        data = {"categories": []}
        save_categories(data)
        return data
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {"categories": []}
        save_categories(data)
    return data


def save_categories(data: Dict) -> None:
    """Save the category hierarchy to JSON."""
    _ensure_dirs()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _gen_id() -> str:
    import uuid
    return uuid.uuid4().hex[:12]


def find_category(data: Dict, category_id: str) -> Optional[Dict]:
    """Find a category by id anywhere in the tree."""
    for cat in data.get("categories", []):
        if cat.get("id") == category_id:
            return cat
        found = _find_sub(cat, category_id)
        if found is not None:
            return found
    return None


def _find_sub(cat: Dict, category_id: str) -> Optional[Dict]:
    for sub in cat.get("subcategories", []):
        if sub.get("id") == category_id:
            return sub
        found = _find_sub(sub, category_id)
        if found is not None:
            return found
    return None


def find_parent(data: Dict, category_id: str):
    """Return (parent_list, index) for a category, or None."""
    for i, cat in enumerate(data.get("categories", [])):
        if cat.get("id") == category_id:
            return data["categories"], i
    for cat in data.get("categories", []):
        res = _find_parent_sub(cat, category_id)
        if res is not None:
            return res
    return None


def _find_parent_sub(cat: Dict, category_id: str):
    for i, sub in enumerate(cat.get("subcategories", [])):
        if sub.get("id") == category_id:
            return cat["subcategories"], i
        res = _find_parent_sub(sub, category_id)
        if res is not None:
            return res
    return None


def add_category(name: str, parent_id: Optional[str] = None) -> Dict:
    """Add a top-level category or a subcategory under parent_id."""
    data = load_categories()
    new_cat = {
        "id": _gen_id(),
        "name": name,
        "subcategories": [],
        "files": [],
    }
    if parent_id is None:
        data["categories"].append(new_cat)
    else:
        parent = find_category(data, parent_id)
        if parent is None:
            raise ValueError("Parent category not found")
        parent.setdefault("subcategories", []).append(new_cat)
    save_categories(data)
    return new_cat


def delete_category(category_id: str) -> bool:
    """Delete a category and all its children (files on disk are NOT removed)."""
    data = load_categories()
    res = find_parent(data, category_id)
    if res is None:
        return False
    lst, idx = res
    del lst[idx]
    save_categories(data)
    return True


def rename_category(category_id: str, new_name: str) -> bool:
    cat = None
    data = load_categories()
    cat = find_category(data, category_id)
    if cat is None:
        return False
    cat["name"] = new_name
    save_categories(data)
    return True


def add_file(category_id: str, name: str, content: str = "") -> Dict:
    """Create a new .ahk file entry under a category and write content to disk."""
    data = load_categories()
    cat = find_category(data, category_id)
    if cat is None:
        raise ValueError("Category not found")
    # ensure unique filename
    safe_name = name if name.endswith(".ahk") else name + ".ahk"
    # avoid duplicates in same category
    existing = [f["name"] for f in cat.get("files", [])]
    if safe_name in existing:
        raise ValueError("File already exists in this category")
    file_id = _gen_id()
    rel_path = os.path.join("ahk_scripts", f"{file_id}_{safe_name}")
    abs_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    entry = {"id": file_id, "name": safe_name, "path": rel_path}
    cat.setdefault("files", []).append(entry)
    save_categories(data)
    return entry


def delete_file(category_id: str, file_id: str) -> bool:
    """Remove file entry and delete the file on disk."""
    data = load_categories()
    cat = find_category(data, category_id)
    if cat is None:
        return False
    files = cat.get("files", [])
    for i, f in enumerate(files):
        if f.get("id") == file_id:
            rel_path = f.get("path")
            if rel_path:
                abs_path = os.path.join(BASE_DIR, rel_path)
                try:
                    if os.path.exists(abs_path):
                        os.remove(abs_path)
                except OSError:
                    pass
            del files[i]
            save_categories(data)
            return True
    return False


def get_file_path(file_entry: Dict) -> str:
    return os.path.join(BASE_DIR, file_entry["path"])


def read_file_content(file_entry: Dict) -> str:
    path = get_file_path(file_entry)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file_content(file_entry: Dict, content: str) -> None:
    path = get_file_path(file_entry)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def find_file(data: Dict, file_id: str):
    """Find (category, file_entry) by file id."""
    for cat in data.get("categories", []):
        res = _find_file_in(cat, file_id)
        if res is not None:
            return res
    return None


def _find_file_in(cat: Dict, file_id: str):
    for f in cat.get("files", []):
        if f.get("id") == file_id:
            return cat, f
    for sub in cat.get("subcategories", []):
        res = _find_file_in(sub, file_id)
        if res is not None:
            return res
    return None


def find_category_of_file(data: Dict, file_id: str) -> Optional[str]:
    res = find_file(data, file_id)
    if res is None:
        return None
    return res[0].get("id")


def move_file(file_id: str, new_category_id: str) -> bool:
    """Move a file entry from its current category to new_category_id."""
    data = load_categories()
    # find current location
    found = find_file(data, file_id)
    if found is None:
        return False
    old_cat, entry = found
    if old_cat.get("id") == new_category_id:
        return True
    new_cat = find_category(data, new_category_id)
    if new_cat is None:
        return False
    # remove from old
    old_cat["files"] = [f for f in old_cat.get("files", []) if f.get("id") != file_id]
    # avoid duplicate name in target
    existing_names = [f["name"] for f in new_cat.get("files", [])]
    name = entry["name"]
    if name in existing_names:
        base, ext = os.path.splitext(name)
        i = 1
        while f"{base}_{i}{ext}" in existing_names:
            i += 1
        name = f"{base}_{i}{ext}"
        entry["name"] = name
    new_cat.setdefault("files", []).append(entry)
    save_categories(data)
    return True


def move_category(category_id: str, new_parent_id) -> bool:
    """Move a category (and subtree) to be a child of new_parent_id (or top-level if None)."""
    data = load_categories()
    if category_id == new_parent_id:
        return False
    # prevent moving into own descendant
    if new_parent_id is not None and _is_descendant(data, category_id, new_parent_id):
        return False
    res = find_parent(data, category_id)
    if res is None:
        return False
    lst, idx = res
    cat = lst.pop(idx)
    if new_parent_id is None:
        data["categories"].append(cat)
    else:
        parent = find_category(data, new_parent_id)
        if parent is None:
            # restore
            lst.insert(idx, cat)
            save_categories(data)
            return False
        parent.setdefault("subcategories", []).append(cat)
    save_categories(data)
    return True


def _is_descendant(data, ancestor_id, candidate_id) -> bool:
    """Check if candidate_id is a descendant of ancestor_id."""
    anc = find_category(data, ancestor_id)
    if anc is None:
        return False
    def walk(c):
        for sub in c.get("subcategories", []):
            if sub.get("id") == candidate_id:
                return True
            if walk(sub):
                return True
        return False
    return walk(anc)
"""Process manager for AutoHotkey Manager.

Handles running, stopping, restarting AHK scripts and tracking their PIDs.
"""
import os
import subprocess
import psutil
from typing import Optional, Dict


# Common AutoHotkey executable names to try
AHK_EXECUTABLES = [
    "AutoHotkey64.exe",
    "AutoHotkey32.exe",
    "AutoHotkey.exe",
    "AutoHotkeyU64.exe",
    "AutoHotkeyU32.exe",
]


def _find_ahk_exe() -> Optional[str]:
    """Locate an AutoHotkey executable on the system."""
    # Check common install paths
    candidates = []
    for name in AHK_EXECUTABLES:
        candidates.append(name)
    # Search in PATH
    for name in AHK_EXECUTABLES:
        path = shutil_which(name)
        if path:
            return path
    # Common install directories
    program_files = [os.environ.get("ProgramFiles", r"C:\Program Files"),
                    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]
    for pf in program_files:
        for sub in ["AutoHotkey", "AutoHotkey\\v2", "AutoHotkey\\v1.1"]:
            for name in AHK_EXECUTABLES:
                p = os.path.join(pf, sub, name)
                if os.path.exists(p):
                    return p
    return None


def shutil_which(cmd: str) -> Optional[str]:
    import shutil
    return shutil.which(cmd)


def is_running(pid: Optional[int]) -> bool:
    """Check whether a process with given PID is still running."""
    if pid is None:
        return False
    try:
        proc = psutil.Process(pid)
        if not proc.is_running():
            return False
        # Ensure it's not a zombie
        status = proc.status()
        if status == psutil.STATUS_ZOMBIE:
            return False
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False


def run_script(file_path: str) -> Optional[int]:
    """Launch an .ahk script and return its PID, or None on failure."""
    ahk_exe = _find_ahk_exe()
    if ahk_exe is None:
        # Fall back: try to run via shell association
        try:
            proc = subprocess.Popen(
                [file_path],
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP") else 0,
            )
            return proc.pid
        except Exception:
            return None
    try:
        proc = subprocess.Popen(
            [ahk_exe, file_path],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP") else 0,
        )
        return proc.pid
    except Exception:
        return None


def stop_script(pid: Optional[int], force: bool = True) -> bool:
    """Stop a script by PID. Force kill by default."""
    if pid is None:
        return False
    try:
        proc = psutil.Process(pid)
        if force:
            # Kill process tree
            children = proc.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        else:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def restart_script(file_path: str, old_pid: Optional[int] = None) -> Optional[int]:
    """Stop old process (if any) and start a new one."""
    if old_pid is not None:
        stop_script(old_pid)
    return run_script(file_path)


class ProcessTracker:
    """Tracks running AHK scripts: file_id -> pid."""

    def __init__(self):
        self._pids: Dict[str, int] = {}

    def set_pid(self, file_id: str, pid: int) -> None:
        self._pids[file_id] = pid

    def get_pid(self, file_id: str) -> Optional[int]:
        return self._pids.get(file_id)

    def remove(self, file_id: str) -> None:
        self._pids.pop(file_id, None)

    def is_file_running(self, file_id: str) -> bool:
        pid = self._pids.get(file_id)
        if pid is None:
            return False
        if not is_running(pid):
            del self._pids[file_id]
            return False
        return True

    def all_running(self) -> Dict[str, int]:
        # prune dead
        dead = [fid for fid, pid in self._pids.items() if not is_running(pid)]
        for fid in dead:
            del self._pids[fid]
        return dict(self._pids)

    def stop_all(self) -> None:
        for pid in list(self._pids.values()):
            stop_script(pid)
        self._pids.clear()
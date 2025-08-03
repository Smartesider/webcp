"""
LOCK ENFORCER MODULE

All system-critical operations must use this module to ensure
compliance with port, directory, and API restrictions.

Failure to use these locks will break system integrity.
"""

import os
import fcntl
from pathlib import Path
from typing import Callable

from config import API_PORT, BASE_FRONTEND_DIR, LOCK_DIR

def ensure_port(port: int):
    """
    Raises exception if port is not the locked port.
    """
    if port != API_PORT:
        raise ValueError(f"Port {port} not allowed. Must be {API_PORT}.")

def ensure_path_allowed(path: str):
    """
    Ensures the path is within allowed BASE_FRONTEND_DIR.
    Raises exception otherwise.
    """
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(os.path.abspath(BASE_FRONTEND_DIR)):
        raise PermissionError(f"Access to {abs_path} denied. Must be inside {BASE_FRONTEND_DIR}.")

def file_lock(file_path: str, func: Callable, *args, **kwargs):
    """
    Acquire an exclusive lock on a lock file before executing func.
    Ensures serialized access to critical resources.
    """
    lock_file = os.path.join(LOCK_DIR, os.path.basename(file_path) + ".lock")
    os.makedirs(LOCK_DIR, exist_ok=True)
    with open(lock_file, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            result = func(*args, **kwargs)
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)
    return result

def backup_file(file_path: str):
    """
    Backup the file before destructive operation.
    Keeps MAX_BACKUP_VERSIONS versions.
    """
    import shutil
    import time

    ensure_path_allowed(file_path)

    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(os.path.dirname(file_path), ".backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup_files = sorted(Path(backup_dir).glob(os.path.basename(file_path) + ".*"), reverse=True)

    # Remove oldest backups if exceeding MAX_BACKUP_VERSIONS
    for old_backup in backup_files[MAX_BACKUP_VERSIONS:]:
        old_backup.unlink()

    backup_path = os.path.join(backup_dir, f"{os.path.basename(file_path)}.{timestamp}.bak")
    shutil.copy2(file_path, backup_path)
    return backup_path

"""Vault locking: prevent concurrent writes via a lockfile."""
from __future__ import annotations

import os
import time
from pathlib import Path


class LockError(Exception):
    pass


def _lock_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".lock")


def acquire(vault_path: str, timeout: float = 5.0, poll: float = 0.1) -> Path:
    """Acquire a lock for the given vault, waiting up to *timeout* seconds.

    Returns the lock file path on success.
    Raises LockError if the lock cannot be acquired in time.
    """
    lock = _lock_path(vault_path)
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise LockError(
                    f"Could not acquire lock for '{vault_path}' within {timeout}s. "
                    f"Remove '{lock}' if no other process is running."
                )
            time.sleep(poll)


def release(lock_path: Path) -> None:
    """Release a previously acquired lock."""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def is_locked(vault_path: str) -> bool:
    """Return True if a lock file exists for the given vault."""
    return _lock_path(vault_path).exists()


def owner_pid(vault_path: str) -> int | None:
    """Return the PID stored in the lock file, or None if not locked."""
    lock = _lock_path(vault_path)
    try:
        return int(lock.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None

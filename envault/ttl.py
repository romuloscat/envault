"""TTL (time-to-live) support for secrets in envault."""

import json
import time
from pathlib import Path
from typing import Optional


class TTLError(Exception):
    pass


def _ttl_path(vault_file: Path) -> Path:
    return vault_file.with_suffix(".ttl.json")


def _load_ttl(vault_file: Path) -> dict:
    p = _ttl_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(vault_file: Path, data: dict) -> None:
    _ttl_path(vault_file).write_text(json.dumps(data, indent=2))


def set_ttl(vault_file: Path, key: str, seconds: int) -> None:
    """Set expiry for a key, `seconds` from now."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive integer.")
    data = _load_ttl(vault_file)
    data[key] = time.time() + seconds
    _save_ttl(vault_file, data)


def get_expiry(vault_file: Path, key: str) -> Optional[float]:
    """Return the expiry timestamp for a key, or None if no TTL set."""
    return _load_ttl(vault_file).get(key)


def is_expired(vault_file: Path, key: str) -> bool:
    """Return True if the key has expired."""
    expiry = get_expiry(vault_file, key)
    if expiry is None:
        return False
    return time.time() > expiry


def clear_ttl(vault_file: Path, key: str) -> None:
    """Remove TTL for a key."""
    data = _load_ttl(vault_file)
    data.pop(key, None)
    _save_ttl(vault_file, data)


def purge_expired(vault_file: Path) -> list:
    """Return list of keys that have expired (does not delete from vault)."""
    data = _load_ttl(vault_file)
    now = time.time()
    return [k for k, exp in data.items() if now > exp]

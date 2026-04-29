"""expiry.py — Set and check hard expiry dates on secrets.

Different from TTL (which is a duration from now), expiry lets you pin
an absolute ISO-8601 date/time after which a secret is considered expired.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ExpiryError(Exception):
    """Raised for expiry-related errors."""


def _expiry_path(vault_file: Path) -> Path:
    return vault_file.with_suffix(".expiry.json")


def _load_expiry(vault_file: Path) -> dict:
    p = _expiry_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(vault_file: Path, data: dict) -> None:
    _expiry_path(vault_file).write_text(json.dumps(data, indent=2))


def set_expiry(vault_file: Path, key: str, expires_at: datetime) -> None:
    """Set an absolute expiry datetime (UTC) for *key*."""
    if expires_at.tzinfo is None:
        raise ExpiryError("expires_at must be timezone-aware (use UTC).")
    data = _load_expiry(vault_file)
    data[key] = expires_at.astimezone(timezone.utc).isoformat()
    _save_expiry(vault_file, data)


def get_expiry(vault_file: Path, key: str) -> Optional[datetime]:
    """Return the expiry datetime for *key*, or None if not set."""
    data = _load_expiry(vault_file)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def remove_expiry(vault_file: Path, key: str) -> None:
    """Remove the expiry for *key*. Raises ExpiryError if not set."""
    data = _load_expiry(vault_file)
    if key not in data:
        raise ExpiryError(f"No expiry set for key '{key}'.")
    del data[key]
    _save_expiry(vault_file, data)


def is_expired(vault_file: Path, key: str) -> bool:
    """Return True if *key* has an expiry that is in the past."""
    expiry = get_expiry(vault_file, key)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expiring(vault_file: Path) -> list[tuple[str, datetime]]:
    """Return all (key, expiry) pairs sorted by expiry date ascending."""
    data = _load_expiry(vault_file)
    pairs = [(k, datetime.fromisoformat(v)) for k, v in data.items()]
    return sorted(pairs, key=lambda t: t[1])

"""Version tracking for vault secrets — record and retrieve value history with diffs."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

from envault.crypto import encrypt, decrypt


class VersionError(Exception):
    pass


def _version_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".versions.json")


def _load_versions(vault_path: str) -> dict:
    vp = _version_path(vault_path)
    if not vp.exists():
        return {}
    return json.loads(vp.read_text())


def _save_versions(vault_path: str, data: dict) -> None:
    _version_path(vault_path).write_text(json.dumps(data, indent=2))


def record_version(vault_path: str, key: str, value: str, password: str) -> None:
    """Encrypt and append a new version entry for *key*."""
    data = _load_versions(vault_path)
    if key not in data:
        data[key] = []
    token = encrypt(value, password)
    data[key].append({"ts": time.time(), "token": token})
    _save_versions(vault_path, data)


def get_versions(vault_path: str, key: str, password: str) -> List[dict]:
    """Return all recorded versions for *key* as list of {ts, value} dicts."""
    data = _load_versions(vault_path)
    if key not in data:
        return []
    result = []
    for entry in data[key]:
        try:
            value = decrypt(entry["token"], password)
        except Exception:
            value = "<unreadable>"
        result.append({"ts": entry["ts"], "value": value})
    return result


def get_version_at(vault_path: str, key: str, password: str, index: int) -> Optional[str]:
    """Return the decrypted value at a specific version index (0 = oldest)."""
    versions = get_versions(vault_path, key, password)
    if not versions:
        raise VersionError(f"No versions recorded for key '{key}'")
    if index < 0 or index >= len(versions):
        raise VersionError(f"Version index {index} out of range (0-{len(versions)-1})")
    return versions[index]["value"]


def clear_versions(vault_path: str, key: str) -> int:
    """Delete all version history for *key*. Returns number of entries removed."""
    data = _load_versions(vault_path)
    removed = len(data.pop(key, []))
    _save_versions(vault_path, data)
    return removed

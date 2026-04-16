"""Vault store: read/write encrypted .env vault files."""

import json
import os
from pathlib import Path

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"


def _load_raw(vault_path: Path) -> dict:
    """Load raw JSON from vault file, returning empty dict if missing."""
    if not vault_path.exists():
        return {}
    with vault_path.open("r") as f:
        return json.load(f)


def _save_raw(vault_path: Path, data: dict) -> None:
    """Write raw JSON to vault file."""
    with vault_path.open("w") as f:
        json.dump(data, f, indent=2)


def set_secret(key: str, value: str, password: str, vault_path: Path = None) -> None:
    """Encrypt and store a secret under the given key."""
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    data = _load_raw(vault_path)
    data[key] = encrypt(value, password)
    _save_raw(vault_path, data)


def get_secret(key: str, password: str, vault_path: Path = None) -> str:
    """Retrieve and decrypt a secret by key."""
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    data = _load_raw(vault_path)
    if key not in data:
        raise KeyError(f"Key '{key}' not found in vault.")
    return decrypt(data[key], password)


def delete_secret(key: str, vault_path: Path = None) -> bool:
    """Remove a key from the vault. Returns True if key existed."""
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    data = _load_raw(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_raw(vault_path, data)
    return True


def list_keys(vault_path: Path = None) -> list[str]:
    """Return all stored keys (without decrypting values)."""
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    return list(_load_raw(vault_path).keys())

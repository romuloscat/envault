"""Backup and restore vault to/from an encrypted archive file."""

import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from envault.store import _load_raw, _save_raw
from envault.crypto import encrypt, decrypt


class BackupError(Exception):
    pass


def export_backup(vault_file: Path, password: str, output_path: Path) -> Path:
    """Export an encrypted backup of the vault to output_path.

    The backup is a JSON file containing metadata and re-encrypted secrets
    using the same password.
    """
    raw = _load_raw(vault_file)
    payload = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "vault": raw,
    }
    plaintext = json.dumps(payload)
    token = encrypt(plaintext, password)
    output_path.write_text(token)
    return output_path


def import_backup(backup_path: Path, password: str, vault_file: Path, overwrite: bool = False) -> int:
    """Import secrets from an encrypted backup file into the vault.

    Returns the number of secrets imported.
    """
    if not backup_path.exists():
        raise BackupError(f"Backup file not found: {backup_path}")

    token = backup_path.read_text().strip()
    try:
        plaintext = decrypt(token, password)
    except Exception as exc:
        raise BackupError(f"Failed to decrypt backup: {exc}") from exc

    try:
        payload = json.loads(plaintext)
    except json.JSONDecodeError as exc:
        raise BackupError(f"Corrupt backup payload: {exc}") from exc

    backup_secrets: dict = payload.get("vault", {})

    if overwrite:
        _save_raw(vault_file, backup_secrets)
    else:
        existing = _load_raw(vault_file)
        merged = {**backup_secrets, **existing}  # existing keys win
        _save_raw(vault_file, merged)

    return len(backup_secrets)

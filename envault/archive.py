"""Archive (soft-delete) secrets without permanently removing them."""

import json
import time
from pathlib import Path
from typing import List, Optional

from envault.store import get_secret, delete_secret


class ArchiveError(Exception):
    pass


def _archive_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".archive.json")


def _load_archive(vault_path: str) -> dict:
    p = _archive_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_archive(vault_path: str, data: dict) -> None:
    _archive_path(vault_path).write_text(json.dumps(data, indent=2))


def archive_secret(vault_path: str, key: str, password: str) -> None:
    """Move a secret from the live vault into the archive store."""
    value = get_secret(vault_path, key, password)
    data = _load_archive(vault_path)
    data[key] = {
        "token": value,
        "archived_at": time.time(),
    }
    _save_archive(vault_path, data)
    delete_secret(vault_path, key)


def restore_secret(vault_path: str, key: str, password: str) -> None:
    """Restore an archived secret back into the live vault."""
    from envault.store import set_secret

    data = _load_archive(vault_path)
    if key not in data:
        raise ArchiveError(f"Key '{key}' not found in archive")
    # The stored token is already encrypted; write it back raw.
    raw_token = data.pop(key)["token"]
    _save_archive(vault_path, data)
    # Re-encrypt under the same password via normal set_secret path.
    from envault.crypto import decrypt
    plaintext = decrypt(raw_token, password)
    set_secret(vault_path, key, plaintext, password)


def list_archived(vault_path: str) -> List[dict]:
    """Return metadata for all archived secrets, sorted by key name."""
    data = _load_archive(vault_path)
    return sorted(
        [{"key": k, "archived_at": v["archived_at"]} for k, v in data.items()],
        key=lambda x: x["key"],
    )


def purge_archived(vault_path: str, key: Optional[str] = None) -> int:
    """Permanently delete archived secrets.  Returns number of entries removed."""
    data = _load_archive(vault_path)
    if key is not None:
        if key not in data:
            raise ArchiveError(f"Key '{key}' not found in archive")
        del data[key]
        count = 1
    else:
        count = len(data)
        data = {}
    _save_archive(vault_path, data)
    return count

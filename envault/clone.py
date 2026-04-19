"""Clone secrets from one vault file to another."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional, List

from envault.store import list_secrets, get_secret, set_secret
from envault.crypto import decrypt, encrypt


class CloneError(Exception):
    pass


def clone_vault(
    src_vault: Path,
    dst_vault: Path,
    src_password: str,
    dst_password: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> int:
    """Clone secrets from src_vault into dst_vault.

    Args:
        src_vault: Path to the source vault file.
        dst_vault: Path to the destination vault file.
        src_password: Password for the source vault.
        dst_password: Password for the destination vault.
        keys: Optional list of keys to clone; clones all if None.
        overwrite: If False, skip keys that already exist in dst_vault.

    Returns:
        Number of secrets cloned.
    """
    if not src_vault.exists():
        raise CloneError(f"Source vault not found: {src_vault}")

    available = list_secrets(src_vault, src_password)
    to_clone = keys if keys is not None else available

    missing = [k for k in to_clone if k not in available]
    if missing:
        raise CloneError(f"Keys not found in source vault: {', '.join(missing)}")

    if dst_vault.exists():
        existing = list_secrets(dst_vault, dst_password)
    else:
        existing = []

    count = 0
    for key in to_clone:
        if key in existing and not overwrite:
            continue
        value = get_secret(src_vault, key, src_password)
        set_secret(dst_vault, key, value, dst_password)
        count += 1

    return count

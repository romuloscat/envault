"""Key rotation: re-encrypt all secrets with a new password."""

from __future__ import annotations

from typing import Optional

from envault.store import _load_raw, _save_raw, list_secrets
from envault.crypto import decrypt, encrypt
from envault.audit import log_event


class RotationError(Exception):
    pass


def rotate_vault(
    vault_path: str,
    old_password: str,
    new_password: str,
) -> int:
    """Re-encrypt every secret in *vault_path* under *new_password*.

    Returns the number of rotated entries.
    Raises RotationError if any entry cannot be decrypted with *old_password*.
    """
    data = _load_raw(vault_path)

    if not data:
        return 0

    rotated: dict[str, str] = {}
    for key, token in data.items():
        try:
            plaintext = decrypt(token, old_password)
        except Exception as exc:
            raise RotationError(
                f"Failed to decrypt key '{key}' with the old password: {exc}"
            ) from exc
        rotated[key] = encrypt(plaintext, new_password)

    _save_raw(vault_path, rotated)
    log_event(vault_path, "rotate", f"rotated {len(rotated)} key(s)")
    return len(rotated)

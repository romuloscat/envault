"""Merge secrets from one vault into another, with conflict resolution strategies."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from envault.store import list_secrets, get_secret, set_secret

MergeStrategy = Literal["ours", "theirs", "skip", "error"]


class MergeError(Exception):
    """Raised when a merge cannot be completed."""


class MergeConflict(MergeError):
    """Raised when a key exists in both vaults and strategy is 'error'."""

    def __init__(self, key: str) -> None:
        super().__init__(f"Conflict on key '{key}': exists in both source and destination")
        self.key = key


def merge_vaults(
    src_vault: Path,
    dst_vault: Path,
    password: str,
    *,
    strategy: MergeStrategy = "skip",
    keys: list[str] | None = None,
) -> dict[str, str]:
    """Merge secrets from *src_vault* into *dst_vault*.

    Parameters
    ----------
    src_vault:  Path to the source vault file.
    dst_vault:  Path to the destination vault file.
    password:   Shared password used for both vaults.
    strategy:   How to handle keys that exist in both vaults.
                - ``"ours"``   – keep the destination value.
                - ``"theirs"`` – overwrite with the source value.
                - ``"skip"``   – silently skip conflicting keys (same as ``"ours"``).
                - ``"error"``  – raise :class:`MergeConflict`.
    keys:       Optional allowlist of keys to merge.  If *None*, all source keys
                are considered.

    Returns
    -------
    dict mapping each key to the action taken: ``"added"``, ``"skipped"``,
    ``"overwritten"``.
    """
    src_keys = list_secrets(src_vault, password)
    dst_keys = set(list_secrets(dst_vault, password)) if dst_vault.exists() else set()

    if keys is not None:
        missing = set(keys) - set(src_keys)
        if missing:
            raise MergeError(f"Keys not found in source vault: {sorted(missing)}")
        src_keys = [k for k in src_keys if k in keys]

    result: dict[str, str] = {}

    for key in src_keys:
        if key in dst_keys:
            if strategy == "error":
                raise MergeConflict(key)
            elif strategy == "theirs":
                value = get_secret(src_vault, key, password)
                set_secret(dst_vault, key, value, password)
                result[key] = "overwritten"
            else:  # "ours" or "skip"
                result[key] = "skipped"
        else:
            value = get_secret(src_vault, key, password)
            set_secret(dst_vault, key, value, password)
            result[key] = "added"

    return result

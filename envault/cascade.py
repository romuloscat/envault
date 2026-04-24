"""Cascade: resolve a key by walking a chain of vaults (fallback chain).

A cascade defines an ordered list of vault files. When resolving a key,
envault walks the list and returns the first vault that contains the key.
This enables environment-specific overrides (e.g. dev -> staging -> prod).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from envault.store import get_secret, list_secrets


class CascadeError(Exception):
    """Raised for cascade configuration errors."""


def _cascade_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".cascade.json")


def _load_cascade(vault_path: Path) -> List[str]:
    p = _cascade_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_cascade(vault_path: Path, chain: List[str]) -> None:
    _cascade_path(vault_path).write_text(json.dumps(chain, indent=2))


def set_cascade(vault_path: Path, chain: List[str]) -> None:
    """Set the fallback chain for *vault_path*.

    *chain* is an ordered list of vault file paths (strings).  The first
    element is the highest-priority fallback (checked after the primary vault).
    """
    if not chain:
        raise CascadeError("Cascade chain must contain at least one vault path.")
    for entry in chain:
        p = Path(entry)
        if not p.exists():
            raise CascadeError(f"Cascade vault not found: {entry}")
    _save_cascade(vault_path, [str(e) for e in chain])


def get_cascade(vault_path: Path) -> List[str]:
    """Return the configured fallback chain for *vault_path*."""
    return _load_cascade(vault_path)


def clear_cascade(vault_path: Path) -> None:
    """Remove the cascade configuration for *vault_path*."""
    p = _cascade_path(vault_path)
    if p.exists():
        p.unlink()


def resolve_key(
    key: str,
    password: str,
    vault_path: Path,
) -> Optional[str]:
    """Resolve *key* by searching the primary vault then the fallback chain.

    Returns the decrypted value from the first vault that contains *key*, or
    ``None`` if the key is absent in every vault in the chain.
    """
    vaults = [vault_path] + [Path(p) for p in _load_cascade(vault_path)]
    for vp in vaults:
        if not vp.exists():
            continue
        try:
            value = get_secret(key, password, vault_path=vp)
            return value
        except KeyError:
            continue
    return None


def cascade_all_keys(
    password: str,
    vault_path: Path,
) -> dict:
    """Return a merged dict of all keys, with primary vault taking precedence."""
    vaults = [vault_path] + [Path(p) for p in _load_cascade(vault_path)]
    merged: dict = {}
    for vp in reversed(vaults):
        if not vp.exists():
            continue
        for key in list_secrets(password, vault_path=vp):
            try:
                merged[key] = get_secret(key, password, vault_path=vp)
            except KeyError:
                pass
    return merged

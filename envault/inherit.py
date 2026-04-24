"""Vault inheritance: overlay one vault's secrets on top of a base vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.store import get_secret, set_secret, list_secrets
from envault.crypto import decrypt, encrypt


class InheritError(Exception):
    """Raised when an inheritance operation fails."""


def _inherit_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".inherit.json")


def _load_inherit(vault_path: Path) -> Dict[str, str]:
    p = _inherit_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_inherit(vault_path: Path, data: Dict[str, str]) -> None:
    _inherit_path(vault_path).write_text(json.dumps(data, indent=2))


def set_parent(vault_path: Path, parent_path: Path) -> None:
    """Register *parent_path* as the parent vault for *vault_path*."""
    if not parent_path.exists():
        raise InheritError(f"Parent vault not found: {parent_path}")
    resolved = str(parent_path.resolve())
    if resolved == str(vault_path.resolve()):
        raise InheritError("A vault cannot inherit from itself.")
    data = _load_inherit(vault_path)
    data["parent"] = resolved
    _save_inherit(vault_path, data)


def get_parent(vault_path: Path) -> Optional[Path]:
    """Return the registered parent vault path, or None."""
    data = _load_inherit(vault_path)
    parent = data.get("parent")
    return Path(parent) if parent else None


def remove_parent(vault_path: Path) -> None:
    """Remove the parent relationship from *vault_path*."""
    data = _load_inherit(vault_path)
    if "parent" not in data:
        raise InheritError("No parent vault is set.")
    del data["parent"]
    _save_inherit(vault_path, data)


def resolve_secret(
    key: str,
    vault_path: Path,
    password: str,
    *,
    _visited: Optional[List[str]] = None,
) -> str:
    """Return the secret for *key*, walking up the parent chain if needed."""
    if _visited is None:
        _visited = []
    resolved = str(vault_path.resolve())
    if resolved in _visited:
        raise InheritError("Circular inheritance detected.")
    _visited.append(resolved)

    keys = list_secrets(vault_path)
    if key in keys:
        return get_secret(vault_path, key, password)

    parent = get_parent(vault_path)
    if parent is None:
        raise InheritError(f"Key '{key}' not found in vault or any parent vault.")

    return resolve_secret(key, parent, password, _visited=_visited)

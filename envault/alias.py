"""Key aliasing: map short names to full secret keys."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


class AliasError(Exception):
    pass


def _alias_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".aliases.json")


def _load_aliases(vault_file: str) -> Dict[str, str]:
    p = _alias_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(vault_file: str, data: Dict[str, str]) -> None:
    _alias_path(vault_file).write_text(json.dumps(data, indent=2))


def set_alias(vault_file: str, alias: str, key: str) -> None:
    """Create or update an alias pointing to key."""
    if not alias:
        raise AliasError("Alias name must not be empty.")
    if not key:
        raise AliasError("Target key must not be empty.")
    data = _load_aliases(vault_file)
    data[alias] = key
    _save_aliases(vault_file, data)


def remove_alias(vault_file: str, alias: str) -> None:
    """Remove an alias."""
    data = _load_aliases(vault_file)
    if alias not in data:
        raise AliasError(f"Alias '{alias}' does not exist.")
    del data[alias]
    _save_aliases(vault_file, data)


def resolve_alias(vault_file: str, alias: str) -> str:
    """Return the key that alias points to, or alias itself if not found."""
    data = _load_aliases(vault_file)
    return data.get(alias, alias)


def list_aliases(vault_file: str) -> Dict[str, str]:
    """Return all alias -> key mappings."""
    return _load_aliases(vault_file)


def aliases_for_key(vault_file: str, key: str) -> List[str]:
    """Return all aliases that point to the given key."""
    data = _load_aliases(vault_file)
    return [a for a, k in data.items() if k == key]

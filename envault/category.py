"""Category support for grouping secrets by logical domain (e.g. 'database', 'api', 'auth')."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class CategoryError(Exception):
    """Raised when a category operation fails."""


def _category_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".categories.json")


def _load_categories(vault_file: str) -> Dict[str, str]:
    """Return mapping of key -> category."""
    path = _category_path(vault_file)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_categories(vault_file: str, data: Dict[str, str]) -> None:
    path = _category_path(vault_file)
    path.write_text(json.dumps(data, indent=2))


def set_category(vault_file: str, key: str, category: str) -> None:
    """Assign *category* to *key*."""
    if not category.strip():
        raise CategoryError("Category name must not be empty.")
    data = _load_categories(vault_file)
    data[key] = category.strip()
    _save_categories(vault_file, data)


def get_category(vault_file: str, key: str) -> Optional[str]:
    """Return the category assigned to *key*, or None if unset."""
    return _load_categories(vault_file).get(key)


def remove_category(vault_file: str, key: str) -> None:
    """Remove the category assignment for *key*."""
    data = _load_categories(vault_file)
    if key not in data:
        raise CategoryError(f"Key '{key}' has no category assigned.")
    del data[key]
    _save_categories(vault_file, data)


def list_by_category(vault_file: str, category: str) -> List[str]:
    """Return sorted list of keys that belong to *category*."""
    data = _load_categories(vault_file)
    return sorted(k for k, v in data.items() if v == category)


def list_categories(vault_file: str) -> List[str]:
    """Return sorted list of distinct category names in use."""
    data = _load_categories(vault_file)
    return sorted(set(data.values()))

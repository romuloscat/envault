"""Visibility control for vault secrets.

Allows marking secrets as 'public', 'private', or 'confidential',
enabling filtering and display decisions based on sensitivity level.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

# Ordered from least to most sensitive
VISIBILITY_LEVELS = ("public", "private", "confidential")


class VisibilityError(Exception):
    """Raised when a visibility operation fails."""


def _visibility_path(vault_path: str) -> Path:
    """Return the path to the visibility metadata file."""
    return Path(vault_path).with_suffix(".visibility.json")


def _load_visibility(vault_path: str) -> Dict[str, str]:
    """Load visibility metadata from disk, returning an empty dict if absent."""
    path = _visibility_path(vault_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_visibility(vault_path: str, data: Dict[str, str]) -> None:
    """Persist visibility metadata to disk."""
    path = _visibility_path(vault_path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_visibility(vault_path: str, key: str, level: str) -> None:
    """Set the visibility level for *key*.

    Args:
        vault_path: Path to the vault file.
        key: The secret key to annotate.
        level: One of 'public', 'private', or 'confidential'.

    Raises:
        VisibilityError: If *level* is not a recognised visibility level.
    """
    if level not in VISIBILITY_LEVELS:
        raise VisibilityError(
            f"Unknown visibility level {level!r}. "
            f"Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    data = _load_visibility(vault_path)
    data[key] = level
    _save_visibility(vault_path, data)


def get_visibility(vault_path: str, key: str) -> Optional[str]:
    """Return the visibility level for *key*, or ``None`` if unset."""
    return _load_visibility(vault_path).get(key)


def remove_visibility(vault_path: str, key: str) -> None:
    """Remove the visibility annotation for *key*.

    Raises:
        VisibilityError: If *key* has no visibility annotation.
    """
    data = _load_visibility(vault_path)
    if key not in data:
        raise VisibilityError(f"No visibility annotation found for key {key!r}.")
    del data[key]
    _save_visibility(vault_path, data)


def list_by_visibility(vault_path: str, level: str) -> List[str]:
    """Return all keys whose visibility matches *level*, sorted alphabetically.

    Raises:
        VisibilityError: If *level* is not a recognised visibility level.
    """
    if level not in VISIBILITY_LEVELS:
        raise VisibilityError(
            f"Unknown visibility level {level!r}. "
            f"Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    data = _load_visibility(vault_path)
    return sorted(k for k, v in data.items() if v == level)


def filter_keys_by_max_visibility(
    vault_path: str, keys: List[str], max_level: str
) -> List[str]:
    """Return only those *keys* whose visibility is at most *max_level*.

    Keys with no visibility annotation are treated as 'public'.

    Args:
        vault_path: Path to the vault file.
        keys: Candidate list of secret keys.
        max_level: The most sensitive level to include.

    Raises:
        VisibilityError: If *max_level* is not a recognised visibility level.
    """
    if max_level not in VISIBILITY_LEVELS:
        raise VisibilityError(
            f"Unknown visibility level {max_level!r}. "
            f"Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    threshold = VISIBILITY_LEVELS.index(max_level)
    data = _load_visibility(vault_path)
    result = []
    for key in keys:
        level = data.get(key, "public")
        if VISIBILITY_LEVELS.index(level) <= threshold:
            result.append(key)
    return result

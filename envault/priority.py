"""Priority management for vault secrets.

Allows assigning an integer priority level to secrets,
enabling ordered retrieval and processing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PriorityError(Exception):
    """Raised when a priority operation fails."""


DEFAULT_PRIORITY = 50
_MIN_PRIORITY = 1
_MAX_PRIORITY = 100


def _priority_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".priorities.json")


def _load_priorities(vault_path: str) -> Dict[str, int]:
    path = _priority_path(vault_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_priorities(vault_path: str, data: Dict[str, int]) -> None:
    path = _priority_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_priority(vault_path: str, key: str, priority: int) -> None:
    """Assign a priority level (1-100) to a secret key."""
    if not (_MIN_PRIORITY <= priority <= _MAX_PRIORITY):
        raise PriorityError(
            f"Priority must be between {_MIN_PRIORITY} and {_MAX_PRIORITY}, got {priority}."
        )
    data = _load_priorities(vault_path)
    data[key] = priority
    _save_priorities(vault_path, data)


def get_priority(vault_path: str, key: str) -> int:
    """Return the priority for *key*, or DEFAULT_PRIORITY if not set."""
    data = _load_priorities(vault_path)
    return data.get(key, DEFAULT_PRIORITY)


def remove_priority(vault_path: str, key: str) -> None:
    """Remove an explicit priority for *key* (reverts to default)."""
    data = _load_priorities(vault_path)
    if key not in data:
        raise PriorityError(f"No priority set for key '{key}'.")
    del data[key]
    _save_priorities(vault_path, data)


def reset_priorities(vault_path: str) -> int:
    """Remove all explicit priorities, reverting every key to the default.

    Returns the number of priorities that were cleared.
    """
    data = _load_priorities(vault_path)
    count = len(data)
    _save_priorities(vault_path, {})
    return count


def list_by_priority(
    vault_path: str, keys: Optional[List[str]] = None
) -> List[Tuple[str, int]]:
    """Return (key, priority) pairs sorted highest-priority first.

    If *keys* is provided, only those keys are included; any key without
    an explicit priority is assigned DEFAULT_PRIORITY.
    """
    data = _load_priorities(vault_path)
    if keys is None:
        items = list(data.items())
    else:
        items = [(k, data.get(k, DEFAULT_PRIORITY)) for k in keys]
    return sorted(items, key=lambda t: t[1], reverse=True)

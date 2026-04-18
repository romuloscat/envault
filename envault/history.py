"""Track a changelog of set/delete operations per key in the vault."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


class HistoryError(Exception):
    pass


def _history_path(vault_file: Path) -> Path:
    return vault_file.parent / (vault_file.stem + ".history.json")


def _load_history(vault_file: Path) -> Dict[str, List[Dict[str, Any]]]:
    path = _history_path(vault_file)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_history(vault_file: Path, data: Dict[str, List[Dict[str, Any]]]) -> None:
    path = _history_path(vault_file)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def record_event(
    vault_file: Path,
    key: str,
    action: str,
    actor: Optional[str] = None,
) -> None:
    """Append an event (set/delete) for *key* to the history log."""
    if action not in ("set", "delete"):
        raise HistoryError(f"Unknown action '{action}'; must be 'set' or 'delete'")
    data = _load_history(vault_file)
    entry: Dict[str, Any] = {"action": action, "timestamp": time.time()}
    if actor:
        entry["actor"] = actor
    data.setdefault(key, []).append(entry)
    _save_history(vault_file, data)


def get_history(vault_file: Path, key: str) -> List[Dict[str, Any]]:
    """Return all recorded events for *key*, oldest first."""
    data = _load_history(vault_file)
    return data.get(key, [])


def clear_history(vault_file: Path, key: Optional[str] = None) -> int:
    """Clear history for *key*, or all keys if *key* is None. Returns count removed."""
    data = _load_history(vault_file)
    if key is not None:
        removed = len(data.pop(key, []))
    else:
        removed = sum(len(v) for v in data.values())
        data = {}
    _save_history(vault_file, data)
    return removed

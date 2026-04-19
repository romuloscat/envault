"""Label support for envault secrets — attach arbitrary key/value metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class LabelError(Exception):
    pass


def _label_path(vault_file: Path) -> Path:
    return vault_file.with_suffix(".labels.json")


def _load_labels(vault_file: Path) -> Dict[str, Dict[str, str]]:
    p = _label_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_labels(vault_file: Path, data: Dict[str, Dict[str, str]]) -> None:
    _label_path(vault_file).write_text(json.dumps(data, indent=2))


def set_label(vault_file: Path, key: str, label: str, value: str) -> None:
    """Attach a label (label=value) to *key*."""
    data = _load_labels(vault_file)
    data.setdefault(key, {})[label] = value
    _save_labels(vault_file, data)


def remove_label(vault_file: Path, key: str, label: str) -> None:
    """Remove a single label from *key*."""
    data = _load_labels(vault_file)
    if key not in data or label not in data[key]:
        raise LabelError(f"Label '{label}' not found on key '{key}'")
    del data[key][label]
    if not data[key]:
        del data[key]
    _save_labels(vault_file, data)


def get_labels(vault_file: Path, key: str) -> Dict[str, str]:
    """Return all labels for *key* (empty dict if none)."""
    return _load_labels(vault_file).get(key, {})


def find_by_label(vault_file: Path, label: str, value: Optional[str] = None) -> list[str]:
    """Return keys that have *label* (optionally matching *value*)."""
    data = _load_labels(vault_file)
    results = []
    for k, labels in data.items():
        if label in labels:
            if value is None or labels[label] == value:
                results.append(k)
    return sorted(results)

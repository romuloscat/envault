"""Reference resolution: allow a secret's value to point to another key."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

REF_PREFIX = "ref:"
MAX_DEPTH = 10


class RefError(Exception):
    """Raised for reference-related problems."""


class CircularRefError(RefError):
    """Raised when a circular reference chain is detected."""


def _ref_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".refs.json")


def _load_refs(vault_path: str) -> dict:
    p = _ref_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_refs(vault_path: str, data: dict) -> None:
    _ref_path(vault_path).write_text(json.dumps(data, indent=2))


def set_ref(vault_path: str, key: str, target: str) -> None:
    """Make *key* a reference to *target*."""
    if key == target:
        raise RefError(f"Key '{key}' cannot reference itself.")
    refs = _load_refs(vault_path)
    refs[key] = target
    _save_refs(vault_path, refs)


def remove_ref(vault_path: str, key: str) -> None:
    """Remove the reference for *key*, if it exists."""
    refs = _load_refs(vault_path)
    if key not in refs:
        raise RefError(f"No reference defined for key '{key}'.")
    del refs[key]
    _save_refs(vault_path, refs)


def get_ref(vault_path: str, key: str) -> Optional[str]:
    """Return the target key that *key* references, or None."""
    return _load_refs(vault_path).get(key)


def resolve_ref(vault_path: str, key: str) -> str:
    """Follow the reference chain and return the terminal (non-ref) key.

    Raises CircularRefError if a cycle is detected.
    Raises RefError if the chain exceeds MAX_DEPTH.
    """
    refs = _load_refs(vault_path)
    visited: list[str] = []
    current = key
    for _ in range(MAX_DEPTH):
        if current in visited:
            raise CircularRefError(
                f"Circular reference detected: {' -> '.join(visited + [current])}"
            )
        if current not in refs:
            return current
        visited.append(current)
        current = refs[current]
    raise RefError(
        f"Reference chain for '{key}' exceeds maximum depth ({MAX_DEPTH})."
    )


def list_refs(vault_path: str) -> dict[str, str]:
    """Return all defined references as {key: target} mapping."""
    return dict(_load_refs(vault_path))

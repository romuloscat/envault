"""Track dependencies between secrets (one secret references another)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List


class DependencyError(Exception):
    pass


def _dep_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".deps.json")


def _load_deps(vault_file: str) -> Dict[str, List[str]]:
    p = _dep_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(vault_file: str, data: Dict[str, List[str]]) -> None:
    _dep_path(vault_file).write_text(json.dumps(data, indent=2))


def add_dependency(vault_file: str, key: str, depends_on: str) -> None:
    """Record that *key* depends on *depends_on*."""
    if key == depends_on:
        raise DependencyError("A secret cannot depend on itself.")
    data = _load_deps(vault_file)
    deps = data.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save_deps(vault_file, data)


def remove_dependency(vault_file: str, key: str, depends_on: str) -> None:
    data = _load_deps(vault_file)
    if key not in data or depends_on not in data[key]:
        raise DependencyError(f"Dependency '{key}' -> '{depends_on}' not found.")
    data[key].remove(depends_on)
    if not data[key]:
        del data[key]
    _save_deps(vault_file, data)


def get_dependencies(vault_file: str, key: str) -> List[str]:
    """Return keys that *key* directly depends on."""
    return _load_deps(vault_file).get(key, [])


def get_dependents(vault_file: str, key: str) -> List[str]:
    """Return keys that directly depend on *key*."""
    data = _load_deps(vault_file)
    return [k for k, deps in data.items() if key in deps]


def all_dependencies(vault_file: str) -> Dict[str, List[str]]:
    return _load_deps(vault_file)

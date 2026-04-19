"""Group secrets under named logical groups."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict


class GroupError(Exception):
    pass


def _group_path(vault_file: Path) -> Path:
    return vault_file.with_suffix(".groups.json")


def _load_groups(vault_file: Path) -> Dict[str, List[str]]:
    p = _group_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_groups(vault_file: Path, data: Dict[str, List[str]]) -> None:
    _group_path(vault_file).write_text(json.dumps(data, indent=2))


def add_to_group(vault_file: Path, group: str, key: str) -> None:
    data = _load_groups(vault_file)
    members = data.setdefault(group, [])
    if key not in members:
        members.append(key)
    _save_groups(vault_file, data)


def remove_from_group(vault_file: Path, group: str, key: str) -> None:
    data = _load_groups(vault_file)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    if key not in data[group]:
        raise GroupError(f"Key '{key}' not in group '{group}'.")
    data[group].remove(key)
    if not data[group]:
        del data[group]
    _save_groups(vault_file, data)


def list_groups(vault_file: Path) -> List[str]:
    return sorted(_load_groups(vault_file).keys())


def get_group_members(vault_file: Path, group: str) -> List[str]:
    data = _load_groups(vault_file)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    return list(data[group])


def delete_group(vault_file: Path, group: str) -> None:
    data = _load_groups(vault_file)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    del data[group]
    _save_groups(vault_file, data)

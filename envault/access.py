"""Access control: restrict which keys a named profile can read/write."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


class AccessError(Exception):
    pass


def _access_path(vault_file: Path) -> Path:
    return vault_file.with_suffix(".access.json")


def _load_acl(vault_file: Path) -> Dict[str, List[str]]:
    p = _access_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_acl(vault_file: Path, acl: Dict[str, List[str]]) -> None:
    _access_path(vault_file).write_text(json.dumps(acl, indent=2))


def grant(vault_file: Path, profile: str, key: str) -> None:
    """Grant *profile* read access to *key*."""
    acl = _load_acl(vault_file)
    acl.setdefault(profile, [])
    if key not in acl[profile]:
        acl[profile].append(key)
    _save_acl(vault_file, acl)


def revoke(vault_file: Path, profile: str, key: str) -> None:
    """Revoke *profile* access to *key*."""
    acl = _load_acl(vault_file)
    if profile not in acl:
        raise AccessError(f"Profile '{profile}' not found")
    if key not in acl[profile]:
        raise AccessError(f"Key '{key}' not in profile '{profile}'")
    acl[profile].remove(key)
    _save_acl(vault_file, acl)


def allowed_keys(vault_file: Path, profile: str) -> List[str]:
    """Return list of keys accessible to *profile*."""
    return list(_load_acl(vault_file).get(profile, []))


def check_access(vault_file: Path, profile: str, key: str) -> bool:
    """Return True if *profile* may access *key*."""
    return key in _load_acl(vault_file).get(profile, [])


def list_profiles(vault_file: Path) -> List[str]:
    return list(_load_acl(vault_file).keys())


def delete_profile(vault_file: Path, profile: str) -> None:
    acl = _load_acl(vault_file)
    if profile not in acl:
        raise AccessError(f"Profile '{profile}' not found")
    del acl[profile]
    _save_acl(vault_file, acl)

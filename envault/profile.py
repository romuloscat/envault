"""Profile management: named sets of secrets for different environments."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from envault.store import set_secret, get_secret, list_secrets

class ProfileError(Exception):
    pass

def _profile_path(vault_file: Path) -> Path:
    return vault_file.parent / (vault_file.stem + ".profiles.json")

def _load_profiles(vault_file: Path) -> Dict[str, List[str]]:
    p = _profile_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())

def _save_profiles(vault_file: Path, data: Dict[str, List[str]]) -> None:
    _profile_path(vault_file).write_text(json.dumps(data, indent=2))

def add_key_to_profile(vault_file: Path, profile: str, key: str) -> None:
    data = _load_profiles(vault_file)
    keys = data.setdefault(profile, [])
    if key not in keys:
        keys.append(key)
    _save_profiles(vault_file, data)

def remove_key_from_profile(vault_file: Path, profile: str, key: str) -> None:
    data = _load_profiles(vault_file)
    if profile not in data:
        raise ProfileError(f"Profile '{profile}' not found.")
    if key not in data[profile]:
        raise ProfileError(f"Key '{key}' not in profile '{profile}'.")
    data[profile].remove(key)
    _save_profiles(vault_file, data)

def list_profiles(vault_file: Path) -> List[str]:
    return list(_load_profiles(vault_file).keys())

def get_profile_keys(vault_file: Path, profile: str) -> List[str]:
    data = _load_profiles(vault_file)
    if profile not in data:
        raise ProfileError(f"Profile '{profile}' not found.")
    return list(data[profile])

def delete_profile(vault_file: Path, profile: str) -> None:
    data = _load_profiles(vault_file)
    if profile not in data:
        raise ProfileError(f"Profile '{profile}' not found.")
    del data[profile]
    _save_profiles(vault_file, data)

def export_profile(vault_file: Path, profile: str, password: str) -> Dict[str, str]:
    keys = get_profile_keys(vault_file, profile)
    result = {}
    for key in keys:
        result[key] = get_secret(vault_file, key, password)
    return result

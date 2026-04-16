"""Tag-based grouping for vault secrets."""
from __future__ import annotations
import fnmatch
from typing import Dict, List
from envault.store import _load_raw, _save_raw


class TagError(Exception):
    pass


_TAGS_KEY = "__tags__"


def _load_tags(vault_path: str) -> Dict[str, List[str]]:
    """Return mapping of key -> list of tags."""
    raw = _load_raw(vault_path)
    return raw.get(_TAGS_KEY, {})


def _save_tags(vault_path: str, tags: Dict[str, List[str]]) -> None:
    raw = _load_raw(vault_path)
    raw[_TAGS_KEY] = tags
    _save_raw(vault_path, raw)


def tag_secret(vault_path: str, key: str, tag: str) -> None:
    """Add a tag to a secret key."""
    raw = _load_raw(vault_path)
    if key not in raw or key == _TAGS_KEY:
        raise TagError(f"Key '{key}' not found in vault.")
    tags = _load_tags(vault_path)
    key_tags = tags.get(key, [])
    if tag not in key_tags:
        key_tags.append(tag)
    tags[key] = key_tags
    _save_tags(vault_path, tags)


def untag_secret(vault_path: str, key: str, tag: str) -> None:
    """Remove a tag from a secret key."""
    tags = _load_tags(vault_path)
    key_tags = tags.get(key, [])
    if tag not in key_tags:
        raise TagError(f"Tag '{tag}' not found on key '{key}'.")
    key_tags.remove(tag)
    tags[key] = key_tags
    _save_tags(vault_path, tags)


def get_tags(vault_path: str, key: str) -> List[str]:
    """Return tags for a given key."""
    return _load_tags(vault_path).get(key, [])


def keys_by_tag(vault_path: str, tag_pattern: str) -> List[str]:
    """Return all keys that have at least one tag matching the glob pattern."""
    tags = _load_tags(vault_path)
    result = []
    for key, key_tags in tags.items():
        if any(fnmatch.fnmatch(t, tag_pattern) for t in key_tags):
            result.append(key)
    return sorted(result)

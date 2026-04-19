"""Inline comments for vault secrets."""
from __future__ import annotations
import json
from pathlib import Path


class CommentError(Exception):
    pass


def _comment_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".comments.json")


def _load_comments(vault_file: str) -> dict:
    p = _comment_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_comments(vault_file: str, data: dict) -> None:
    _comment_path(vault_file).write_text(json.dumps(data, indent=2))


def set_comment(vault_file: str, key: str, comment: str) -> None:
    """Attach a comment to a secret key."""
    if not comment.strip():
        raise CommentError("Comment must not be empty.")
    data = _load_comments(vault_file)
    data[key] = comment.strip()
    _save_comments(vault_file, data)


def get_comment(vault_file: str, key: str) -> str | None:
    """Return the comment for a key, or None if not set."""
    return _load_comments(vault_file).get(key)


def remove_comment(vault_file: str, key: str) -> None:
    """Remove the comment for a key."""
    data = _load_comments(vault_file)
    if key not in data:
        raise CommentError(f"No comment found for key: {key!r}")
    del data[key]
    _save_comments(vault_file, data)


def list_comments(vault_file: str) -> dict:
    """Return all key -> comment mappings."""
    return dict(_load_comments(vault_file))

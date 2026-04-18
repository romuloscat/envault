"""Per-secret notes/comments storage."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional


class NoteError(Exception):
    pass


def _notes_path(vault_file: Path) -> Path:
    return vault_file.with_suffix(".notes.json")


def _load_notes(vault_file: Path) -> dict:
    p = _notes_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_notes(vault_file: Path, data: dict) -> None:
    _notes_path(vault_file).write_text(json.dumps(data, indent=2))


def set_note(vault_file: Path, key: str, note: str) -> None:
    """Attach a note to a secret key."""
    data = _load_notes(vault_file)
    data[key] = note
    _save_notes(vault_file, data)


def get_note(vault_file: Path, key: str) -> Optional[str]:
    """Return the note for a key, or None if not set."""
    return _load_notes(vault_file).get(key)


def remove_note(vault_file: Path, key: str) -> None:
    """Remove the note for a key."""
    data = _load_notes(vault_file)
    if key not in data:
        raise NoteError(f"No note found for key: {key}")
    del data[key]
    _save_notes(vault_file, data)


def list_notes(vault_file: Path) -> dict:
    """Return all key->note mappings."""
    return dict(_load_notes(vault_file))

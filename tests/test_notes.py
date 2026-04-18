"""Tests for envault.notes."""
import pytest
from pathlib import Path
from envault.notes import set_note, get_note, remove_note, list_notes, NoteError


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_set_and_get_note(vault_file):
    set_note(vault_file, "API_KEY", "Rotate every 90 days")
    assert get_note(vault_file, "API_KEY") == "Rotate every 90 days"


def test_get_note_missing_key_returns_none(vault_file):
    assert get_note(vault_file, "MISSING") is None


def test_set_note_overwrites(vault_file):
    set_note(vault_file, "DB_PASS", "old note")
    set_note(vault_file, "DB_PASS", "new note")
    assert get_note(vault_file, "DB_PASS") == "new note"


def test_remove_note(vault_file):
    set_note(vault_file, "TOKEN", "some note")
    remove_note(vault_file, "TOKEN")
    assert get_note(vault_file, "TOKEN") is None


def test_remove_missing_note_raises(vault_file):
    with pytest.raises(NoteError, match="No note found"):
        remove_note(vault_file, "GHOST")


def test_list_notes_empty(vault_file):
    assert list_notes(vault_file) == {}


def test_list_notes_multiple(vault_file):
    set_note(vault_file, "A", "note a")
    set_note(vault_file, "B", "note b")
    result = list_notes(vault_file)
    assert result == {"A": "note a", "B": "note b"}


def test_notes_stored_in_separate_file(vault_file):
    set_note(vault_file, "X", "hi")
    notes_file = vault_file.with_suffix(".notes.json")
    assert notes_file.exists()
    assert not vault_file.exists()

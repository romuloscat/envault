"""Tests for CLI notes commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_notes import notes_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_note_set_and_get(runner, vault_file):
    r = runner.invoke(notes_cmd, ["set", "API_KEY", "rotate monthly", "--vault", str(vault_file)])
    assert r.exit_code == 0
    assert "Note set" in r.output

    r = runner.invoke(notes_cmd, ["get", "API_KEY", "--vault", str(vault_file)])
    assert r.exit_code == 0
    assert "rotate monthly" in r.output


def test_note_get_missing(runner, vault_file):
    r = runner.invoke(notes_cmd, ["get", "MISSING", "--vault", str(vault_file)])
    assert r.exit_code == 0
    assert "No note" in r.output


def test_note_remove(runner, vault_file):
    runner.invoke(notes_cmd, ["set", "K", "v", "--vault", str(vault_file)])
    r = runner.invoke(notes_cmd, ["remove", "K", "--vault", str(vault_file)])
    assert r.exit_code == 0
    assert "removed" in r.output


def test_note_remove_missing_exits_nonzero(runner, vault_file):
    r = runner.invoke(notes_cmd, ["remove", "GHOST", "--vault", str(vault_file)])
    assert r.exit_code != 0


def test_note_list_empty(runner, vault_file):
    r = runner.invoke(notes_cmd, ["list", "--vault", str(vault_file)])
    assert r.exit_code == 0
    assert "No notes" in r.output


def test_note_list_shows_entries(runner, vault_file):
    runner.invoke(notes_cmd, ["set", "FOO", "bar note", "--vault", str(vault_file)])
    runner.invoke(notes_cmd, ["set", "BAZ", "qux note", "--vault", str(vault_file)])
    r = runner.invoke(notes_cmd, ["list", "--vault", str(vault_file)])
    assert "FOO" in r.output
    assert "BAZ" in r.output

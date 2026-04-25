"""Tests for envault.ref and envault.cli_ref."""
import pytest
from click.testing import CliRunner

from envault.ref import (
    CircularRefError,
    RefError,
    get_ref,
    list_refs,
    remove_ref,
    resolve_ref,
    set_ref,
)
from envault.cli_ref import ref_cmd


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Unit tests — ref.py
# ---------------------------------------------------------------------------

def test_set_and_get_ref(vault_file):
    set_ref(vault_file, "DB_URL", "DATABASE_URL")
    assert get_ref(vault_file, "DB_URL") == "DATABASE_URL"


def test_get_ref_missing_key_returns_none(vault_file):
    assert get_ref(vault_file, "NONEXISTENT") is None


def test_set_ref_self_raises(vault_file):
    with pytest.raises(RefError, match="cannot reference itself"):
        set_ref(vault_file, "KEY", "KEY")


def test_set_ref_overwrites(vault_file):
    set_ref(vault_file, "A", "B")
    set_ref(vault_file, "A", "C")
    assert get_ref(vault_file, "A") == "C"


def test_remove_ref(vault_file):
    set_ref(vault_file, "A", "B")
    remove_ref(vault_file, "A")
    assert get_ref(vault_file, "A") is None


def test_remove_ref_missing_raises(vault_file):
    with pytest.raises(RefError, match="No reference defined"):
        remove_ref(vault_file, "GHOST")


def test_resolve_ref_no_chain(vault_file):
    # key with no reference resolves to itself
    assert resolve_ref(vault_file, "PLAIN_KEY") == "PLAIN_KEY"


def test_resolve_ref_single_hop(vault_file):
    set_ref(vault_file, "ALIAS", "REAL_KEY")
    assert resolve_ref(vault_file, "ALIAS") == "REAL_KEY"


def test_resolve_ref_multi_hop(vault_file):
    set_ref(vault_file, "A", "B")
    set_ref(vault_file, "B", "C")
    assert resolve_ref(vault_file, "A") == "C"


def test_resolve_ref_circular_raises(vault_file):
    set_ref(vault_file, "X", "Y")
    set_ref(vault_file, "Y", "X")
    with pytest.raises(CircularRefError, match="Circular reference"):
        resolve_ref(vault_file, "X")


def test_list_refs_empty(vault_file):
    assert list_refs(vault_file) == {}


def test_list_refs_returns_all(vault_file):
    set_ref(vault_file, "A", "B")
    set_ref(vault_file, "C", "D")
    assert list_refs(vault_file) == {"A": "B", "C": "D"}


# ---------------------------------------------------------------------------
# CLI tests — cli_ref.py
# ---------------------------------------------------------------------------

def _opt(vault_file):
    return ["--vault", vault_file]


def test_cli_ref_set_and_show(runner, vault_file):
    result = runner.invoke(ref_cmd, ["set", "DB", "DATABASE_URL"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "DB -> DATABASE_URL" in result.output

    result = runner.invoke(ref_cmd, ["show", "DB"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "DB -> DATABASE_URL" in result.output


def test_cli_ref_show_missing(runner, vault_file):
    result = runner.invoke(ref_cmd, ["show", "MISSING"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "no reference" in result.output


def test_cli_ref_resolve(runner, vault_file):
    runner.invoke(ref_cmd, ["set", "A", "B"] + _opt(vault_file))
    result = runner.invoke(ref_cmd, ["resolve", "A"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "B" in result.output


def test_cli_ref_remove(runner, vault_file):
    runner.invoke(ref_cmd, ["set", "A", "B"] + _opt(vault_file))
    result = runner.invoke(ref_cmd, ["remove", "A"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_ref_list_empty(runner, vault_file):
    result = runner.invoke(ref_cmd, ["list"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "No references" in result.output


def test_cli_ref_list_shows_entries(runner, vault_file):
    runner.invoke(ref_cmd, ["set", "P", "Q"] + _opt(vault_file))
    result = runner.invoke(ref_cmd, ["list"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "P -> Q" in result.output

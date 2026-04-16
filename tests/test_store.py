"""Tests for envault.store module."""

import json
import pytest
from pathlib import Path

from envault.store import set_secret, get_secret, delete_secret, list_keys

PASSWORD = "test-password-123"


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / ".envault"


def test_set_and_get_secret(vault_file):
    set_secret("DB_URL", "postgres://localhost/db", PASSWORD, vault_file)
    result = get_secret("DB_URL", PASSWORD, vault_file)
    assert result == "postgres://localhost/db"


def test_set_creates_vault_file(vault_file):
    assert not vault_file.exists()
    set_secret("KEY", "value", PASSWORD, vault_file)
    assert vault_file.exists()


def test_vault_file_contains_encrypted_value(vault_file):
    set_secret("SECRET", "plaintext", PASSWORD, vault_file)
    raw = json.loads(vault_file.read_text())
    assert "SECRET" in raw
    assert raw["SECRET"] != "plaintext"


def test_get_missing_key_raises(vault_file):
    with pytest.raises(KeyError, match="MISSING"):
        get_secret("MISSING", PASSWORD, vault_file)


def test_get_wrong_password_raises(vault_file):
    set_secret("API_KEY", "secret", PASSWORD, vault_file)
    with pytest.raises(Exception):
        get_secret("API_KEY", "wrong-password", vault_file)


def test_list_keys_empty(vault_file):
    assert list_keys(vault_file) == []


def test_list_keys_returns_all_keys(vault_file):
    set_secret("A", "1", PASSWORD, vault_file)
    set_secret("B", "2", PASSWORD, vault_file)
    keys = list_keys(vault_file)
    assert sorted(keys) == ["A", "B"]


def test_delete_existing_key(vault_file):
    set_secret("TO_DELETE", "val", PASSWORD, vault_file)
    removed = delete_secret("TO_DELETE", vault_file)
    assert removed is True
    assert "TO_DELETE" not in list_keys(vault_file)


def test_delete_missing_key_returns_false(vault_file):
    assert delete_secret("GHOST", vault_file) is False


def test_overwrite_secret(vault_file):
    set_secret("KEY", "old", PASSWORD, vault_file)
    set_secret("KEY", "new", PASSWORD, vault_file)
    assert get_secret("KEY", PASSWORD, vault_file) == "new"
    assert list_keys(vault_file).count("KEY") == 1

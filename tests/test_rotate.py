"""Tests for envault.rotate."""

from __future__ import annotations

import pytest

from envault.store import set_secret, get_secret, list_secrets
from envault.rotate import rotate_vault, RotationError


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "test.vault")


def test_rotate_reencrypts_all_keys(vault_file):
    set_secret(vault_file, "DB_URL", "postgres://localhost", "old")
    set_secret(vault_file, "API_KEY", "secret123", "old")

    count = rotate_vault(vault_file, "old", "new")

    assert count == 2
    assert get_secret(vault_file, "DB_URL", "new") == "postgres://localhost"
    assert get_secret(vault_file, "API_KEY", "new") == "secret123"


def test_rotate_old_password_no_longer_works(vault_file):
    set_secret(vault_file, "TOKEN", "abc", "old")
    rotate_vault(vault_file, "old", "new")

    with pytest.raises(Exception):
        get_secret(vault_file, "TOKEN", "old")


def test_rotate_empty_vault_returns_zero(vault_file):
    count = rotate_vault(vault_file, "old", "new")
    assert count == 0


def test_rotate_wrong_old_password_raises(vault_file):
    set_secret(vault_file, "KEY", "value", "correct")

    with pytest.raises(RotationError):
        rotate_vault(vault_file, "wrong", "new")


def test_rotate_preserves_all_keys(vault_file):
    keys = {"A": "1", "B": "2", "C": "3"}
    for k, v in keys.items():
        set_secret(vault_file, k, v, "pass1")

    rotate_vault(vault_file, "pass1", "pass2")

    assert sorted(list_secrets(vault_file)) == sorted(keys.keys())
    for k, v in keys.items():
        assert get_secret(vault_file, k, "pass2") == v

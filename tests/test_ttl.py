"""Tests for envault.ttl module."""

import time
import pytest
from pathlib import Path
from envault.ttl import (
    set_ttl, get_expiry, is_expired, clear_ttl, purge_expired, TTLError
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_set_and_get_expiry(vault_file):
    set_ttl(vault_file, "KEY", 60)
    expiry = get_expiry(vault_file, "KEY")
    assert expiry is not None
    assert expiry > time.time()


def test_get_expiry_missing_key_returns_none(vault_file):
    assert get_expiry(vault_file, "MISSING") is None


def test_is_not_expired(vault_file):
    set_ttl(vault_file, "KEY", 60)
    assert not is_expired(vault_file, "KEY")


def test_is_expired(vault_file):
    set_ttl(vault_file, "KEY", 1)
    # Manually backdate the expiry
    from envault.ttl import _load_ttl, _save_ttl
    data = _load_ttl(vault_file)
    data["KEY"] = time.time() - 10
    _save_ttl(vault_file, data)
    assert is_expired(vault_file, "KEY")


def test_no_ttl_is_not_expired(vault_file):
    assert not is_expired(vault_file, "KEY")


def test_clear_ttl(vault_file):
    set_ttl(vault_file, "KEY", 60)
    clear_ttl(vault_file, "KEY")
    assert get_expiry(vault_file, "KEY") is None


def test_clear_ttl_missing_key_no_error(vault_file):
    clear_ttl(vault_file, "NONEXISTENT")  # should not raise


def test_purge_expired_returns_expired_keys(vault_file):
    from envault.ttl import _load_ttl, _save_ttl
    set_ttl(vault_file, "LIVE", 120)
    set_ttl(vault_file, "DEAD", 1)
    data = _load_ttl(vault_file)
    data["DEAD"] = time.time() - 5
    _save_ttl(vault_file, data)
    expired = purge_expired(vault_file)
    assert "DEAD" in expired
    assert "LIVE" not in expired


def test_set_ttl_invalid_raises(vault_file):
    with pytest.raises(TTLError):
        set_ttl(vault_file, "KEY", 0)
    with pytest.raises(TTLError):
        set_ttl(vault_file, "KEY", -5)

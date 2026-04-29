"""Tests for envault/expiry.py"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from envault.expiry import (
    ExpiryError,
    set_expiry,
    get_expiry,
    remove_expiry,
    is_expired,
    list_expiring,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / "vault.json"
    vf.write_text("{}")
    return vf


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


def test_set_and_get_expiry(vault_file):
    exp = _future()
    set_expiry(vault_file, "API_KEY", exp)
    result = get_expiry(vault_file, "API_KEY")
    assert result is not None
    assert abs((result - exp).total_seconds()) < 1


def test_get_expiry_missing_key_returns_none(vault_file):
    assert get_expiry(vault_file, "MISSING") is None


def test_set_expiry_naive_datetime_raises(vault_file):
    naive = datetime(2030, 1, 1)  # no tzinfo
    with pytest.raises(ExpiryError, match="timezone-aware"):
        set_expiry(vault_file, "KEY", naive)


def test_is_not_expired_for_future(vault_file):
    set_expiry(vault_file, "TOKEN", _future())
    assert is_expired(vault_file, "TOKEN") is False


def test_is_expired_for_past(vault_file):
    set_expiry(vault_file, "OLD_KEY", _past())
    assert is_expired(vault_file, "OLD_KEY") is True


def test_is_expired_returns_false_when_no_expiry(vault_file):
    assert is_expired(vault_file, "NO_EXPIRY") is False


def test_remove_expiry(vault_file):
    set_expiry(vault_file, "DB_PASS", _future())
    remove_expiry(vault_file, "DB_PASS")
    assert get_expiry(vault_file, "DB_PASS") is None


def test_remove_expiry_missing_key_raises(vault_file):
    with pytest.raises(ExpiryError, match="No expiry set"):
        remove_expiry(vault_file, "GHOST")


def test_list_expiring_sorted(vault_file):
    soon = _future(60)
    later = _future(7200)
    set_expiry(vault_file, "LATER", later)
    set_expiry(vault_file, "SOON", soon)
    pairs = list_expiring(vault_file)
    keys = [k for k, _ in pairs]
    assert keys == ["SOON", "LATER"]


def test_list_expiring_empty_when_none(vault_file):
    assert list_expiring(vault_file) == []


def test_expiry_persists_across_calls(vault_file):
    exp = _future(500)
    set_expiry(vault_file, "PERSIST", exp)
    # Reload from disk implicitly via a fresh call
    result = get_expiry(vault_file, "PERSIST")
    assert result is not None
    assert abs((result - exp).total_seconds()) < 1

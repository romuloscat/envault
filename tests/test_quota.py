"""Tests for envault.quota."""

import pytest

from envault.store import set_secret
from envault.quota import (
    QuotaError,
    QuotaExceeded,
    check_quota,
    get_quota,
    quota_status,
    remove_quota,
    set_quota,
)

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_and_get_quota(vault_file):
    set_quota(vault_file, 10)
    assert get_quota(vault_file) == 10


def test_set_quota_zero_raises(vault_file):
    with pytest.raises(QuotaError, match="positive integer"):
        set_quota(vault_file, 0)


def test_set_quota_negative_raises(vault_file):
    with pytest.raises(QuotaError, match="positive integer"):
        set_quota(vault_file, -5)


def test_get_quota_returns_none_when_not_set(vault_file):
    assert get_quota(vault_file) is None


def test_remove_quota(vault_file):
    set_quota(vault_file, 5)
    remove_quota(vault_file)
    assert get_quota(vault_file) is None


def test_remove_quota_not_set_raises(vault_file):
    with pytest.raises(QuotaError, match="No quota configured"):
        remove_quota(vault_file)


def test_check_quota_no_limit_passes(vault_file):
    set_secret(vault_file, PASSWORD, "KEY1", "val1")
    # Should not raise when no quota is set
    check_quota(vault_file, PASSWORD)


def test_check_quota_under_limit_passes(vault_file):
    set_secret(vault_file, PASSWORD, "KEY1", "val1")
    set_quota(vault_file, 3)
    check_quota(vault_file, PASSWORD)  # 1 of 3 used — should pass


def test_check_quota_at_limit_raises(vault_file):
    set_secret(vault_file, PASSWORD, "KEY1", "val1")
    set_secret(vault_file, PASSWORD, "KEY2", "val2")
    set_quota(vault_file, 2)
    with pytest.raises(QuotaExceeded, match="quota of 2"):
        check_quota(vault_file, PASSWORD)


def test_quota_status_with_limit(vault_file):
    set_secret(vault_file, PASSWORD, "A", "1")
    set_secret(vault_file, PASSWORD, "B", "2")
    set_quota(vault_file, 5)
    status = quota_status(vault_file, PASSWORD)
    assert status["limit"] == 5
    assert status["used"] == 2
    assert status["available"] == 3


def test_quota_status_without_limit(vault_file):
    set_secret(vault_file, PASSWORD, "A", "1")
    status = quota_status(vault_file, PASSWORD)
    assert status["limit"] is None
    assert status["used"] == 1
    assert status["available"] is None


def test_set_quota_overwrites_previous(vault_file):
    set_quota(vault_file, 10)
    set_quota(vault_file, 20)
    assert get_quota(vault_file) == 20

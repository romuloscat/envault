"""Tests for envault.archive."""

import pytest

from envault.store import set_secret, get_secret
from envault.archive import (
    ArchiveError,
    archive_secret,
    restore_secret,
    list_archived,
    purge_archived,
)

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_archive_removes_key_from_live_vault(vault_file):
    set_secret(vault_file, "API_KEY", "secret123", PASSWORD)
    archive_secret(vault_file, "API_KEY", PASSWORD)
    with pytest.raises(KeyError):
        get_secret(vault_file, "API_KEY", PASSWORD)


def test_archive_secret_appears_in_list(vault_file):
    set_secret(vault_file, "TOKEN", "abc", PASSWORD)
    archive_secret(vault_file, "TOKEN", PASSWORD)
    entries = list_archived(vault_file)
    keys = [e["key"] for e in entries]
    assert "TOKEN" in keys


def test_archived_entry_has_timestamp(vault_file):
    import time
    before = time.time()
    set_secret(vault_file, "DB_PASS", "hunter2", PASSWORD)
    archive_secret(vault_file, "DB_PASS", PASSWORD)
    after = time.time()
    entries = list_archived(vault_file)
    ts = entries[0]["archived_at"]
    assert before <= ts <= after


def test_restore_secret_back_to_live_vault(vault_file):
    set_secret(vault_file, "MY_KEY", "original_value", PASSWORD)
    archive_secret(vault_file, "MY_KEY", PASSWORD)
    restore_secret(vault_file, "MY_KEY", PASSWORD)
    assert get_secret(vault_file, "MY_KEY", PASSWORD) == "original_value"


def test_restore_removes_from_archive(vault_file):
    set_secret(vault_file, "MY_KEY", "val", PASSWORD)
    archive_secret(vault_file, "MY_KEY", PASSWORD)
    restore_secret(vault_file, "MY_KEY", PASSWORD)
    assert list_archived(vault_file) == []


def test_restore_missing_key_raises(vault_file):
    with pytest.raises(ArchiveError, match="not found in archive"):
        restore_secret(vault_file, "GHOST", PASSWORD)


def test_list_archived_sorted_by_key(vault_file):
    for k in ["ZEBRA", "ALPHA", "MIDDLE"]:
        set_secret(vault_file, k, "v", PASSWORD)
        archive_secret(vault_file, k, PASSWORD)
    keys = [e["key"] for e in list_archived(vault_file)]
    assert keys == sorted(keys)


def test_purge_single_key(vault_file):
    set_secret(vault_file, "OLD", "v", PASSWORD)
    archive_secret(vault_file, "OLD", PASSWORD)
    count = purge_archived(vault_file, "OLD")
    assert count == 1
    assert list_archived(vault_file) == []


def test_purge_all_keys(vault_file):
    for k in ["A", "B", "C"]:
        set_secret(vault_file, k, "v", PASSWORD)
        archive_secret(vault_file, k, PASSWORD)
    count = purge_archived(vault_file)
    assert count == 3
    assert list_archived(vault_file) == []


def test_purge_missing_key_raises(vault_file):
    with pytest.raises(ArchiveError, match="not found in archive"):
        purge_archived(vault_file, "NONEXISTENT")


def test_list_archived_empty_when_none(vault_file):
    assert list_archived(vault_file) == []

import pytest
import time
from pathlib import Path

from envault.version import (
    record_version,
    get_versions,
    get_version_at,
    clear_versions,
    VersionError,
)

PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_record_and_get_versions(vault_file):
    record_version(vault_file, "API_KEY", "v1", PASSWORD)
    record_version(vault_file, "API_KEY", "v2", PASSWORD)
    versions = get_versions(vault_file, "API_KEY", PASSWORD)
    assert len(versions) == 2
    assert versions[0]["value"] == "v1"
    assert versions[1]["value"] == "v2"


def test_versions_have_timestamps(vault_file):
    before = time.time()
    record_version(vault_file, "DB_PASS", "secret", PASSWORD)
    after = time.time()
    versions = get_versions(vault_file, "DB_PASS", PASSWORD)
    assert len(versions) == 1
    assert before <= versions[0]["ts"] <= after


def test_get_versions_empty_for_unknown_key(vault_file):
    result = get_versions(vault_file, "MISSING", PASSWORD)
    assert result == []


def test_get_version_at_index(vault_file):
    for val in ["alpha", "beta", "gamma"]:
        record_version(vault_file, "KEY", val, PASSWORD)
    assert get_version_at(vault_file, "KEY", PASSWORD, 0) == "alpha"
    assert get_version_at(vault_file, "KEY", PASSWORD, 2) == "gamma"


def test_get_version_at_invalid_index_raises(vault_file):
    record_version(vault_file, "KEY", "only", PASSWORD)
    with pytest.raises(VersionError, match="out of range"):
        get_version_at(vault_file, "KEY", PASSWORD, 5)


def test_get_version_at_no_history_raises(vault_file):
    with pytest.raises(VersionError, match="No versions"):
        get_version_at(vault_file, "GHOST", PASSWORD, 0)


def test_clear_versions_returns_count(vault_file):
    record_version(vault_file, "X", "a", PASSWORD)
    record_version(vault_file, "X", "b", PASSWORD)
    removed = clear_versions(vault_file, "X")
    assert removed == 2
    assert get_versions(vault_file, "X", PASSWORD) == []


def test_clear_versions_missing_key_returns_zero(vault_file):
    assert clear_versions(vault_file, "NOPE") == 0


def test_versions_file_is_separate_from_vault(vault_file, tmp_path):
    record_version(vault_file, "K", "v", PASSWORD)
    versions_file = tmp_path / "vault.versions.json"
    assert versions_file.exists()
    vault_main = tmp_path / "vault.json"
    assert not vault_main.exists()

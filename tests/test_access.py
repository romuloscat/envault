import pytest
from pathlib import Path
from envault.access import (
    grant, revoke, allowed_keys, check_access,
    list_profiles, delete_profile, AccessError
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_grant_allows_key(vault_file):
    grant(vault_file, "ci", "DB_PASS")
    assert check_access(vault_file, "ci", "DB_PASS")


def test_grant_idempotent(vault_file):
    grant(vault_file, "ci", "DB_PASS")
    grant(vault_file, "ci", "DB_PASS")
    assert allowed_keys(vault_file, "ci").count("DB_PASS") == 1


def test_revoke_removes_key(vault_file):
    grant(vault_file, "ci", "API_KEY")
    revoke(vault_file, "ci", "API_KEY")
    assert not check_access(vault_file, "ci", "API_KEY")


def test_revoke_missing_profile_raises(vault_file):
    with pytest.raises(AccessError):
        revoke(vault_file, "ghost", "KEY")


def test_revoke_missing_key_raises(vault_file):
    grant(vault_file, "ci", "OTHER")
    with pytest.raises(AccessError):
        revoke(vault_file, "ci", "MISSING")


def test_allowed_keys_multiple(vault_file):
    grant(vault_file, "dev", "A")
    grant(vault_file, "dev", "B")
    keys = allowed_keys(vault_file, "dev")
    assert set(keys) == {"A", "B"}


def test_check_access_unknown_profile(vault_file):
    assert not check_access(vault_file, "nobody", "KEY")


def test_list_profiles(vault_file):
    grant(vault_file, "ci", "X")
    grant(vault_file, "dev", "Y")
    assert set(list_profiles(vault_file)) == {"ci", "dev"}


def test_delete_profile(vault_file):
    grant(vault_file, "temp", "Z")
    delete_profile(vault_file, "temp")
    assert "temp" not in list_profiles(vault_file)


def test_delete_missing_profile_raises(vault_file):
    with pytest.raises(AccessError):
        delete_profile(vault_file, "nope")


def test_acl_file_created(vault_file):
    grant(vault_file, "ci", "KEY")
    acl_file = vault_file.with_suffix(".access.json")
    assert acl_file.exists()

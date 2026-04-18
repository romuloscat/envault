import pytest
import json
from pathlib import Path
from envault.profile import (
    add_key_to_profile, remove_key_from_profile, list_profiles,
    get_profile_keys, delete_profile, export_profile, ProfileError
)
from envault.store import set_secret

PASSWORD = "testpass"

@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"

def test_add_key_to_profile(vault_file):
    add_key_to_profile(vault_file, "dev", "DB_URL")
    keys = get_profile_keys(vault_file, "dev")
    assert "DB_URL" in keys

def test_add_key_idempotent(vault_file):
    add_key_to_profile(vault_file, "dev", "DB_URL")
    add_key_to_profile(vault_file, "dev", "DB_URL")
    assert get_profile_keys(vault_file, "dev").count("DB_URL") == 1

def test_add_multiple_keys(vault_file):
    add_key_to_profile(vault_file, "prod", "API_KEY")
    add_key_to_profile(vault_file, "prod", "SECRET")
    keys = get_profile_keys(vault_file, "prod")
    assert set(keys) == {"API_KEY", "SECRET"}

def test_remove_key_from_profile(vault_file):
    add_key_to_profile(vault_file, "dev", "DB_URL")
    remove_key_from_profile(vault_file, "dev", "DB_URL")
    assert get_profile_keys(vault_file, "dev") == []

def test_remove_missing_key_raises(vault_file):
    add_key_to_profile(vault_file, "dev", "DB_URL")
    with pytest.raises(ProfileError):
        remove_key_from_profile(vault_file, "dev", "MISSING")

def test_remove_missing_profile_raises(vault_file):
    with pytest.raises(ProfileError):
        remove_key_from_profile(vault_file, "ghost", "KEY")

def test_list_profiles(vault_file):
    add_key_to_profile(vault_file, "dev", "A")
    add_key_to_profile(vault_file, "prod", "B")
    profiles = list_profiles(vault_file)
    assert set(profiles) == {"dev", "prod"}

def test_list_profiles_empty(vault_file):
    assert list_profiles(vault_file) == []

def test_delete_profile(vault_file):
    add_key_to_profile(vault_file, "dev", "A")
    delete_profile(vault_file, "dev")
    assert "dev" not in list_profiles(vault_file)

def test_delete_missing_profile_raises(vault_file):
    with pytest.raises(ProfileError):
        delete_profile(vault_file, "ghost")

def test_export_profile(vault_file):
    set_secret(vault_file, "DB_URL", "postgres://localhost", PASSWORD)
    set_secret(vault_file, "API_KEY", "abc123", PASSWORD)
    add_key_to_profile(vault_file, "dev", "DB_URL")
    add_key_to_profile(vault_file, "dev", "API_KEY")
    result = export_profile(vault_file, "dev", PASSWORD)
    assert result["DB_URL"] == "postgres://localhost"
    assert result["API_KEY"] == "abc123"

def test_export_missing_profile_raises(vault_file):
    with pytest.raises(ProfileError):
        export_profile(vault_file, "nonexistent", PASSWORD)

def test_get_profile_keys_missing_profile_raises(vault_file):
    with pytest.raises(ProfileError):
        get_profile_keys(vault_file, "nonexistent")

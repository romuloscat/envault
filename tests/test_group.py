import pytest
from pathlib import Path
from envault.group import (
    add_to_group, remove_from_group, list_groups,
    get_group_members, delete_group, GroupError
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.enc"


def test_add_and_get_members(vault_file):
    add_to_group(vault_file, "backend", "DB_URL")
    add_to_group(vault_file, "backend", "DB_PASS")
    members = get_group_members(vault_file, "backend")
    assert "DB_URL" in members
    assert "DB_PASS" in members


def test_add_idempotent(vault_file):
    add_to_group(vault_file, "backend", "DB_URL")
    add_to_group(vault_file, "backend", "DB_URL")
    assert get_group_members(vault_file, "backend").count("DB_URL") == 1


def test_list_groups_empty_when_none(vault_file):
    assert list_groups(vault_file) == []


def test_list_groups_returns_sorted(vault_file):
    add_to_group(vault_file, "frontend", "API_KEY")
    add_to_group(vault_file, "backend", "DB_URL")
    assert list_groups(vault_file) == ["backend", "frontend"]


def test_remove_key_from_group(vault_file):
    add_to_group(vault_file, "backend", "DB_URL")
    add_to_group(vault_file, "backend", "DB_PASS")
    remove_from_group(vault_file, "backend", "DB_URL")
    members = get_group_members(vault_file, "backend")
    assert "DB_URL" not in members
    assert "DB_PASS" in members


def test_remove_last_key_deletes_group(vault_file):
    add_to_group(vault_file, "solo", "ONLY_KEY")
    remove_from_group(vault_file, "solo", "ONLY_KEY")
    assert "solo" not in list_groups(vault_file)


def test_remove_missing_key_raises(vault_file):
    add_to_group(vault_file, "backend", "DB_URL")
    with pytest.raises(GroupError):
        remove_from_group(vault_file, "backend", "MISSING")


def test_remove_from_missing_group_raises(vault_file):
    with pytest.raises(GroupError):
        remove_from_group(vault_file, "ghost", "KEY")


def test_get_members_missing_group_raises(vault_file):
    with pytest.raises(GroupError):
        get_group_members(vault_file, "nonexistent")


def test_delete_group(vault_file):
    add_to_group(vault_file, "temp", "FOO")
    delete_group(vault_file, "temp")
    assert "temp" not in list_groups(vault_file)


def test_delete_missing_group_raises(vault_file):
    with pytest.raises(GroupError):
        delete_group(vault_file, "ghost")

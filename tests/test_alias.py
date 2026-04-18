import pytest
import json
from pathlib import Path
from envault.alias import (
    set_alias, remove_alias, resolve_alias,
    list_aliases, aliases_for_key, AliasError,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_and_resolve_alias(vault_file):
    set_alias(vault_file, "db", "DATABASE_URL")
    assert resolve_alias(vault_file, "db") == "DATABASE_URL"


def test_resolve_unknown_returns_itself(vault_file):
    assert resolve_alias(vault_file, "unknown") == "unknown"


def test_set_alias_overwrites(vault_file):
    set_alias(vault_file, "db", "DATABASE_URL")
    set_alias(vault_file, "db", "DB_URI")
    assert resolve_alias(vault_file, "db") == "DB_URI"


def test_remove_alias(vault_file):
    set_alias(vault_file, "db", "DATABASE_URL")
    remove_alias(vault_file, "db")
    assert resolve_alias(vault_file, "db") == "db"


def test_remove_missing_alias_raises(vault_file):
    with pytest.raises(AliasError, match="does not exist"):
        remove_alias(vault_file, "ghost")


def test_list_aliases(vault_file):
    set_alias(vault_file, "db", "DATABASE_URL")
    set_alias(vault_file, "secret", "API_KEY")
    result = list_aliases(vault_file)
    assert result == {"db": "DATABASE_URL", "secret": "API_KEY"}


def test_list_aliases_empty(vault_file):
    assert list_aliases(vault_file) == {}


def test_aliases_for_key(vault_file):
    set_alias(vault_file, "db", "DATABASE_URL")
    set_alias(vault_file, "database", "DATABASE_URL")
    set_alias(vault_file, "key", "API_KEY")
    result = aliases_for_key(vault_file, "DATABASE_URL")
    assert sorted(result) == ["database", "db"]


def test_set_empty_alias_raises(vault_file):
    with pytest.raises(AliasError):
        set_alias(vault_file, "", "DATABASE_URL")


def test_set_empty_key_raises(vault_file):
    with pytest.raises(AliasError):
        set_alias(vault_file, "db", "")

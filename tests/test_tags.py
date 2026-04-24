"""Tests for envault.tags module."""
import pytest
import json
from pathlib import Path
from envault.store import set_secret
from envault.tags import tag_secret, untag_secret, get_tags, keys_by_tag, TagError

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.json"
    set_secret(str(p), "DB_HOST", "localhost", PASSWORD)
    set_secret(str(p), "DB_PASS", "secret", PASSWORD)
    set_secret(str(p), "API_KEY", "abc123", PASSWORD)
    return str(p)


def test_tag_and_get_tags(vault_file):
    tag_secret(vault_file, "DB_HOST", "database")
    assert "database" in get_tags(vault_file, "DB_HOST")


def test_tag_multiple_tags(vault_file):
    tag_secret(vault_file, "DB_HOST", "database")
    tag_secret(vault_file, "DB_HOST", "production")
    tags = get_tags(vault_file, "DB_HOST")
    assert "database" in tags
    assert "production" in tags


def test_tag_duplicate_is_idempotent(vault_file):
    tag_secret(vault_file, "DB_HOST", "database")
    tag_secret(vault_file, "DB_HOST", "database")
    assert get_tags(vault_file, "DB_HOST").count("database") == 1


def test_untag_secret(vault_file):
    tag_secret(vault_file, "DB_HOST", "database")
    untag_secret(vault_file, "DB_HOST", "database")
    assert "database" not in get_tags(vault_file, "DB_HOST")


def test_untag_missing_tag_raises(vault_file):
    with pytest.raises(TagError, match="Tag"):
        untag_secret(vault_file, "DB_HOST", "nonexistent")


def test_tag_missing_key_raises(vault_file):
    with pytest.raises(TagError, match="Key"):
        tag_secret(vault_file, "MISSING_KEY", "sometag")


def test_get_tags_missing_key_raises(vault_file):
    """get_tags should raise TagError when the key does not exist in the vault."""
    with pytest.raises(TagError, match="Key"):
        get_tags(vault_file, "MISSING_KEY")


def test_get_tags_no_tags_returns_empty(vault_file):
    assert get_tags(vault_file, "API_KEY") == []


def test_keys_by_tag(vault_file):
    tag_secret(vault_file, "DB_HOST", "database")
    tag_secret(vault_file, "DB_PASS", "database")
    tag_secret(vault_file, "API_KEY", "external")
    result = keys_by_tag(vault_file, "database")
    assert "DB_HOST" in result
    assert "DB_PASS" in result
    assert "API_KEY" not in result


def test_keys_by_tag_glob(vault_file):
    tag_secret(vault_file, "DB_HOST", "db-primary")
    tag_secret(vault_file, "DB_PASS", "db-replica")
    tag_secret(vault_file, "API_KEY", "external")
    result = keys_by_tag(vault_file, "db-*")
    assert "DB_HOST" in result
    assert "DB_PASS" in result


def test_keys_by_tag_no_match_returns_empty(vault_file):
    assert keys_by_tag(vault_file, "ghost") == []

"""Tests for envault.comment."""
import pytest
from pathlib import Path
from envault.comment import (
    set_comment, get_comment, remove_comment, list_comments, CommentError
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_and_get_comment(vault_file):
    set_comment(vault_file, "API_KEY", "Production API key")
    assert get_comment(vault_file, "API_KEY") == "Production API key"


def test_get_comment_missing_key_returns_none(vault_file):
    assert get_comment(vault_file, "MISSING") is None


def test_set_comment_overwrites(vault_file):
    set_comment(vault_file, "DB_PASS", "old comment")
    set_comment(vault_file, "DB_PASS", "new comment")
    assert get_comment(vault_file, "DB_PASS") == "new comment"


def test_set_empty_comment_raises(vault_file):
    with pytest.raises(CommentError):
        set_comment(vault_file, "KEY", "   ")


def test_remove_comment(vault_file):
    set_comment(vault_file, "TOKEN", "Auth token")
    remove_comment(vault_file, "TOKEN")
    assert get_comment(vault_file, "TOKEN") is None


def test_remove_missing_comment_raises(vault_file):
    with pytest.raises(CommentError):
        remove_comment(vault_file, "NONEXISTENT")


def test_list_comments_empty_when_none(vault_file):
    assert list_comments(vault_file) == {}


def test_list_comments_returns_all(vault_file):
    set_comment(vault_file, "A", "alpha")
    set_comment(vault_file, "B", "beta")
    result = list_comments(vault_file)
    assert result == {"A": "alpha", "B": "beta"}


def test_comment_file_created_next_to_vault(vault_file, tmp_path):
    set_comment(vault_file, "KEY", "some note")
    expected = tmp_path / "vault.comments.json"
    assert expected.exists()

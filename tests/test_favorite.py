"""Tests for envault.favorite module."""

import pytest
from pathlib import Path
from envault.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    FavoriteError,
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_add_and_is_favorite(vault_file):
    add_favorite(vault_file, "API_KEY")
    assert is_favorite(vault_file, "API_KEY")


def test_add_favorite_idempotent(vault_file):
    add_favorite(vault_file, "API_KEY")
    add_favorite(vault_file, "API_KEY")
    assert list_favorites(vault_file).count("API_KEY") == 1


def test_list_favorites_empty_when_none(vault_file):
    assert list_favorites(vault_file) == []


def test_list_favorites_returns_all(vault_file):
    add_favorite(vault_file, "KEY_A")
    add_favorite(vault_file, "KEY_B")
    favs = list_favorites(vault_file)
    assert "KEY_A" in favs
    assert "KEY_B" in favs
    assert len(favs) == 2


def test_remove_favorite(vault_file):
    add_favorite(vault_file, "API_KEY")
    remove_favorite(vault_file, "API_KEY")
    assert not is_favorite(vault_file, "API_KEY")


def test_remove_missing_favorite_raises(vault_file):
    with pytest.raises(FavoriteError, match="not in favorites"):
        remove_favorite(vault_file, "MISSING_KEY")


def test_is_favorite_returns_false_for_unknown(vault_file):
    assert not is_favorite(vault_file, "UNKNOWN")


def test_favorites_persisted_across_calls(vault_file):
    add_favorite(vault_file, "PERSIST_KEY")
    # Re-read from disk
    result = list_favorites(vault_file)
    assert "PERSIST_KEY" in result

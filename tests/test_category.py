"""Tests for envault.category."""

import pytest

from envault.category import (
    CategoryError,
    get_category,
    list_by_category,
    list_categories,
    remove_category,
    set_category,
)


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_and_get_category(vault_file):
    set_category(vault_file, "DB_PASSWORD", "database")
    assert get_category(vault_file, "DB_PASSWORD") == "database"


def test_get_category_missing_key_returns_none(vault_file):
    assert get_category(vault_file, "MISSING") is None


def test_set_category_overwrites(vault_file):
    set_category(vault_file, "API_KEY", "api")
    set_category(vault_file, "API_KEY", "auth")
    assert get_category(vault_file, "API_KEY") == "auth"


def test_set_empty_category_raises(vault_file):
    with pytest.raises(CategoryError, match="empty"):
        set_category(vault_file, "KEY", "   ")


def test_remove_category(vault_file):
    set_category(vault_file, "TOKEN", "auth")
    remove_category(vault_file, "TOKEN")
    assert get_category(vault_file, "TOKEN") is None


def test_remove_missing_category_raises(vault_file):
    with pytest.raises(CategoryError, match="no category"):
        remove_category(vault_file, "GHOST")


def test_list_by_category(vault_file):
    set_category(vault_file, "DB_HOST", "database")
    set_category(vault_file, "DB_PASSWORD", "database")
    set_category(vault_file, "API_KEY", "api")
    result = list_by_category(vault_file, "database")
    assert result == ["DB_HOST", "DB_PASSWORD"]


def test_list_by_category_no_match(vault_file):
    set_category(vault_file, "API_KEY", "api")
    assert list_by_category(vault_file, "database") == []


def test_list_categories(vault_file):
    set_category(vault_file, "DB_HOST", "database")
    set_category(vault_file, "API_KEY", "api")
    set_category(vault_file, "JWT_SECRET", "auth")
    assert list_categories(vault_file) == ["api", "auth", "database"]


def test_list_categories_empty_when_none(vault_file):
    assert list_categories(vault_file) == []


def test_list_categories_deduplicates(vault_file):
    set_category(vault_file, "DB_HOST", "database")
    set_category(vault_file, "DB_PORT", "database")
    assert list_categories(vault_file) == ["database"]

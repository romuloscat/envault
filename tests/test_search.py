"""Tests for envault.search module."""

import json
import pytest
from click.testing import CliRunner

from envault.store import set_secret
from envault.search import search_secrets, SearchError


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    password = "hunter2"
    set_secret(path, "DB_HOST", "localhost", password)
    set_secret(path, "DB_PORT", "5432", password)
    set_secret(path, "API_KEY", "abc123", password)
    set_secret(path, "API_SECRET", "supersecret", password)
    return path, password


def test_search_glob_key_prefix(vault_file):
    path, pw = vault_file
    results = search_secrets(path, pw, "DB_*")
    assert set(results.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_glob_exact_key(vault_file):
    path, pw = vault_file
    results = search_secrets(path, pw, "API_KEY")
    assert list(results.keys()) == ["API_KEY"]
    assert results["API_KEY"] == "abc123"


def test_search_no_match_returns_empty(vault_file):
    path, pw = vault_file
    results = search_secrets(path, pw, "MISSING_*")
    assert results == {}


def test_search_by_value(vault_file):
    path, pw = vault_file
    results = search_secrets(path, pw, "*secret*", search_values=True)
    assert "API_SECRET" in results


def test_search_regex_key(vault_file):
    path, pw = vault_file
    results = search_secrets(path, pw, r"^API_", regex=True)
    assert set(results.keys()) == {"API_KEY", "API_SECRET"}


def test_search_regex_value(vault_file):
    path, pw = vault_file
    results = search_secrets(path, pw, r"\d+", regex=True, search_values=True)
    assert "DB_PORT" in results
    assert "API_KEY" in results


def test_search_invalid_regex_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(SearchError, match="Invalid regex"):
        search_secrets(path, pw, r"[invalid", regex=True)


def test_search_empty_vault(tmp_path):
    path = str(tmp_path / "empty.json")
    import json
    with open(path, "w") as f:
        json.dump({}, f)
    results = search_secrets(path, "pw", "*")
    assert results == {}

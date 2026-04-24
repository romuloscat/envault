"""Tests for envault.cascade."""

import json
import pytest
from pathlib import Path

from envault.store import set_secret
from envault.cascade import (
    CascadeError,
    set_cascade,
    get_cascade,
    clear_cascade,
    resolve_key,
    cascade_all_keys,
)

PASSWORD = "test-pass"


@pytest.fixture()
def primary(tmp_path):
    p = tmp_path / "primary.vault"
    set_secret("SHARED_KEY", "primary-value", PASSWORD, vault_path=p)
    set_secret("PRIMARY_ONLY", "only-in-primary", PASSWORD, vault_path=p)
    return p


@pytest.fixture()
def fallback(tmp_path):
    p = tmp_path / "fallback.vault"
    set_secret("SHARED_KEY", "fallback-value", PASSWORD, vault_path=p)
    set_secret("FALLBACK_ONLY", "only-in-fallback", PASSWORD, vault_path=p)
    return p


def test_set_and_get_cascade(primary, fallback):
    set_cascade(primary, [str(fallback)])
    chain = get_cascade(primary)
    assert chain == [str(fallback)]


def test_set_cascade_nonexistent_vault_raises(primary, tmp_path):
    ghost = tmp_path / "ghost.vault"
    with pytest.raises(CascadeError, match="not found"):
        set_cascade(primary, [str(ghost)])


def test_set_cascade_empty_chain_raises(primary):
    with pytest.raises(CascadeError, match="at least one"):
        set_cascade(primary, [])


def test_clear_cascade(primary, fallback):
    set_cascade(primary, [str(fallback)])
    clear_cascade(primary)
    assert get_cascade(primary) == []


def test_clear_cascade_idempotent(primary):
    # Should not raise even if no cascade file exists
    clear_cascade(primary)


def test_resolve_key_found_in_primary(primary, fallback):
    set_cascade(primary, [str(fallback)])
    value = resolve_key("PRIMARY_ONLY", PASSWORD, primary)
    assert value == "only-in-primary"


def test_resolve_key_found_in_fallback(primary, fallback):
    set_cascade(primary, [str(fallback)])
    value = resolve_key("FALLBACK_ONLY", PASSWORD, primary)
    assert value == "only-in-fallback"


def test_resolve_key_primary_takes_precedence(primary, fallback):
    set_cascade(primary, [str(fallback)])
    value = resolve_key("SHARED_KEY", PASSWORD, primary)
    assert value == "primary-value"


def test_resolve_key_missing_returns_none(primary, fallback):
    set_cascade(primary, [str(fallback)])
    value = resolve_key("DOES_NOT_EXIST", PASSWORD, primary)
    assert value is None


def test_resolve_key_no_cascade(primary):
    value = resolve_key("PRIMARY_ONLY", PASSWORD, primary)
    assert value == "only-in-primary"


def test_cascade_all_keys_merges(primary, fallback):
    set_cascade(primary, [str(fallback)])
    merged = cascade_all_keys(PASSWORD, primary)
    assert "PRIMARY_ONLY" in merged
    assert "FALLBACK_ONLY" in merged
    assert merged["SHARED_KEY"] == "primary-value"


def test_cascade_all_keys_no_cascade(primary):
    merged = cascade_all_keys(PASSWORD, primary)
    assert "PRIMARY_ONLY" in merged
    assert "FALLBACK_ONLY" not in merged

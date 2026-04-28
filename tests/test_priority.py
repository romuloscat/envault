"""Tests for envault.priority."""

from __future__ import annotations

import pytest

from envault.priority import (
    DEFAULT_PRIORITY,
    PriorityError,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_and_get_priority(vault_file):
    set_priority(vault_file, "API_KEY", 80)
    assert get_priority(vault_file, "API_KEY") == 80


def test_get_priority_missing_key_returns_default(vault_file):
    assert get_priority(vault_file, "MISSING") == DEFAULT_PRIORITY


def test_set_priority_overwrites(vault_file):
    set_priority(vault_file, "DB_PASS", 30)
    set_priority(vault_file, "DB_PASS", 70)
    assert get_priority(vault_file, "DB_PASS") == 70


def test_set_priority_below_min_raises(vault_file):
    with pytest.raises(PriorityError, match="between"):
        set_priority(vault_file, "KEY", 0)


def test_set_priority_above_max_raises(vault_file):
    with pytest.raises(PriorityError, match="between"):
        set_priority(vault_file, "KEY", 101)


def test_set_priority_boundary_values(vault_file):
    set_priority(vault_file, "LOW", 1)
    set_priority(vault_file, "HIGH", 100)
    assert get_priority(vault_file, "LOW") == 1
    assert get_priority(vault_file, "HIGH") == 100


def test_remove_priority(vault_file):
    set_priority(vault_file, "TOKEN", 90)
    remove_priority(vault_file, "TOKEN")
    assert get_priority(vault_file, "TOKEN") == DEFAULT_PRIORITY


def test_remove_missing_priority_raises(vault_file):
    with pytest.raises(PriorityError, match="No priority set"):
        remove_priority(vault_file, "GHOST")


def test_list_by_priority_sorted_descending(vault_file):
    set_priority(vault_file, "B", 20)
    set_priority(vault_file, "A", 90)
    set_priority(vault_file, "C", 55)
    pairs = list_by_priority(vault_file)
    levels = [p for _, p in pairs]
    assert levels == sorted(levels, reverse=True)


def test_list_by_priority_with_explicit_keys(vault_file):
    set_priority(vault_file, "KNOWN", 75)
    pairs = list_by_priority(vault_file, keys=["KNOWN", "UNKNOWN"])
    result = dict(pairs)
    assert result["KNOWN"] == 75
    assert result["UNKNOWN"] == DEFAULT_PRIORITY


def test_list_by_priority_empty(vault_file):
    assert list_by_priority(vault_file) == []

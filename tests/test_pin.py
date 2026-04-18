"""Tests for envault.pin"""
import pytest
from pathlib import Path
from envault.pin import (
    pin_secret,
    unpin_secret,
    is_pinned,
    list_pins,
    assert_not_pinned,
    PinError,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_pin_and_is_pinned(vault_file):
    pin_secret(vault_file, "API_KEY")
    assert is_pinned(vault_file, "API_KEY")


def test_unpin_secret(vault_file):
    pin_secret(vault_file, "API_KEY")
    unpin_secret(vault_file, "API_KEY")
    assert not is_pinned(vault_file, "API_KEY")


def test_pin_idempotent(vault_file):
    pin_secret(vault_file, "API_KEY", reason="stable")
    pin_secret(vault_file, "API_KEY", reason="changed")  # should not overwrite
    pins = list_pins(vault_file)
    assert pins[0]["reason"] == "stable"


def test_unpin_missing_key_raises(vault_file):
    with pytest.raises(PinError, match="not pinned"):
        unpin_secret(vault_file, "MISSING_KEY")


def test_is_pinned_returns_false_when_no_file(vault_file):
    assert not is_pinned(vault_file, "SOME_KEY")


def test_list_pins_empty(vault_file):
    assert list_pins(vault_file) == []


def test_list_pins_returns_sorted(vault_file):
    pin_secret(vault_file, "Z_KEY", reason="last")
    pin_secret(vault_file, "A_KEY", reason="first")
    pins = list_pins(vault_file)
    assert [p["key"] for p in pins] == ["A_KEY", "Z_KEY"]


def test_list_pins_includes_reason(vault_file):
    pin_secret(vault_file, "DB_PASS", reason="production critical")
    pins = list_pins(vault_file)
    assert pins[0]["reason"] == "production critical"


def test_assert_not_pinned_passes_for_unpinned(vault_file):
    assert_not_pinned(vault_file, "FREE_KEY")  # should not raise


def test_assert_not_pinned_raises_for_pinned(vault_file):
    pin_secret(vault_file, "LOCKED", reason="do not touch")
    with pytest.raises(PinError, match="pinned"):
        assert_not_pinned(vault_file, "LOCKED")


def test_assert_not_pinned_includes_reason_in_message(vault_file):
    pin_secret(vault_file, "SECRET", reason="immutable")
    with pytest.raises(PinError, match="immutable"):
        assert_not_pinned(vault_file, "SECRET")

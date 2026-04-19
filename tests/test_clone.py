"""Tests for envault.clone."""
import pytest
from pathlib import Path
from envault.store import set_secret, get_secret, list_secrets
from envault.clone import clone_vault, CloneError


PASSWORD = "test-password"
DST_PASSWORD = "dst-password"


@pytest.fixture
def src_vault(tmp_path):
    p = tmp_path / "src.vault"
    set_secret(p, "ALPHA", "aaa", PASSWORD)
    set_secret(p, "BETA", "bbb", PASSWORD)
    set_secret(p, "GAMMA", "ccc", PASSWORD)
    return p


@pytest.fixture
def dst_vault(tmp_path):
    return tmp_path / "dst.vault"


def test_clone_all_keys(src_vault, dst_vault):
    count = clone_vault(src_vault, dst_vault, PASSWORD, DST_PASSWORD)
    assert count == 3
    assert get_secret(dst_vault, "ALPHA", DST_PASSWORD) == "aaa"
    assert get_secret(dst_vault, "BETA", DST_PASSWORD) == "bbb"
    assert get_secret(dst_vault, "GAMMA", DST_PASSWORD) == "ccc"


def test_clone_selected_keys(src_vault, dst_vault):
    count = clone_vault(src_vault, dst_vault, PASSWORD, DST_PASSWORD, keys=["ALPHA", "GAMMA 2
    keys = list_secrets(dst_vault, DST_PASSWORD)
    assert "ALPHA" in keys
    assert "GAMMA" in keys
    assert "BETA" not in keys


def test_clone_missing_key_raises(src_vault, dst_vault):
    with pytest.raises(CloneError, match="MISSING"):
        clone_vault(src_vault, dst_vault, PASSWORD, DST_PASSWORD, keys=["MISSING"])


def test_clone_missing_src_vault_raises(tmp_path, dst_vault):
    with pytest.raises(CloneError, match="Source vault not found"):
        clone_vault(tmp_path / "nonexistent.vault", dst_vault, PASSWORD, DST_PASSWORD)


def test_clone_no_overwrite_skips_existing(src_vault, dst_vault):
    set_secret(dst_vault, "ALPHA", "original", DST_PASSWORD)
    count = clone_vault(src_vault, dst_vault, PASSWORD, DST_PASSWORD, overwrite=False)
    assert count == 2  # BETA and GAMMA cloned, ALPHA skipped
    assert get_secret(dst_vault, "ALPHA", DST_PASSWORD) == "original"


def test_clone_overwrite_replaces_existing(src_vault, dst_vault):
    set_secret(dst_vault, "ALPHA", "original", DST_PASSWORD)
    count = clone_vault(src_vault, dst_vault, PASSWORD, DST_PASSWORD, overwrite=True)
    assert count == 3
    assert get_secret(dst_vault, "ALPHA", DST_PASSWORD) == "aaa"


def test_clone_empty_selection_returns_zero(src_vault, dst_vault):
    count = clone_vault(src_vault, dst_vault, PASSWORD, DST_PASSWORD, keys=[])
    assert count == 0

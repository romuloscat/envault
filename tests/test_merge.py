"""Tests for envault.merge."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.store import set_secret, get_secret, list_secrets
from envault.merge import merge_vaults, MergeConflict, MergeError

PASSWORD = "test-password"


@pytest.fixture()
def src_vault(tmp_path: Path) -> Path:
    p = tmp_path / "src.vault"
    set_secret(p, "ALPHA", "alpha_val", PASSWORD)
    set_secret(p, "BETA", "beta_val", PASSWORD)
    set_secret(p, "GAMMA", "gamma_val", PASSWORD)
    return p


@pytest.fixture()
def dst_vault(tmp_path: Path) -> Path:
    p = tmp_path / "dst.vault"
    set_secret(p, "BETA", "dst_beta", PASSWORD)
    set_secret(p, "DELTA", "delta_val", PASSWORD)
    return p


def test_merge_adds_new_keys(src_vault: Path, dst_vault: Path) -> None:
    result = merge_vaults(src_vault, dst_vault, PASSWORD, strategy="skip")
    assert result["ALPHA"] == "added"
    assert result["GAMMA"] == "added"
    assert get_secret(dst_vault, "ALPHA", PASSWORD) == "alpha_val"
    assert get_secret(dst_vault, "GAMMA", PASSWORD) == "gamma_val"


def test_merge_skip_strategy_keeps_dst_value(src_vault: Path, dst_vault: Path) -> None:
    result = merge_vaults(src_vault, dst_vault, PASSWORD, strategy="skip")
    assert result["BETA"] == "skipped"
    assert get_secret(dst_vault, "BETA", PASSWORD) == "dst_beta"


def test_merge_ours_strategy_keeps_dst_value(src_vault: Path, dst_vault: Path) -> None:
    result = merge_vaults(src_vault, dst_vault, PASSWORD, strategy="ours")
    assert result["BETA"] == "skipped"
    assert get_secret(dst_vault, "BETA", PASSWORD) == "dst_beta"


def test_merge_theirs_strategy_overwrites(src_vault: Path, dst_vault: Path) -> None:
    result = merge_vaults(src_vault, dst_vault, PASSWORD, strategy="theirs")
    assert result["BETA"] == "overwritten"
    assert get_secret(dst_vault, "BETA", PASSWORD) == "beta_val"


def test_merge_error_strategy_raises_on_conflict(src_vault: Path, dst_vault: Path) -> None:
    with pytest.raises(MergeConflict) as exc_info:
        merge_vaults(src_vault, dst_vault, PASSWORD, strategy="error")
    assert exc_info.value.key == "BETA"


def test_merge_preserves_existing_dst_keys(src_vault: Path, dst_vault: Path) -> None:
    merge_vaults(src_vault, dst_vault, PASSWORD, strategy="skip")
    assert get_secret(dst_vault, "DELTA", PASSWORD) == "delta_val"


def test_merge_selected_keys_only(src_vault: Path, dst_vault: Path) -> None:
    result = merge_vaults(src_vault, dst_vault, PASSWORD, strategy="skip", keys=["ALPHA"])
    assert set(result.keys()) == {"ALPHA"}
    assert "GAMMA" not in list_secrets(dst_vault, PASSWORD) or \
        get_secret(dst_vault, "GAMMA", PASSWORD) is not None  # GAMMA not merged


def test_merge_missing_key_in_src_raises(src_vault: Path, dst_vault: Path) -> None:
    with pytest.raises(MergeError, match="NONEXISTENT"):
        merge_vaults(src_vault, dst_vault, PASSWORD, keys=["NONEXISTENT"])


def test_merge_into_empty_dst(src_vault: Path, tmp_path: Path) -> None:
    empty_dst = tmp_path / "empty.vault"
    result = merge_vaults(src_vault, empty_dst, PASSWORD)
    assert all(v == "added" for v in result.values())
    assert set(list_secrets(empty_dst, PASSWORD)) == {"ALPHA", "BETA", "GAMMA"}

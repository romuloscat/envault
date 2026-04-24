"""Tests for envault.inherit."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.store import set_secret
from envault.inherit import (
    InheritError,
    get_parent,
    remove_parent,
    resolve_secret,
    set_parent,
)
from envault.cli_inherit import inherit_cmd

PASSWORD = "test-password"


@pytest.fixture()
def base_vault(tmp_path: Path) -> Path:
    p = tmp_path / "base.vault"
    set_secret(p, "BASE_KEY", "base_value", PASSWORD)
    set_secret(p, "SHARED_KEY", "from_base", PASSWORD)
    return p


@pytest.fixture()
def child_vault(tmp_path: Path) -> Path:
    p = tmp_path / "child.vault"
    set_secret(p, "CHILD_KEY", "child_value", PASSWORD)
    set_secret(p, "SHARED_KEY", "from_child", PASSWORD)
    return p


def test_set_and_get_parent(base_vault: Path, child_vault: Path) -> None:
    set_parent(child_vault, base_vault)
    assert get_parent(child_vault) == base_vault.resolve()


def test_get_parent_returns_none_when_not_set(child_vault: Path) -> None:
    assert get_parent(child_vault) is None


def test_set_parent_nonexistent_raises(tmp_path: Path, child_vault: Path) -> None:
    with pytest.raises(InheritError, match="not found"):
        set_parent(child_vault, tmp_path / "ghost.vault")


def test_set_parent_self_raises(child_vault: Path) -> None:
    with pytest.raises(InheritError, match="itself"):
        set_parent(child_vault, child_vault)


def test_remove_parent(base_vault: Path, child_vault: Path) -> None:
    set_parent(child_vault, base_vault)
    remove_parent(child_vault)
    assert get_parent(child_vault) is None


def test_remove_parent_when_none_raises(child_vault: Path) -> None:
    with pytest.raises(InheritError, match="No parent"):
        remove_parent(child_vault)


def test_resolve_secret_found_in_child(base_vault: Path, child_vault: Path) -> None:
    set_parent(child_vault, base_vault)
    assert resolve_secret("CHILD_KEY", child_vault, PASSWORD) == "child_value"


def test_resolve_secret_falls_back_to_parent(base_vault: Path, child_vault: Path) -> None:
    set_parent(child_vault, base_vault)
    assert resolve_secret("BASE_KEY", child_vault, PASSWORD) == "base_value"


def test_resolve_secret_child_overrides_parent(base_vault: Path, child_vault: Path) -> None:
    set_parent(child_vault, base_vault)
    assert resolve_secret("SHARED_KEY", child_vault, PASSWORD) == "from_child"


def test_resolve_secret_missing_raises(base_vault: Path, child_vault: Path) -> None:
    set_parent(child_vault, base_vault)
    with pytest.raises(InheritError, match="not found"):
        resolve_secret("NO_SUCH_KEY", child_vault, PASSWORD)


def test_cli_set_parent_and_resolve(tmp_path: Path, base_vault: Path, child_vault: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        inherit_cmd,
        ["set-parent", "--vault", str(child_vault), "--parent", str(base_vault)],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        inherit_cmd,
        ["resolve", "--vault", str(child_vault), "--password", PASSWORD, "BASE_KEY"],
    )
    assert result.exit_code == 0
    assert "base_value" in result.output


def test_cli_resolve_missing_key_exits_nonzero(child_vault: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        inherit_cmd,
        ["resolve", "--vault", str(child_vault), "--password", PASSWORD, "GHOST"],
    )
    assert result.exit_code != 0

"""CLI tests for checkpoint commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_checkpoint import checkpoint_cmd
from envault.store import set_secret

PASSWORD = "test-password"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    set_secret(vf, PASSWORD, "KEY1", "val1")
    set_secret(vf, PASSWORD, "KEY2", "val2")
    return vf


def _opt(vault_file):
    return ["--vault", str(vault_file), "--password", PASSWORD]


def test_cp_create(runner, vault_file):
    result = runner.invoke(
        checkpoint_cmd, ["create", "release-1"] + _opt(vault_file)
    )
    assert result.exit_code == 0
    assert "release-1" in result.output


def test_cp_list_empty(runner, vault_file):
    result = runner.invoke(checkpoint_cmd, ["list", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "No checkpoints" in result.output


def test_cp_list_shows_checkpoint(runner, vault_file):
    runner.invoke(checkpoint_cmd, ["create", "v1"] + _opt(vault_file) + ["--description", "first"])
    result = runner.invoke(checkpoint_cmd, ["list", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "v1" in result.output
    assert "first" in result.output


def test_cp_create_duplicate_exits_nonzero(runner, vault_file):
    runner.invoke(checkpoint_cmd, ["create", "v1"] + _opt(vault_file))
    result = runner.invoke(checkpoint_cmd, ["create", "v1"] + _opt(vault_file))
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cp_restore(runner, vault_file):
    runner.invoke(checkpoint_cmd, ["create", "v1"] + _opt(vault_file))
    result = runner.invoke(checkpoint_cmd, ["restore", "v1"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_cp_delete(runner, vault_file):
    runner.invoke(checkpoint_cmd, ["create", "v1"] + _opt(vault_file))
    result = runner.invoke(checkpoint_cmd, ["delete", "v1", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_cp_delete_missing_exits_nonzero(runner, vault_file):
    result = runner.invoke(checkpoint_cmd, ["delete", "ghost", "--vault", str(vault_file)])
    assert result.exit_code != 0

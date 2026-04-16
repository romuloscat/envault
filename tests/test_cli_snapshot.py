"""CLI tests for snapshot commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_snapshot import snapshot_cmd
from envault.store import set_secret

PASSWORD = "cli-snap-pass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.json"
    set_secret(p, "HELLO", "world", PASSWORD)
    return p


def test_snap_create(runner, vault_file):
    result = runner.invoke(snapshot_cmd, ["create", "--vault", str(vault_file), "--label", "test"])
    assert result.exit_code == 0
    assert "Snapshot created" in result.output
    assert "test" in result.output


def test_snap_list_empty(runner, vault_file):
    result = runner.invoke(snapshot_cmd, ["list", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "No snapshots found" in result.output


def test_snap_list_shows_snapshots(runner, vault_file):
    runner.invoke(snapshot_cmd, ["create", "--vault", str(vault_file), "--label", "alpha"])
    result = runner.invoke(snapshot_cmd, ["list", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "alpha" in result.output


def test_snap_restore(runner, vault_file):
    runner.invoke(snapshot_cmd, ["create", "--vault", str(vault_file)])
    snaps_result = runner.invoke(snapshot_cmd, ["list", "--vault", str(vault_file)])
    snap_name = snaps_result.output.strip().splitlines()[0].strip()
    result = runner.invoke(snapshot_cmd, ["restore", snap_name, "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_snap_restore_missing(runner, vault_file):
    result = runner.invoke(snapshot_cmd, ["restore", "ghost.json", "--vault", str(vault_file)])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_snap_delete(runner, vault_file):
    runner.invoke(snapshot_cmd, ["create", "--vault", str(vault_file), "--label", "del"])
    snaps_result = runner.invoke(snapshot_cmd, ["list", "--vault", str(vault_file)])
    snap_name = snaps_result.output.strip().splitlines()[0].strip().split()[0]
    result = runner.invoke(snapshot_cmd, ["delete", snap_name, "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Deleted" in result.output

"""Tests for envault.checkpoint."""

import json
import pytest
from pathlib import Path

from envault.store import set_secret
from envault.checkpoint import (
    CheckpointError,
    create_checkpoint,
    list_checkpoints,
    restore_checkpoint,
    delete_checkpoint,
    _checkpoint_path,
)

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.enc"
    set_secret(vf, PASSWORD, "ALPHA", "one")
    set_secret(vf, PASSWORD, "BETA", "two")
    return vf


def test_create_checkpoint_returns_path(vault_file):
    path = create_checkpoint(vault_file, PASSWORD, "v1")
    assert Path(path).exists()


def test_create_checkpoint_records_metadata(vault_file):
    create_checkpoint(vault_file, PASSWORD, "v1", description="initial")
    checkpoints = list_checkpoints(vault_file)
    assert len(checkpoints) == 1
    assert checkpoints[0]["name"] == "v1"
    assert checkpoints[0]["description"] == "initial"
    assert checkpoints[0]["created_at"] > 0


def test_create_duplicate_checkpoint_raises(vault_file):
    create_checkpoint(vault_file, PASSWORD, "v1")
    with pytest.raises(CheckpointError, match="already exists"):
        create_checkpoint(vault_file, PASSWORD, "v1")


def test_list_checkpoints_empty_when_none(vault_file):
    result = list_checkpoints(vault_file)
    assert result == []


def test_list_checkpoints_sorted_by_time(vault_file):
    create_checkpoint(vault_file, PASSWORD, "first")
    create_checkpoint(vault_file, PASSWORD, "second")
    names = [c["name"] for c in list_checkpoints(vault_file)]
    assert names == ["first", "second"]


def test_restore_checkpoint_restores_keys(vault_file):
    create_checkpoint(vault_file, PASSWORD, "snap1")
    # Add a new key after checkpoint
    set_secret(vault_file, PASSWORD, "GAMMA", "three")
    count = restore_checkpoint(vault_file, PASSWORD, "snap1")
    assert count == 2  # ALPHA, BETA


def test_restore_unknown_checkpoint_raises(vault_file):
    with pytest.raises(CheckpointError, match="not found"):
        restore_checkpoint(vault_file, PASSWORD, "ghost")


def test_delete_checkpoint_removes_entry(vault_file):
    create_checkpoint(vault_file, PASSWORD, "v1")
    delete_checkpoint(vault_file, "v1")
    assert list_checkpoints(vault_file) == []


def test_delete_missing_checkpoint_raises(vault_file):
    with pytest.raises(CheckpointError, match="not found"):
        delete_checkpoint(vault_file, "nope")


def test_restore_with_missing_snapshot_file_raises(vault_file):
    create_checkpoint(vault_file, PASSWORD, "v1")
    # Corrupt the snapshot path in the metadata
    cp_path = _checkpoint_path(vault_file)
    data = json.loads(cp_path.read_text())
    data["v1"]["snapshot"] = "/nonexistent/path.snap"
    cp_path.write_text(json.dumps(data))
    with pytest.raises(CheckpointError, match="Snapshot file missing"):
        restore_checkpoint(vault_file, PASSWORD, "v1")

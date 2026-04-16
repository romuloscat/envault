"""Tests for envault.snapshot."""

import json
import pytest
from pathlib import Path

from envault.store import set_secret, get_secret
from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    SnapshotError,
)

PASSWORD = "snap-pass"


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_create_snapshot_returns_path(vault_file):
    set_secret(vault_file, "K", "V", PASSWORD)
    snap = create_snapshot(vault_file, label="v1")
    assert snap.exists()
    assert "v1" in snap.name


def test_snapshot_contains_encrypted_data(vault_file):
    set_secret(vault_file, "KEY", "VALUE", PASSWORD)
    snap = create_snapshot(vault_file)
    meta = json.loads(snap.read_text())
    assert "KEY" in meta["data"]
    # value should be encrypted, not plaintext
    assert meta["data"]["KEY"] != "VALUE"


def test_list_snapshots_empty_when_none(vault_file):
    set_secret(vault_file, "A", "B", PASSWORD)
    assert list_snapshots(vault_file) == []


def test_list_snapshots_returns_metadata(vault_file):
    set_secret(vault_file, "A", "B", PASSWORD)
    create_snapshot(vault_file, label="first")
    create_snapshot(vault_file, label="second")
    snaps = list_snapshots(vault_file)
    assert len(snaps) == 2
    labels = [s["label"] for s in snaps]
    assert "first" in labels and "second" in labels


def test_restore_snapshot_recovers_keys(vault_file):
    set_secret(vault_file, "FOO", "bar", PASSWORD)
    snap = create_snapshot(vault_file)
    # overwrite with new data
    set_secret(vault_file, "FOO", "changed", PASSWORD)
    assert get_secret(vault_file, "FOO", PASSWORD) == "changed"
    # restore
    n = restore_snapshot(vault_file, snap.name)
    assert n == 1
    assert get_secret(vault_file, "FOO", PASSWORD) == "bar"


def test_restore_missing_snapshot_raises(vault_file):
    set_secret(vault_file, "X", "Y", PASSWORD)
    with pytest.raises(SnapshotError):
        restore_snapshot(vault_file, "nonexistent.json")


def test_delete_snapshot_removes_file(vault_file):
    set_secret(vault_file, "A", "B", PASSWORD)
    snap = create_snapshot(vault_file)
    delete_snapshot(vault_file, snap.name)
    assert not snap.exists()


def test_delete_missing_snapshot_raises(vault_file):
    set_secret(vault_file, "A", "B", PASSWORD)
    with pytest.raises(SnapshotError):
        delete_snapshot(vault_file, "ghost.json")

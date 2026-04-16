"""Tests for envault.diff module."""
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.diff import _compute_diff, diff_snapshot_vs_live, diff_snapshots, DiffError


# --- unit tests for _compute_diff ---

def test_compute_diff_added():
    result = _compute_diff({}, {"KEY": "val"})
    assert result == [{"key": "KEY", "status": "added", "old": None, "new": "val"}]


def test_compute_diff_removed():
    result = _compute_diff({"KEY": "val"}, {})
    assert result == [{"key": "KEY", "status": "removed", "old": "val", "new": None}]


def test_compute_diff_changed():
    result = _compute_diff({"KEY": "old"}, {"KEY": "new"})
    assert result == [{"key": "KEY", "status": "changed", "old": "old", "new": "new"}]


def test_compute_diff_no_changes():
    result = _compute_diff({"KEY": "same"}, {"KEY": "same"})
    assert result == []


def test_compute_diff_sorted_keys():
    result = _compute_diff({"B": "1"}, {"A": "2"})
    keys = [r["key"] for r in result]
    assert keys == sorted(keys)


# --- integration-style tests using mocks ---

def test_diff_snapshots_delegates(tmp_path):
    snap_a = tmp_path / "a.snap"
    snap_b = tmp_path / "b.snap"
    snap_a.write_text("x")
    snap_b.write_text("x")
    with patch("envault.diff.restore_snapshot") as mock_restore:
        mock_restore.side_effect = [{"FOO": "bar"}, {"FOO": "baz"}]
        changes = diff_snapshots(snap_a, snap_b, "pw")
    assert len(changes) == 1
    assert changes[0]["status"] == "changed"


def test_diff_snapshot_vs_live(tmp_path):
    snap = tmp_path / "snap"
    snap.write_text("x")
    vault = tmp_path / "vault"
    with patch("envault.diff.restore_snapshot", return_value={"A": "1", "B": "2"}), \
         patch("envault.diff.list_secrets", return_value=["A", "C"]), \
         patch("envault.diff.get_secret", side_effect=lambda v, k, p: {"A": "1", "C": "3"}[k]):
        changes = diff_snapshot_vs_live(snap, vault, "pw")
    keys_status = {c["key"]: c["status"] for c in changes}
    assert keys_status["B"] == "removed"
    assert keys_status["C"] == "added"
    assert "A" not in keys_status


def test_diff_raises_diff_error_on_bad_snapshot(tmp_path):
    snap = tmp_path / "snap"
    snap.write_text("x")
    from envault.snapshot import SnapshotError
    with patch("envault.diff.restore_snapshot", side_effect=SnapshotError("bad")):
        with pytest.raises(DiffError):
            diff_snapshots(snap, snap, "pw")

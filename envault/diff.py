"""Diff two snapshots or a snapshot against the live vault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from envault.snapshot import restore_snapshot, SnapshotError
from envault.store import list_secrets, get_secret


class DiffError(Exception):
    pass


def _decrypt_snapshot(snapshot_path: Path, password: str) -> Dict[str, str]:
    """Return plaintext key/value pairs from a snapshot file."""
    try:
        return restore_snapshot(snapshot_path, password)
    except SnapshotError as e:
        raise DiffError(str(e)) from e


def diff_snapshots(
    path_a: Path,
    path_b: Path,
    password: str,
) -> List[dict]:
    """Compare two snapshot files and return a list of change records."""
    secrets_a = _decrypt_snapshot(path_a, password)
    secrets_b = _decrypt_snapshot(path_b, password)
    return _compute_diff(secrets_a, secrets_b)


def diff_snapshot_vs_live(
    snapshot_path: Path,
    vault_file: Path,
    password: str,
) -> List[dict]:
    """Compare a snapshot against the current live vault."""
    secrets_snap = _decrypt_snapshot(snapshot_path, password)
    keys = list_secrets(vault_file)
    secrets_live = {k: get_secret(vault_file, k, password) for k in keys}
    return _compute_diff(secrets_snap, secrets_live)


def _compute_diff(a: Dict[str, str], b: Dict[str, str]) -> List[dict]:
    changes = []
    all_keys = set(a) | set(b)
    for key in sorted(all_keys):
        if key not in a:
            changes.append({"key": key, "status": "added", "old": None, "new": b[key]})
        elif key not in b:
            changes.append({"key": key, "status": "removed", "old": a[key], "new": None})
        elif a[key] != b[key]:
            changes.append({"key": key, "status": "changed", "old": a[key], "new": b[key]})
    return changes

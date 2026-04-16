"""Snapshot: create and restore point-in-time backups of a vault."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Dict

from envault.store import _load_raw, _save_raw


class SnapshotError(Exception):
    pass


def _snapshot_dir(vault_path: Path) -> Path:
    d = vault_path.parent / ".envault_snapshots"
    d.mkdir(exist_ok=True)
    return d


def create_snapshot(vault_path: Path, label: str = "") -> Path:
    """Save a snapshot of the current encrypted vault state."""
    raw = _load_raw(vault_path)  # dict of key -> encrypted value
    ts = int(time.time())
    name = f"{ts}_{label}.json" if label else f"{ts}.json"
    snap_path = _snapshot_dir(vault_path) / name
    snap_path.write_text(json.dumps({"ts": ts, "label": label, "data": raw}, indent=2))
    return snap_path


def list_snapshots(vault_path: Path) -> List[Dict]:
    """Return snapshot metadata sorted newest-first."""
    d = _snapshot_dir(vault_path)
    snaps = []
    for f in sorted(d.glob("*.json"), reverse=True):
        try:
            meta = json.loads(f.read_text())
            snaps.append({"file": f.name, "ts": meta["ts"], "label": meta.get("label", "")})
        except (json.JSONDecodeError, KeyError):
            pass
    return snaps


def restore_snapshot(vault_path: Path, snapshot_name: str) -> int:
    """Restore vault from a snapshot file. Returns number of keys restored."""
    snap_path = _snapshot_dir(vault_path) / snapshot_name
    if not snap_path.exists():
        raise SnapshotError(f"Snapshot not found: {snapshot_name}")
    meta = json.loads(snap_path.read_text())
    data: dict = meta.get("data", {})
    _save_raw(vault_path, data)
    return len(data)


def delete_snapshot(vault_path: Path, snapshot_name: str) -> None:
    """Delete a named snapshot."""
    snap_path = _snapshot_dir(vault_path) / snapshot_name
    if not snap_path.exists():
        raise SnapshotError(f"Snapshot not found: {snapshot_name}")
    snap_path.unlink()

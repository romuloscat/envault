"""Checkpoint module: named, annotated vault snapshots with metadata."""

import json
import time
from pathlib import Path
from typing import Optional

from envault.snapshot import create_snapshot, restore_snapshot, SnapshotError


class CheckpointError(Exception):
    pass


def _checkpoint_path(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_checkpoints.json"


def _load_checkpoints(vault_path: Path) -> dict:
    p = _checkpoint_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_checkpoints(vault_path: Path, data: dict) -> None:
    _checkpoint_path(vault_path).write_text(json.dumps(data, indent=2))


def create_checkpoint(
    vault_path: Path, password: str, name: str, description: str = ""
) -> Path:
    """Create a named checkpoint backed by a snapshot."""
    checkpoints = _load_checkpoints(vault_path)
    if name in checkpoints:
        raise CheckpointError(f"Checkpoint '{name}' already exists.")
    snap_path = create_snapshot(vault_path, password)
    checkpoints[name] = {
        "snapshot": str(snap_path),
        "description": description,
        "created_at": time.time(),
    }
    _save_checkpoints(vault_path, checkpoints)
    return snap_path


def list_checkpoints(vault_path: Path) -> list:
    """Return sorted list of checkpoint metadata dicts."""
    checkpoints = _load_checkpoints(vault_path)
    result = []
    for name, meta in checkpoints.items():
        result.append({"name": name, **meta})
    return sorted(result, key=lambda x: x["created_at"])


def restore_checkpoint(vault_path: Path, password: str, name: str) -> int:
    """Restore vault from a named checkpoint. Returns number of keys restored."""
    checkpoints = _load_checkpoints(vault_path)
    if name not in checkpoints:
        raise CheckpointError(f"Checkpoint '{name}' not found.")
    snap_path = Path(checkpoints[name]["snapshot"])
    if not snap_path.exists():
        raise CheckpointError(f"Snapshot file missing for checkpoint '{name}'.")
    return restore_snapshot(vault_path, password, snap_path)


def delete_checkpoint(vault_path: Path, name: str) -> None:
    """Remove a named checkpoint (does not delete the underlying snapshot file)."""
    checkpoints = _load_checkpoints(vault_path)
    if name not in checkpoints:
        raise CheckpointError(f"Checkpoint '{name}' not found.")
    del checkpoints[name]
    _save_checkpoints(vault_path, checkpoints)

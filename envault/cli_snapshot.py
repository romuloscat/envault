"""CLI commands for vault snapshot management."""

from __future__ import annotations

import click
from pathlib import Path

from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    SnapshotError,
)


@click.group("snapshot")
def snapshot_cmd():
    """Create and restore vault snapshots."""


@snapshot_cmd.command("create")
@click.option("--vault", default="vault.json", show_default=True)
@click.option("--label", default="", help="Optional label for the snapshot.")
def snap_create(vault, label):
    """Create a snapshot of the current vault."""
    path = Path(vault)
    try:
        snap = create_snapshot(path, label=label)
        click.echo(f"Snapshot created: {snap.name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("list")
@click.option("--vault", default="vault.json", show_default=True)
def snap_list(vault):
    """List available snapshots."""
    snaps = list_snapshots(Path(vault))
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f"  [{s['label']}]" if s["label"] else ""
        click.echo(f"{s['file']}{label}")


@snapshot_cmd.command("restore")
@click.argument("name")
@click.option("--vault", default="vault.json", show_default=True)
def snap_restore(name, vault):
    """Restore vault from snapshot NAME."""
    try:
        n = restore_snapshot(Path(vault), name)
        click.echo(f"Restored {n} key(s) from {name}.")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("delete")
@click.argument("name")
@click.option("--vault", default="vault.json", show_default=True)
def snap_delete(name, vault):
    """Delete snapshot NAME."""
    try:
        delete_snapshot(Path(vault), name)
        click.echo(f"Deleted snapshot: {name}")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

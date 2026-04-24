"""CLI commands for checkpoint management."""

import click
from pathlib import Path
from datetime import datetime

from envault.checkpoint import (
    CheckpointError,
    create_checkpoint,
    list_checkpoints,
    restore_checkpoint,
    delete_checkpoint,
)


@click.group("checkpoint")
def checkpoint_cmd():
    """Manage named vault checkpoints."""


@checkpoint_cmd.command("create")
@click.argument("name")
@click.option("--vault", required=True, type=click.Path(), help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--description", default="", help="Optional description.")
def cp_create(name, vault, password, description):
    """Create a named checkpoint."""
    try:
        path = create_checkpoint(Path(vault), password, name, description)
        click.echo(f"Checkpoint '{name}' created: {path}")
    except CheckpointError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@checkpoint_cmd.command("list")
@click.option("--vault", required=True, type=click.Path(), help="Path to vault file.")
def cp_list(vault):
    """List all checkpoints."""
    checkpoints = list_checkpoints(Path(vault))
    if not checkpoints:
        click.echo("No checkpoints found.")
        return
    for cp in checkpoints:
        ts = datetime.fromtimestamp(cp["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
        desc = f" — {cp['description']}" if cp["description"] else ""
        click.echo(f"  {cp['name']:20s} {ts}{desc}")


@checkpoint_cmd.command("restore")
@click.argument("name")
@click.option("--vault", required=True, type=click.Path(), help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
def cp_restore(name, vault, password):
    """Restore vault from a named checkpoint."""
    try:
        count = restore_checkpoint(Path(vault), password, name)
        click.echo(f"Restored {count} key(s) from checkpoint '{name}'.")
    except CheckpointError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@checkpoint_cmd.command("delete")
@click.argument("name")
@click.option("--vault", required=True, type=click.Path(), help="Path to vault file.")
def cp_delete(name, vault):
    """Delete a named checkpoint."""
    try:
        delete_checkpoint(Path(vault), name)
        click.echo(f"Checkpoint '{name}' deleted.")
    except CheckpointError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

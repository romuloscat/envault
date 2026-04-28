"""CLI commands for secret priority management."""

from __future__ import annotations

import click

from envault.priority import (
    DEFAULT_PRIORITY,
    PriorityError,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)
from envault.store import list_secrets


@click.group("priority", help="Manage secret priority levels.")
def priority_cmd() -> None:
    pass


@priority_cmd.command("set")
@click.option("--vault", required=True, help="Path to vault file.")
@click.argument("key")
@click.argument("level", type=int)
def priority_set(vault: str, key: str, level: int) -> None:
    """Set the PRIORITY LEVEL (1-100) for KEY."""
    try:
        set_priority(vault, key, level)
        click.echo(f"Priority for '{key}' set to {level}.")
    except PriorityError as exc:
        raise click.ClickException(str(exc))


@priority_cmd.command("get")
@click.option("--vault", required=True, help="Path to vault file.")
@click.argument("key")
def priority_get(vault: str, key: str) -> None:
    """Show the priority level for KEY."""
    level = get_priority(vault, key)
    suffix = " (default)" if level == DEFAULT_PRIORITY else ""
    click.echo(f"{key}: {level}{suffix}")


@priority_cmd.command("remove")
@click.option("--vault", required=True, help="Path to vault file.")
@click.argument("key")
def priority_remove(vault: str, key: str) -> None:
    """Remove the explicit priority for KEY (reverts to default)."""
    try:
        remove_priority(vault, key)
        click.echo(f"Priority for '{key}' removed.")
    except PriorityError as exc:
        raise click.ClickException(str(exc))


@priority_cmd.command("list")
@click.option("--vault", required=True, help="Path to vault file.")
@click.option("--password", default=None, help="Vault password (to list all keys).")
def priority_list(vault: str, password: str | None) -> None:
    """List all keys sorted by priority (highest first)."""
    if password:
        keys = list_secrets(vault, password)
    else:
        keys = None
    pairs = list_by_priority(vault, keys)
    if not pairs:
        click.echo("No priority entries found.")
        return
    for key, level in pairs:
        suffix = " (default)" if level == DEFAULT_PRIORITY else ""
        click.echo(f"{key}: {level}{suffix}")

"""CLI commands for managing secret groups."""
import click
from pathlib import Path
from envault.group import (
    add_to_group, remove_from_group, list_groups,
    get_group_members, delete_group, GroupError
)


@click.group("group")
def group_cmd():
    """Organise secrets into named groups."""


@group_cmd.command("add")
@click.argument("group")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def group_add(group, key, vault):
    """Add KEY to GROUP."""
    try:
        add_to_group(Path(vault), group, key)
        click.echo(f"Added '{key}' to group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("remove")
@click.argument("group")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def group_remove(group, key, vault):
    """Remove KEY from GROUP."""
    try:
        remove_from_group(Path(vault), group, key)
        click.echo(f"Removed '{key}' from group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("list")
@click.option("--vault", default="vault.enc", show_default=True)
def group_list(vault):
    """List all groups."""
    groups = list_groups(Path(vault))
    if not groups:
        click.echo("No groups defined.")
    for g in groups:
        click.echo(g)


@group_cmd.command("show")
@click.argument("group")
@click.option("--vault", default="vault.enc", show_default=True)
def group_show(group, vault):
    """Show members of GROUP."""
    try:
        members = get_group_members(Path(vault), group)
        if not members:
            click.echo(f"Group '{group}' is empty.")
        for m in members:
            click.echo(m)
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("delete")
@click.argument("group")
@click.option("--vault", default="vault.enc", show_default=True)
def group_delete(group, vault):
    """Delete an entire GROUP."""
    try:
        delete_group(Path(vault), group)
        click.echo(f"Deleted group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

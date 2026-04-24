"""CLI commands for vault inheritance."""

from __future__ import annotations

from pathlib import Path

import click

from envault.inherit import (
    InheritError,
    get_parent,
    remove_parent,
    resolve_secret,
    set_parent,
)


@click.group("inherit", help="Manage vault inheritance (parent/child overlays).")
def inherit_cmd() -> None:  # pragma: no cover
    pass


@inherit_cmd.command("set-parent")
@click.option("--vault", required=True, type=click.Path(), help="Child vault file.")
@click.option("--parent", required=True, type=click.Path(), help="Parent vault file.")
def inherit_set_parent(vault: str, parent: str) -> None:
    """Set the parent vault for a child vault."""
    try:
        set_parent(Path(vault), Path(parent))
        click.echo(f"Parent vault set to '{parent}' for '{vault}'.")
    except InheritError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@inherit_cmd.command("get-parent")
@click.option("--vault", required=True, type=click.Path(), help="Child vault file.")
def inherit_get_parent(vault: str) -> None:
    """Show the registered parent vault."""
    parent = get_parent(Path(vault))
    if parent is None:
        click.echo("No parent vault set.")
    else:
        click.echo(str(parent))


@inherit_cmd.command("remove-parent")
@click.option("--vault", required=True, type=click.Path(), help="Child vault file.")
def inherit_remove_parent(vault: str) -> None:
    """Remove the parent vault association."""
    try:
        remove_parent(Path(vault))
        click.echo("Parent vault removed.")
    except InheritError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@inherit_cmd.command("resolve")
@click.option("--vault", required=True, type=click.Path(), help="Child vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", help="Vault password.")
@click.argument("key")
def inherit_resolve(vault: str, password: str, key: str) -> None:
    """Resolve a secret key, falling back to parent vaults."""
    try:
        value = resolve_secret(key, Path(vault), password)
        click.echo(value)
    except InheritError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

"""CLI commands for managing vault cascade (fallback) chains."""

from __future__ import annotations

import click
from pathlib import Path

from envault.cascade import (
    CascadeError,
    set_cascade,
    get_cascade,
    clear_cascade,
    resolve_key,
    cascade_all_keys,
)


@click.group("cascade")
def cascade_cmd():
    """Manage vault fallback chains."""


@cascade_cmd.command("set")
@click.option("--vault", required=True, type=click.Path(), help="Primary vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.argument("fallbacks", nargs=-1, required=True)
def cascade_set(vault, password, fallbacks):
    """Set the fallback chain for VAULT.

    FALLBACKS are one or more vault file paths, checked in order.
    """
    try:
        set_cascade(Path(vault), list(fallbacks))
        click.echo(f"Cascade set: {' -> '.join([vault] + list(fallbacks))}")
    except CascadeError as exc:
        raise click.ClickException(str(exc))


@cascade_cmd.command("show")
@click.option("--vault", required=True, type=click.Path(), help="Primary vault file.")
def cascade_show(vault):
    """Show the configured fallback chain for VAULT."""
    chain = get_cascade(Path(vault))
    if not chain:
        click.echo("No cascade configured.")
        return
    click.echo(f"{vault}")
    for entry in chain:
        click.echo(f"  -> {entry}")


@cascade_cmd.command("clear")
@click.option("--vault", required=True, type=click.Path(), help="Primary vault file.")
def cascade_clear(vault):
    """Remove the cascade configuration for VAULT."""
    clear_cascade(Path(vault))
    click.echo("Cascade cleared.")


@cascade_cmd.command("resolve")
@click.option("--vault", required=True, type=click.Path(), help="Primary vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.argument("key")
def cascade_resolve(vault, password, key):
    """Resolve KEY by walking the cascade chain."""
    value = resolve_key(key, password, Path(vault))
    if value is None:
        raise click.ClickException(f"Key '{key}' not found in cascade chain.")
    click.echo(value)


@cascade_cmd.command("dump")
@click.option("--vault", required=True, type=click.Path(), help="Primary vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def cascade_dump(vault, password):
    """Dump all resolved key=value pairs from the full cascade."""
    merged = cascade_all_keys(password, Path(vault))
    if not merged:
        click.echo("No secrets found in cascade.")
        return
    for key, value in sorted(merged.items()):
        click.echo(f"{key}={value}")

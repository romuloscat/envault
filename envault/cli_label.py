"""CLI commands for managing secret labels."""

from __future__ import annotations

import click
from pathlib import Path
from envault.label import set_label, remove_label, get_labels, find_by_label, LabelError


@click.group("label")
def label_cmd():
    """Manage labels on secrets."""


@label_cmd.command("set")
@click.argument("key")
@click.argument("label")
@click.argument("value")
@click.option("--vault", default="vault.json", show_default=True)
def label_set(key, label, value, vault):
    """Attach LABEL=VALUE to KEY."""
    set_label(Path(vault), key, label, value)
    click.echo(f"Label '{label}={value}' set on '{key}'.")


@label_cmd.command("remove")
@click.argument("key")
@click.argument("label")
@click.option("--vault", default="vault.json", show_default=True)
def label_remove(key, label, vault):
    """Remove LABEL from KEY."""
    try:
        remove_label(Path(vault), key, label)
        click.echo(f"Label '{label}' removed from '{key}'.")
    except LabelError as e:
        raise click.ClickException(str(e))


@label_cmd.command("list")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def label_list(key, vault):
    """List all labels for KEY."""
    labels = get_labels(Path(vault), key)
    if not labels:
        click.echo(f"No labels for '{key}'.")
        return
    for k, v in sorted(labels.items()):
        click.echo(f"  {k}={v}")


@label_cmd.command("find")
@click.argument("label")
@click.option("--value", default=None, help="Filter by label value.")
@click.option("--vault", default="vault.json", show_default=True)
def label_find(label, value, vault):
    """Find keys that have LABEL (optionally matching VALUE)."""
    keys = find_by_label(Path(vault), label, value)
    if not keys:
        click.echo("No matching keys.")
        return
    for k in keys:
        click.echo(k)

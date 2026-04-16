"""CLI commands for diffing snapshots."""
import click
from pathlib import Path

from envault.diff import diff_snapshots, diff_snapshot_vs_live, DiffError


@click.group("diff")
def diff_cmd():
    """Diff snapshots or compare a snapshot to the live vault."""


@diff_cmd.command("snapshots")
@click.argument("snapshot_a", type=click.Path(exists=True))
@click.argument("snapshot_b", type=click.Path(exists=True))
@click.option("--password", "-p", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def diff_two(snapshot_a, snapshot_b, password):
    """Compare two snapshot files."""
    try:
        changes = diff_snapshots(Path(snapshot_a), Path(snapshot_b), password)
    except DiffError as e:
        raise click.ClickException(str(e))
    if not changes:
        click.echo("No differences found.")
        return
    for c in changes:
        _print_change(c)


@diff_cmd.command("live")
@click.argument("snapshot", type=click.Path(exists=True))
@click.option("--vault", "-v", default=".envault", show_default=True)
@click.option("--password", "-p", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def diff_live(snapshot, vault, password):
    """Compare a snapshot to the live vault."""
    try:
        changes = diff_snapshot_vs_live(Path(snapshot), Path(vault), password)
    except DiffError as e:
        raise click.ClickException(str(e))
    if not changes:
        click.echo("No differences found.")
        return
    for c in changes:
        _print_change(c)


def _print_change(c: dict):
    status = c["status"]
    key = c["key"]
    if status == "added":
        click.echo(click.style(f"+ {key} = {c['new']}", fg="green"))
    elif status == "removed":
        click.echo(click.style(f"- {key} = {c['old']}", fg="red"))
    else:
        click.echo(click.style(f"~ {key}: {c['old']} -> {c['new']}", fg="yellow"))

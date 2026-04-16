"""CLI entry point for envault."""

import click

from envault.store import set_secret, get_secret, delete_secret, list_secrets
from envault.export import export_secrets, SUPPORTED_FORMATS


@click.group()
def cli() -> None:
    """envault — encrypted environment variable manager."""


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--vault", default=".envault", show_default=True)
def set_cmd(key: str, value: str, password: str, vault: str) -> None:
    """Set a secret KEY to VALUE."""
    set_secret(vault, password, key, value)
    click.echo(f"Set {key}")


@cli.command("get")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", default=".envault", show_default=True)
def get_cmd(key: str, password: str, vault: str) -> None:
    """Get the value of a secret KEY."""
    try:
        click.echo(get_secret(vault, password, key))
    except KeyError:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)


@cli.command("delete")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", default=".envault", show_default=True)
def delete_cmd(key: str, password: str, vault: str) -> None:
    """Delete a secret KEY."""
    try:
        delete_secret(vault, password, key)
        click.echo(f"Deleted {key}")
    except KeyError:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)


@cli.command("list")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", default=".envault", show_default=True)
def list_cmd(password: str, vault: str) -> None:
    """List all secret keys."""
    keys = list_secrets(vault, password)
    for k in sorted(keys):
        click.echo(k)


@cli.command("export")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", default=".envault", show_default=True)
@click.option(
    "--format", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format",
)
def export_cmd(password: str, vault: str, fmt: str) -> None:
    """Export all secrets to stdout in the chosen format."""
    keys = list_secrets(vault, password)
    secrets = {k: get_secret(vault, password, k) for k in keys}
    click.echo(export_secrets(secrets, fmt=fmt))

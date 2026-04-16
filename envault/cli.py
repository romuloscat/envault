"""CLI entry-point for envault."""

import click
from envault.store import set_secret, get_secret, delete_secret, list_secrets
from envault.export import export_secrets
from envault.importenv import import_secrets

DEFAULT_VAULT = ".envault"


@click.group()
def cli():
    """envault — encrypted environment variable manager."""


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def set_cmd(key, value, vault, password):
    """Store a secret KEY=VALUE in the vault."""
    set_secret(vault, password, key, value)
    click.echo(f"Stored '{key}'.")


@cli.command("get")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def get_cmd(key, vault, password):
    """Retrieve a secret by KEY."""
    value = get_secret(vault, password, key)
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def delete_cmd(key, vault, password):
    """Delete a secret by KEY."""
    delete_secret(vault, password, key)
    click.echo(f"Deleted '{key}'.")


@cli.command("list")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def list_cmd(vault, password):
    """List all secret keys in the vault."""
    keys = list_secrets(vault, password)
    for k in keys:
        click.echo(k)


@cli.command("export")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--format", "fmt", default="dotenv", type=click.Choice(["dotenv", "bash", "json"]), show_default=True)
def export_cmd(vault, password, fmt):
    """Export all secrets in the chosen format."""
    output = export_secrets(vault, password, fmt)
    click.echo(output)


@cli.command("import")
@click.argument("source", type=click.Path(exists=True))
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--format", "fmt", default="dotenv", type=click.Choice(["dotenv", "json"]), show_default=True)
def import_cmd(source, vault, password, fmt):
    """Import secrets from a .env or JSON file into the vault."""
    count = import_secrets(source, fmt, vault, password)
    click.echo(f"Imported {count} secret(s) from '{source}'.")


if __name__ == "__main__":
    cli()

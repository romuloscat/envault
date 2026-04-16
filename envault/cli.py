"""CLI entry point for envault."""

import sys
import click
from envault.store import set_secret, get_secret, delete_secret, list_keys


@click.group()
def cli():
    """envault — manage and encrypt environment variables."""
    pass


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
@click.password_option("--password", prompt="Master password", help="Master password.")
def set_cmd(key, value, vault, password):
    """Set a secret KEY to VALUE in the vault."""
    set_secret(vault, password, key, value)
    click.echo(f"✓ Set '{key}' in {vault}")


@cli.command("get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
@click.password_option("--password", prompt="Master password", confirmation_prompt=False, help="Master password.")
def get_cmd(key, vault, password):
    """Get the decrypted value of KEY from the vault."""
    try:
        value = get_secret(vault, password, key)
        click.echo(value)
    except KeyError:
        click.echo(f"Error: key '{key}' not found.", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
@click.password_option("--password", prompt="Master password", confirmation_prompt=False, help="Master password.")
def delete_cmd(key, vault, password):
    """Delete KEY from the vault."""
    try:
        delete_secret(vault, password, key)
        click.echo(f"✓ Deleted '{key}' from {vault}")
    except KeyError:
        click.echo(f"Error: key '{key}' not found.", err=True)
        sys.exit(1)


@cli.command("list")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
def list_cmd(vault):
    """List all key names stored in the vault."""
    keys = list_keys(vault)
    if not keys:
        click.echo("(empty vault)")
    else:
        for k in sorted(keys):
            click.echo(k)


if __name__ == "__main__":
    cli()

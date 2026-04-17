"""CLI commands for TTL management in envault."""

import click
from pathlib import Path
from envault.ttl import set_ttl, get_expiry, clear_ttl, purge_expired, TTLError
from envault.store import list_secrets
import time


@click.group("ttl")
def ttl_cmd():
    """Manage secret expiry (TTL)."""


@ttl_cmd.command("set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--vault", default="vault.env", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ttl_set(key, seconds, vault, password):
    """Set TTL for KEY (in seconds)."""
    vault_file = Path(vault)
    try:
        list_secrets(vault_file, password)  # validates password + key exists
    except Exception as e:
        raise click.ClickException(str(e))
    try:
        set_ttl(vault_file, key, seconds)
        click.echo(f"TTL set: '{key}' expires in {seconds}s.")
    except TTLError as e:
        raise click.ClickException(str(e))


@ttl_cmd.command("get")
@click.argument("key")
@click.option("--vault", default="vault.env", show_default=True)
def ttl_get(key, vault):
    """Show expiry timestamp for KEY."""
    vault_file = Path(vault)
    expiry = get_expiry(vault_file, key)
    if expiry is None:
        click.echo(f"No TTL set for '{key}'.")
    else:
        remaining = max(0, expiry - time.time())
        click.echo(f"'{key}' expires at {expiry:.0f} ({remaining:.0f}s remaining).")


@ttl_cmd.command("clear")
@click.argument("key")
@click.option("--vault", default="vault.env", show_default=True)
def ttl_clear(key, vault):
    """Remove TTL for KEY."""
    vault_file = Path(vault)
    clear_ttl(vault_file, key)
    click.echo(f"TTL cleared for '{key}'.")


@ttl_cmd.command("purge")
@click.option("--vault", default="vault.env", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ttl_purge(vault, password):
    """List and remove expired secrets from the vault."""
    from envault.store import delete_secret
    vault_file = Path(vault)
    expired = purge_expired(vault_file)
    if not expired:
        click.echo("No expired secrets found.")
        return
    for key in expired:
        delete_secret(vault_file, password, key)
        clear_ttl(vault_file, key)
        click.echo(f"Purged expired secret: '{key}'.")

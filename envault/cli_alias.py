"""CLI commands for managing key aliases."""
import click
from envault.alias import (
    set_alias, remove_alias, resolve_alias,
    list_aliases, aliases_for_key, AliasError,
)


@click.group("alias")
def alias_cmd():
    """Manage key aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def alias_set(alias, key, vault):
    """Create or update ALIAS pointing to KEY."""
    try:
        set_alias(vault, alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' set.")
    except AliasError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_cmd.command("remove")
@click.argument("alias")
@click.option("--vault", default="vault.json", show_default=True)
def alias_remove(alias, vault):
    """Remove an alias."""
    try:
        remove_alias(vault, alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_cmd.command("resolve")
@click.argument("alias")
@click.option("--vault", default="vault.json", show_default=True)
def alias_resolve(alias, vault):
    """Print the key that ALIAS resolves to."""
    click.echo(resolve_alias(vault, alias))


@alias_cmd.command("list")
@click.option("--vault", default="vault.json", show_default=True)
def alias_list(vault):
    """List all aliases."""
    data = list_aliases(vault)
    if not data:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(data.items()):
        click.echo(f"{alias} -> {key}")


@alias_cmd.command("find")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def alias_find(key, vault):
    """Find all aliases pointing to KEY."""
    results = aliases_for_key(vault, key)
    if not results:
        click.echo(f"No aliases for '{key}'.")
        return
    for a in sorted(results):
        click.echo(a)

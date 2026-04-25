"""CLI commands for secret reference management."""
import click

from .ref import (
    CircularRefError,
    RefError,
    get_ref,
    list_refs,
    remove_ref,
    resolve_ref,
    set_ref,
)


@click.group("ref", help="Manage secret references (aliases that point to other keys).")
def ref_cmd() -> None:  # pragma: no cover
    pass


@ref_cmd.command("set")
@click.argument("key")
@click.argument("target")
@click.option("--vault", default="vault.enc", show_default=True, help="Vault file path.")
def ref_set(key: str, target: str, vault: str) -> None:
    """Make KEY a reference to TARGET."""
    try:
        set_ref(vault, key, target)
        click.echo(f"Reference set: {key} -> {target}")
    except RefError as exc:
        raise click.ClickException(str(exc)) from exc


@ref_cmd.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True, help="Vault file path.")
def ref_remove(key: str, vault: str) -> None:
    """Remove the reference defined for KEY."""
    try:
        remove_ref(vault, key)
        click.echo(f"Reference for '{key}' removed.")
    except RefError as exc:
        raise click.ClickException(str(exc)) from exc


@ref_cmd.command("show")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True, help="Vault file path.")
def ref_show(key: str, vault: str) -> None:
    """Show the direct reference target for KEY."""
    target = get_ref(vault, key)
    if target is None:
        click.echo(f"'{key}' has no reference defined.")
    else:
        click.echo(f"{key} -> {target}")


@ref_cmd.command("resolve")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True, help="Vault file path.")
def ref_resolve(key: str, vault: str) -> None:
    """Follow the reference chain for KEY and print the terminal key."""
    try:
        terminal = resolve_ref(vault, key)
        click.echo(terminal)
    except (RefError, CircularRefError) as exc:
        raise click.ClickException(str(exc)) from exc


@ref_cmd.command("list")
@click.option("--vault", default="vault.enc", show_default=True, help="Vault file path.")
def ref_list(vault: str) -> None:
    """List all defined references."""
    refs = list_refs(vault)
    if not refs:
        click.echo("No references defined.")
        return
    for key, target in sorted(refs.items()):
        click.echo(f"{key} -> {target}")

"""CLI commands for profile management."""
import click
from pathlib import Path
from envault.profile import (
    add_key_to_profile, remove_key_from_profile, list_profiles,
    get_profile_keys, delete_profile, export_profile, ProfileError
)

@click.group("profile")
def profile_cmd():
    """Manage named profiles (groups of secrets)."""

@profile_cmd.command("add")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def profile_add(profile, key, vault):
    """Add KEY to PROFILE."""
    try:
        add_key_to_profile(Path(vault), profile, key)
        click.echo(f"Added '{key}' to profile '{profile}'.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

@profile_cmd.command("remove")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def profile_remove(profile, key, vault):
    """Remove KEY from PROFILE."""
    try:
        remove_key_from_profile(Path(vault), profile, key)
        click.echo(f"Removed '{key}' from profile '{profile}'.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

@profile_cmd.command("list")
@click.option("--vault", default="vault.json", show_default=True)
def profile_list(vault):
    """List all profiles."""
    profiles = list_profiles(Path(vault))
    if not profiles:
        click.echo("No profiles defined.")
    for p in profiles:
        click.echo(p)

@profile_cmd.command("show")
@click.argument("profile")
@click.option("--vault", default="vault.json", show_default=True)
def profile_show(profile, vault):
    """Show keys in PROFILE."""
    try:
        keys = get_profile_keys(Path(vault), profile)
        for k in keys:
            click.echo(k)
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

@profile_cmd.command("delete")
@click.argument("profile")
@click.option("--vault", default="vault.json", show_default=True)
def profile_delete(profile, vault):
    """Delete PROFILE entirely."""
    try:
        delete_profile(Path(vault), profile)
        click.echo(f"Deleted profile '{profile}'.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

@profile_cmd.command("export")
@click.argument("profile")
@click.password_option(prompt="Vault password")
@click.option("--vault", default="vault.json", show_default=True)
def profile_export(profile, password, vault):
    """Export all secrets in PROFILE as KEY=VALUE lines."""
    try:
        secrets = export_profile(Path(vault), profile, password)
        for k, v in secrets.items():
            click.echo(f"{k}={v}")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

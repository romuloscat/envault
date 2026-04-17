"""CLI commands for access control profiles."""
import click
from pathlib import Path
from envault.access import (
    grant, revoke, allowed_keys, list_profiles,
    delete_profile, AccessError
)


@click.group("access")
def access_cmd():
    """Manage per-profile key access control."""


@access_cmd.command("grant")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def access_grant(profile, key, vault):
    """Grant PROFILE access to KEY."""
    try:
        grant(Path(vault), profile, key)
        click.echo(f"Granted '{profile}' access to '{key}'.")
    except Exception as e:
        raise click.ClickException(str(e))


@access_cmd.command("revoke")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def access_revoke(profile, key, vault):
    """Revoke PROFILE access to KEY."""
    try:
        revoke(Path(vault), profile, key)
        click.echo(f"Revoked '{profile}' access to '{key}'.")
    except AccessError as e:
        raise click.ClickException(str(e))


@access_cmd.command("list")
@click.argument("profile")
@click.option("--vault", default="vault.json", show_default=True)
def access_list(profile, vault):
    """List keys accessible to PROFILE."""
    keys = allowed_keys(Path(vault), profile)
    if not keys:
        click.echo(f"No keys granted to '{profile}'.")
    else:
        for k in sorted(keys):
            click.echo(k)


@access_cmd.command("profiles")
@click.option("--vault", default="vault.json", show_default=True)
def access_profiles(vault):
    """List all profiles."""
    profiles = list_profiles(Path(vault))
    if not profiles:
        click.echo("No profiles defined.")
    else:
        for p in sorted(profiles):
            click.echo(p)


@access_cmd.command("delete-profile")
@click.argument("profile")
@click.option("--vault", default="vault.json", show_default=True)
def access_delete_profile(profile, vault):
    """Delete PROFILE and all its grants."""
    try:
        delete_profile(Path(vault), profile)
        click.echo(f"Deleted profile '{profile}'.")
    except AccessError as e:
        raise click.ClickException(str(e))

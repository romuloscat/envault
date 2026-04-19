"""CLI commands for managing secret dependencies."""
import click
from envault.dependency import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    all_dependencies,
    DependencyError,
)


@click.group("dep")
def dep_cmd():
    """Manage secret dependencies."""


@dep_cmd.command("add")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Vault file path.")
def dep_add(key, depends_on, vault):
    """Record that KEY depends on DEPENDS_ON."""
    try:
        add_dependency(vault, key, depends_on)
        click.echo(f"Added dependency: {key} -> {depends_on}")
    except DependencyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@dep_cmd.command("remove")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Vault file path.")
def dep_remove(key, depends_on, vault):
    """Remove a dependency from KEY."""
    try:
        remove_dependency(vault, key, depends_on)
        click.echo(f"Removed dependency: {key} -> {depends_on}")
    except DependencyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@dep_cmd.command("list")
@click.argument("key")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Vault file path.")
def dep_list(key, vault):
    """List what KEY depends on."""
    deps = get_dependencies(vault, key)
    if not deps:
        click.echo(f"{key} has no dependencies.")
    else:
        for d in deps:
            click.echo(d)


@dep_cmd.command("dependents")
@click.argument("key")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Vault file path.")
def dep_dependents(key, vault):
    """List secrets that depend on KEY."""
    result = get_dependents(vault, key)
    if not result:
        click.echo(f"No secrets depend on {key}.")
    else:
        for d in result:
            click.echo(d)


@dep_cmd.command("show-all")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Vault file path.")
def dep_show_all(vault):
    """Show the full dependency map."""
    data = all_dependencies(vault)
    if not data:
        click.echo("No dependencies recorded.")
    else:
        for key, deps in sorted(data.items()):
            click.echo(f"{key}: {', '.join(deps)}")

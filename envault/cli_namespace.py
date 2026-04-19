"""CLI commands for namespace-aware secret management."""

import click
from envault.store import set_secret, get_secret, delete_secret, list_secrets
from envault.namespace import join, filter_by_namespace, list_namespaces, NamespaceError


@click.group("ns")
def namespace_cmd():
    """Manage secrets within namespaces."""


@namespace_cmd.command("set")
@click.argument("namespace")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default="vault.enc", show_default=True)
@click.password_option("--password", prompt="Password")
def ns_set(namespace, key, value, vault, password):
    """Set a secret under a namespace."""
    try:
        full_key = join(namespace, key)
    except NamespaceError as e:
        raise click.ClickException(str(e))
    set_secret(vault, full_key, value, password)
    click.echo(f"Set {full_key}")


@namespace_cmd.command("get")
@click.argument("namespace")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ns_get(namespace, key, vault, password):
    """Get a secret from a namespace."""
    try:
        full_key = join(namespace, key)
    except NamespaceError as e:
        raise click.ClickException(str(e))
    value = get_secret(vault, full_key, password)
    click.echo(value)


@namespace_cmd.command("list")
@click.argument("namespace")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ns_list(namespace, vault, password):
    """List all keys within a namespace."""
    keys = list_secrets(vault, password)
    matched = filter_by_namespace(keys, namespace)
    if not matched:
        click.echo(f"No secrets found in namespace '{namespace}'.")
        return
    for k in sorted(matched):
        click.echo(k)


@namespace_cmd.command("namespaces")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ns_namespaces(vault, password):
    """List all namespaces present in the vault."""
    keys = list_secrets(vault, password)
    namespaces = list_namespaces(keys)
    if not namespaces:
        click.echo("No namespaces found.")
        return
    for ns in namespaces:
        click.echo(ns)

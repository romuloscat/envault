"""CLI commands for secret tagging."""
import click
from envault.tags import tag_secret, untag_secret, get_tags, keys_by_tag, TagError


@click.group("tags")
def tags_cmd():
    """Manage tags on secrets."""


@tags_cmd.command("add")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default="vault.json", show_default=True)
def tag_add(key, tag, vault):
    """Add TAG to secret KEY."""
    try:
        tag_secret(vault, key, tag)
        click.echo(f"Tagged '{key}' with '{tag}'.")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tags_cmd.command("remove")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default="vault.json", show_default=True)
def tag_remove(key, tag, vault):
    """Remove TAG from secret KEY."""
    try:
        untag_secret(vault, key, tag)
        click.echo(f"Removed tag '{tag}' from '{key}'.")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tags_cmd.command("list")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def tag_list(key, vault):
    """List tags on secret KEY."""
    tags = get_tags(vault, key)
    if not tags:
        click.echo(f"No tags on '{key}'.")
    else:
        for t in tags:
            click.echo(t)


@tags_cmd.command("find")
@click.argument("pattern")
@click.option("--vault", default="vault.json", show_default=True)
def tag_find(pattern, vault):
    """Find keys whose tags match PATTERN (glob)."""
    keys = keys_by_tag(vault, pattern)
    if not keys:
        click.echo("No keys found.")
    else:
        for k in keys:
            click.echo(k)

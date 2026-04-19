"""CLI commands for managing secret comments."""
import click
from envault.comment import set_comment, get_comment, remove_comment, list_comments, CommentError


@click.group("comment")
def comment_cmd():
    """Manage inline comments for secrets."""


@comment_cmd.command("set")
@click.option("--vault", required=True, help="Path to vault file.")
@click.argument("key")
@click.argument("comment")
def comment_set(vault, key, comment):
    """Attach COMMENT to KEY."""
    try:
        set_comment(vault, key, comment)
        click.echo(f"Comment set for '{key}'.")
    except CommentError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@comment_cmd.command("get")
@click.option("--vault", required=True, help="Path to vault file.")
@click.argument("key")
def comment_get(vault, key):
    """Show the comment for KEY."""
    c = get_comment(vault, key)
    if c is None:
        click.echo(f"No comment for '{key}'.")
    else:
        click.echo(c)


@comment_cmd.command("remove")
@click.option("--vault", required=True, help="Path to vault file.")
@click.argument("key")
def comment_remove(vault, key):
    """Remove the comment for KEY."""
    try:
        remove_comment(vault, key)
        click.echo(f"Comment removed for '{key}'.")
    except CommentError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@comment_cmd.command("list")
@click.option("--vault", required=True, help="Path to vault file.")
def comment_list(vault):
    """List all comments."""
    comments = list_comments(vault)
    if not comments:
        click.echo("No comments found.")
    else:
        for key, text in sorted(comments.items()):
            click.echo(f"{key}: {text}")

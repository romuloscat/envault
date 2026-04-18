"""CLI commands for per-secret notes."""
import click
from pathlib import Path
from envault.notes import set_note, get_note, remove_note, list_notes, NoteError


@click.group("notes")
def notes_cmd():
    """Manage notes attached to secrets."""


@notes_cmd.command("set")
@click.argument("key")
@click.argument("note")
@click.option("--vault", default="vault.json", show_default=True)
def note_set(key, note, vault):
    """Attach NOTE to KEY."""
    set_note(Path(vault), key, note)
    click.echo(f"Note set for '{key}'.")


@notes_cmd.command("get")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def note_get(key, vault):
    """Print the note for KEY."""
    note = get_note(Path(vault), key)
    if note is None:
        click.echo(f"No note for '{key}'.")
    else:
        click.echo(note)


@notes_cmd.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def note_remove(key, vault):
    """Remove the note for KEY."""
    try:
        remove_note(Path(vault), key)
        click.echo(f"Note removed for '{key}'.")
    except NoteError as e:
        raise click.ClickException(str(e))


@notes_cmd.command("list")
@click.option("--vault", default="vault.json", show_default=True)
def note_list(vault):
    """List all notes."""
    data = list_notes(Path(vault))
    if not data:
        click.echo("No notes found.")
        return
    for key, note in sorted(data.items()):
        click.echo(f"{key}: {note}")

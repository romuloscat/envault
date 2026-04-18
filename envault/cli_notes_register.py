"""Register notes sub-command with the main CLI."""
from envault.cli_notes import notes_cmd


def register(cli):
    cli.add_command(notes_cmd)

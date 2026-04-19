"""Register label commands into the main CLI."""

from envault.cli_label import label_cmd


def register(cli):
    cli.add_command(label_cmd)

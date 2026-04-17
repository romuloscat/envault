"""Register access_cmd into the main CLI."""
from envault.cli import cli
from envault.cli_access import access_cmd


def register():
    cli.add_command(access_cmd)

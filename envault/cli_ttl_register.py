"""Register TTL commands with the main CLI."""

from envault.cli import cli
from envault.cli_ttl import ttl_cmd


def register():
    cli.add_command(ttl_cmd)


if __name__ == "__main__":
    register()
    cli()

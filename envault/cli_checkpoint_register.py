"""Register the checkpoint command group with the main CLI."""

from envault.cli_checkpoint import checkpoint_cmd


def register(cli):
    cli.add_command(checkpoint_cmd)

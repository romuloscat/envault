"""Register profile commands with the main CLI."""
from envault.cli_profile import profile_cmd

def register(cli):
    cli.add_command(profile_cmd)

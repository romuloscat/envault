from envault.cli_alias import alias_cmd


def register(cli):
    """Register alias-related commands with the CLI application.

    Args:
        cli: The Click CLI group to register commands with.
    """
    cli.add_command(alias_cmd)

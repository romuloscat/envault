from envault.cli_alias import alias_cmd


def register(cli):
    cli.add_command(alias_cmd)

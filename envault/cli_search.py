"""CLI commands for searching secrets in a vault."""

import click
from envault.search import search_secrets, SearchError


@click.command("search")
@click.argument("pattern")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD", help="Master password.")
@click.option("--values", is_flag=True, default=False, help="Also search in decrypted values.")
@click.option("--regex", is_flag=True, default=False, help="Treat PATTERN as a regular expression.")
@click.option("--count", is_flag=True, default=False, help="Print only the number of matching secrets.")
def search_cmd(pattern, vault, password, values, regex, count):
    """Search secrets by key PATTERN (glob or regex).

    Examples:

      envault search 'DB_*' --vault vault.json

      envault search '^API' --vault vault.json --regex

      envault search 'prod' --vault vault.json --values

      envault search 'DB_*' --vault vault.json --count
    """
    try:
        results = search_secrets(vault, password, pattern, search_values=values, regex=regex)
    except SearchError as exc:
        raise click.ClickException(str(exc))

    if not results:
        click.echo("No matching secrets found.")
        return

    if count:
        click.echo(len(results))
        return

    max_key_len = max(len(k) for k in results)
    for key, value in sorted(results.items()):
        click.echo(f"{key:<{max_key_len}}  =  {value}")

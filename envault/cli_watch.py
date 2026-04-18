"""CLI commands for the watch feature."""

import click
from envault.watch import watch_and_run, WatchError


@click.group("watch")
def watch_cmd():
    """Watch vault for changes and re-run a command."""


@watch_cmd.command("run")
@click.option("--vault", required=True, envvar="ENVAULT_VAULT", help="Path to vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--interval", default=1.0, show_default=True, help="Poll interval in seconds.")
@click.option("--key", "keys", multiple=True, help="Secret keys to inject (repeatable). Defaults to all.")
@click.argument("command", nargs=-1, required=True)
def watch_run(vault, password, interval, keys, command):
    """Watch VAULT and re-run COMMAND whenever secrets change.

    Example:

        envault watch run --vault .vault --password s3cr3t -- ./start.sh
    """
    selected_keys = list(keys) if keys else None
    click.echo(f"Watching {vault} (interval={interval}s) ...")
    try:
        watch_and_run(
            vault_path=vault,
            command=list(command),
            password=password,
            interval=interval,
            env_keys=selected_keys,
        )
    except WatchError as exc:
        raise click.ClickException(str(exc))
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")

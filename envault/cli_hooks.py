"""CLI commands for managing vault hooks."""
import click
from envault.hooks import register_hook, unregister_hook, list_hooks, HookError, HOOK_EVENTS


@click.group("hooks")
def hooks_cmd():
    """Manage pre/post operation hooks."""


@hooks_cmd.command("add")
@click.argument("event")
@click.argument("command")
@click.option("--vault", default="vault.json", show_default=True)
def hook_add(event, command, vault):
    """Register a shell COMMAND for EVENT."""
    try:
        register_hook(vault, event, command)
        click.echo(f"Hook registered: [{event}] -> {command}")
    except HookError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks_cmd.command("remove")
@click.argument("event")
@click.argument("command")
@click.option("--vault", default="vault.json", show_default=True)
def hook_remove(event, command, vault):
    """Unregister a COMMAND from EVENT."""
    try:
        unregister_hook(vault, event, command)
        click.echo(f"Hook removed: [{event}] -> {command}")
    except HookError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks_cmd.command("list")
@click.option("--vault", default="vault.json", show_default=True)
def hook_list(vault):
    """List all registered hooks."""
    try:
        hooks = list_hooks(vault)
    except HookError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if not hooks:
        click.echo("No hooks registered.")
        return
    for event in HOOK_EVENTS:
        cmds = hooks.get(event, [])
        if cmds:
            click.echo(f"[{event}]")
            for cmd in cmds:
                click.echo(f"  {cmd}")

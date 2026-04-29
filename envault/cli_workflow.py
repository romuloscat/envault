"""CLI commands for workflow management."""

from __future__ import annotations

import click

from envault.workflow import (
    WorkflowError,
    WorkflowViolation,
    get_workflow,
    list_workflows,
    remove_workflow,
    set_workflow,
    validate_workflow,
)


@click.group("workflow", help="Define and validate ordered key workflows.")
def workflow_cmd() -> None:
    pass


@workflow_cmd.command("set")
@click.option("--vault", required=True, help="Path to vault file.")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
def wf_set(vault: str, name: str, keys: tuple) -> None:
    """Define a workflow NAME with an ordered list of KEYS."""
    try:
        set_workflow(vault, name, list(keys))
        click.echo(f"Workflow '{name}' set with {len(keys)} key(s).")
    except WorkflowError as exc:
        raise click.ClickException(str(exc))


@workflow_cmd.command("remove")
@click.option("--vault", required=True)
@click.argument("name")
def wf_remove(vault: str, name: str) -> None:
    """Remove a workflow by NAME."""
    try:
        remove_workflow(vault, name)
        click.echo(f"Workflow '{name}' removed.")
    except WorkflowError as exc:
        raise click.ClickException(str(exc))


@workflow_cmd.command("show")
@click.option("--vault", required=True)
@click.argument("name")
def wf_show(vault: str, name: str) -> None:
    """Show keys in workflow NAME."""
    keys = get_workflow(vault, name)
    if keys is None:
        raise click.ClickException(f"Workflow '{name}' not found.")
    for i, key in enumerate(keys, 1):
        click.echo(f"  {i}. {key}")


@workflow_cmd.command("list")
@click.option("--vault", required=True)
def wf_list(vault: str) -> None:
    """List all defined workflows."""
    names = list_workflows(vault)
    if not names:
        click.echo("No workflows defined.")
    else:
        for name in names:
            click.echo(name)


@workflow_cmd.command("validate")
@click.option("--vault", required=True)
@click.option("--password", required=True, hide_input=True, prompt=True)
@click.argument("name")
def wf_validate(vault: str, password: str, name: str) -> None:
    """Validate that all keys in workflow NAME exist in the vault."""
    try:
        keys = validate_workflow(vault, name, password)
        click.echo(f"Workflow '{name}' is valid ({len(keys)} key(s) present).")
    except WorkflowViolation as exc:
        raise click.ClickException(str(exc))
    except WorkflowError as exc:
        raise click.ClickException(str(exc))

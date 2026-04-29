"""Registration helper for the workflow CLI group."""

from envault.cli_workflow import workflow_cmd


def register(cli: object) -> None:  # type: ignore[type-arg]
    cli.add_command(workflow_cmd)  # type: ignore[attr-defined]

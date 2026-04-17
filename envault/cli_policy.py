"""CLI commands for secret policy management."""
import click
from envault.policy import set_policy, remove_policy, get_policy, enforce_policies, PolicyError


@click.group("policy")
def policy_cmd():
    """Manage validation policies for secrets."""


@policy_cmd.command("set")
@click.argument("key")
@click.option("--vault", default="vault.env", show_default=True)
@click.option("--min-length", type=int, default=None)
@click.option("--max-length", type=int, default=None)
@click.option("--pattern", default=None, help="Regex pattern the value must match")
@click.option("--required", is_flag=True, default=False)
def policy_set(key, vault, min_length, max_length, pattern, required):
    """Set policy rules for a key."""
    rules = {}
    if min_length is not None:
        rules["min_length"] = min_length
    if max_length is not None:
        rules["max_length"] = max_length
    if pattern is not None:
        rules["pattern"] = pattern
    if required:
        rules["required"] = True
    if not rules:
        raise click.UsageError("Specify at least one rule.")
    try:
        set_policy(vault, key, rules)
        click.echo(f"Policy set for '{key}'.")
    except PolicyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@policy_cmd.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.env", show_default=True)
def policy_remove(key, vault):
    """Remove policy for a key."""
    try:
        remove_policy(vault, key)
        click.echo(f"Policy removed for '{key}'.")
    except PolicyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@policy_cmd.command("show")
@click.argument("key")
@click.option("--vault", default="vault.env", show_default=True)
def policy_show(key, vault):
    """Show policy rules for a key."""
    rules = get_policy(vault, key)
    if rules is None:
        click.echo(f"No policy defined for '{key}'.")
    else:
        for rule, val in rules.items():
            click.echo(f"  {rule}: {val}")


@policy_cmd.command("enforce")
@click.option("--vault", default="vault.env", show_default=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def policy_enforce(vault, password):
    """Enforce all policies against current vault values."""
    violations = enforce_policies(vault, password)
    if not violations:
        click.echo("All policies satisfied.")
    else:
        for v in violations:
            click.echo(f"  VIOLATION: {v}")
        raise SystemExit(1)

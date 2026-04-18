"""CLI commands for rotation reminders."""
import click
from envault.remind import record_rotation, remove_reminder, check_reminders, RemindError


@click.group("remind")
def remind_cmd():
    """Manage secret rotation reminders."""


@remind_cmd.command("record")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def remind_record(key, vault):
    """Record that KEY was rotated now."""
    record_rotation(vault, key)
    click.echo(f"Recorded rotation for '{key}'.")


@remind_cmd.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def remind_remove(key, vault):
    """Remove rotation record for KEY."""
    try:
        remove_reminder(vault, key)
        click.echo(f"Removed reminder for '{key}'.")
    except RemindError as e:
        raise click.ClickException(str(e))


@remind_cmd.command("check")
@click.option("--days", default=90, show_default=True, help="Max days before overdue.")
@click.option("--vault", default=".envault", show_default=True)
def remind_check(days, vault):
    """List secrets overdue for rotation."""
    issues = check_reminders(vault, days)
    if not issues:
        click.echo("All secrets are within rotation policy.")
        return
    click.echo(f"{'KEY':<30} {'DAYS OVERDUE'}")
    click.echo("-" * 44)
    for issue in issues:
        click.echo(f"{issue.key:<30} {issue.days_overdue}")

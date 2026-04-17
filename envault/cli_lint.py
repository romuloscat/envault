"""CLI surface for the lint command."""
import click
from envault.lint import lint_vault, LintError


@click.group('lint')
def lint_cmd():
    """Lint vault secrets for common issues."""


@lint_cmd.command('run')
@click.option('--vault', required=True, envvar='ENVAULT_VAULT', help='Path to vault file')
@click.option('--password', required=True, envvar='ENVAULT_PASSWORD', prompt=True, hide_input=True)
@click.option('--level', default='warning', type=click.Choice(['warning', 'error']), show_default=True,
              help='Minimum issue level to display')
@click.option('--fail-on-error', is_flag=True, default=False, help='Exit with code 1 if errors found')
def lint_run(vault, password, level, fail_on_error):
    """Run lint checks against the vault."""
    try:
        issues = lint_vault(vault, password)
    except LintError as exc:
        raise click.ClickException(str(exc))

    levels = ['warning', 'error'] if level == 'warning' else ['error']
    visible = [i for i in issues if i.level in levels]

    if not visible:
        click.echo('No issues found.')
        return

    for issue in visible:
        colour = 'red' if issue.level == 'error' else 'yellow'
        click.echo(click.style(f'[{issue.level.upper()}]', fg=colour) + f' {issue.key}: {issue.message}')

    errors = [i for i in issues if i.level == 'error']
    if fail_on_error and errors:
        raise SystemExit(1)

"""CLI commands for template rendering."""
import click
from envault.template import render_string, render_file, TemplateError


@click.group(name="template")
def template_cmd():
    """Render templates with secrets from the vault."""


@template_cmd.command(name="render")
@click.argument("src", type=click.Path(exists=True))
@click.argument("dst", type=click.Path())
@click.option("--vault", default="vault.json", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def render_file_cmd(src, dst, vault, password):
    """Render template file SRC into DST substituting vault secrets."""
    try:
        count = render_file(src, dst, password, vault)
        click.echo(f"Rendered {count} placeholder(s) -> {dst}")
    except TemplateError as e:
        raise click.ClickException(str(e))


@template_cmd.command(name="echo")
@click.argument("template_str")
@click.option("--vault", default="vault.json", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def render_echo_cmd(template_str, vault, password):
    """Render a template string and print the result."""
    try:
        result = render_string(template_str, password, vault)
        click.echo(result)
    except TemplateError as e:
        raise click.ClickException(str(e))

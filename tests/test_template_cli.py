"""Tests for the CLI template commands (render-file and render-echo)."""

import pytest
from click.testing import CliRunner
from pathlib import Path
import tempfile
import os

from envault.cli_template import template_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.env"
    return vf


def _set_secret(runner, vault_file, key, value, password="pass"):
    from envault.cli import set_cmd
    result = runner.invoke(
        set_cmd, ["--vault", str(vault_file), "--password", password, key, value]
    )
    assert result.exit_code == 0


def test_render_echo_substitutes_placeholder(runner, vault_file):
    from envault.cli import set_cmd
    runner.invoke(
        set_cmd,
        ["--vault", str(vault_file), "--password", "secret", "APP_HOST", "localhost"],
    )
    result = runner.invoke(
        template_cmd,
        [
            "render-echo",
            "--vault", str(vault_file),
            "--password", "secret",
            "Connect to {{APP_HOST}}",
        ],
    )
    assert result.exit_code == 0
    assert "Connect to localhost" in result.output


def test_render_echo_missing_key_exits_nonzero(runner, vault_file):
    from envault.cli import set_cmd
    runner.invoke(
        set_cmd,
        ["--vault", str(vault_file), "--password", "secret", "EXISTING", "val"],
    )
    result = runner.invoke(
        template_cmd,
        [
            "render-echo",
            "--vault", str(vault_file),
            "--password", "secret",
            "Hello {{MISSING_KEY}}",
        ],
    )
    assert result.exit_code != 0
    assert "MISSING_KEY" in result.output


def test_render_file_writes_output(runner, vault_file, tmp_path):
    from envault.cli import set_cmd
    runner.invoke(
        set_cmd,
        ["--vault", str(vault_file), "--password", "secret", "DB_PORT", "5432"],
    )
    template_path = tmp_path / "config.tmpl"
    output_path = tmp_path / "config.out"
    template_path.write_text("port = {{DB_PORT}}\n")

    result = runner.invoke(
        template_cmd,
        [
            "render-file",
            "--vault", str(vault_file),
            "--password", "secret",
            "--output", str(output_path),
            str(template_path),
        ],
    )
    assert result.exit_code == 0
    assert output_path.exists()
    assert "5432" in output_path.read_text()


def test_render_file_prints_to_stdout_when_no_output(runner, vault_file, tmp_path):
    from envault.cli import set_cmd
    runner.invoke(
        set_cmd,
        ["--vault", str(vault_file), "--password", "secret", "REGION", "us-east-1"],
    )
    template_path = tmp_path / "infra.tmpl"
    template_path.write_text("region = {{REGION}}\n")

    result = runner.invoke(
        template_cmd,
        [
            "render-file",
            "--vault", str(vault_file),
            "--password", "secret",
            str(template_path),
        ],
    )
    assert result.exit_code == 0
    assert "us-east-1" in result.output


def test_render_file_missing_template_exits_nonzero(runner, vault_file, tmp_path):
    result = runner.invoke(
        template_cmd,
        [
            "render-file",
            "--vault", str(vault_file),
            "--password", "secret",
            str(tmp_path / "nonexistent.tmpl"),
        ],
    )
    assert result.exit_code != 0

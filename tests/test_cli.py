"""Tests for the envault CLI commands."""

import pytest
from click.testing import CliRunner
from envault.cli import cli


PASSWORD = "test-password"


@pytest.fixture
def runner(tmp_path):
    """Return a Click test runner with a temp vault path."""
    return CliRunner(), str(tmp_path / "test.vault")


def test_set_and_get(runner):
    r, vault = runner
    result = r.invoke(cli, ["set", "API_KEY", "secret123", "--vault", vault, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "API_KEY" in result.output

    result = r.invoke(cli, ["get", "API_KEY", "--vault", vault, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "secret123" in result.output


def test_get_missing_key(runner):
    r, vault = runner
    result = r.invoke(cli, ["get", "MISSING", "--vault", vault, "--password", PASSWORD])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_delete_key(runner):
    r, vault = runner
    r.invoke(cli, ["set", "TO_DELETE", "bye", "--vault", vault, "--password", PASSWORD])
    result = r.invoke(cli, ["delete", "TO_DELETE", "--vault", vault, "--password", PASSWORD])
    assert result.exit_code == 0

    result = r.invoke(cli, ["get", "TO_DELETE", "--vault", vault, "--password", PASSWORD])
    assert result.exit_code != 0


def test_delete_missing_key(runner):
    r, vault = runner
    result = r.invoke(cli, ["delete", "NOPE", "--vault", vault, "--password", PASSWORD])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_list_empty_vault(runner):
    r, vault = runner
    result = r.invoke(cli, ["list", "--vault", vault])
    assert result.exit_code == 0
    assert "empty" in result.output


def test_list_keys(runner):
    r, vault = runner
    r.invoke(cli, ["set", "FOO", "1", "--vault", vault, "--password", PASSWORD])
    r.invoke(cli, ["set", "BAR", "2", "--vault", vault, "--password", PASSWORD])
    result = r.invoke(cli, ["list", "--vault", vault])
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "BAR" in result.output

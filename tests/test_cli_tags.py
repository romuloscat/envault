"""Tests for CLI tag commands."""
import pytest
from click.testing import CliRunner
from envault.store import set_secret
from envault.cli_tags import tags_cmd

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.json"
    set_secret(str(p), "DB_HOST", "localhost", PASSWORD)
    set_secret(str(p), "API_KEY", "abc", PASSWORD)
    return str(p)


def test_tag_add(runner, vault_file):
    result = runner.invoke(tags_cmd, ["add", "DB_HOST", "infra", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Tagged" in result.output


def test_tag_add_missing_key(runner, vault_file):
    result = runner.invoke(tags_cmd, ["add", "MISSING", "infra", "--vault", vault_file])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_tag_remove(runner, vault_file):
    runner.invoke(tags_cmd, ["add", "DB_HOST", "infra", "--vault", vault_file])
    result = runner.invoke(tags_cmd, ["remove", "DB_HOST", "infra", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_tag_remove_missing_tag(runner, vault_file):
    result = runner.invoke(tags_cmd, ["remove", "DB_HOST", "ghost", "--vault", vault_file])
    assert result.exit_code == 1


def test_tag_list(runner, vault_file):
    runner.invoke(tags_cmd, ["add", "DB_HOST", "infra", "--vault", vault_file])
    result = runner.invoke(tags_cmd, ["list", "DB_HOST", "--vault", vault_file])
    assert result.exit_code == 0
    assert "infra" in result.output


def test_tag_list_no_tags(runner, vault_file):
    result = runner.invoke(tags_cmd, ["list", "API_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_tag_find(runner, vault_file):
    runner.invoke(tags_cmd, ["add", "DB_HOST", "database", "--vault", vault_file])
    runner.invoke(tags_cmd, ["add", "API_KEY", "external", "--vault", vault_file])
    result = runner.invoke(tags_cmd, ["find", "database", "--vault", vault_file])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "API_KEY" not in result.output


def test_tag_find_no_match(runner, vault_file):
    result = runner.invoke(tags_cmd, ["find", "ghost", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No keys found" in result.output

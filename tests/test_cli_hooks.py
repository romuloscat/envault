import pytest
from click.testing import CliRunner
from envault.cli_hooks import hooks_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_hook_add(runner, vault_file):
    result = runner.invoke(hooks_cmd, ["add", "post_set", "echo hello", "--vault", vault_file])
    assert result.exit_code == 0
    assert "registered" in result.output


def test_hook_add_invalid_event(runner, vault_file):
    result = runner.invoke(hooks_cmd, ["add", "bad_event", "echo x", "--vault", vault_file])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_hook_remove(runner, vault_file):
    runner.invoke(hooks_cmd, ["add", "pre_delete", "echo bye", "--vault", vault_file])
    result = runner.invoke(hooks_cmd, ["remove", "pre_delete", "echo bye", "--vault", vault_file])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_hook_remove_missing(runner, vault_file):
    result = runner.invoke(hooks_cmd, ["remove", "pre_set", "echo x", "--vault", vault_file])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_hook_list_empty(runner, vault_file):
    result = runner.invoke(hooks_cmd, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No hooks" in result.output


def test_hook_list_shows_hooks(runner, vault_file):
    runner.invoke(hooks_cmd, ["add", "post_get", "echo got", "--vault", vault_file])
    result = runner.invoke(hooks_cmd, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "post_get" in result.output
    assert "echo got" in result.output

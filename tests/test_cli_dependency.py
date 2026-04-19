import pytest
from click.testing import CliRunner
from envault.cli_dependency import dep_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def _opt(vault_file):
    return ["--vault", vault_file]


def test_dep_add(runner, vault_file):
    result = runner.invoke(dep_cmd, ["add", "APP", "SECRET"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "APP -> SECRET" in result.output


def test_dep_add_self_raises(runner, vault_file):
    result = runner.invoke(dep_cmd, ["add", "KEY", "KEY"] + _opt(vault_file))
    assert result.exit_code != 0
    assert "Error" in result.output


def test_dep_list(runner, vault_file):
    runner.invoke(dep_cmd, ["add", "APP", "DB_PASS"] + _opt(vault_file))
    result = runner.invoke(dep_cmd, ["list", "APP"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "DB_PASS" in result.output


def test_dep_list_empty(runner, vault_file):
    result = runner.invoke(dep_cmd, ["list", "NOTHING"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "no dependencies" in result.output


def test_dep_remove(runner, vault_file):
    runner.invoke(dep_cmd, ["add", "A", "B"] + _opt(vault_file))
    result = runner.invoke(dep_cmd, ["remove", "A", "B"] + _opt(vault_file))
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_dep_remove_missing_raises(runner, vault_file):
    result = runner.invoke(dep_cmd, ["remove", "X", "Y"] + _opt(vault_file))
    assert result.exit_code != 0


def test_dep_dependents(runner, vault_file):
    runner.invoke(dep_cmd, ["add", "APP", "SHARED"] + _opt(vault_file))
    result = runner.invoke(dep_cmd, ["dependents", "SHARED"] + _opt(vault_file))
    assert "APP" in result.output


def test_dep_show_all(runner, vault_file):
    runner.invoke(dep_cmd, ["add", "A", "B"] + _opt(vault_file))
    result = runner.invoke(dep_cmd, ["show-all"] + _opt(vault_file))
    assert "A" in result.output
    assert "B" in result.output


def test_dep_show_all_empty(runner, vault_file):
    result = runner.invoke(dep_cmd, ["show-all"] + _opt(vault_file))
    assert "No dependencies" in result.output

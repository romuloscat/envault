import pytest
from click.testing import CliRunner
from pathlib import Path
import json

from envault.cli_dependency import dep_cmd
from envault.store import set_secret

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def _opt(vault_file):
    return ["--vault", str(vault_file), "--password", PASSWORD]


def test_dep_add(runner, vault_file):
    set_secret("API_KEY", "secret", PASSWORD, vault_file)
    set_secret("API_URL", "https://example.com", PASSWORD, vault_file)

    result = runner.invoke(dep_cmd, _opt(vault_file) + ["add", "API_KEY", "API_URL"])
    assert result.exit_code == 0
    assert "API_URL" in result.output


def test_dep_add_self_raises(runner, vault_file):
    set_secret("API_KEY", "secret", PASSWORD, vault_file)

    result = runner.invoke(dep_cmd, _opt(vault_file) + ["add", "API_KEY", "API_KEY"])
    assert result.exit_code != 0
    assert "self" in result.output.lower() or "cannot" in result.output.lower()


def test_dep_list(runner, vault_file):
    set_secret("A", "1", PASSWORD, vault_file)
    set_secret("B", "2", PASSWORD, vault_file)
    set_secret("C", "3", PASSWORD, vault_file)

    runner.invoke(dep_cmd, _opt(vault_file) + ["add", "A", "B"])
    runner.invoke(dep_cmd, _opt(vault_file) + ["add", "A", "C"])

    result = runner.invoke(dep_cmd, _opt(vault_file) + ["list", "A"])
    assert result.exit_code == 0
    assert "B" in result.output
    assert "C" in result.output


def test_dep_list_empty(runner, vault_file):
    set_secret("LONELY", "val", PASSWORD, vault_file)

    result = runner.invoke(dep_cmd, _opt(vault_file) + ["list", "LONELY"])
    assert result.exit_code == 0
    assert "no dependencies" in result.output.lower() or result.output.strip() == ""


def test_dep_remove(runner, vault_file):
    set_secret("X", "1", PASSWORD, vault_file)
    set_secret("Y", "2", PASSWORD, vault_file)

    runner.invoke(dep_cmd, _opt(vault_file) + ["add", "X", "Y"])
    result = runner.invoke(dep_cmd, _opt(vault_file) + ["remove", "X", "Y"])
    assert result.exit_code == 0

    result = runner.invoke(dep_cmd, _opt(vault_file) + ["list", "X"])
    assert "Y" not in result.output


def test_dep_dependents(runner, vault_file):
    set_secret("BASE", "base", PASSWORD, vault_file)
    set_secret("CHILD1", "c1", PASSWORD, vault_file)
    set_secret("CHILD2", "c2", PASSWORD, vault_file)

    runner.invoke(dep_cmd, _opt(vault_file) + ["add", "CHILD1", "BASE"])
    runner.invoke(dep_cmd, _opt(vault_file) + ["add", "CHILD2", "BASE"])

    result = runner.invoke(dep_cmd, _opt(vault_file) + ["dependents", "BASE"])
    assert result.exit_code == 0
    assert "CHILD1" in result.output
    assert "CHILD2" in result.output

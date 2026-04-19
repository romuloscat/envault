import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_label import label_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def _vault_opt(vault_file):
    return ["--vault", str(vault_file)]


def test_label_set_and_list(runner, vault_file):
    result = runner.invoke(label_cmd, ["set", "DB_URL", "env", "prod"] + _vault_opt(vault_file))
    assert result.exit_code == 0
    assert "env=prod" in result.output

    result = runner.invoke(label_cmd, ["list", "DB_URL"] + _vault_opt(vault_file))
    assert result.exit_code == 0
    assert "env=prod" in result.output


def test_label_list_empty(runner, vault_file):
    result = runner.invoke(label_cmd, ["list", "MISSING"] + _vault_opt(vault_file))
    assert result.exit_code == 0
    assert "No labels" in result.output


def test_label_remove(runner, vault_file):
    runner.invoke(label_cmd, ["set", "KEY", "env", "dev"] + _vault_opt(vault_file))
    result = runner.invoke(label_cmd, ["remove", "KEY", "env"] + _vault_opt(vault_file))
    assert result.exit_code == 0
    assert "removed" in result.output


def test_label_remove_missing_raises(runner, vault_file):
    result = runner.invoke(label_cmd, ["remove", "GHOST", "env"] + _vault_opt(vault_file))
    assert result.exit_code != 0


def test_label_find(runner, vault_file):
    runner.invoke(label_cmd, ["set", "A", "team", "ops"] + _vault_opt(vault_file))
    runner.invoke(label_cmd, ["set", "B", "team", "dev"] + _vault_opt(vault_file))
    result = runner.invoke(label_cmd, ["find", "team"] + _vault_opt(vault_file))
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_label_find_with_value(runner, vault_file):
    runner.invoke(label_cmd, ["set", "A", "env", "prod"] + _vault_opt(vault_file))
    runner.invoke(label_cmd, ["set", "B", "env", "dev"] + _vault_opt(vault_file))
    result = runner.invoke(label_cmd, ["find", "env", "--value", "prod"] + _vault_opt(vault_file))
    assert "A" in result.output
    assert "B" not in result.output


def test_label_find_no_match(runner, vault_file):
    result = runner.invoke(label_cmd, ["find", "nonexistent"] + _vault_opt(vault_file))
    assert result.exit_code == 0
    assert "No matching" in result.output

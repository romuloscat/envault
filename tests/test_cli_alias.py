import pytest
from click.testing import CliRunner
from envault.cli_alias import alias_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_alias_set(runner, vault_file):
    result = runner.invoke(alias_cmd, ["set", "db", "DATABASE_URL", "--vault", vault_file])
    assert result.exit_code == 0
    assert "db" in result.output
    assert "DATABASE_URL" in result.output


def test_alias_resolve(runner, vault_file):
    runner.invoke(alias_cmd, ["set", "db", "DATABASE_URL", "--vault", vault_file])
    result = runner.invoke(alias_cmd, ["resolve", "db", "--vault", vault_file])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output


def test_alias_resolve_unknown(runner, vault_file):
    result = runner.invoke(alias_cmd, ["resolve", "ghost", "--vault", vault_file])
    assert result.exit_code == 0
    assert "ghost" in result.output


def test_alias_list_empty(runner, vault_file):
    result = runner.invoke(alias_cmd, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_alias_list_shows_aliases(runner, vault_file):
    runner.invoke(alias_cmd, ["set", "db", "DATABASE_URL", "--vault", vault_file])
    runner.invoke(alias_cmd, ["set", "key", "API_KEY", "--vault", vault_file])
    result = runner.invoke(alias_cmd, ["list", "--vault", vault_file])
    assert "db -> DATABASE_URL" in result.output
    assert "key -> API_KEY" in result.output


def test_alias_remove(runner, vault_file):
    runner.invoke(alias_cmd, ["set", "db", "DATABASE_URL", "--vault", vault_file])
    result = runner.invoke(alias_cmd, ["remove", "db", "--vault", vault_file])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_alias_remove_missing(runner, vault_file):
    result = runner.invoke(alias_cmd, ["remove", "ghost", "--vault", vault_file])
    assert result.exit_code == 1


def test_alias_find(runner, vault_file):
    runner.invoke(alias_cmd, ["set", "db", "DATABASE_URL", "--vault", vault_file])
    runner.invoke(alias_cmd, ["set", "database", "DATABASE_URL", "--vault", vault_file])
    result = runner.invoke(alias_cmd, ["find", "DATABASE_URL", "--vault", vault_file])
    assert "db" in result.output
    assert "database" in result.output

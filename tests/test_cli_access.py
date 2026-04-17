import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_access import access_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_grant_and_list(runner, vault_file):
    result = runner.invoke(access_cmd, ["grant", "ci", "DB_PASS", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Granted" in result.output

    result = runner.invoke(access_cmd, ["list", "ci", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output


def test_list_empty_profile(runner, vault_file):
    result = runner.invoke(access_cmd, ["list", "nobody", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "No keys" in result.output


def test_revoke(runner, vault_file):
    runner.invoke(access_cmd, ["grant", "ci", "API_KEY", "--vault", str(vault_file)])
    result = runner.invoke(access_cmd, ["revoke", "ci", "API_KEY", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Revoked" in result.output


def test_revoke_missing_raises(runner, vault_file):
    result = runner.invoke(access_cmd, ["revoke", "ghost", "KEY", "--vault", str(vault_file)])
    assert result.exit_code != 0


def test_profiles_list(runner, vault_file):
    runner.invoke(access_cmd, ["grant", "dev", "X", "--vault", str(vault_file)])
    runner.invoke(access_cmd, ["grant", "ci", "Y", "--vault", str(vault_file)])
    result = runner.invoke(access_cmd, ["profiles", "--vault", str(vault_file)])
    assert "dev" in result.output
    assert "ci" in result.output


def test_delete_profile(runner, vault_file):
    runner.invoke(access_cmd, ["grant", "temp", "Z", "--vault", str(vault_file)])
    result = runner.invoke(access_cmd, ["delete-profile", "temp", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_delete_missing_profile(runner, vault_file):
    result = runner.invoke(access_cmd, ["delete-profile", "nope", "--vault", str(vault_file)])
    assert result.exit_code != 0

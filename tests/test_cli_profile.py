import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_profile import profile_cmd
from envault.store import set_secret

PASSWORD = "testpass"

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"

def test_profile_add(runner, vault_file):
    result = runner.invoke(profile_cmd, ["add", "dev", "DB_URL", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Added" in result.output

def test_profile_list_empty(runner, vault_file):
    result = runner.invoke(profile_cmd, ["list", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "No profiles" in result.output

def test_profile_list_shows_profiles(runner, vault_file):
    runner.invoke(profile_cmd, ["add", "dev", "KEY", "--vault", str(vault_file)])
    runner.invoke(profile_cmd, ["add", "prod", "KEY", "--vault", str(vault_file)])
    result = runner.invoke(profile_cmd, ["list", "--vault", str(vault_file)])
    assert "dev" in result.output
    assert "prod" in result.output

def test_profile_show(runner, vault_file):
    runner.invoke(profile_cmd, ["add", "dev", "DB_URL", "--vault", str(vault_file)])
    result = runner.invoke(profile_cmd, ["show", "dev", "--vault", str(vault_file)])
    assert "DB_URL" in result.output

def test_profile_show_missing_raises(runner, vault_file):
    result = runner.invoke(profile_cmd, ["show", "ghost", "--vault", str(vault_file)])
    assert result.exit_code != 0

def test_profile_remove(runner, vault_file):
    runner.invoke(profile_cmd, ["add", "dev", "DB_URL", "--vault", str(vault_file)])
    result = runner.invoke(profile_cmd, ["remove", "dev", "DB_URL", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Removed" in result.output

def test_profile_delete(runner, vault_file):
    runner.invoke(profile_cmd, ["add", "dev", "KEY", "--vault", str(vault_file)])
    result = runner.invoke(profile_cmd, ["delete", "dev", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "Deleted" in result.output

def test_profile_delete_missing(runner, vault_file):
    result = runner.invoke(profile_cmd, ["delete", "ghost", "--vault", str(vault_file)])
    assert result.exit_code != 0

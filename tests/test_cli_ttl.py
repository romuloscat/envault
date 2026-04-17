"""Tests for CLI TTL commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_ttl import ttl_cmd
from envault.store import set_secret
from envault.ttl import _load_ttl, _save_ttl
import time


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "vault.env"
    set_secret(vf, "password", "API_KEY", "secret123")
    return vf


def test_ttl_set(runner, vault_file):
    result = runner.invoke(
        ttl_cmd, ["set", "API_KEY", "300", "--vault", str(vault_file), "--password", "password"]
    )
    assert result.exit_code == 0
    assert "expires in 300s" in result.output


def test_ttl_set_invalid_seconds(runner, vault_file):
    result = runner.invoke(
        ttl_cmd, ["set", "API_KEY", "0", "--vault", str(vault_file), "--password", "password"]
    )
    assert result.exit_code != 0


def test_ttl_get_no_ttl(runner, vault_file):
    result = runner.invoke(ttl_cmd, ["get", "API_KEY", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "No TTL set" in result.output


def test_ttl_get_with_ttl(runner, vault_file):
    runner.invoke(
        ttl_cmd, ["set", "API_KEY", "600", "--vault", str(vault_file), "--password", "password"]
    )
    result = runner.invoke(ttl_cmd, ["get", "API_KEY", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "remaining" in result.output


def test_ttl_clear(runner, vault_file):
    runner.invoke(
        ttl_cmd, ["set", "API_KEY", "600", "--vault", str(vault_file), "--password", "password"]
    )
    result = runner.invoke(ttl_cmd, ["clear", "API_KEY", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_ttl_purge_removes_expired(runner, vault_file):
    from envault.ttl import set_ttl
    set_ttl(vault_file, "API_KEY", 1)
    data = _load_ttl(vault_file)
    data["API_KEY"] = time.time() - 10
    _save_ttl(vault_file, data)
    result = runner.invoke(
        ttl_cmd, ["purge", "--vault", str(vault_file), "--password", "password"]
    )
    assert result.exit_code == 0
    assert "Purged" in result.output

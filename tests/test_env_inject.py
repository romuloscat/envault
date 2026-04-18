import os
import sys
import pytest
from pathlib import Path

from envault.store import set_secret
from envault.ttl import set_ttl
from envault.env_inject import build_env, run_with_secrets, InjectError

PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_build_env_contains_secrets(vault_file):
    set_secret(vault_file, PASSWORD, "MY_KEY", "hello")
    env = build_env(vault_file, PASSWORD)
    assert env["MY_KEY"] == "hello"


def test_build_env_merges_os_environ(vault_file, monkeypatch):
    monkeypatch.setenv("EXISTING_VAR", "exists")
    set_secret(vault_file, PASSWORD, "NEW_KEY", "new")
    env = build_env(vault_file, PASSWORD)
    assert env["EXISTING_VAR"] == "exists"
    assert env["NEW_KEY"] == "new"


def test_build_env_filters_by_keys(vault_file):
    set_secret(vault_file, PASSWORD, "KEY_A", "aaa")
    set_secret(vault_file, PASSWORD, "KEY_B", "bbb")
    env = build_env(vault_file, PASSWORD, keys=["KEY_A"])
    assert env["KEY_A"] == "aaa"
    assert "KEY_B" not in env


def test_build_env_unknown_key_raises(vault_file):
    set_secret(vault_file, PASSWORD, "REAL", "val")
    with pytest.raises(InjectError, match="GHOST"):
        build_env(vault_file, PASSWORD, keys=["GHOST"])


def test_build_env_skips_expired(vault_file):
    set_secret(vault_file, PASSWORD, "FRESH", "ok")
    set_secret(vault_file, PASSWORD, "STALE", "old")
    set_ttl(vault_file, "STALE", -1)  # already expired
    env = build_env(vault_file, PASSWORD, skip_expired=True)
    assert "FRESH" in env
    assert "STALE" not in env


def test_build_env_includes_expired_when_flag_false(vault_file):
    set_secret(vault_file, PASSWORD, "STALE", "old")
    set_ttl(vault_file, "STALE", -1)
    env = build_env(vault_file, PASSWORD, skip_expired=False)
    assert env["STALE"] == "old"


def test_run_with_secrets_returns_exit_code(vault_file):
    set_secret(vault_file, PASSWORD, "PING", "pong")
    code = run_with_secrets(vault_file, PASSWORD, [sys.executable, "-c", "import os; assert os.environ['PING']=='pong'"])
    assert code == 0


def test_run_with_secrets_no_command_raises(vault_file):
    with pytest.raises(InjectError, match="No command"):
        run_with_secrets(vault_file, PASSWORD, [])

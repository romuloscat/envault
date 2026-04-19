"""Tests for envault.lock and envault.cli_lock."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault import lock as _lock
from envault.cli_lock import lock_cmd


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    p = tmp_path / "vault.enc"
    p.write_text("{}")
    return str(p)


# --- unit tests ---

def test_acquire_creates_lock_file(vault_file):
    lp = _lock.acquire(vault_file)
    try:
        assert lp.exists()
    finally:
        _lock.release(lp)


def test_release_removes_lock_file(vault_file):
    lp = _lock.acquire(vault_file)
    _lock.release(lp)
    assert not lp.exists()


def test_is_locked_true_while_held(vault_file):
    lp = _lock.acquire(vault_file)
    try:
        assert _lock.is_locked(vault_file)
    finally:
        _lock.release(lp)


def test_is_locked_false_after_release(vault_file):
    lp = _lock.acquire(vault_file)
    _lock.release(lp)
    assert not _lock.is_locked(vault_file)


def test_owner_pid_matches_current_process(vault_file):
    lp = _lock.acquire(vault_file)
    try:
        assert _lock.owner_pid(vault_file) == os.getpid()
    finally:
        _lock.release(lp)


def test_acquire_times_out_when_already_locked(vault_file):
    lp = _lock.acquire(vault_file)
    try:
        with pytest.raises(_lock.LockError):
            _lock.acquire(vault_file, timeout=0.2, poll=0.05)
    finally:
        _lock.release(lp)


def test_release_is_idempotent(vault_file):
    lp = _lock.acquire(vault_file)
    _lock.release(lp)
    _lock.release(lp)  # should not raise


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_status_unlocked(runner, vault_file):
    result = runner.invoke(lock_cmd, ["status", "--vault", vault_file])
    assert result.exit_code == 0
    assert "UNLOCKED" in result.output


def test_cli_acquire_and_status_locked(runner, vault_file):
    result = runner.invoke(lock_cmd, ["acquire", "--vault", vault_file])
    assert result.exit_code == 0
    result2 = runner.invoke(lock_cmd, ["status", "--vault", vault_file])
    assert "LOCKED" in result2.output
    # cleanup
    _lock.release(_lock._lock_path(vault_file))


def test_cli_release(runner, vault_file):
    _lock.acquire(vault_file)
    result = runner.invoke(lock_cmd, ["release", "--vault", vault_file])
    assert result.exit_code == 0
    assert not _lock.is_locked(vault_file)


def test_cli_release_no_lock_exits_nonzero(runner, vault_file):
    result = runner.invoke(lock_cmd, ["release", "--vault", vault_file])
    assert result.exit_code != 0

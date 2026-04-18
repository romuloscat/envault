"""Tests for envault.watch."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from envault.watch import watch_and_run, WatchError


@pytest.fixture
def vault_file(tmp_path):
    from envault.store import set_secret
    vf = tmp_path / "test.vault"
    set_secret(str(vf), "password", "API_KEY", "hunter2")
    set_secret(str(vf), "password", "DB_URL", "postgres://localhost/db")
    return str(vf)


def test_watch_raises_on_empty_command(vault_file):
    with pytest.raises(WatchError, match="command must not be empty"):
        watch_and_run(vault_file, [], "password", max_cycles=1)


def test_watch_spawns_process_on_first_cycle(vault_file):
    with patch("envault.watch.subprocess.Popen") as mock_popen:
        watch_and_run(
            vault_file,
            ["echo", "hello"],
            "password",
            interval=0,
            max_cycles=1,
        )
        mock_popen.assert_called_once()
        _, kwargs = mock_popen.call_args
        assert "env" in kwargs
        assert kwargs["env"]["API_KEY"] == "hunter2"


def test_watch_does_not_respawn_when_unchanged(vault_file):
    with patch("envault.watch.subprocess.Popen") as mock_popen:
        watch_and_run(
            vault_file,
            ["echo", "hi"],
            "password",
            interval=0,
            max_cycles=3,
        )
        # Only called once because mtime doesn't change between cycles
        assert mock_popen.call_count == 1


def test_watch_respawns_when_mtime_changes(vault_file):
    mtimes = [1.0, 1.0, 2.0]
    call_iter = iter(mtimes)

    def fake_mtime(path):
        try:
            return next(call_iter)
        except StopIteration:
            return 2.0

    with patch("envault.watch._mtime", side_effect=fake_mtime):
        with patch("envault.watch.subprocess.Popen") as mock_popen:
            watch_and_run(
                vault_file,
                ["echo", "changed"],
                "password",
                interval=0,
                max_cycles=3,
            )
            assert mock_popen.call_count == 2


def test_watch_filters_env_keys(vault_file):
    with patch("envault.watch.subprocess.Popen") as mock_popen:
        watch_and_run(
            vault_file,
            ["printenv"],
            "password",
            interval=0,
            max_cycles=1,
            env_keys=["API_KEY"],
        )
        _, kwargs = mock_popen.call_args
        assert "API_KEY" in kwargs["env"]
        assert "DB_URL" not in kwargs["env"]


def test_watch_raises_on_bad_password(vault_file):
    with pytest.raises(WatchError, match="Failed to build env"):
        watch_and_run(
            vault_file,
            ["echo"],
            "wrong_password",
            interval=0,
            max_cycles=1,
        )

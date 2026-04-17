import json
import pytest
from pathlib import Path
from envault.hooks import (
    register_hook, unregister_hook, list_hooks, fire_hook,
    HookError, HOOK_EVENTS,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_register_hook_creates_entry(vault_file):
    register_hook(vault_file, "post_set", "echo set")
    hooks = list_hooks(vault_file)
    assert "post_set" in hooks
    assert "echo set" in hooks["post_set"]


def test_register_hook_idempotent(vault_file):
    register_hook(vault_file, "post_set", "echo set")
    register_hook(vault_file, "post_set", "echo set")
    assert list_hooks(vault_file)["post_set"].count("echo set") == 1


def test_register_multiple_hooks(vault_file):
    register_hook(vault_file, "post_set", "echo a")
    register_hook(vault_file, "post_set", "echo b")
    assert len(list_hooks(vault_file)["post_set"]) == 2


def test_register_invalid_event_raises(vault_file):
    with pytest.raises(HookError, match="Unknown event"):
        register_hook(vault_file, "on_explode", "echo x")


def test_unregister_hook(vault_file):
    register_hook(vault_file, "pre_delete", "echo del")
    unregister_hook(vault_file, "pre_delete", "echo del")
    hooks = list_hooks(vault_file)
    assert "pre_delete" not in hooks


def test_unregister_missing_raises(vault_file):
    with pytest.raises(HookError, match="not found"):
        unregister_hook(vault_file, "pre_set", "echo x")


def test_list_hooks_empty_when_no_file(vault_file):
    assert list_hooks(vault_file) == {}


def test_fire_hook_executes_command(vault_file, tmp_path):
    marker = tmp_path / "fired.txt"
    register_hook(vault_file, "post_set", f"touch {marker}")
    executed = fire_hook(vault_file, "post_set", "MY_KEY")
    assert marker.exists()
    assert len(executed) == 1


def test_fire_hook_no_commands_returns_empty(vault_file):
    result = fire_hook(vault_file, "post_get", "KEY")
    assert result == []


def test_fire_hook_failing_command_raises(vault_file):
    register_hook(vault_file, "pre_set", "exit 1")
    with pytest.raises(HookError, match="Hook command failed"):
        fire_hook(vault_file, "pre_set", "KEY")

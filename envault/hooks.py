"""Pre/post hooks for vault operations."""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional

HOOK_EVENTS = ("pre_set", "post_set", "pre_get", "post_get", "pre_delete", "post_delete")


class HookError(Exception):
    pass


def _hooks_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".hooks.json")


def _load_hooks(vault_path: str) -> Dict[str, List[str]]:
    p = _hooks_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_hooks(vault_path: str, hooks: Dict[str, List[str]]) -> None:
    p = _hooks_path(vault_path)
    with open(p, "w") as f:
        json.dump(hooks, f, indent=2)


def register_hook(vault_path: str, event: str, command: str) -> None:
    if event not in HOOK_EVENTS:
        raise HookError(f"Unknown event '{event}'. Valid: {HOOK_EVENTS}")
    hooks = _load_hooks(vault_path)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    _save_hooks(vault_path, hooks)


def unregister_hook(vault_path: str, event: str, command: str) -> None:
    hooks = _load_hooks(vault_path)
    if event not in hooks or command not in hooks[event]:
        raise HookError(f"Hook '{command}' not found for event '{event}'")
    hooks[event].remove(command)
    if not hooks[event]:
        del hooks[event]
    _save_hooks(vault_path, hooks)


def list_hooks(vault_path: str) -> Dict[str, List[str]]:
    return _load_hooks(vault_path)


def fire_hook(vault_path: str, event: str, key: str) -> List[str]:
    """Run all commands for the event. Returns list of commands executed."""
    hooks = _load_hooks(vault_path)
    commands = hooks.get(event, [])
    env = {**os.environ, "ENVAULT_EVENT": event, "ENVAULT_KEY": key}
    executed = []
    for cmd in commands:
        ret = os.system(f"ENVAULT_EVENT={event} ENVAULT_KEY={key} {cmd}")
        if ret != 0:
            raise HookError(f"Hook command failed (exit {ret}): {cmd}")
        executed.append(cmd)
    return executed

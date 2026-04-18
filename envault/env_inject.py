"""Inject decrypted secrets into a subprocess environment."""
from __future__ import annotations

import os
import subprocess
from typing import List, Optional

from envault.store import list_secrets, get_secret
from envault.ttl import is_expired


class InjectError(Exception):
    pass


def build_env(
    vault_path: str,
    password: str,
    keys: Optional[List[str]] = None,
    skip_expired: bool = True,
) -> dict:
    """Return a copy of the current environment augmented with vault secrets."""
    all_keys = list_secrets(vault_path, password)
    target_keys = keys if keys is not None else all_keys

    unknown = set(target_keys) - set(all_keys)
    if unknown:
        raise InjectError(f"Keys not found in vault: {', '.join(sorted(unknown))}")

    env = os.environ.copy()
    for key in target_keys:
        if skip_expired and is_expired(vault_path, key):
            continue
        env[key] = get_secret(vault_path, password, key)
    return env


def run_with_secrets(
    vault_path: str,
    password: str,
    command: List[str],
    keys: Optional[List[str]] = None,
    skip_expired: bool = True,
) -> int:
    """Run *command* with vault secrets injected; return the exit code."""
    if not command:
        raise InjectError("No command provided.")
    env = build_env(vault_path, password, keys=keys, skip_expired=skip_expired)
    result = subprocess.run(command, env=env)
    return result.returncode

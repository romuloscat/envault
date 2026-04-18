"""Watch a vault file for changes and run a command when secrets are updated."""

import os
import time
import subprocess
from typing import Optional


class WatchError(Exception):
    pass


def _mtime(path: str) -> Optional[float]:
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return None


def watch_and_run(
    vault_path: str,
    command: list[str],
    password: str,
    interval: float = 1.0,
    max_cycles: Optional[int] = None,
    env_keys: Optional[list[str]] = None,
) -> None:
    """Poll vault_path every `interval` seconds; re-run command when it changes.

    Args:
        vault_path: Path to the .vault file to watch.
        command: Shell command list passed to subprocess.
        password: Vault password used to decrypt secrets for the subprocess env.
        interval: Polling interval in seconds.
        max_cycles: Stop after this many poll cycles (None = run forever).
        env_keys: Specific keys to inject; None injects all keys.
    """
    from envault.env_inject import build_env

    if not command:
        raise WatchError("command must not be empty")

    last_mtime = None
    cycles = 0

    while True:
        current_mtime = _mtime(vault_path)

        if current_mtime != last_mtime:
            last_mtime = current_mtime
            try:
                env = build_env(vault_path, password, keys=env_keys)
            except Exception as exc:
                raise WatchError(f"Failed to build env: {exc}") from exc
            subprocess.Popen(command, env=env)

        cycles += 1
        if max_cycles is not None and cycles >= max_cycles:
            break

        time.sleep(interval)

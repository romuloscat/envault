"""Pin secrets to specific versions, preventing accidental overwrites."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


class PinError(Exception):
    pass


def _pin_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".pins.json")


def _load_pins(vault_file: str) -> dict:
    p = _pin_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(vault_file: str, pins: dict) -> None:
    _pin_path(vault_file).write_text(json.dumps(pins, indent=2))


def pin_secret(vault_file: str, key: str, reason: str = "") -> None:
    """Pin a key so it cannot be overwritten without explicit unpin."""
    pins = _load_pins(vault_file)
    if key in pins:
        return  # idempotent
    pins[key] = {"reason": reason}
    _save_pins(vault_file, pins)


def unpin_secret(vault_file: str, key: str) -> None:
    """Remove pin from a key."""
    pins = _load_pins(vault_file)
    if key not in pins:
        raise PinError(f"Key '{key}' is not pinned.")
    del pins[key]
    _save_pins(vault_file, pins)


def is_pinned(vault_file: str, key: str) -> bool:
    """Return True if the key is pinned."""
    return key in _load_pins(vault_file)


def list_pins(vault_file: str) -> List[dict]:
    """Return list of pinned keys with metadata."""
    pins = _load_pins(vault_file)
    return [{"key": k, "reason": v.get("reason", "")} for k, v in sorted(pins.items())]


def assert_not_pinned(vault_file: str, key: str) -> None:
    """Raise PinError if the key is pinned."""
    if is_pinned(vault_file, key):
        info = _load_pins(vault_file)[key]
        reason = info.get("reason", "")
        msg = f"Key '{key}' is pinned and cannot be modified."
        if reason:
            msg += f" Reason: {reason}"
        raise PinError(msg)

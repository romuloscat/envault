"""Quota management: enforce maximum number of secrets per vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.store import list_secrets


class QuotaError(Exception):
    """Raised when a quota operation fails."""


class QuotaExceeded(QuotaError):
    """Raised when adding a secret would exceed the configured quota."""


def _quota_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".quota.json")


def _load_quota(vault_path: str) -> dict:
    p = _quota_path(vault_path)
    if not p.exists():
        return {}
    with p.open() as fh:
        return json.load(fh)


def _save_quota(vault_path: str, data: dict) -> None:
    p = _quota_path(vault_path)
    with p.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_quota(vault_path: str, limit: int) -> None:
    """Set the maximum number of secrets allowed in the vault."""
    if limit < 1:
        raise QuotaError("Quota limit must be a positive integer.")
    data = _load_quota(vault_path)
    data["limit"] = limit
    _save_quota(vault_path, data)


def get_quota(vault_path: str) -> Optional[int]:
    """Return the configured quota limit, or None if not set."""
    data = _load_quota(vault_path)
    return data.get("limit")


def remove_quota(vault_path: str) -> None:
    """Remove the quota configuration for the vault."""
    p = _quota_path(vault_path)
    if not p.exists():
        raise QuotaError("No quota configured for this vault.")
    p.unlink()


def check_quota(vault_path: str, password: str) -> None:
    """Raise QuotaExceeded if the vault is at or over its limit."""
    limit = get_quota(vault_path)
    if limit is None:\n    current = len(list_secrets(vault_path, password))
    if current >= limit:
        raise QuotaExceeded(
            f"Vault has reached its quota of {limit} secret(s) "
            f"(current: {current})."
        )


def quota_status(vault_path: str, password: str) -> dict:
    """Return a dict with 'limit', 'used', and 'available' fields."""
    limit = get_quota(vault_path)
    used = len(list_secrets(vault_path, password))
    return {
        "limit": limit,
        "used": used,
        "available": (limit - used) if limit is not None else None,
    }

"""Lint vault secrets for common issues (weak keys, expired TTLs, untagged secrets)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List

from envault.store import list_secrets
from envault.ttl import get_expiry, is_expired
from envault.tags import get_tags


class LintError(Exception):
    pass


@dataclass
class LintIssue:
    key: str
    level: str  # 'warning' | 'error'
    message: str


_WEAK_KEY_PATTERN = re.compile(r'^(secret|password|key|token|test|tmp|temp)$', re.IGNORECASE)
_VALID_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')


def lint_vault(vault_path, password: str) -> List[LintIssue]:
    """Run all lint checks and return a list of LintIssue."""
    issues: List[LintIssue] = []
    try:
        keys = list_secrets(vault_path, password)
    except Exception as exc:
        raise LintError(f"Could not open vault: {exc}") from exc

    for key in keys:
        # Naming convention
        if not _VALID_KEY_PATTERN.match(key):
            issues.append(LintIssue(key, 'warning', 'Key should be UPPER_SNAKE_CASE'))

        # Generic / weak key names
        if _WEAK_KEY_PATTERN.match(key):
            issues.append(LintIssue(key, 'warning', 'Key name is too generic'))

        # Expired TTL
        expiry = get_expiry(vault_path, key)
        if expiry is not None and is_expired(vault_path, key):
            issues.append(LintIssue(key, 'error', f'Secret expired at {expiry}'))

        # No tags
        tags = get_tags(vault_path, key)
        if not tags:
            issues.append(LintIssue(key, 'warning', 'Secret has no tags'))

    return issues

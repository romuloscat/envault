"""Policy enforcement: define rules that secrets must satisfy."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

from envault.store import list_secrets, get_secret


class PolicyError(Exception):
    pass


class PolicyViolation(Exception):
    def __init__(self, violations: list[str]):
        self.violations = violations
        super().__init__("Policy violations found:\n" + "\n".join(violations))


def _policy_path(vault_file: str) -> Path:
    return Path(vault_file).with_suffix(".policy.json")


def _load_policies(vault_file: str) -> dict[str, Any]:
    p = _policy_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policies(vault_file: str, data: dict[str, Any]) -> None:
    _policy_path(vault_file).write_text(json.dumps(data, indent=2))


_VALID_RULES = {"min_length", "max_length", "pattern", "required"}


def set_policy(vault_file: str, key: str, rules: dict[str, Any]) -> None:
    """Attach validation rules to a key."""
    unknown = set(rules) - _VALID_RULES
    if unknown:
        raise PolicyError(f"Unknown rule(s): {', '.join(sorted(unknown))}")
    data = _load_policies(vault_file)
    data[key] = rules
    _save_policies(vault_file, data)


def remove_policy(vault_file: str, key: str) -> None:
    data = _load_policies(vault_file)
    if key not in data:
        raise PolicyError(f"No policy for key '{key}'")
    del data[key]
    _save_policies(vault_file, data)


def get_policy(vault_file: str, key: str) -> dict[str, Any] | None:
    return _load_policies(vault_file).get(key)


def enforce_policies(vault_file: str, password: str) -> list[str]:
    """Check all policies against live vault values. Returns list of violation messages."""
    data = _load_policies(vault_file)
    violations: list[str] = []
    keys = list_secrets(vault_file)
    for key, rules in data.items():
        if rules.get("required") and key not in keys:
            violations.append(f"{key}: required but missing")
            continue
        if key not in keys:
            continue
        value = get_secret(vault_file, key, password)
        if "min_length" in rules and len(value) < rules["min_length"]:
            violations.append(f"{key}: value too short (min {rules['min_length']})")
        if "max_length" in rules and len(value) > rules["max_length"]:
            violations.append(f"{key}: value too long (max {rules['max_length']})")
        if "pattern" in rules and not re.search(rules["pattern"], value):
            violations.append(f"{key}: value does not match pattern '{rules['pattern']}'")
    return violations

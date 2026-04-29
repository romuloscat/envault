"""Workflow: define ordered sequences of keys that must all be present and valid."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.store import get_secret


class WorkflowError(Exception):
    pass


class WorkflowViolation(Exception):
    def __init__(self, workflow: str, missing: List[str]) -> None:
        self.workflow = workflow
        self.missing = missing
        super().__init__(
            f"Workflow '{workflow}' violated: missing keys {missing}"
        )


def _workflow_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".workflows.json")


def _load_workflows(vault_path: str) -> Dict[str, List[str]]:
    p = _workflow_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_workflows(vault_path: str, data: Dict[str, List[str]]) -> None:
    _workflow_path(vault_path).write_text(json.dumps(data, indent=2))


def set_workflow(vault_path: str, name: str, keys: List[str]) -> None:
    """Define or overwrite a named workflow with an ordered list of keys."""
    if not name:
        raise WorkflowError("Workflow name must not be empty.")
    if not keys:
        raise WorkflowError("Workflow must contain at least one key.")
    data = _load_workflows(vault_path)
    data[name] = list(keys)
    _save_workflows(vault_path, data)


def remove_workflow(vault_path: str, name: str) -> None:
    """Delete a named workflow."""
    data = _load_workflows(vault_path)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    del data[name]
    _save_workflows(vault_path, data)


def get_workflow(vault_path: str, name: str) -> Optional[List[str]]:
    """Return the key list for a workflow, or None if not defined."""
    return _load_workflows(vault_path).get(name)


def list_workflows(vault_path: str) -> List[str]:
    """Return sorted list of workflow names."""
    return sorted(_load_workflows(vault_path).keys())


def validate_workflow(vault_path: str, name: str, password: str) -> List[str]:
    """Check that every key in the workflow exists in the vault.

    Returns the list of present keys in order.
    Raises WorkflowViolation if any keys are missing.
    """
    data = _load_workflows(vault_path)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    keys = data[name]
    missing = []
    for key in keys:
        try:
            get_secret(vault_path, key, password)
        except Exception:
            missing.append(key)
    if missing:
        raise WorkflowViolation(name, missing)
    return keys

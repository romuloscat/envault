"""Tests for envault.workflow."""

from __future__ import annotations

import pytest

from envault.store import set_secret
from envault.workflow import (
    WorkflowError,
    WorkflowViolation,
    get_workflow,
    list_workflows,
    remove_workflow,
    set_workflow,
    validate_workflow,
)

PASSWORD = "test-pass"


@pytest.fixture()
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_set_and_get_workflow(vault_file):
    set_workflow(vault_file, "deploy", ["DB_URL", "API_KEY"])
    keys = get_workflow(vault_file, "deploy")
    assert keys == ["DB_URL", "API_KEY"]


def test_get_workflow_missing_returns_none(vault_file):
    assert get_workflow(vault_file, "nonexistent") is None


def test_set_workflow_empty_name_raises(vault_file):
    with pytest.raises(WorkflowError, match="empty"):
        set_workflow(vault_file, "", ["KEY"])


def test_set_workflow_empty_keys_raises(vault_file):
    with pytest.raises(WorkflowError, match="at least one"):
        set_workflow(vault_file, "deploy", [])


def test_set_workflow_overwrites(vault_file):
    set_workflow(vault_file, "deploy", ["A", "B"])
    set_workflow(vault_file, "deploy", ["C"])
    assert get_workflow(vault_file, "deploy") == ["C"]


def test_remove_workflow(vault_file):
    set_workflow(vault_file, "deploy", ["A"])
    remove_workflow(vault_file, "deploy")
    assert get_workflow(vault_file, "deploy") is None


def test_remove_missing_workflow_raises(vault_file):
    with pytest.raises(WorkflowError, match="not found"):
        remove_workflow(vault_file, "ghost")


def test_list_workflows_empty(vault_file):
    assert list_workflows(vault_file) == []


def test_list_workflows_sorted(vault_file):
    set_workflow(vault_file, "zebra", ["Z"])
    set_workflow(vault_file, "alpha", ["A"])
    assert list_workflows(vault_file) == ["alpha", "zebra"]


def test_validate_workflow_all_present(vault_file):
    set_secret(vault_file, "DB_URL", "postgres://", PASSWORD)
    set_secret(vault_file, "API_KEY", "abc123", PASSWORD)
    set_workflow(vault_file, "deploy", ["DB_URL", "API_KEY"])
    keys = validate_workflow(vault_file, "deploy", PASSWORD)
    assert keys == ["DB_URL", "API_KEY"]


def test_validate_workflow_missing_key_raises(vault_file):
    set_secret(vault_file, "DB_URL", "postgres://", PASSWORD)
    set_workflow(vault_file, "deploy", ["DB_URL", "MISSING_KEY"])
    with pytest.raises(WorkflowViolation) as exc_info:
        validate_workflow(vault_file, "deploy", PASSWORD)
    assert "MISSING_KEY" in exc_info.value.missing
    assert exc_info.value.workflow == "deploy"


def test_validate_unknown_workflow_raises(vault_file):
    with pytest.raises(WorkflowError, match="not found"):
        validate_workflow(vault_file, "ghost", PASSWORD)

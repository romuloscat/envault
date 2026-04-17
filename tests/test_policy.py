"""Tests for envault.policy"""
import pytest
from pathlib import Path
from envault.store import set_secret
from envault.policy import (
    set_policy, remove_policy, get_policy, enforce_policies, PolicyError
)

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.env")


def test_set_and_get_policy(vault_file):
    set_policy(vault_file, "API_KEY", {"min_length": 8})
    rules = get_policy(vault_file, "API_KEY")
    assert rules == {"min_length": 8}


def test_set_policy_unknown_rule_raises(vault_file):
    with pytest.raises(PolicyError, match="Unknown rule"):
        set_policy(vault_file, "KEY", {"nonexistent": 1})


def test_remove_policy(vault_file):
    set_policy(vault_file, "X", {"required": True})
    remove_policy(vault_file, "X")
    assert get_policy(vault_file, "X") is None


def test_remove_missing_policy_raises(vault_file):
    with pytest.raises(PolicyError, match="No policy"):
        remove_policy(vault_file, "GHOST")


def test_get_policy_no_file_returns_none(vault_file):
    assert get_policy(vault_file, "ANYTHING") is None


def test_enforce_min_length_pass(vault_file):
    set_secret(vault_file, "TOKEN", "supersecret", PASSWORD)
    set_policy(vault_file, "TOKEN", {"min_length": 5})
    violations = enforce_policies(vault_file, PASSWORD)
    assert violations == []


def test_enforce_min_length_fail(vault_file):
    set_secret(vault_file, "TOKEN", "abc", PASSWORD)
    set_policy(vault_file, "TOKEN", {"min_length": 8})
    violations = enforce_policies(vault_file, PASSWORD)
    assert any("too short" in v for v in violations)


def test_enforce_max_length_fail(vault_file):
    set_secret(vault_file, "TOKEN", "verylongvalue", PASSWORD)
    set_policy(vault_file, "TOKEN", {"max_length": 5})
    violations = enforce_policies(vault_file, PASSWORD)
    assert any("too long" in v for v in violations)


def test_enforce_pattern_pass(vault_file):
    set_secret(vault_file, "PORT", "8080", PASSWORD)
    set_policy(vault_file, "PORT", {"pattern": r"^\d+$"})
    assert enforce_policies(vault_file, PASSWORD) == []


def test_enforce_pattern_fail(vault_file):
    set_secret(vault_file, "PORT", "abc", PASSWORD)
    set_policy(vault_file, "PORT", {"pattern": r"^\d+$"})
    violations = enforce_policies(vault_file, PASSWORD)
    assert any("pattern" in v for v in violations)


def test_enforce_required_missing(vault_file):
    set_policy(vault_file, "MUST_EXIST", {"required": True})
    violations = enforce_policies(vault_file, PASSWORD)
    assert any("required but missing" in v for v in violations)


def test_enforce_required_present(vault_file):
    set_secret(vault_file, "MUST_EXIST", "value", PASSWORD)
    set_policy(vault_file, "MUST_EXIST", {"required": True})
    assert enforce_policies(vault_file, PASSWORD) == []

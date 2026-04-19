import pytest
import json
from pathlib import Path
from envault.dependency import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    all_dependencies,
    DependencyError,
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


def test_add_and_get_dependency(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_PASS")
    assert get_dependencies(vault_file, "DB_URL") == ["DB_PASS"]


def test_add_multiple_dependencies(vault_file):
    add_dependency(vault_file, "APP_DSN", "DB_HOST")
    add_dependency(vault_file, "APP_DSN", "DB_PORT")
    deps = get_dependencies(vault_file, "APP_DSN")
    assert "DB_HOST" in deps
    assert "DB_PORT" in deps


def test_add_dependency_idempotent(vault_file):
    add_dependency(vault_file, "A", "B")
    add_dependency(vault_file, "A", "B")
    assert get_dependencies(vault_file, "A").count("B") == 1


def test_self_dependency_raises(vault_file):
    with pytest.raises(DependencyError):
        add_dependency(vault_file, "KEY", "KEY")


def test_remove_dependency(vault_file):
    add_dependency(vault_file, "X", "Y")
    remove_dependency(vault_file, "X", "Y")
    assert get_dependencies(vault_file, "X") == []


def test_remove_missing_dependency_raises(vault_file):
    with pytest.raises(DependencyError):
        remove_dependency(vault_file, "X", "Y")


def test_get_dependents(vault_file):
    add_dependency(vault_file, "APP", "SECRET")
    add_dependency(vault_file, "WORKER", "SECRET")
    dependents = get_dependents(vault_file, "SECRET")
    assert "APP" in dependents
    assert "WORKER" in dependents


def test_get_dependents_empty(vault_file):
    assert get_dependents(vault_file, "ORPHAN") == []


def test_all_dependencies_returns_full_map(vault_file):
    add_dependency(vault_file, "A", "B")
    add_dependency(vault_file, "C", "D")
    result = all_dependencies(vault_file)
    assert "A" in result
    assert "C" in result


def test_remove_last_dep_cleans_key(vault_file):
    add_dependency(vault_file, "A", "B")
    remove_dependency(vault_file, "A", "B")
    data = all_dependencies(vault_file)
    assert "A" not in data

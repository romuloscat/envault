import json
import pytest
from pathlib import Path
from envault.schema import (
    set_schema, remove_schema, validate_value, validate_vault,
    get_schema, SchemaError, SchemaViolation
)


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_and_get_schema(vault_file):
    set_schema(vault_file, "PORT", "integer")
    schema = get_schema(vault_file)
    assert "PORT" in schema
    assert schema["PORT"]["type"] == "integer"


def test_set_schema_unknown_type_raises(vault_file):
    with pytest.raises(SchemaError, match="Unsupported type"):
        set_schema(vault_file, "KEY", "uuid")


def test_remove_schema(vault_file):
    set_schema(vault_file, "API_KEY", "string")
    remove_schema(vault_file, "API_KEY")
    assert "API_KEY" not in get_schema(vault_file)


def test_remove_missing_schema_raises(vault_file):
    with pytest.raises(SchemaError, match="No schema defined"):
        remove_schema(vault_file, "NONEXISTENT")


def test_validate_value_integer_ok():
    validate_value("PORT", "8080", {"type": "integer"})


def test_validate_value_integer_fail():
    with pytest.raises(SchemaViolation, match="PORT"):
        validate_value("PORT", "not-a-number", {"type": "integer"})


def test_validate_value_url_ok():
    validate_value("ENDPOINT", "https://example.com/api", {"type": "url"})


def test_validate_value_url_fail():
    with pytest.raises(SchemaViolation):
        validate_value("ENDPOINT", "not-a-url", {"type": "url"})


def test_validate_value_email_ok():
    validate_value("ADMIN", "admin@example.com", {"type": "email"})


def test_validate_value_email_fail():
    with pytest.raises(SchemaViolation):
        validate_value("ADMIN", "not-an-email", {"type": "email"})


def test_validate_value_boolean_ok():
    for val in ("true", "false", "1", "0", "yes", "no", "True", "YES"):
        validate_value("FLAG", val, {"type": "boolean"})


def test_validate_vault_required_missing(vault_file):
    set_schema(vault_file, "DB_URL", "url", required=True)
    issues = validate_vault(vault_file, {})
    assert any(i.key == "DB_URL" and "required" in i.reason for i in issues)


def test_validate_vault_type_mismatch(vault_file):
    set_schema(vault_file, "PORT", "integer")
    issues = validate_vault(vault_file, {"PORT": "abc"})
    assert len(issues) == 1
    assert issues[0].key == "PORT"


def test_validate_vault_no_issues(vault_file):
    set_schema(vault_file, "PORT", "integer")
    set_schema(vault_file, "HOST", "string")
    issues = validate_vault(vault_file, {"PORT": "3000", "HOST": "localhost"})
    assert issues == []

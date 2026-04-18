"""Schema validation for vault secrets — enforce type/format rules on values."""

import re
from pathlib import Path
from typing import Any

SCHEMA_FILE = ".envault_schema.json"

SUPPORTED_TYPES = {"string", "integer", "boolean", "url", "email"}

_PATTERNS = {
    "url": re.compile(r"^https?://[^\s]+$"),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "integer": re.compile(r"^-?\d+$"),
    "boolean": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
}


class SchemaError(Exception):
    pass


class SchemaViolation(Exception):
    def __init__(self, key: str, reason: str):
        self.key = key
        self.reason = reason
        super().__init__(f"{key}: {reason}")


def _schema_path(vault_path: str) -> Path:
    return Path(vault_path).parent / SCHEMA_FILE


def _load_schema(vault_path: str) -> dict:
    import json
    p = _schema_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_schema(vault_path: str, schema: dict) -> None:
    import json
    p = _schema_path(vault_path)
    p.write_text(json.dumps(schema, indent=2))


def set_schema(vault_path: str, key: str, type_: str, required: bool = False) -> None:
    if type_ not in SUPPORTED_TYPES:
        raise SchemaError(f"Unsupported type '{type_}'. Choose from: {', '.join(sorted(SUPPORTED_TYPES))}")
    schema = _load_schema(vault_path)
    schema[key] = {"type": type_, "required": required}
    _save_schema(vault_path, schema)


def remove_schema(vault_path: str, key: str) -> None:
    schema = _load_schema(vault_path)
    if key not in schema:
        raise SchemaError(f"No schema defined for key '{key}'")
    del schema[key]
    _save_schema(vault_path, schema)


def validate_value(key: str, value: str, rule: dict) -> None:
    type_ = rule.get("type", "string")
    if type_ == "string":
        return
    pattern = _PATTERNS.get(type_)
    if pattern and not pattern.match(value):
        raise SchemaViolation(key, f"value does not match type '{type_}'")


def validate_vault(vault_path: str, secrets: dict[str, str]) -> list[SchemaViolation]:
    schema = _load_schema(vault_path)
    issues = []
    for key, rule in schema.items():
        if rule.get("required") and key not in secrets:
            issues.append(SchemaViolation(key, "required key is missing"))
            continue
        if key in secrets:
            try:
                validate_value(key, secrets[key], rule)
            except SchemaViolation as e:
                issues.append(e)
    return issues


def get_schema(vault_path: str) -> dict:
    return _load_schema(vault_path)

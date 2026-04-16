"""Import secrets from external formats (.env, JSON) into the vault."""

import json
import re
from pathlib import Path
from typing import Dict


def parse_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env file content into a dict of key/value pairs."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        # Strip optional surrounding quotes
        for quote in ('"', "'"):
            if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
                value = value[1:-1]
                break
        result[key] = value
    return result


def parse_json(text: str) -> Dict[str, str]:
    """Parse a JSON object into a dict of key/value pairs (values coerced to str)."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON input must be a top-level object")
    return {k: str(v) for k, v in data.items()}


def import_secrets(source: str, fmt: str, vault_path: str, password: str) -> int:
    """Read secrets from *source* file and store them in the vault.

    Returns the number of secrets imported.
    """
    from envault.store import set_secret

    text = Path(source).read_text(encoding="utf-8")
    if fmt == "dotenv":
        secrets = parse_dotenv(text)
    elif fmt == "json":
        secrets = parse_json(text)
    else:
        raise ValueError(f"Unsupported import format: {fmt}")

    for key, value in secrets.items():
        set_secret(vault_path, password, key, value)

    return len(secrets)

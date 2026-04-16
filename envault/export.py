"""Export vault secrets to various shell formats."""

from __future__ import annotations

from typing import Dict

SUPPORTED_FORMATS = ("dotenv", "bash", "json")


def export_secrets(secrets: Dict[str, str], fmt: str = "dotenv") -> str:
    """Render decrypted secrets dict into the requested format string."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    if fmt == "dotenv":
        return _to_dotenv(secrets)
    elif fmt == "bash":
        return _to_bash(secrets)
    elif fmt == "json":
        return _to_json(secrets)


def _to_dotenv(secrets: Dict[str, str]) -> str:
    lines = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def _to_bash(secrets: Dict[str, str]) -> str:
    lines = ["#!/usr/bin/env bash"]
    for key, value in sorted(secrets.items()):
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines)


def _to_json(secrets: Dict[str, str]) -> str:
    import json
    return json.dumps(secrets, indent=2, sort_keys=True)

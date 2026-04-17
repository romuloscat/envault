"""Template rendering: substitute secrets into template strings."""
from __future__ import annotations
import re
from pathlib import Path
from envault.store import get_secret


class TemplateError(Exception):
    pass


_PATTERN = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


def render_string(template: str, password: str, vault_file: str) -> str:
    """Replace {{KEY}} placeholders with decrypted secrets from the vault."""
    missing: list[str] = []

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        try:
            return get_secret(vault_file, key, password)
        except KeyError:
            missing.append(key)
            return match.group(0)

    result = _PATTERN.sub(_replace, template)
    if missing:
        raise TemplateError(f"Missing secrets for keys: {', '.join(missing)}")
    return result


def render_file(src: str, dst: str, password: str, vault_file: str) -> int:
    """Render a template file and write output to dst. Returns substitution count."""
    content = Path(src).read_text()
    keys_found = _PATTERN.findall(content)
    rendered = render_string(content, password, vault_file)
    Path(dst).write_text(rendered)
    return len(keys_found)

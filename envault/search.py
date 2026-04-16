"""Search and filter secrets in a vault by key pattern or value content."""

import fnmatch
import re
from typing import Optional

from envault.store import list_secrets, get_secret


class SearchError(Exception):
    pass


def search_secrets(
    vault_path: str,
    password: str,
    pattern: str,
    search_values: bool = False,
    regex: bool = False,
) -> dict[str, str]:
    """Return secrets whose keys (or optionally values) match *pattern*.

    Args:
        vault_path: Path to the vault file.
        password: Master password for decryption.
        pattern: Glob pattern (default) or regex string when *regex* is True.
        search_values: Also match against decrypted values.
        regex: Treat *pattern* as a regular expression instead of a glob.

    Returns:
        Mapping of matching key -> decrypted value.
    """
    keys = list_secrets(vault_path)
    if not keys:
        return {}

    try:
        if regex:
            compiled = re.compile(pattern)
            key_match = lambda k: bool(compiled.search(k))
            val_match = lambda v: bool(compiled.search(v))
        else:
            key_match = lambda k: fnmatch.fnmatch(k, pattern)
            val_match = lambda v: fnmatch.fnmatch(v, pattern)
    except re.error as exc:
        raise SearchError(f"Invalid regex pattern: {exc}") from exc

    results: dict[str, str] = {}
    for key in keys:
        value = get_secret(vault_path, key, password)
        if key_match(key) or (search_values and val_match(value)):
            results[key] = value

    return results

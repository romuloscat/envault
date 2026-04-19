"""Namespace support: group secrets under logical prefixes (e.g. 'prod/DB_URL')."""

from __future__ import annotations

SEP = "/"


class NamespaceError(Exception):
    pass


def join(namespace: str, key: str) -> str:
    """Return a namespaced key like 'prod/DB_URL'."""
    namespace = namespace.strip(SEP)
    key = key.strip(SEP)
    if not namespace:
        raise NamespaceError("Namespace must not be empty.")
    if not key:
        raise NamespaceError("Key must not be empty.")
    return f"{namespace}{SEP}{key}"


def split(namespaced_key: str) -> tuple[str, str]:
    """Split 'prod/DB_URL' into ('prod', 'DB_URL').
    Returns ('', key) if no namespace prefix is present.
    """
    if SEP not in namespaced_key:
        return "", namespaced_key
    namespace, _, key = namespaced_key.partition(SEP)
    return namespace, key


def filter_by_namespace(keys: list[str], namespace: str) -> list[str]:
    """Return only keys that belong to the given namespace."""
    prefix = namespace.strip(SEP) + SEP
    return [k for k in keys if k.startswith(prefix)]


def strip_namespace(namespaced_key: str) -> str:
    """Return the bare key, removing any namespace prefix."""
    _, key = split(namespaced_key)
    return key


def list_namespaces(keys: list[str]) -> list[str]:
    """Return a sorted, deduplicated list of namespaces present in keys."""
    namespaces = set()
    for k in keys:
        ns, _ = split(k)
        if ns:
            namespaces.add(ns)
    return sorted(namespaces)

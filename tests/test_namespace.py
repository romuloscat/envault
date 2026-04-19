import pytest
from envault.namespace import (
    join, split, filter_by_namespace, strip_namespace,
    list_namespaces, NamespaceError,
)


def test_join_basic():
    assert join("prod", "DB_URL") == "prod/DB_URL"


def test_join_strips_slashes():
    assert join("/prod/", "/DB_URL/") == "prod/DB_URL"


def test_join_empty_namespace_raises():
    with pytest.raises(NamespaceError):
        join("", "DB_URL")


def test_join_empty_key_raises():
    with pytest.raises(NamespaceError):
        join("prod", "")


def test_split_with_namespace():
    assert split("prod/DB_URL") == ("prod", "DB_URL")


def test_split_without_namespace():
    assert split("DB_URL") == ("", "DB_URL")


def test_filter_by_namespace():
    keys = ["prod/DB_URL", "prod/SECRET", "staging/DB_URL", "BARE_KEY"]
    assert filter_by_namespace(keys, "prod") == ["prod/DB_URL", "prod/SECRET"]


def test_filter_by_namespace_no_match():
    keys = ["prod/DB_URL", "staging/SECRET"]
    assert filter_by_namespace(keys, "dev") == []


def test_strip_namespace():
    assert strip_namespace("prod/DB_URL") == "DB_URL"


def test_strip_namespace_no_prefix():
    assert strip_namespace("DB_URL") == "DB_URL"


def test_list_namespaces():
    keys = ["prod/A", "prod/B", "staging/C", "BARE"]
    assert list_namespaces(keys) == ["prod", "staging"]


def test_list_namespaces_empty():
    assert list_namespaces(["BARE_KEY"]) == []


def test_list_namespaces_deduplicates():
    keys = ["prod/A", "prod/B", "prod/C"]
    assert list_namespaces(keys) == ["prod"]

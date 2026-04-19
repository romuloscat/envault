import pytest
from pathlib import Path
from envault.label import set_label, remove_label, get_labels, find_by_label, LabelError


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_set_and_get_label(vault_file):
    set_label(vault_file, "DB_URL", "env", "production")
    labels = get_labels(vault_file, "DB_URL")
    assert labels["env"] == "production"


def test_set_multiple_labels(vault_file):
    set_label(vault_file, "API_KEY", "env", "staging")
    set_label(vault_file, "API_KEY", "owner", "team-a")
    labels = get_labels(vault_file, "API_KEY")
    assert labels == {"env": "staging", "owner": "team-a"}


def test_set_label_overwrites(vault_file):
    set_label(vault_file, "SECRET", "env", "dev")
    set_label(vault_file, "SECRET", "env", "prod")
    assert get_labels(vault_file, "SECRET")["env"] == "prod"


def test_get_labels_missing_key_returns_empty(vault_file):
    assert get_labels(vault_file, "MISSING") == {}


def test_remove_label(vault_file):
    set_label(vault_file, "TOKEN", "env", "prod")
    remove_label(vault_file, "TOKEN", "env")
    assert get_labels(vault_file, "TOKEN") == {}


def test_remove_last_label_cleans_key(vault_file):
    set_label(vault_file, "X", "a", "1")
    remove_label(vault_file, "X", "a")
    data = get_labels(vault_file, "X")
    assert data == {}


def test_remove_missing_label_raises(vault_file):
    set_label(vault_file, "KEY", "env", "dev")
    with pytest.raises(LabelError):
        remove_label(vault_file, "KEY", "nonexistent")


def test_remove_label_missing_key_raises(vault_file):
    with pytest.raises(LabelError):
        remove_label(vault_file, "GHOST", "env")


def test_find_by_label_no_value(vault_file):
    set_label(vault_file, "A", "env", "prod")
    set_label(vault_file, "B", "env", "dev")
    set_label(vault_file, "C", "owner", "me")
    result = find_by_label(vault_file, "env")
    assert result == ["A", "B"]


def test_find_by_label_with_value(vault_file):
    set_label(vault_file, "A", "env", "prod")
    set_label(vault_file, "B", "env", "dev")
    result = find_by_label(vault_file, "env", "prod")
    assert result == ["A"]


def test_find_by_label_no_match_returns_empty(vault_file):
    assert find_by_label(vault_file, "env") == []

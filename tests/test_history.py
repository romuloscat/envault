"""Tests for envault.history"""

import time
import pytest
from pathlib import Path
from envault.history import (
    record_event,
    get_history,
    clear_history,
    HistoryError,
    _history_path,
)


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


def test_record_set_creates_history_file(vault_file):
    record_event(vault_file, "API_KEY", "set")
    assert _history_path(vault_file).exists()


def test_get_history_returns_empty_for_unknown_key(vault_file):
    assert get_history(vault_file, "MISSING") == []


def test_record_and_get_single_event(vault_file):
    before = time.time()
    record_event(vault_file, "API_KEY", "set")
    events = get_history(vault_file, "API_KEY")
    assert len(events) == 1
    assert events[0]["action"] == "set"
    assert events[0]["timestamp"] >= before


def test_multiple_events_appended_in_order(vault_file):
    record_event(vault_file, "DB_PASS", "set")
    record_event(vault_file, "DB_PASS", "set")
    record_event(vault_file, "DB_PASS", "delete")
    events = get_history(vault_file, "DB_PASS")
    assert len(events) == 3
    assert events[-1]["action"] == "delete"


def test_actor_recorded_when_provided(vault_file):
    record_event(vault_file, "TOKEN", "set", actor="alice")
    events = get_history(vault_file, "TOKEN")
    assert events[0]["actor"] == "alice"


def test_actor_absent_when_not_provided(vault_file):
    record_event(vault_file, "TOKEN", "set")
    events = get_history(vault_file, "TOKEN")
    assert "actor" not in events[0]


def test_invalid_action_raises(vault_file):
    with pytest.raises(HistoryError, match="Unknown action"):
        record_event(vault_file, "KEY", "update")


def test_clear_history_for_specific_key(vault_file):
    record_event(vault_file, "A", "set")
    record_event(vault_file, "B", "set")
    removed = clear_history(vault_file, "A")
    assert removed == 1
    assert get_history(vault_file, "A") == []
    assert len(get_history(vault_file, "B")) == 1


def test_clear_all_history(vault_file):
    record_event(vault_file, "A", "set")
    record_event(vault_file, "B", "set")
    record_event(vault_file, "B", "delete")
    removed = clear_history(vault_file)
    assert removed == 3
    assert get_history(vault_file, "A") == []
    assert get_history(vault_file, "B") == []


def test_clear_missing_key_returns_zero(vault_file):
    assert clear_history(vault_file, "NONEXISTENT") == 0

"""Tests for envault.audit module."""

import pytest
from pathlib import Path
from envault.audit import log_event, read_events, clear_events


@pytest.fixture
def audit_file(tmp_path):
    return str(tmp_path / "test_audit.log")


def test_log_creates_file(audit_file):
    log_event("set", "MY_KEY", "vault.json", audit_file=audit_file)
    assert Path(audit_file).exists()


def test_log_event_fields(audit_file):
    log_event("set", "DB_PASS", "vault.json", success=True, audit_file=audit_file)
    events = read_events(audit_file=audit_file)
    assert len(events) == 1
    ev = events[0]
    assert ev["action"] == "set"
    assert ev["key"] == "DB_PASS"
    assert ev["vault"] == "vault.json"
    assert ev["success"] is True
    assert "timestamp" in ev


def test_multiple_events_appended(audit_file):
    log_event("set", "A", "vault.json", audit_file=audit_file)
    log_event("get", "A", "vault.json", audit_file=audit_file)
    log_event("delete", "A", "vault.json", audit_file=audit_file)
    events = read_events(audit_file=audit_file)
    assert len(events) == 3
    assert [e["action"] for e in events] == ["set", "get", "delete"]


def test_read_events_empty_when_no_file(audit_file):
    events = read_events(audit_file=audit_file)
    assert events == []


def test_clear_events_removes_log(audit_file):
    log_event("set", "X", "vault.json", audit_file=audit_file)
    clear_events(audit_file=audit_file)
    assert not Path(audit_file).exists()
    assert read_events(audit_file=audit_file) == []


def test_clear_events_no_file_is_safe(audit_file):
    # Should not raise even if file doesn't exist
    clear_events(audit_file=audit_file)


def test_failed_event_recorded(audit_file):
    log_event("get", "MISSING", "vault.json", success=False, audit_file=audit_file)
    events = read_events(audit_file=audit_file)
    assert events[0]["success"] is False

"""Audit log for envault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_AUDIT_FILE = ".envault_audit.log"


def _audit_path(audit_file: Optional[str] = None) -> Path:
    return Path(audit_file or DEFAULT_AUDIT_FILE)


def log_event(
    action: str,
    key: str,
    vault_file: str,
    success: bool = True,
    audit_file: Optional[str] = None,
) -> None:
    """Append a single audit event to the audit log."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "vault": str(vault_file),
        "success": success,
    }
    path = _audit_path(audit_file)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_events(audit_file: Optional[str] = None) -> list:
    """Return all audit events as a list of dicts."""
    path = _audit_path(audit_file)
    if not path.exists():
        return []
    events = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def clear_events(audit_file: Optional[str] = None) -> None:
    """Clear the audit log."""
    path = _audit_path(audit_file)
    if path.exists():
        path.unlink()

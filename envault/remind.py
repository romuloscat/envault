"""Rotation reminders: warn when secrets haven't been rotated in N days."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

REMIND_FILE = ".envault_remind.json"


class RemindError(Exception):
    pass


@dataclass
class ReminderIssue:
    key: str
    last_rotated: float
    days_overdue: int


def _remind_path(vault_file: str) -> Path:
    return Path(vault_file).parent / REMIND_FILE


def _load_remind(vault_file: str) -> dict:
    p = _remind_path(vault_file)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_remind(vault_file: str, data: dict) -> None:
    _remind_path(vault_file).write_text(json.dumps(data, indent=2))


def record_rotation(vault_file: str, key: str, ts: Optional[float] = None) -> None:
    """Record that a key was rotated now (or at given timestamp)."""
    data = _load_remind(vault_file)
    data[key] = ts if ts is not None else time.time()
    _save_remind(vault_file, data)


def remove_reminder(vault_file: str, key: str) -> None:
    data = _load_remind(vault_file)
    if key not in data:
        raise RemindError(f"No rotation record for key: {key}")
    del data[key]
    _save_remind(vault_file, data)


def check_reminders(vault_file: str, max_days: int) -> List[ReminderIssue]:
    """Return keys overdue for rotation beyond max_days."""
    data = _load_remind(vault_file)
    now = time.time()
    issues: List[ReminderIssue] = []
    for key, ts in data.items():
        age_days = int((now - ts) / 86400)
        if age_days > max_days:
            issues.append(ReminderIssue(key=key, last_rotated=ts, days_overdue=age_days - max_days))
    return sorted(issues, key=lambda i: i.key)

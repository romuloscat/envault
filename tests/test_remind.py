import time
import pytest
from click.testing import CliRunner
from envault.remind import record_rotation, remove_reminder, check_reminders, RemindError
from envault.cli_remind import remind_cmd


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / ".envault")


def test_record_and_check_not_overdue(vault_file):
    record_rotation(vault_file, "API_KEY")
    issues = check_reminders(vault_file, max_days=90)
    assert issues == []


def test_check_overdue(vault_file):
    old_ts = time.time() - (100 * 86400)  # 100 days ago
    record_rotation(vault_file, "DB_PASS", ts=old_ts)
    issues = check_reminders(vault_file, max_days=90)
    assert len(issues) == 1
    assert issues[0].key == "DB_PASS"
    assert issues[0].days_overdue >= 9


def test_check_multiple_keys_sorted(vault_file):
    old = time.time() - (200 * 86400)
    record_rotation(vault_file, "Z_KEY", ts=old)
    record_rotation(vault_file, "A_KEY", ts=old)
    issues = check_reminders(vault_file, max_days=90)
    assert [i.key for i in issues] == ["A_KEY", "Z_KEY"]


def test_remove_reminder(vault_file):
    record_rotation(vault_file, "TOKEN")
    remove_reminder(vault_file, "TOKEN")
    issues = check_reminders(vault_file, max_days=0)
    assert all(i.key != "TOKEN" for i in issues)


def test_remove_missing_raises(vault_file):
    with pytest.raises(RemindError):
        remove_reminder(vault_file, "GHOST")


def test_check_empty_vault(vault_file):
    issues = check_reminders(vault_file, max_days=30)
    assert issues == []


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_record(runner, vault_file):
    result = runner.invoke(remind_cmd, ["record", "MY_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output


def test_cli_check_clean(runner, vault_file):
    record_rotation(vault_file, "CLEAN_KEY")
    result = runner.invoke(remind_cmd, ["check", "--vault", vault_file, "--days", "90"])
    assert result.exit_code == 0
    assert "within rotation policy" in result.output


def test_cli_check_overdue(runner, vault_file):
    old = time.time() - (200 * 86400)
    record_rotation(vault_file, "OLD_KEY", ts=old)
    result = runner.invoke(remind_cmd, ["check", "--vault", vault_file, "--days", "90"])
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output


def test_cli_remove_missing(runner, vault_file):
    result = runner.invoke(remind_cmd, ["remove", "NOPE", "--vault", vault_file])
    assert result.exit_code != 0

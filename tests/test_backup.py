"""Tests for envault.backup."""

import pytest
from pathlib import Path

from envault.backup import export_backup, import_backup, BackupError
from envault.store import set_secret, get_secret, _load_raw
from envault.crypto import decrypt


PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / "vault.json"


@pytest.fixture
def backup_file(tmp_path):
    return tmp_path / "backup.env.bak"


def _populate(vault_file):
    set_secret(vault_file, PASSWORD, "KEY1", "value1")
    set_secret(vault_file, PASSWORD, "KEY2", "value2")


def test_export_creates_file(vault_file, backup_file):
    _populate(vault_file)
    result = export_backup(vault_file, PASSWORD, backup_file)
    assert result == backup_file
    assert backup_file.exists()
    assert len(backup_file.read_text()) > 0


def test_export_content_is_encrypted(vault_file, backup_file):
    _populate(vault_file)
    export_backup(vault_file, PASSWORD, backup_file)
    token = backup_file.read_text().strip()
    # Should not contain plaintext values
    assert "value1" not in token
    assert "KEY1" not in token


def test_export_decryptable(vault_file, backup_file):
    import json
    _populate(vault_file)
    export_backup(vault_file, PASSWORD, backup_file)
    token = backup_file.read_text().strip()
    plaintext = decrypt(token, PASSWORD)
    payload = json.loads(plaintext)
    assert "vault" in payload
    assert "version" in payload


def test_import_restores_secrets(vault_file, backup_file, tmp_path):
    _populate(vault_file)
    export_backup(vault_file, PASSWORD, backup_file)

    new_vault = tmp_path / "new_vault.json"
    count = import_backup(backup_file, PASSWORD, new_vault, overwrite=True)
    assert count == 2
    assert get_secret(new_vault, PASSWORD, "KEY1") == "value1"
    assert get_secret(new_vault, PASSWORD, "KEY2") == "value2"


def test_import_wrong_password_raises(vault_file, backup_file, tmp_path):
    _populate(vault_file)
    export_backup(vault_file, PASSWORD, backup_file)
    new_vault = tmp_path / "new_vault.json"
    with pytest.raises(BackupError, match="Failed to decrypt"):
        import_backup(backup_file, "wrong-password", new_vault)


def test_import_missing_file_raises(tmp_path):
    vault = tmp_path / "vault.json"
    missing = tmp_path / "missing.bak"
    with pytest.raises(BackupError, match="not found"):
        import_backup(missing, PASSWORD, vault)


def test_import_no_overwrite_preserves_existing(vault_file, backup_file, tmp_path):
    _populate(vault_file)
    export_backup(vault_file, PASSWORD, backup_file)

    new_vault = tmp_path / "new_vault.json"
    set_secret(new_vault, PASSWORD, "KEY1", "existing_value")

    import_backup(backup_file, PASSWORD, new_vault, overwrite=False)
    # Existing key should not be overwritten
    assert get_secret(new_vault, PASSWORD, "KEY1") == "existing_value"
    assert get_secret(new_vault, PASSWORD, "KEY2") == "value2"

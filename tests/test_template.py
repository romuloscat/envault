import pytest
from pathlib import Path
from envault.template import render_string, render_file, TemplateError
from envault.store import set_secret


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / "vault.json")


PASSWORD = "test-password"


def test_render_single_placeholder(vault_file):
    set_secret(vault_file, "DB_HOST", "localhost", PASSWORD)
    result = render_string("host={{ DB_HOST }}", PASSWORD, vault_file)
    assert result == "host=localhost"


def test_render_multiple_placeholders(vault_file):
    set_secret(vault_file, "USER", "admin", PASSWORD)
    set_secret(vault_file, "PASS", "secret", PASSWORD)
    result = render_string("{{USER}}:{{PASS}}", PASSWORD, vault_file)
    assert result == "admin:secret"


def test_render_missing_key_raises(vault_file):
    with pytest.raises(TemplateError, match="MISSING_KEY"):
        render_string("value={{MISSING_KEY}}", PASSWORD, vault_file)


def test_render_no_placeholders(vault_file):
    result = render_string("no placeholders here", PASSWORD, vault_file)
    assert result == "no placeholders here"


def test_render_file(tmp_path, vault_file):
    set_secret(vault_file, "API_URL", "https://api.example.com", PASSWORD)
    src = tmp_path / "template.txt"
    dst = tmp_path / "output.txt"
    src.write_text("endpoint={{ API_URL }}")
    count = render_file(str(src), str(dst), PASSWORD, vault_file)
    assert count == 1
    assert dst.read_text() == "endpoint=https://api.example.com"


def test_render_file_missing_key_raises(tmp_path, vault_file):
    src = tmp_path / "template.txt"
    dst = tmp_path / "output.txt"
    src.write_text("val={{NOPE}}")
    with pytest.raises(TemplateError):
        render_file(str(src), str(dst), PASSWORD, vault_file)
    assert not dst.exists()


def test_render_multiple_missing_keys_listed(vault_file):
    with pytest.raises(TemplateError) as exc_info:
        render_string("{{FOO}} {{BAR}}", PASSWORD, vault_file)
    msg = str(exc_info.value)
    assert "FOO" in msg and "BAR" in msg

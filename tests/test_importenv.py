"""Tests for envault.importenv."""

import json
import pytest
from envault.importenv import parse_dotenv, parse_json, import_secrets
from envault.store import get_secret


# --- parse_dotenv ---

def test_parse_dotenv_simple():
    text = "FOO=bar\nBAZ=qux\n"
    assert parse_dotenv(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_dotenv_strips_double_quotes():
    assert parse_dotenv('KEY="hello world"') == {"KEY": "hello world"}


def test_parse_dotenv_strips_single_quotes():
    assert parse_dotenv("KEY='hello'") == {"KEY": "hello"}


def test_parse_dotenv_ignores_comments():
    text = "# comment\nFOO=1\n"
    assert parse_dotenv(text) == {"FOO": "1"}


def test_parse_dotenv_ignores_blank_lines():
    text = "\nFOO=1\n\nBAR=2\n"
    assert parse_dotenv(text) == {"FOO": "1", "BAR": "2"}


def test_parse_dotenv_skips_invalid_lines():
    text = "INVALID LINE\nFOO=bar\n"
    assert parse_dotenv(text) == {"FOO": "bar"}


# --- parse_json ---

def test_parse_json_basic():
    data = json.dumps({"A": "1", "B": "2"})
    assert parse_json(data) == {"A": "1", "B": "2"}


def test_parse_json_coerces_values():
    data = json.dumps({"NUM": 42, "FLAG": True})
    result = parse_json(data)
    assert result["NUM"] == "42"
    assert result["FLAG"] == "True"


def test_parse_json_rejects_non_object():
    with pytest.raises(ValueError, match="top-level object"):
        parse_json(json.dumps(["a", "b"]))


# --- import_secrets integration ---

def test_import_secrets_dotenv(tmp_path):
    env_file = tmp_path / "sample.env"
    env_file.write_text("ALPHA=one\nBETA=two\n")
    vault = str(tmp_path / "vault.json")
    count = import_secrets(str(env_file), "dotenv", vault, "pass")
    assert count == 2
    assert get_secret(vault, "pass", "ALPHA") == "one"
    assert get_secret(vault, "pass", "BETA") == "two"


def test_import_secrets_json(tmp_path):
    json_file = tmp_path / "secrets.json"
    json_file.write_text(json.dumps({"X": "10", "Y": "20"}))
    vault = str(tmp_path / "vault.json")
    count = import_secrets(str(json_file), "json", vault, "pass")
    assert count == 2
    assert get_secret(vault, "pass", "X") == "10"


def test_import_secrets_unsupported_format(tmp_path):
    f = tmp_path / "data.toml"
    f.write_text("key = 'val'\n")
    with pytest.raises(ValueError, match="Unsupported"):
        import_secrets(str(f), "toml", str(tmp_path / "vault.json"), "pass")
